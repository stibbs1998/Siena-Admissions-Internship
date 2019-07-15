import pandas as pd

#################
#################

path = '../../data/external/'

filename = 'ACS_17_5YR_B01003_with_ann.csv'

county_populations = pd.read_csv(path+filename,encoding='ISO-8859-1',header=1)

county_populations[['County','State']] = county_populations.Geography.str.split(',',expand=True)

county_populations[['County','drop']] = county_populations.County.str.split(' ', n=1, expand=True)

county_populations = county_populations.drop(columns=['drop','Geography'])

county_populations = county_populations.rename(columns={county_populations.columns[2]:"Total"})

county_populations.Id2 = county_populations.Id2.astype(str)


##################
##################

fips = pd.read_csv(path+'FIPS.csv')

fips.FIPS = fips.FIPS.astype(str)

fips['Real_FIPS'] = fips.FIPS.str.slice(-3)

fips.Real_FIPS = fips.State + fips.Real_FIPS

#################
#################

df = pd.merge(fips,county_populations,how='left',left_on='FIPS',right_on='Id2')

df.to_csv('../../data/processed/county_populations.csv')
