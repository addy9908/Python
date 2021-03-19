import numpy as np
import math
import pandas as pd
from pandas import ExcelWriter
import os
import pathlib
from pathlib import Path
import io
import glob
import itertools
import shutil
import openpyxl
from openpyxl import load_workbook
from openpyxl.utils.dataframe import dataframe_to_rows
import seaborn as sns

import time
from time import sleep
import datetime
import csv
import matplotlib.pyplot as plt
from scipy import stats
import researchpy as rp
import statsmodels.api as sm
from statsmodels.formula.api import ols
from statsmodels.stats.multicomp import MultiComparison, pairwise_tukeyhsd
from statsmodels.stats.libqsturng import psturng
from tkinter import *
from tkinter.filedialog import askopenfilename
import matplotlib
from matplotlib.backends.backend_pdf import PdfPages
# import addcopyfighandler

class openfile():
    def __init__(self):
        root = Tk()
        root.withdraw()
        self.filename = askopenfilename(parent = root,
                                initialdir=os.getcwd(),
                                title="Please select a file:")
        self.source_name = os.path.basename(self.filename)
        self.source_dir = os.path.dirname(self.filename)
        self.output_dir = os.path.join(self.source_dir,'Output')
        if os.path.isdir(self.output_dir):
            pass
        else:
            os.mkdir(self.output_dir)
f = openfile()
source_file = f.filename
source_dir = f.source_dir
output_dir = f.output_dir
msg = 'The source file is: ' + f.source_name + ', will save to Output'
print(msg)

# cherry is Merlot, pickle/Mint/Olive/Lime is raisin, Jam is mixed with Apple
CON_LIST = ['Cherry', 'Pickle', 'Mint', 'Olive', 'Lime', 'Orchid', 'Mauve', 'Plum', 'Iris', 'Apple', 'Mustard', 'Corn', 'Gold', 'Butter']
SCZ_LIST = ['Pine', 'Sage', 'Lilac', 'Grape', 'Ruby', 'Gamet', 'Honey', 'Dijon', 'Sun', 'Yellow']
# CON_LIST = ['Orchid', 'Mauve', 'Plum', 'Iris', 'Raisin', 'Apple', 'Merlot', 'Mustard', 'Corn', 'Gold', 'Butter']
# SCZ_LIST = ['Pine', 'Sage', 'Lilac', 'Grape', 'Ruby', 'Gamet', 'Honey', 'Dijon', 'Sun', 'Yellow']

now = datetime.datetime.now()
Geno = "SCZ"
#MONTH = "Sept 2018"
VERSION = str(now.year).zfill(4) + str(now.month).zfill(2) + str(now.day).zfill(2)+str(now.hour).zfill(2)+str(now.minute).zfill(2)

# col_Names = ['Neurons', 'DIV', 'Line_week', 'Geno_week', 'Threshold (10mV/ms)', 'Amplitude', 'HW', 'AHP', 'onset_to_peak (ms)']
#col_List = [0,1,25,28,31,32,34,35,38]
#col_List = [0,1,31,32,34,35,38]
col_List = [0,1,28,29,31,32,37,39,40]
col_Names = ['Neurons', 'DIV', 'Threshold at 10mV/ms (mV)', 'Amplitude (mV)', 'Half_width (ms)', 'AHP (mV)',
             'onset_to_peak (ms)', 'Max dV/dt (V/s)','Min dV/dt (V/s)']
df = pd.read_excel(source_file, sheet_name="ZY_AP_20190424", header=None, usecols=col_List, names=col_Names,skiprows=1) #.dropna().reset_index(drop=True)

# create lineName, if not created in excel
neuronName = df.Neurons
df['lineName'] = neuronName.str.split('_').str[2]
df_filtered = df[df['lineName'].isin(CON_LIST+SCZ_LIST)]
#remove those amplitude less than 30mV
Amp_filter = 30
df_filtered = df_filtered[df_filtered['Amplitude (mV)'] > Amp_filter]

df_final = df_filtered.dropna().reset_index(drop=True) #remove row with any NA and re-index

# create Week, and Genotype from neuron filename, if not created in excel
df_final['Week'] = df_final['DIV'].astype(int)//7

conditions = [(df_final['lineName'].isin(CON_LIST)),(df_final['lineName'].isin(SCZ_LIST))]
choices = ['CON','SCZ']
df_final['Genotype'] = np.select(conditions,choices,default='MM')

df_final['Line_wk'] = df_final['lineName'] + '_' + df_final['Week'].map(str) + 'wk'
df_final['Geno_wk'] = df_final['Genotype'] + '_' + df_final['Week'].map(str) + 'wk'



groups = ['CON_8wk','CON_10wk','SCZ_8wk','SCZ_10wk']
targetCols = col_Names[2:]
#df_final.boxplot(targetCols,by=['Genotype', 'Week'])
#targetSum = rp.summary_cont(df_final[targetCols].groupby(df_final['Geno_wk']))

# fig, ax = plt.subplots(nrows = math.ceil(len(targetCols)/2), ncols = 2,tight_layout=True)
output_Name='AP_properties_' + VERSION + '.pdf'
pp = PdfPages(os.path.join(output_dir,output_Name))
matplotlib.use('TkAgg')

for i, targetCol in enumerate(targetCols):
    rp.summary_cont(df_final[targetCol].groupby(df_final['Geno_wk']))
    mc = MultiComparison(df_final[targetCol], df_final['Geno_wk'])
    mc_results = mc.tukeyhsd()

    print('Comparison of '+ targetCol + ':\n')
    print(mc_results)
    p_values = psturng(np.abs(mc_results.meandiffs / mc_results.std_pairs), len(mc_results.groupsunique), mc_results.df_total)
    p_values = np.round(p_values,3)
    print("p values:", p_values)
    #rp.summary_cont(df_final[targetCol].groupby([df_final['Genotype'],df_final['Week']]))
    #results = ols(targetCol+' ~ C(Geno_wk)', data=df_final).fit()
    #results.summary()

    axis = sns.swarmplot(y=targetCol, x='Geno_wk', data=df_final, order=groups, size = 8)
    sns.boxplot(y=targetCol, x='Geno_wk', data=df_final, ax=axis,order=groups)
    msg = 'p(8w)=' + str(p_values[4]) + ', p(10w)=' + str(p_values[1])
    axis.set_title(msg,fontsize=8)
    axis.set(xlabel='', ylabel=targetCol)
    axis.tick_params(axis='x', labelsize=8)
    fig = axis.get_figure()
    # Put figure window on top of all other windows
    fig.canvas.manager.window.attributes('-topmost', 1)
    # After placing figure window on top, allow other windows to be on top of it later
    fig.canvas.manager.window.attributes('-topmost', 0)
    # plt.show()

    plt.show(block=False)

    pp.savefig(fig)
    # plt.pause(5)  # do not close to reuse the fig
    plt.clf()




# fig.delaxes(ax[2, 1])  # remove empty subplot

#pp = PdfPages('foo.pdf')
# output_Name='AP_properties_' + VERSION + '.pdf'
# plt.savefig(output_dir + output_Name,bbox_inches='tight')
# plt.show()
plt.close()
pp.close()