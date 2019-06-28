import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from xgboost import plot_importance
from matplotlib.ticker import FormatStrFormatter

def kde_w_mean(series, b, ylabel, figsize=(10,6),**kwargs):

	"""

	Plots a histogram with a KDE, and a line at the mean value.
	----------------------------------------------------
	Parameters:

	# series (pd.Series): A pandas series of data to create the plot from.

	# b (int): The number of bins for the histogram.

	# ylabel (string): The ylabel on the histogram.

	# figsize (float,float): Tuple (width,height) for figure size, default of (10,6).

	# kwargs_dist (dict): Other keyword arguments for sns.distplot().

	"""
	start = series.min()
	end = series.max()
	mean = series.mean()
	step = (end-start)/5
	sns.distplot(series,bins=b,kde=False,**kwargs)
	plt.xticks(np.arange(0,end,step).astype(int))
	plt.ylabel(ylabel)
	ax2 = plt.twinx()
	sns.kdeplot(series, ax = ax2)
	ax2.yaxis.set_major_formatter(FormatStrFormatter('%.2f'))
	plt.yticks(ax2.get_yticks(), np.around(np.array(ax2.get_yticks()).astype(float)*100, decimals=2))
	plt.ylabel("Kernel Density Estimate (%)")
	plt.axvline(x=mean,color='red',label='Mean: %.2f' %mean)
	plt.legend(loc='best')

def my_plot_importance(booster, figsize=(10,6), importance_type='weight', **kwargs): 

	"""

	Plots feature importance, as documented for xgboost.plot_importance(),
	with the option to increase figure size.
	----------------------------------------------------
	Parameters:

	# booster: The XGBoost model we want to call plot_importance() on. 

	# figsize (float,float): Tuple (width,height) for figure size, default of (10,6).

	# importance_type (string): The method used to caluclate feature importance.  Default is 'weight',
	other options are 'cover' and 'gain'.
	
	# kwargs (dict): Other keyword arguments for xgb.plot_importance().

	"""
	fig, ax = plt.subplots(1,1,figsize=figsize)
	return plot_importance(booster=booster, ax=ax,importance_type=importance_type, **kwargs)
