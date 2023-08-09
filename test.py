import io
from bam2img import bam2img


def main():
    out = io.BytesIO()
    bam2img(
        bam='test/XY2302027.sorted.bam',
        ref='/project/bioit/database/reference/Homo_sapiens_assembly38.fasta',
        chrom='chr1',
        start=3505398,
        end=3505398,
        extend=50,
        img=out
    )
    with open('tt.png', 'wb') as writer:
        writer.write(out.getvalue())


if __name__ == '__main__':
    main()
