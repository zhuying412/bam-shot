import io
from typing import Optional, Union
from .bam import tview_bam
from .img import plot_bam


def bam2img(bam: str, ref: str, chrom: str, start: int, end: int, extend: int, img: Union[str, io.BytesIO], depth: Optional[int] = None, title: str = "", ref_with_ins=True, dpi: int = 200):
    reference, consensus, reads = tview_bam(bam=bam, ref=ref, chrom=chrom, start=start, end=end, extend=extend, depth=depth, ref_with_ins=ref_with_ins)
    plot_bam(reference=reference, consensus=consensus, reads=reads, extend=extend, img=img, title=title, dpi=dpi)
