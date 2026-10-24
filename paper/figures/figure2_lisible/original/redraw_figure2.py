"""Redraw archived SelectNorm cost data; no training or score changes.
Run: python redraw_figure2.py. Requires matplotlib and numpy.
"""
from pathlib import Path
import csv
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

HERE = Path(__file__).resolve().parent
ROWS = list(csv.DictReader((HERE / 'pareto_original.csv').open()))
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
plt.rcParams.update({'font.family':'DejaVu Sans', 'font.size':9,
 'axes.labelsize':9, 'axes.titlesize':10, 'xtick.labelsize':8,
 'ytick.labelsize':8, 'pdf.fonttype':42, 'ps.fonttype':42})

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
    ax.plot(x,y,color=color,marker=marker,linestyle=ls,linewidth=1.8 if emphasis else 1.25,
            markersize=4.5 if emphasis else 3.8,zorder=4 if emphasis else 3)
    if sd:
        ax.errorbar(x,y,yerr=err,fmt='none',ecolor=color,alpha=.42,
                    elinewidth=.8,capsize=2,zorder=2)

def base(ax,s,full=False):
    for m,label,marker in BASES:
        r=selected(s,m)[0];x=float(r['cost']);y=float(r['f1'])
        if m=='B0_original' and not full and s!='S6_myc_lat':
            # A textual reference outside the axes, not an invented boundary point.
            continue
        ax.plot(x,y,marker=marker,markersize=6,color='#424242',
                markerfacecolor='white' if m=='B1_always' else '#424242',
                linestyle='none',zorder=5)

# Compact all-methods version: genuine overlaps retained; annotation arrows removed.
fig,axs=plt.subplots(2,2,figsize=(8.1,5.9))
for ax,(s,title) in zip(axs.flat,SETS):
    frame(ax)
    for m,label,col,mark,ls in METHODS: curve(ax,s,m,col,mark,ls,emphasis=m=='B5_selectnorm_adapt')
    base(ax,s)
    ax.set_title(title,pad=9)
    lohi={'S3_tsac_lat':(73,84),'S4_tunizi':(61.8,68.4),
          'S5_narabizi':(65.4,71.8),'S6_myc_lat':(52.3,55.0)}
    ax.set_ylim(*lohi[s]);ax.set_ylabel('Macro-F1')
    ax.set_xlabel('Estimated cost (original pass = 1)')
    r=selected(s,'B0_original')[0]
    note=(f"B0: {float(r['f1']):.1f} at cost 1.00 (outside y-range)"
          if s!='S6_myc_lat' else 'B0, B1 and R shown at their recorded values')
    ax.text(0,-.35,note,transform=ax.transAxes,fontsize=7.6,color='#4b5563')
handles=[Line2D([],[],color=c,marker=mk,ls=ls,label=lab,linewidth=1.5)
         for _,lab,c,mk,ls in METHODS]
handles += [Line2D([],[],color='#424242',marker=mk,ls='',label=lab,
                  markerfacecolor='white' if m=='B1_always' else '#424242') for m,lab,mk in BASES]
fig.legend(handles=handles,loc='upper center',ncol=4,frameon=False,fontsize=8,
           bbox_to_anchor=(.5,1.02),columnspacing=1.4,handlelength=2.2)
fig.subplots_adjust(top=.86,bottom=.15,left=.08,right=.985,hspace=.88,wspace=.28)
for ext in ['pdf','png','svg']:fig.savefig(HERE/f'Figure2_lisible.{ext}',dpi=240,bbox_inches='tight')
plt.close(fig)

# Faceted alternative: every method isolated, all 108 original operating points kept.
fig,axs=plt.subplots(4,4,figsize=(10.2,8.6),sharex=True,sharey='col')
for row,(m,label,col,mark,ls) in enumerate(METHODS):
    for j,(s,title) in enumerate(SETS):
        ax=axs[row,j];frame(ax)
        curve(ax,s,m,col,mark,ls,emphasis=True);base(ax,s,full=True)
        vals=[float(r['f1']) for r in ROWS if r['set']==s]
        spread=max(vals)-min(vals);ax.set_ylim(min(vals)-.08*spread-.15,max(vals)+.09*spread+.15)
        if row==0:ax.set_title(title.replace(' · ','\n'),fontsize=9,pad=8)
        if j==0:ax.set_ylabel(label+'\nMacro-F1',fontsize=8.5)
        if row==3:ax.set_xlabel('Estimated cost',fontsize=8)
        ax.tick_params(labelsize=7.3)
fig.subplots_adjust(top=.87,bottom=.09,left=.115,right=.99,hspace=.27,wspace=.13)
fig.legend(handles=handles[4:],loc='upper center',ncol=3,frameon=False,bbox_to_anchor=(.55,.98),fontsize=9)
fig.text(.55,.925,'One router per panel · grey markers: single-/two-view references',ha='center',fontsize=10)
for ext in ['pdf','png','svg']:fig.savefig(HERE/f'Figure2_methodes_separees.{ext}',dpi=240,bbox_inches='tight')
plt.close(fig)
print('Redrew compact and fully faceted versions from',len(ROWS),'archived rows; scores unchanged.')
