"""Figuras estáticas sin dependencias de red desde datos auditados."""
from html import escape
from itertools import groupby
import math


COLORS = ('#175b83', '#ad5721', '#22806c', '#814b9e', '#93512e')


class Figure:
    def __init__(self, title, subtitle, height=640):
        self.height = height
        self.parts = ['<svg xmlns="http://www.w3.org/2000/svg" width="1200" '
                      f'height="{height}" viewBox="0 0 1200 {height}">',
                      '<rect width="100%" height="100%" fill="white"/>']
        self.text(55, 55, title, 29, bold=True)
        self.text(55, 85, subtitle, 16, color='#47566b')

    def text(self, x, y, value, size=15, anchor='start', color='#172a41', bold=False):
        weight = '700' if bold else '400'
        self.parts.append(f'<text x="{x}" y="{y}" font-family="Arial, sans-serif" '
                          f'font-weight="{weight}" font-size="{size}" text-anchor="{anchor}" '
                          f'fill="{color}">{escape(str(value))}</text>')

    def line(self, x1, y1, x2, y2, color='#dbe4ec', width=1, dash=''):
        dashes = f' stroke-dasharray="{dash}"' if dash else ''
        self.parts.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" '
                          f'stroke="{color}" stroke-width="{width}"{dashes}/>')

    def rect(self, x, y, w, h, color, edge='none'):
        self.parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" '
                          f'fill="{color}" stroke="{edge}"/>')

    def point(self, x, y, color, radius=5):
        self.parts.append(f'<circle cx="{x}" cy="{y}" r="{radius}" fill="{color}"/>')

    def series(self, points, x, y, color, dash=''):
        dashes = f' stroke-dasharray="{dash}"' if dash else ''
        for valid, segment in groupby(points, key=lambda p: p[1] is not None and math.isfinite(p[1])):
            if valid:
                coords = ' '.join(f'{x(a):.2f},{y(b):.2f}' for a, b in segment)
                self.parts.append(f'<polyline points="{coords}" fill="none" '
                                  f'stroke="{color}" stroke-width="2.4"{dashes}/>')

    def axes(self, box, xticks, yticks, xlabel, ylabel, label_xticks=True):
        left, top, width, height = box
        x = lambda v: left + width * (v - xticks[0]) / (xticks[-1] - xticks[0])
        y = lambda v: top + height * (yticks[-1] - v) / (yticks[-1] - yticks[0])
        for t in xticks:
            self.line(x(t), top, x(t), top + height)
            if label_xticks:
                self.text(x(t), top + height + 22, t, 13, 'middle')
        for t in yticks:
            self.line(left, y(t), left + width, y(t))
            self.text(left - 12, y(t) + 4, t, 13, 'end')
        self.text(left, top - 13, ylabel, 15, bold=True)
        self.text(left + width / 2, top + height + 44, xlabel, 14, 'middle')
        return x, y

    def legend(self, items, x=100, y=112, spacing=165):
        for i, (label, color, dash) in enumerate(items):
            px = x + spacing * i
            self.line(px, y - 5, px + 27, y - 5, color, 3, dash)
            self.text(px + 35, y, label, 15)

    def save(self, path, note):
        self.text(55, self.height - 22, note, 14, color='#47566b')
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text('\n'.join([*self.parts, '</svg>', '']), encoding='utf-8', newline='\n')
