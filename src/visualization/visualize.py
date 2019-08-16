import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from xgboost import plot_importance
from matplotlib.ticker import FormatStrFormatter
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.decomposition import PCA
from sklearn.preprocessing import scale

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


def residual_error(X_train,X_test,y_train,y_test, reg="linear"):
    
	"""

	Plot the residual error of the Regresssion model for the input data, 
	and return the fitted Regression model.
	-------------------------------------------------------------------
	# Parameters

	# X_train,X_test,y_train,y_test (np.arrays):  Given X, a 2-D array of Data,
	and y, an array of target data, we can use:

	sklearn.model_selection.train_test_split(X,y)
	
	to obtain X_train, X_test, y_train, and y_test.

	# reg (string): Whether the regression model is linear or logistical (default="linear").

	"""

	if reg.lower() == "linear":
		reg=LinearRegression()
		reg.fit(X_train,y_train)

	elif reg.lower() == "logistic":
		reg=LogisticRegression()
		reg.fit(X_train,y_train)

	## setting plot style 
	plt.style.use('fivethirtyeight') 

	## plotting residual errors in training data 
	plt.scatter(reg.predict(X_train), reg.predict(X_train) - y_train, 
		color = "green", s = 10, label = 'Train data') 

	## plotting residual errors in test data 
	plt.scatter(reg.predict(X_test), reg.predict(X_test) - y_test, 
		color = "blue", s = 10, label = 'Test data') 

	## plotting line for zero residual error 
	plt.hlines(y = 0, xmin = 0, xmax = 50, linewidth = 2) 

	## plotting legend 
	plt.legend(loc = 'upper right') 

	## plot title 
	plt.title("Residual errors") 

	return reg

def plot_explained_variance_ratio(pca):

	"""

	Plot the Scree Plot to Explain the variance
	of the dataset.
	-------------------------------------------
	# Parameters:

	# pca: The sklearn.decomposition.PCA() object
	to plot variance for.

	"""

	plt.plot(pca.explained_variance_ratio_)
	plt.xlabel('number of components')
	plt.ylabel('cumulative explained variance')
	return 1


def pca_results(scaled, pca):

	"""

	Plot the explained variance of the DataSet as a barchart,
	and return a DataFrame with the explained variance for each
	feature, for each dimension of the PCA.
	-----------------------------------------------------------
	# Parameters:

	# scaled (pd.DataFrame): The DataFrame in which we are performing PCA on, scaled
	down using sklearn.preprocessing.scale():

	from sklearn.preprocessing import scale
	scaled = pd.DataFrame(scale(data))

	Where `data` is the original DataFrame.

	# pca: The sklearn.decomposition.PCA() object, which has been fitted to the 
	scaled down DataFrame:

	pca = PCA(**args).fit(scaled)    

	"""

	# Dimension indexing
	dimensions = ['Dimension {}'.format(i) for i in range(1,len(pca.components_)+1)]

	# PCA components
	components = pd.DataFrame(np.round(pca.components_, 4), columns = scaled.keys()) 
	components.index = dimensions

	# PCA explained variance
	ratios = pca.explained_variance_ratio_.reshape(len(pca.components_), 1) 
	variance_ratios = pd.DataFrame(np.round(ratios, 4), columns = ['Explained Variance']) 
	variance_ratios.index = dimensions

	# Create a bar plot visualization
	fig, ax = plt.subplots(figsize = (14,8))

	# Plot the feature weights as a function of the components
	components.plot(ax = ax, kind = 'bar')
	ax.set_ylabel("Feature Weights") 
	ax.set_xticklabels(dimensions, rotation=0)

	# Display the explained variance ratios# 
	for i, ev in enumerate(pca.explained_variance_ratio_): 
		ax.text(i-0.40, ax.get_ylim()[1] + 0.05, "Explained Variance\n %.4f"%(ev))

	# Return a concatenated DataFrame
	return pd.concat([variance_ratios, components], axis = 1)


def biplot(data, scaled, pca):
    
	"""

	Create a biplot of the data.
	-----------------------------------------------------------
	# Parameters:
    
    # data (pd.DataFrame): The original data.

	# scaled (pd.DataFrame): The DataFrame in which we are performing PCA on, scaled
	down using sklearn.preprocessing.scale():

	from sklearn.preprocessing import scale
	scaled = pd.DataFrame(scale(data))

	Where `data` is the original DataFrame.

	# pca: The sklearn.decomposition.PCA() object, which has been fitted to the 
	scaled down DataFrame:

	pca = PCA(**args).fit(scaled)    

	"""
    
	pca = PCA(n_components=2).fit(scaled)
	reduced_data = pca.transform(scaled)
    
	pca_samples = pca.transform(scaled)
	reduced_data = pd.DataFrame(reduced_data, columns = ['Dimension 1', 'Dimension 2'])
    
	fig, ax = plt.subplots(figsize = (14,8))
    
    # scatterplot of the reduced data 
	ax.scatter(x=reduced_data.loc[:, 'Dimension 1'], y=reduced_data.loc[:, 'Dimension 2'], facecolors='b', edgecolors='b', s=70, alpha=0.5)
    
	feature_vectors = pca.components_.T

    # using scaling factors to make the arrows
	arrow_size, text_pos = 7.0, 8.0,

    # projections of the original features
	for i, v in enumerate(feature_vectors):
		ax.arrow(0, 0, arrow_size*v[0], arrow_size*v[1], head_width=0.2, head_length=0.2, linewidth=2, color='red')
		ax.text(v[0]*text_pos, v[1]*text_pos, data.columns[i], color='black', ha='center', va='center', fontsize=18)

	ax.set_xlabel("Dimension 1", fontsize=14)
	ax.set_ylabel("Dimension 2", fontsize=14)
	ax.set_title("PC plane with original feature projections.", fontsize=16);
	return ax