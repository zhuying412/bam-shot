import re
import argparse
from .bam import tview_bam
from .img import plot_bam


def get_options():
    parser = argparse.ArgumentParser(description='SpliceAI Wrapper')
    parser.add_argument('--bam', '-i', required=True, help='path to the input BAM file')
    parser.add_argument('--ref', '-r', required=True, help='path to the input reference fasta file')
    parser.add_argument('--img', '-o', required=True, help='path to the output IMAGE file')
    parser.add_argument('--pos', '-p', required=True, help='position for samtools format, such as chr:pos or chr:start-end')
    parser.add_argument('--ext', '-e', type=int, default=50, help='extend length base on position, defaults to 50')
    parser.add_argument('--depth', '-d', type=int, default=100, help='max reads depth, defaults to 100')
    parser.add_argument('--title', '-t', help='image title, defaults to "postion" value')
    parser.add_argument('--ref_with_ins', '-ins', action='store_true', help='refenece with insertion')
    parser.add_argument('--dpi', '-dpi', type=int, default=200, help='image DPI for png, defaults to 200')
    return parser.parse_args()


def main():
    args = get_options()
    pos = re.split('-|:', args.pos)
    if len(pos) in [2, 3]:
        chrom, start = pos[0], int(pos[1])
        end = int(pos[1]) if len(pos) == 2 else int(pos[2])
    else:
        raise Exception("-p/--pos must be chr:pos or chr:start-end format")
    title = args.title or args.pos
    reference, consensus, reads = tview_bam(bam=args.bam, ref=args.ref, chrom=chrom, start=start, end=end, extend=args.ext, depth=args.depth, ref_with_ins=args.ref_with_ins)
    plot_bam(reference=reference, consensus=consensus, reads=reads, extend=args.ext, img=args.img, title=title, dpi=args.dpi)


if __name__ == '__main__':
    main()
