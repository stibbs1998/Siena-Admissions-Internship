import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from xgboost import plot_importance

def kde_w_mean(series, b, ylabel, figsize=(10,6)):
	"""
	Plots a histogram with a KDE, and a line at the mean value.
	----------------------------------------------------
	Parameters:
	series: A pandas series of data to create the plot from.
	b: The number of bins for the histogram.
	ylabel: A string for the ylabel on the histogram.
	figsize: Tuple for figure size, default of (10,6).
	"""
	start = series.min()
	end = series.max()
	mean = series.mean()
	step = (end-start)/10
	sns.distplot(series,bins=b,kde=False)
	plt.xticks(np.arange(0,end,step))
	plt.ylabel(ylabel)
	ax2 = plt.twinx()
	sns.kdeplot(series, ax = ax2)
	plt.ylabel("Kernel Density Estimate")
	plt.axvline(x=mean,color='red',label='Mean: %.2f' %mean)
	plt.legend(loc='best')

def my_plot_importance(booster, figsize, importance_type='weight', **kwargs): 
	"""
	Plots feature importance, as documented for xgboost.plot_importance(),
	with the option to increase figure size.
	"""
	fig, ax = plt.subplots(1,1,figsize=figsize)
	return plot_importance(booster=booster, ax=ax,importance_type=importance_type, **kwargs)
