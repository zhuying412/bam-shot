from pathlib import Path
import argparse
from .bam2img import Bam2Img, SNV


def run_bam2img(args):
    args_vars = dict(vars(args))
    snv = SNV.parse_str(args_vars.pop('variant'))
    args_vars.update({'snv': snv})
    with open(args.out_img, 'wb') as writer:
        img = Bam2Img(**args_vars).run()
        writer.write(img.getvalue())

def get_options():
    parser = argparse.ArgumentParser(description='BAM to Image')
    parser.add_argument('--bam_file', '-i', required=True, type=Path, help='input, path to the input BAM file')
    parser.add_argument('--reference_file', '-r', required=True, type=Path, help='input, path to the input reference fasta file')
    parser.add_argument('--sample', '-s', required=True, help='input, sample, sample name')
    parser.add_argument('--out_img', '-o', required=True, help='output, path to the output IMAGE file')
    parser.add_argument('--variant', '-v', required=True, help='parameter, position for samtools format, such as chr:pos or chrom:pos')
    parser.add_argument('--extend', '-e', type=int, default=50, help='parameter,extend length base on position, defaults to 50')
    parser.add_argument('--depth', '-d', type=int, default=100, help='parameter,max reads depth, defaults to 100')
    parser.add_argument('--dpi', '-dpi', type=int, default=200, help='parameter,image DPI for png, defaults to 200')
    parser.add_argument('--ref_with_ins', '-ins', action='store_true', help='parameter, reference with insertion')
    parser.set_defaults(func=run_bam2img)
    return parser.parse_args()


def main():
    args = get_options()
    args.func(args)