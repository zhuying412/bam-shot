import io
import os

from matplotlib import pyplot as plt
from .bam import tview_bam


class Image:
    ColorMap = {'A': 'C2', 'T': 'C3', 'G': 'C4', 'C': 'C0', 'D': 'C7'}

    def __init__(self, title: str, reference: str, consensus: str, reads: list[str], extend: int):
        self.title = title
        self.reference = reference
        self.consensus = consensus
        self.reads = reads
        self.length = len(self.reference)
        self.depth = len(self.reads)
        self.extend = extend

    @classmethod
    def get_color(cls, base: str = None):
        return cls.ColorMap.get(base, cls.ColorMap.get('D'))

    def set_global(self):
        plt.figure(figsize=(self.length / 8, self.depth / 6))
        # plt.rc('font', family='DejaVu Sans Mono')
        plt.xlim((0, self.length + 1))
        plt.ylim((-4, self.depth + 1))
        plt.xticks([])
        yticks, ynames = [-2, -1], ['Reference', 'Consensus']
        for i in range(10, self.depth + 1, 10):
            yticks.append(i)
            ynames.append(f'{i}X')
        plt.yticks(yticks, ynames)
        ax = plt.gca()
        ax.invert_yaxis()
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.spines["bottom"].set_visible(False)
        ax.set_title(self.title)

    def write_base_xy(self, read: str, y: int, x_dict: dict, y_dict: dict, bases: set):
        for i in range(self.length):
            base = read[i].upper().replace('*', '-')
            if base != " ":
                bases.add(base)
                x_dict.setdefault(base, list()).append(i + 1)
                y_dict.setdefault(base, list()).append(y)

    def plot_bases(self):
        x_dict, y_dict, bases = dict(), dict(), set()
        self.write_base_xy(self.reference, -2, x_dict, y_dict, bases)
        self.write_base_xy(self.consensus, -1, x_dict, y_dict, bases)
        for i in range(self.depth):
            self.write_base_xy(self.reads[i], i + 1, x_dict, y_dict, bases)
        for base in bases:
            plt.scatter(x_dict.get(base), y_dict.get(base), c=self.get_color(base), linewidths=0.5, marker=f'${base}$')

    def plot_hlines(self):
        plt.hlines(0, xmin=0, xmax=self.length)

    def plot_arrow(self):
        plt.arrow(self.extend + 1, -4, 0, 1, head_width=0.2, lw=2, color='red', length_includes_head=True)

    def plot(self, img, dpi: int, format: str):
        self.set_global()
        self.plot_bases()
        self.plot_hlines()
        self.plot_arrow()
        plt.savefig(img, dpi=dpi, format=format, bbox_inches='tight')
        plt.close()


def plotBAM(img, bam: str, ref: str, chrom: str, start: int, end: int, extend: int, depth: int = None, title: str = "", dpi: int = 200, format: str = 'png'):
    reference, consensus, reads = tview_bam(bam=bam, ref=ref, chrom=chrom, start=start, end=end, extend=extend, depth=depth)
    Image(title=title, reference=reference, consensus=consensus, reads=reads, extend=extend).plot(img=img, dpi=dpi, format=format)
