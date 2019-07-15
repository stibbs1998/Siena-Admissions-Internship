import pandas as pd

path = '../../data/external/'

#_2015 = pd.read_csv(path+'Enrollment_2015.csv')
#_2016 = pd.read_csv(path+'Enrollment_2016.csv')

_2017 = pd.read_csv(path+'Enrollment_2017.csv')

def rename(df):
    df = df.rename(columns={ df.columns[3]: "freshman_enrollment", df.columns[1]: "instituion_name"})
    return df

#_2015 = rename(_2015)
#_2016 = rename(_2016)

_2017 = rename(_2017)

#df = pd.concat([_2017,_2016,_2015])

df = _2017

df.instituion_name = df.instituion_name.str.upper()

df.to_csv('../../data/processed/Enrollment.csv')
