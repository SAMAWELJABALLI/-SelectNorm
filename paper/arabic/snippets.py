"""Pre-render the Arabic-script snippets of the LNCS paper as vector PDF pages.

The LNCS template is compiled with pdfLaTeX (T1, newtx), which cannot shape Arabic. Each snippet is
typeset once with LuaLaTeX and the Amiri font (SIL OFL), cropped to its TeX box, and included in the
paper with \\ar{key}; the baseline is kept by lowering the graphic by its depth ratio.
Mixed runs (Latin words left in Latin script by the normaliser) are set left-to-right inside the
right-to-left line. Normaliser outputs are copied from results/qualitative/examples_mE5.json.
Usage: python3 snippets.py && lualatex arabic.tex   (writes arabic.pdf and ar_index.tex)
"""
import json, os, re

HERE = os.path.dirname(os.path.abspath(__file__))
EX = json.load(open(os.path.join(HERE, '..', '..', 'results', 'qualitative', 'examples_mE5.json')))
EX = {r['id']: r for r in EX}

SNIPS = [
    ('ain', 'ع'), ('hha', 'ح'), ('qaf', 'ق'), ('kha', 'خ'), ('shin', 'ش'), ('ha', 'ه'),
    ('laugh', 'ههه'), ('ma', 'ما'), ('la', 'لا'),
    # normaliser outputs of the quoted examples (TSAC: LGPL-3.0; NArabizi: UD release, CC BY-SA 4.0)
    ('exAa', EX['S3_tsac_lat:1091']['norm']), ('exAb', EX['S3_tsac_lat:40']['norm']),
    ('exBa', EX['S5_narabizi:240']['norm']), ('exBb', EX['S5_narabizi:298']['norm']),
]
ARABIC = re.compile(r'[؀-ۿ]')


def runs(s):
    """Split into Arabic and non-Arabic runs; spaces and punctuation join the Arabic stream."""
    out, cur, cur_ar = [], '', None
    for tok in re.split(r'(\s+)', s):
        if not tok:
            continue
        is_lat = bool(re.search(r'[A-Za-z]', tok))
        kind = not is_lat
        if cur_ar is None or kind == cur_ar or tok.isspace():
            cur += tok
            cur_ar = kind if cur_ar is None and not tok.isspace() else cur_ar
        else:
            out.append((cur_ar, cur))
            cur, cur_ar = tok, kind
    out.append((cur_ar, cur))
    return out


def tex(s):
    parts = []
    for ar, t in runs(s):
        t = t.replace('’', '\\char"2019{}')
        parts.append(t if ar else '\\hbox{\\textdir TLT\\latinfont ' + t.strip() + '}' + (' ' if t.endswith(' ') else ''))
    return ''.join(parts)


def main():
    lines = [r'\documentclass{article}', r'\usepackage{fontspec}',
             r'\newfontfamily\arabicfont[Script=Arabic,Path=fonts/,Extension=.ttf,UprightFont=*-Regular,BoldFont=*-Bold,Scale=1.1]{Amiri}',
             r'\newfontfamily\latinfont{TeX Gyre Termes}',
             r'\hoffset=-1in \voffset=-1in \topskip=0pt \parindent=0pt',
             r'\newwrite\idx \immediate\openout\idx=ar_index.tex',
             r'\newcount\pg \pg=0',
             r'\def\snip#1#2{\setbox0\hbox{\textdir TRT\arabicfont #2}\global\advance\pg by 1 '
             r'\pagewidth=\wd0 \pageheight=\dimexpr\ht0+\dp0\relax '
             r'\immediate\write\idx{\string\arsnip{#1}{\the\pg}{\the\numexpr\dp0*1000/(\ht0+\dp0)\relax}}'
             r'\shipout\vbox{\box0}}',
             r'\begin{document}', r'\fontsize{10}{12}\selectfont']
    for k, s in SNIPS:
        lines.append(r'\snip{%s}{%s}' % (k, tex(s)))
    lines += [r'\immediate\closeout\idx', r'\end{document}']
    body = '\n'.join(lines)
    open(os.path.join(HERE, 'arabic.tex'), 'w').write(body + '\n')


if __name__ == '__main__':
    main()
