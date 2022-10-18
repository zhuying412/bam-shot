import re
from enum import Enum
from matplotlib import pyplot as plt
from .bam import tview_bam


class BaseColor(Enum):
    A = 'C2'
    T = 'C3'
    G = 'C4'
    C = 'C0'
    D = 'C7'

    @classmethod
    def get(cls, base: str) -> str:
        if base == 'A':
            return str(cls.A)
        if base == 'T':
            return str(cls.T)
        if base == 'G':
            return str(cls.G)
        if base == 'C':
            return str(cls.C)
        return str(cls.D)


class Image:
    OptionMap = {
        'A': {'c': 'C2'},
        'T': {'c': 'C3'},
        'G': {'c': 'C4'},
        'C': {'c': 'C0'},
        'I': {'c': "C5", 'marker': 7},
        'D': {'c': 'C7'}
    }

    def __init__(self, title: str, reference: list[str], consensus: list[str], reads: list[list[str]], extend: int):
        self.title = title
        self.reference = reference
        self.consensus = consensus
        self.reads = reads
        self.length = len(self.reference)
        self.depth = len(self.reads)
        self.extend = extend

    @classmethod
    def get_options(cls, base: str = None, **kwargs):
        options = cls.OptionMap.get(base, cls.OptionMap.get('D'))
        kwargs.update(options)
        return kwargs

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

    def write_base_xy(self, read: list[str], y: int, x_dict: dict, y_dict: dict):
        for i in range(self.length):
            base = read[i]
            if base != " ":
                x_dict.setdefault(base[0], list()).append(i + 1)
                y_dict.setdefault(base[0], list()).append(y)
                if len(base) > 1:
                    x_dict.setdefault(base[-1], list()).append(i + 1.5)
                    y_dict.setdefault(base[-1], list()).append(y)

    def plot_bases(self):
        x_dict, y_dict = dict(), dict()
        self.write_base_xy(self.reference, -2, x_dict, y_dict)
        self.write_base_xy(self.consensus, -1, x_dict, y_dict)
        for i in range(self.depth):
            self.write_base_xy(self.reads[i], i + 1, x_dict, y_dict)
        for base in x_dict.keys():
            plt.scatter(x_dict.get(base), y_dict.get(base), **self.get_options(base, marker=f'${base}$'))

    def plot_hlines(self):
        plt.hlines(0, xmin=0, xmax=self.length)

    def plot_arrow(self):
        x = self.extend + 1
        x += len(list(filter(lambda x:x == '-', self.reference[:self.extend])))
        plt.arrow(x, -4, 0, 1, head_width=0.2, lw=2, color='red', length_includes_head=True)

    def plot(self, img, dpi: int, format: str):
        self.set_global()
        self.plot_bases()
        self.plot_hlines()
        self.plot_arrow()
        plt.savefig(img, dpi=dpi, format=format, bbox_inches='tight')
        plt.close()


def bam2img(img, bam: str, ref: str, chrom: str, start: int, end: int, extend: int, depth: int = None, title: str = "", ref_with_ins=True, dpi: int = 200, format: str = 'png'):
    reference, consensus, reads = tview_bam(bam=bam, ref=ref, chrom=chrom, start=start, end=end, extend=extend, depth=depth, ref_with_ins=ref_with_ins)
    Image(title=title, reference=reference, consensus=consensus, reads=reads, extend=extend).plot(img=img, dpi=dpi, format=format)
