import pandas as pd
import numpy as np

income = pd.read_csv('../../data/external/income_data.csv')

income[['Census_Tract','County','State']] = income.Geography.str.split(',',expand=True)
income[['County','Word_County']]= income.County.str.strip().str.split(' ', 1,expand=True)
income.Census_Tract = income.Census_Tract.str.split(' ',expand=True)[2].astype(float)
income = income.drop(columns=['Geography','Word_County'])

income = income.rename(columns={'Median income (dollars); Estimate; Households':'Median_Income',
				'Median income (dollars); Margin of Error; Households':'Margin_of_Error'})

is_numeric_income = income.Median_Income.str.replace('-','').str.replace('+','').str.strip().str.isdigit() 

is_numeric_error =  income.Margin_of_Error.str.replace('*'," ").str.strip().str.isdigit()

income = income[is_numeric_error & is_numeric_income]

income.to_csv('../../data/processed/income_data.csv')

