"""LNCS-size rendering of Figure3_horizontale (1 x 4 layout, one panel per encoder).

Derived from original/redraw_figure3_horizontale.py (supplied with SelectNorm_Figure3_Horizontale.zip).
Layout, colours, markers, legend, row order, vertical offsets, AUC axis and the 0.5 line are unchanged.
Changes: (1) data are read from figure3_data_full.csv, built from the archived ../mechanism_table.csv, so
the target-label reference and its interval are plotted at full precision instead of the two decimals of
Tables 3 and S4 (the supplied figure3_data.csv agrees with it at its precision); (2) the physical size is
4.8 in (LNCS text width) with font and marker sizes adapted for 1:1 printing.
Run from the paper folder: python3 figures/figure3_horizontale/redraw_figure3_lncs.py
"""
from pathlib import Path
import csv
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

P=Path(__file__).resolve().parent
rows=list(csv.DictReader((P/'figure3_data_full.csv').open()))
assert len(rows)==16
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':7,
 'axes.labelsize':7,'axes.titlesize':7.6,'xtick.labelsize':6.5,
 'ytick.labelsize':7,'pdf.fonttype':42,'axes.linewidth':.6,
 'xtick.major.width':.6,'xtick.major.size':2.5})
series=[('auc_pi',r'$\hat\pi$: disagreement | unlabelled target','#0072B2','o',.24),
 ('auc_rho',r'$\hat\rho$: winning view | source labels','#D55E00','s',0),
 ('auc_rho_target',r'$\hat\rho$: winning view | target-label CV reference','#009E73','^',-.24)]
fig,axes=plt.subplots(1,4,figsize=(4.8,2.12),sharex=True,sharey=True)
for ax,enc in zip(axes.flat,['mE5','XLM-R','LaBSE','MARBERTv2']):
 for j,s in enumerate(['S3','S4','S5','S6']):
  y=3-j
  if j%2==0:ax.axhspan(y-.43,y+.43,color='#f4f5f7',zorder=0)
  r=next(a for a in rows if a['encoder']==enc and a['set']==s)
  for key,label,color,marker,offset in series:
   val,lo,hi=[float(r[key+suffix]) for suffix in ['', '_lo','_hi']]
   assert lo<=val<=hi
   ax.errorbar(val,y+offset,xerr=np.array([[val-lo],[hi-val]]),
    fmt=marker,color=color,markersize=3.4,capsize=1.5,elinewidth=.85,
    markerfacecolor='white' if marker=='s' else color,markeredgewidth=.8,zorder=3)
 ax.axvline(.5,color='#777777',ls='--',lw=.7,zorder=1)
 ax.set_title(enc,pad=4,fontweight='semibold')
 ax.set_xlim(.33,.80);ax.set_xticks([.4,.5,.6,.7,.8]);ax.set_ylim(-.5,3.5)
 ax.set_yticks([3,2,1,0],['$S_3$','$S_4$','$S_5$','$S_6$'])
 ax.tick_params(axis='y',length=0,labelleft=(enc=='mE5'),pad=3)
 ax.tick_params(axis='x',labelbottom=True)
 ax.set_xlabel('AUC',labelpad=1.5)
 ax.spines[['top','right','left']].set_visible(False)
handles=[Line2D([],[],marker=m,color=c,ls='-',lw=.85,markersize=3.6,
 markerfacecolor='white' if m=='s' else c,label=l) for k,l,c,m,o in series]
fig.legend(handles=handles,loc='upper left',bbox_to_anchor=(.065,1.01),
 frameon=False,ncol=1,fontsize=6.8,handlelength=2,labelspacing=.3)
fig.subplots_adjust(left=.065,right=.99,top=.66,bottom=.16,wspace=.16)
for ext in ['pdf','png']:
 fig.savefig(P/f'Figure3_horizontale.{ext}',bbox_inches='tight',dpi=300,pad_inches=.02)
plt.close(fig)
print('16 encoder-corpus cells; 48 estimates at archived full precision.')
