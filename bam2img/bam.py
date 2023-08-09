import os
import re
from collections import namedtuple
from pysam import FastaFile

BamTview = namedtuple('BamTview', ['reference', 'consensus', 'reads'])


def check_samtools():
    for cmdpath in os.environ['PATH'].split(':'):
        if os.path.isdir(cmdpath) and 'samtools' in os.listdir(cmdpath):
            return
    raise Exception("ERROR: samtools not found, please install it first")


def check_or_create_bai(bam: str):
    bai = re.sub(r'bam$', 'bai', bam)
    if not os.path.exists(bai):
        cmd = f"samtools index {bam}"
        if os.system(cmd) != 0:
            raise Exception(f"Error: run '{cmd}' failed")


def create_cigars(seq: str) -> list[str]:
    cigars = ['M'] * len(seq)
    for i in range(len(seq)):
        if seq[i] == '*':
            cigars[i] = 'I'
    return cigars


def create_reference(ref: str, chrom: str, start: int, end: int, cigars: list[str], ref_with_ins: bool) -> list[str]:
    seq = FastaFile(ref).fetch(reference=chrom, start=start - 1, end=end).upper()
    bases = list()
    i = 0
    for cigar in cigars:
        if cigar == "I":
            if ref_with_ins:
                bases.append('-')
        else:
            bases.append(seq[i])
            i += 1
    return bases


def create_consensus(seq: str, cigars: list[str], ref_with_ins: bool) -> list[str]:
    bases = list()
    for i in range(len(cigars)):
        if cigars[i] == "I":
            if ref_with_ins:
                bases.append(seq[i])
        else:
            bases.append(seq[i])
    return bases


def create_reads(lines: list[str], cigars: list[str], ref_with_ins: bool) -> list[list[str]]:
    reads = list()
    for line in lines:
        line = line.upper()
        bases = list()
        for i in range(len(cigars)):
            base = '-' if line[i] == '*' else line[i]
            if cigars[i] == 'I':
                if ref_with_ins:
                    bases.append(base)
                else:
                    if base not in [' ', '-']:
                        if not bases[-1].endswith('I'):
                            bases[-1] += 'I'
            else:
                bases.append(base)
        reads.append(bases)
    return reads


def tview_bam(bam: str, ref: str, chrom: str, start: int, end: int, extend: int, depth: int = None, ref_with_ins: bool = True) -> tuple[list[str], list[str], list[list[str]]]:
    check_samtools()
    check_or_create_bai(bam)
    start -= extend
    end += extend
    width = end - start + 1
    cmd = f'export COLUMNS={width} && samtools tview -d T -p {chrom}:{start} {bam}'
    lines = [line.rstrip('\n') for line in os.popen(cmd).readlines()]
    if depth:
        lines = lines[0:depth + 3]
    cigars = create_cigars(lines[1])
    reference = create_reference(ref=ref, chrom=chrom, start=start, end=end, cigars=cigars, ref_with_ins=ref_with_ins)
    consensus = create_consensus(seq=lines[2], cigars=cigars, ref_with_ins=ref_with_ins)
    reads = create_reads(lines[3:], cigars=cigars, ref_with_ins=ref_with_ins)
    return reference, consensus, reads
