import os
import re
from collections import namedtuple
from pysam import FastaFile

BamTview = namedtuple('BamTview', ['reference', 'consensus', 'reads'])
Cigar = namedtuple('Cigar', ['type', 'length'])


def create_cigars(seq: str) -> list[Cigar]:
    cigars = list()
    for base in seq:
        if base == '*':
            cigar = Cigar(type='I', length=0)
            if cigars and cigars[-1].type == 'I':
                cigar = cigars.pop()
            cigars.append(Cigar(type='I', length=cigar.length + 1))
        else:
            cigar = Cigar(type='M', length=0)
            if cigars and cigars[-1].type == 'M':
                cigar = cigars.pop()
            cigars.append(Cigar(type='M', length=cigar.length + 1))
    return cigars


def read_reference(ref: str, chrom: str, start: int, end: int, cigars: list[Cigar]) -> str:
    seq = FastaFile(ref).fetch(reference=chrom, start=start - 1, end=end).upper()
    reference = ""
    i = 0
    for cigar in cigars:
        for j in range(cigar.length):
            base = '-'
            if cigar.type == 'M':
                base = seq[i]
                i += 1
            reference += base
    return reference


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


def tview_bam(bam: str, ref: str, chrom: str, start: int, end: int, extend: int, depth: int = None) -> BamTview:
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
    reference = read_reference(ref=ref, chrom=chrom, start=start, end=end, cigars=cigars)
    return BamTview(reference=reference, consensus=lines[2], reads=lines[3:])
