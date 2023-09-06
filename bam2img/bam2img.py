from enum import Enum
import io
import os
from pathlib import Path
import re
from typing import Optional
from matplotlib import pyplot as plt
from pydantic import BaseModel
from pyfaidx import Fasta

class SNV(BaseModel):
    chrom: str
    pos: int
    ref: str
    alt: str
    gene: Optional[str] = None

    @property
    def name(self) -> str:
        variant = f'{self.chrom}:{self.pos}:{self.ref}:{self.alt}'
        if self.gene:
            return f'{self.gene} {variant}'
        return variant
    
    @classmethod
    def parse_str(cls, text: str) -> 'SNV':
        items = re.split(r':|-', text)
        if len(items) == 4:
            return cls(chrom=items[0], pos=int(items[1]), ref=items[2], alt=items[3])
        if len(items) == 5:
            return cls(gene=items[0], chrom=items[1], pos=int(items[2]), ref=items[3], alt=items[4])
        raise Exception(f'Unknown format: {text}')

class BaseOption(Enum):
    A = {'c': 'C2'}
    T = {'c': 'C3'}
    G = {'c': 'C4'}
    C = {'c': 'C0'}
    I = {'c': "C5", 'marker': 7}
    D = {'c': 'C7'}

    @classmethod
    def get(cls, nt: str, **kwargs) -> dict:
        option = dict()
        match nt:
            case 'A':
                option = cls.A.value
            case 'T':
                option = cls.T.value
            case 'G':
                option = cls.G.value
            case 'C':
                option = cls.C.value
            case 'I':
                option = cls.I.value
            case _:
                option = cls.D.value
        option.update(kwargs)
        return option


class Bam2Img(BaseModel):
    sample: str
    bam_file: Path
    reference_file: Path
    snv: SNV
    extend: int = 50
    depth: Optional[int] = 100
    ref_with_ins: bool = False
    dpi: int = 200

    class Config:
        arbitrary_types_allowed = True

    def check_samtools(self):
        env_paths = [Path(p) for p in os.environ['PATH'].split(':')]
        for path in env_paths:
            if path.exists() and path.is_dir() and (path/'samtools').exists():
                return
        raise Exception("ERROR: samtools not found, please install it first")

    def check_bai(self):
        bai_file = self.bam_file.with_suffix('.bai')
        if not bai_file.exists():
            bai_file = self.bam_file.with_suffix('.bam.bai')
            if not bai_file.exists():
                raise Exception(
                    f"BAM index of {self.bam_file} required, you can create it with: samtools index {self.bam_file}")

    @property
    def start(self) -> int:
        return self.snv.pos - self.extend

    @property
    def end(self) -> int:
        return self.snv.pos + self.extend

    @property
    def width(self) -> int:
        return self.end - self.start + 1

    def get_cigars(self, seq: str) -> list[str]:
        cigars = ['M'] * len(seq)
        for i in range(len(seq)):
            if seq[i] == '*':
                cigars[i] = 'I'
        return cigars

    def get_reference_bases(self, cigars: list[str]) -> list[str]:
        seq = str(Fasta(str(self.reference_file)).get_seq(name=self.snv.chrom, start=self.start, end=self.end)).upper()
        bases = list()
        i = 0
        for cigar in cigars:
            if cigar == "I":
                if self.ref_with_ins:
                    bases.append('-')
            else:
                bases.append(seq[i])
                i += 1
        return bases

    def get_consensus_bases(self, seq: str, cigars: list[str]) -> list[str]:
        bases = list()
        for i in range(len(cigars)):
            if cigars[i] == "I":
                if self.ref_with_ins:
                    bases.append(seq[i])
            else:
                bases.append(seq[i])
        return bases

    def get_reads(self, seq_list: list[str], cigars: list[str]) -> list[list[str]]:
        reads = list()
        for line in seq_list:
            line = line.upper()
            bases = list()
            for i in range(len(cigars)):
                base = '-' if line[i] == '*' else line[i]
                if cigars[i] == 'I':
                    if self.ref_with_ins:
                        bases.append(base)
                    else:
                        if base not in [' ', '-']:
                            if not bases[-1].endswith('I'):
                                bases[-1] += 'I'
                else:
                    bases.append(base)
            reads.append(bases)
        return reads[::-1]

    def do_samtools_tview(self) -> tuple[list[str], list[str], list[list[str]]]:
        self.check_samtools()
        self.check_bai()
        cmd = f'export COLUMNS={self.width} && samtools tview -d T -p {self.snv.chrom}:{self.start} {self.bam_file}'
        lines = [line.rstrip('\n') for line in os.popen(cmd).readlines()]
        if self.depth:
            lines = lines[0:self.depth + 3]
        cigars = self.get_cigars(lines[1])
        reference = self.get_reference_bases(cigars=cigars)
        consensus = self.get_consensus_bases(seq=lines[2], cigars=cigars)
        reads = self.get_reads(seq_list=lines[3:], cigars=cigars)
        return reference, consensus, reads
    
    def get_plot_xy(self, reads: list[list[str]], width: int) -> dict[str, list]:
        data = dict()
        for i, seq in enumerate(reads):
            for j in range(width):
                nt = seq[j]
                if nt != ' ':
                    x,y = j+1, i-2
                    data.setdefault(nt[0], list()).append((x, y))
                    if len(nt) > 1:
                        x += 0.5
                        data.setdefault(nt[-1], list()).append((x, y))
        return data

    def do_plot(self, reference: list[str], consensus: list[str], reads: list[list[str]]) -> io.BytesIO:
        width, depth = len(reference), len(reads)
        plt.figure(figsize=(self.width / 8, max(depth / 6, 2)))
        plt.xlim((0, width + 1))
        plt.ylim((-4, depth + 1))
        plt.xticks([])
        yticks, ynames = list(zip(*[(-2, 'Reference'), (-1, 'Consensus')]+[(i, f'{i}X')for i in range(10, depth + 1, 10)]))
        plt.yticks(yticks, ynames)
        nt_xy_dict = self.get_plot_xy(reads=[reference, consensus, [' ']*width] + reads, width=width)
        for nt, xy in nt_xy_dict.items():
            x, y = zip(*xy)
            plt.scatter(x, y, **BaseOption.get(nt, marker=f'${nt}$'))
        plt.hlines(0, xmin=0, xmax=width)
        arrow_x = self.extend + 1 + len(list(filter(lambda x: x == '-', reference[:self.extend])))
        plt.arrow(arrow_x, -4, 0, 1, head_width=0.2, lw=2,color='red', length_includes_head=True)
        ax = plt.gca()
        ax.invert_yaxis()
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.spines["bottom"].set_visible(False)
        ax.set_title(f'{self.sample} {self.snv.name}')
        img = io.BytesIO()
        plt.savefig(img, dpi=self.dpi, bbox_inches='tight')
        plt.close()
        return img

    def run(self) -> io.BytesIO:
        reference, consensus, reads = self.do_samtools_tview()
        return self.do_plot(reference=reference, consensus=consensus, reads=reads)