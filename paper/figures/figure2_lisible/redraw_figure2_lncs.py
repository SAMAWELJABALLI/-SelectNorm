"""LNCS-size rendering of Figure2_lisible (compact 2x2 version only).

Derived from original/redraw_figure2.py (supplied with SelectNorm_Figure2_Lisible.zip). Data, methods,
colours, markers, line styles, y-ranges, legend and the below-panel B0 notes are unchanged; only the
physical size (4.8 in = LNCS text width), font sizes, marker sizes and spacing are adapted so that the
figure is printed at 1:1 scale with legible text (>= 6.3 pt). Reads ../pareto.csv (identical to
original/pareto_original.csv). Run from the paper folder: python3 figures/figure2_lisible/redraw_figure2_lncs.py
"""
from pathlib import Path
import csv
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

HERE = Path(__file__).resolve().parent
ROWS = list(csv.DictReader((HERE.parent / 'pareto.csv').open()))
assert len(ROWS) == 108
SETS = [('S3_tsac_lat', r'$S_3$ · TSAC-Lat (Tunisian)'),
        ('S4_tunizi', r'$S_4$ · TUNIZI (Tunisian)'),
        ('S5_narabizi', r'$S_5$ · NArabizi (Algerian)'),
        ('S6_myc_lat', r'$S_6$ · MYC-Lat (Moroccan)')]
METHODS = [
 ('B5_selectnorm_adapt', 'SelectNorm · tuned', '#0072B2', 'o', '-'),
 ('B4_direct_gain', 'B4 · direct gain', '#D55E00', '^', '--'),
 ('B5_selectnorm_adapt_theory', 'SelectNorm · Bayes', '#009E73', 'v', '-.'),
 ('B3_conf', 'B3 · confidence', '#CC79A7', 's', ':')]
BASES = [('B0_original','B0 · original','X'),('B1_always','B1 · always','D'),
         ('R_two_view_ensemble','R · two views','P')]
plt.rcParams.update({'font.family':'DejaVu Sans', 'font.size':7,
 'axes.labelsize':7, 'axes.titlesize':7.6, 'xtick.labelsize':6.5,
 'ytick.labelsize':6.5, 'pdf.fonttype':42, 'ps.fonttype':42,
 'axes.linewidth':.6, 'xtick.major.width':.6, 'ytick.major.width':.6,
 'xtick.major.size':2.5, 'ytick.major.size':2.5})

def selected(s, m):
    return sorted([r for r in ROWS if r['set']==s and r['system']==m],
                  key=lambda r: float(r['lam'] or 0))

def frame(ax):
    ax.spines[['top','right']].set_visible(False)
    ax.grid(axis='y',color='#e5e7eb',linewidth=.65)
    ax.set_axisbelow(True)
    ax.set_xlim(.90,2.12)
    ax.set_xticks([1,1.25,1.5,1.75,2])

def curve(ax,s,m,color,marker,ls,sd=True,emphasis=False):
    r=selected(s,m)
    x=np.array([float(a['cost']) for a in r]);y=np.array([float(a['f1']) for a in r])
    err=np.array([float(a['f1_sd']) for a in r])
    ax.plot(x,y,color=color,marker=marker,linestyle=ls,linewidth=1.4 if emphasis else 1.0,
            markersize=3.6 if emphasis else 3.0,zorder=4 if emphasis else 3)
    if sd:
        ax.errorbar(x,y,yerr=err,fmt='none',ecolor=color,alpha=.42,
                    elinewidth=.6,capsize=1.4,zorder=2)

def base(ax,s,full=False):
    for m,label,marker in BASES:
        r=selected(s,m)[0];x=float(r['cost']);y=float(r['f1'])
        if m=='B0_original' and not full and s!='S6_myc_lat':
            # A textual reference outside the axes, not an invented boundary point.
            continue
        ax.plot(x,y,marker=marker,markersize=4.6,color='#424242',
                markerfacecolor='white' if m=='B1_always' else '#424242',
                linestyle='none',zorder=5)

# Compact all-methods version: genuine overlaps retained; annotation arrows removed.
fig,axs=plt.subplots(2,2,figsize=(4.8,3.35))
for ax,(s,title) in zip(axs.flat,SETS):
    frame(ax)
    for m,label,col,mark,ls in METHODS: curve(ax,s,m,col,mark,ls,emphasis=m=='B5_selectnorm_adapt')
    base(ax,s)
    ax.set_title(title,pad=4)
    lohi={'S3_tsac_lat':(73,84),'S4_tunizi':(61.8,68.4),
          'S5_narabizi':(65.4,71.8),'S6_myc_lat':(52.3,55.0)}
    ax.set_ylim(*lohi[s]);ax.set_ylabel('Macro-F1')
    ax.set_xlabel('Estimated cost (original pass = 1)',labelpad=1.5)
    r=selected(s,'B0_original')[0]
    note=(f"B0: {float(r['f1']):.1f} at cost 1.00 (outside y-range)"
          if s!='S6_myc_lat' else 'B0, B1 and R shown at their recorded values')
    ax.text(0,-.47,note,transform=ax.transAxes,fontsize=6.3,color='#4b5563')
handles=[Line2D([],[],color=c,marker=mk,ls=ls,label=lab,linewidth=1.5)
         for _,lab,c,mk,ls in METHODS]
handles += [Line2D([],[],color='#424242',marker=mk,ls='',label=lab,
                  markerfacecolor='white' if m=='B1_always' else '#424242') for m,lab,mk in BASES]
fig.legend(handles=handles,loc='upper center',ncol=4,frameon=False,fontsize=6.6,
           bbox_to_anchor=(.5,1.02),columnspacing=1.2,handlelength=2.2,handletextpad=.5)
fig.subplots_adjust(top=.855,bottom=.15,left=.085,right=.99,hspace=1.0,wspace=.24)
for ext in ['pdf','png']:fig.savefig(HERE/f'Figure2_lisible.{ext}',dpi=300,bbox_inches='tight',pad_inches=.02)
plt.close(fig)
print('Figure2_lisible (LNCS size) redrawn from',len(ROWS),'archived rows; scores unchanged.')

