import argparse
import io
import re
from bam_shot import plotBAM


def main(args):
    pos = re.split(r':|-', args.pos)
    chrom, start = pos[0], int(pos[1])
    end = int(pos[2]) if len(pos) > 2 else start
    title = f'{args.sample} {chrom}:{start}-{end}'
    buffer = io.BytesIO()
    plotBAM(
        img=buffer,
        bam=args.bam,
        ref=args.ref,
        chrom=chrom,
        start=start,
        end=end,
        extend=args.extend,
        depth=args.depth,
        title=title,
    )
    fh = open('test.png', 'wb')
    fh.write(buffer.getvalue())
    fh.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser('BAM View')
    parser.add_argument('--bam', '-i', help='input BAM file')
    parser.add_argument('--ref', '-r', help='refenece FASTA file')
    parser.add_argument('--pos', '-p', help='the position of center site')
    parser.add_argument('--extend', '-e', type=int, default=50, help='the extend length from center site')
    parser.add_argument('--depth', '-d', type=int, required=False, help='the max depth from center site')
    parser.add_argument('--sample', '-s', default='', help='sample name')
    parser.set_defaults(func=main)
    args = parser.parse_args()
    args.func(args)
