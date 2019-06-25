############################
############################

# Import libraries

import numpy as np
import pandas as pd
import pickle as pkl
import operator
import warnings
import csv
warnings.filterwarnings('ignore')

# Import a ProgressBar

from progressbar import ProgressBar
pbar = ProgressBar()

############################
############################

# Import the .csv file without HEOP or Albany Med applicants.

df = pd.read_csv('../../data/processed/CriticalPath_Data_EM_Confidential_lessNoise.csv')

# Import the .csv file taken from https://ope.ed.gov/dapip/#/home.

hd2017_df = pd.read_csv('../../data/external/hd2017.csv',encoding='ISO-8859-1')

# Convert all of the school names to UPPER CASE.  

hd2017_df['INSTNM'] = hd2017_df['INSTNM'].str.upper()

############################ 
############################

# Get a Series of all schools which names match up perfectly to a school name we have in our .csv file.

schools_in_our_df = hd2017_df[hd2017_df['INSTNM'].isin(df['College_chosen_by_non-matrics'])]

# Get a Series of all schools which names do NOT match up to a school name we have in our .csv file.

schools_not_in_our_df = hd2017_df[~hd2017_df['INSTNM'].isin(df['College_chosen_by_non-matrics'])]

print(schools_not_in_our_df['INSTNM'])
# Get a list of all the schools in our .csv file with no match.

non_mapped_schools = list(set(df['College_chosen_by_non-matrics'].unique())  - set(schools_in_our_df['INSTNM']))

print(len(df['College_chosen_by_non-matrics'].unique()))
print(len(schools_in_our_df['INSTNM']))

############################
############################

# List of common words that should not be included in the following for loop.

bad_words = ['THE','OR','OF','AND','COUNTY','COLLEGE','-','STATE','UNIVERSITY','&',' ','  ','NORTH','WEST','SOUTH','EAST']

# Initialize a dictionary that maps the names of the schools we have to their name in the government data file.
# We first add all of the correctly named schools to this dictionary.

mapper = dict(zip(schools_in_our_df['INSTNM'],schools_in_our_df['INSTNM']))

############################
############################

# This loop breaks down each instituion name word by word from both the gov't file and our admissions data file.
# The nested loop checks the name of each institution from the gov't file against the name from the admissions data file word-by-word.
# For each word that matches up, a 'point' is added to the name's 'score'.
# The highest 'score' is deemed to be closest in name to one another, and we add this as a key and value to the 'mapper' dictionary.
# This seems to be roughly 90% reliable.  If a school has a score of 0 for every other school, we ignore it for the purpose of this project.

for unknown in pbar(non_mapped_schools[1:]): # the first entry is NaN

# Strip all extra spaces, hyphens and split the string into a list delimited on the spaces.

	unknown_str = unknown.replace('-',' ')
	unknown_str = unknown_str.replace('   ',' ')
	unknown_str = unknown_str.replace('\t',' ')
	unknown_str = unknown_str.replace('    ',' ')
	unknown_str = unknown_str.replace('  ',' ').strip()
	unknown_str = unknown.upper().split(' ')

	scores = {} # dictionary for list of scores

	for school in schools_not_in_our_df['INSTNM']:

# Strip all extra spaces and hyphens.

		school_str = school.replace('-',' ')
		school_str = school_str.replace('   ',' ')
		school_str = school_str.replace('\t',' ')
		school_str = school_str.replace('    ',' ')
		school_str = school_str.replace('  ',' ').strip()

		if "LYLE" not in school_str: # Lyle's School of Beauty caused a ton of problems, everything is better without it.

			scores[school] = 0 # every school starts with a score of 0

			for word in unknown_str:

				if word.upper() not in bad_words and word.upper() in school_str.strip().upper().split(' '):

					scores[school] += 1 # a word matched! Add a point
				elif word.upper() in ['ST.','ST','SAINT'] and any(x in ['ST.','ST','SAINT'] for x in school_str.strip().upper().split(' ')):
					scores[school] += 1 # Saint/St/St. appears in both! close enough! Add a point

		school_name = max(scores.items(), key=operator.itemgetter(1))[0]  # Get the key name for the maximum value.

		if scores[school_name]>0: # Make sure the maximum value isn't zero.

			mapper[unknown] = school_name # Add this to the mapping dictionary.

############################
############################

# Write to file.

with open('../../data/processed/college_name_mapper.csv', 'w') as csv_file:
	writer = csv.writer(csv_file)
	writer.writerow(["CCBNM","DAPIP"])
	for key, value in mapper.items():
		writer.writerow([key, value])

