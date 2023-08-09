from enum import Enum
import io
from typing import Union
from matplotlib import pyplot as plt


class ImageOption(Enum):
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


def plot_bam(reference: list[str], consensus: list[str], reads: list[list[str]], extend: int, img: Union[str, io.BytesIO], title: str, dpi: int):
    length = len(reference)
    depth = len(reads)
    reads = reads[::-1]
    plt.figure(figsize=(length / 8, max(depth / 6, 2)))
    plt.xlim((0, length + 1))
    plt.ylim((-4, depth + 1))
    plt.xticks([])
    yticks, ynames = [-2, -1], ['Reference', 'Consensus']
    for i in range(10, depth + 1, 10):
        yticks.append(i)
        ynames.append(f'{i}X')
    plt.yticks(yticks, ynames)
    nt_xy_dict = dict()
    for i, seq in enumerate([reference, consensus, [' ']*length] + reads):
        for j in range(length):
            nt = seq[j]
            if nt != ' ':
                nt_x = (j + 1.5) if len(nt) > 1 else (j + 1)
                nt_y = i - 2
                nt_xy_dict.setdefault(nt[-1] if len(nt) > 1 else nt[0], list()).append((nt_x, nt_y))
    for nt, xy in nt_xy_dict.items():
        x, y = zip(*xy)
        plt.scatter(x, y, **ImageOption.get(nt, marker=f'${nt}$'))
    plt.hlines(0, xmin=0, xmax=length)
    arrow_x = extend + 1 + len(list(filter(lambda x: x == '-', reference[:extend])))
    plt.arrow(arrow_x, -4, 0, 1, head_width=0.2, lw=2, color='red', length_includes_head=True)
    ax = plt.gca()
    ax.invert_yaxis()
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["bottom"].set_visible(False)
    ax.set_title(title)
    plt.savefig(img, dpi=dpi, bbox_inches='tight')
    plt.close()
