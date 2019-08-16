import pandas as pd
import numpy as np
import pickle as pkl
import warnings
warnings.filterwarnings('ignore')

#################################################################
#################################################################

print("Read in files.")
## Read in data files

df = pd.read_csv("../../data/raw/CriticalPath_Data_EM_Confidential.csv")
_2017 = pd.read_csv('../../data/raw/201730_Fresh_Not_Enrolled_College_Choice.csv').set_index("SARADAP_PIDM")
_2018 = pd.read_csv('../../data/raw/201830_Fresh_Not_Enrolled_College_Choice.csv').set_index("SARADAP_PIDM")
_2019 = pd.read_csv('../../data/raw/201930_Fresh_Not_Enrolled_College_Choice.csv').rename(columns={"PIDM":"SARADAP_PIDM"}).set_index("SARADAP_PIDM")

#################################################################
#################################################################

# Fix Year_of_entry column

df.Year_of_entry = ( df.Year_of_entry - 30 ) / 100

#################################################################
#################################################################

# Concatenate the files together to get accurate data in column "College_chosen_by_non-matrics"

last_three_years_df = pd.concat([_2017,_2018,_2019])
mapper = last_three_years_df.to_dict()

df = df.drop(columns='College_chosen_by_non-matrics')
df['College_chosen_by_non-matrics'] = df['Unique_student_ID'].map(mapper['CollegeName'])


#################################################################
#################################################################

# Re-write 'Enrolled' column as a True/False column

df['Enrolled'] = df['Enrolled'].map({80:True})
df['Enrolled'] = df['Enrolled'].fillna(False)

df = df[(df['Application_Type']!='AM') & (df['Application_Type']!='HE')]

#################################################################
#################################################################

# Re-write Admission_status as three columns: Applied, Accepted, Enrolled.

mapper = {70: "Accepted", 80: "Enrolled"}
for status in df['Admission_status'].unique():
    if status!=70 and status!=80:
        mapper[status] = "Applied"
        
df['Admission_status'] = df['Admission_status'].map(mapper)

#################################################################
#################################################################

# Calculate the distance to Siena College for each applicant from their home city.

_zipDF = pd.DataFrame.from_dict(pkl.load(open('../../data/external/CARES_zipcode_data_v3.pkl','rb'))[2]).drop_duplicates(subset=['City','StateCode'])

long_latsDF = pd.merge(df,_zipDF,how='left',left_on=['City_perm_res','State_perm_res'],right_on=['MixedCity','StateCode'])
long_latsDF = long_latsDF.drop_duplicates(subset='Unique_student_ID').reset_index()
long_latsDF = long_latsDF.drop(columns='index')

def haversine(lat1, lon1, lat2, lon2):
    R = 6372.8  # Earth radius in kilometers
    dLat = np.deg2rad(lat2 - lat1)
    dLon = np.deg2rad(lon2 - lon1)
    lat1 = np.deg2rad(lat1)
    lat2 = np.deg2rad(lat2)
    a = np.sin(dLat / 2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dLon / 2)**2
    c = 2 * np.arcsin(np.sqrt(a))
    return R * c

siena_lat, siena_long = (42.71833,-73.7533)  # The coordinates of Siena Hall

# Distance to Siena
long_latsDF['Dist_to_Siena'] = haversine(siena_lat,siena_long,long_latsDF['Latitude'],long_latsDF['Longitude'])*0.6213 # 0.6213 converts km to miles

mapper_siena = dict(zip(long_latsDF['Unique_student_ID'],long_latsDF['Dist_to_Siena']))

# Map the distances back to the original DataFrame 

df['Dist_to_Siena'] = np.copy(df['Unique_student_ID'])
df['Dist_to_Siena'] = df['Dist_to_Siena'].map(mapper_siena)

#################################################################
#################################################################

# Now do this for the distance to other schools attended.


hd2017_df = pd.read_csv('../../data/external/hd2017.csv',encoding='ISO-8859-1')

# Convert all of the school names to UPPER CASE.  

hd2017_df['INSTNM'] = hd2017_df['INSTNM'].str.upper()

# Reset long_latsDF 

long_latsDF = pd.merge(df,_zipDF,how='left',left_on=['City_perm_res','State_perm_res'],right_on=['MixedCity','StateCode'])
long_latsDF = long_latsDF.drop_duplicates(subset='Unique_student_ID').reset_index()
long_latsDF = long_latsDF.drop(columns='index')

name_mapper = pd.read_csv('../../data/processed/college_name_mapper.csv')

long_latsDF['Ccbnm_for_dist'] = long_latsDF['College_chosen_by_non-matrics'].map(dict(zip(name_mapper['CCBNM'],name_mapper['DAPIP'])))

new_df = pd.merge(long_latsDF,hd2017_df[['INSTNM','LONGITUD','LATITUDE','COUNTYCD']],how='left',left_on='Ccbnm_for_dist',right_on='INSTNM')

new_df['Dist2Ccbnm'] = haversine(new_df['LATITUDE'],new_df['LONGITUD'],new_df['Latitude'],new_df['Longitude'])*0.6213

# Map the distances back to the original DataFrame.
mapper_Ccbnm = dict(zip(new_df.Unique_student_ID,new_df.Dist2Ccbnm))
mapper_Ccbnm_names = dict(zip(new_df.Unique_student_ID,new_df.Ccbnm_for_dist))
mapper_Ccbnm_lat = dict(zip(new_df.Unique_student_ID,new_df.LATITUDE)) 
mapper_Ccbnm_long =  dict(zip(new_df.Unique_student_ID,new_df.LONGITUD))
mapper_long = dict(zip(new_df.Unique_student_ID,new_df.Longitude))   
mapper_lat = dict(zip(new_df.Unique_student_ID,new_df.Latitude))

df['Dist_to_Ccbnm'] = df['Unique_student_ID'].map(mapper_Ccbnm)
df['Ccbnm_for_dist'] = df['Unique_student_ID'].map(mapper_Ccbnm_names)
df['Ccbnm_lat'] = df['Unique_student_ID'].map(mapper_Ccbnm_lat)
df['Ccbnm_long'] = df['Unique_student_ID'].map(mapper_Ccbnm_long)
df['Home_Lat'] = df['Unique_student_ID'].map(mapper_lat)
df['Home_Long'] = df['Unique_student_ID'].map(mapper_long)

#################################################################
#################################################################

# Get Freshman Enrollemnt (if available) for these colleges 

enroll = pd.read_csv('../../data/processed/Enrollment.csv')
enroll['instituion_name'] = enroll['instituion_name'].map(dict(zip(name_mapper['CCBNM'],name_mapper['DAPIP'])))

df['Fresh_enroll'] = df['Ccbnm_for_dist'].map(dict(zip(enroll['instituion_name'],enroll['freshman_enrollment'])))

# Now get population numbers for
	# County_perm_res
	# County in which the college resides

population = pd.read_csv('../../data/processed/county_populations.csv')

# adjacent_counties = pd.read_csv('../../data/external/county_adjacency.txt',sep='\t',encoding='ISO-8859-1',names=['county','fips','adjacent_county','fips_adjacent_county'])
# adjacent_counties = adjacent_counties.fillna(method='pad')
# 
population = population.dropna(subset=['Id2','Total']) # FIPS County Number | Number of County Residents

# county_population_mapper = {}
# 
# for fips in population.Id2:
# 
# 	fips_adjacent_counties = adjacent_counties[adjacent_counties['fips']==fips]['fips_adjacent_county']
# 	surrounding_population = population[population.Id2.isin(fips_adjacent_counties)]['Total'].sum()	
# 	county_population_mapper[fips] = surrounding_population

mapper_county = dict(zip(new_df.Ccbnm_for_dist,new_df.COUNTYCD))

# df['CollegeTown_pop'] = df['Ccbnm_for_dist'].map(mapper_county)
# df['CollegeTown_pop'] = df['CollegeTown_pop'].map(population.Id2,population.Total)

df['County_perm_res_pop'] = df['County_perm_res'].map(dict(zip(population.Real_FIPS,population.Id2))) 
df['County_perm_res_pop'] = df['County_perm_res_pop'].map(population.Id2,population.Total)

#################################################################
#################################################################

# Convert COA to numeric
df['COA'] = df['COA'].replace('[\$,]', '', regex=True).astype(float)

#################################################################
#################################################################

# Write the DataFrame to a .csv file.

print("Write to file.")

df.to_csv('../../data/processed/CriticalPath_Data_EM_Confidential_lessNoise.csv')

#################################################################
#################################################################

# The following columns should be dropped immediately as instructed by Admissions.

# While the code below should eliminate these columns anyway, it was so important to
# remove these columns from the DataFrame that I did so here.

df = df.drop(columns=['Tuition_waivers_and_exchanges','Outside_aid','Athletic_based_inst_aid','Internal_Academic_rating'])

#################################################################
#################################################################

# Make all columns begining with "Ints" a T/F

# Anyone who was truly interested in one of these programs
# would've taken the time to check off yes on the application.

print("Cut out columns.")

for col in df.columns.values:
    if col.startswith("Ints"):
        df[col] = df[col].map(dict(zip(df[col].unique(), [0,1])))

#################################################################
#################################################################

# Remove all columns with less than 3000 entry points.  

# These are almost all collected after enrollment has occured
# and there is not enough data present to draw any meaningful
# results from.

df = df[df.columns.values[df.count()>3000]]

#################################################################
#################################################################

print("One-hot-encode columns.")

# One hot-encode the following columns:

### 'Dorm_or_commuter_student'

df['COMM'] = pd.get_dummies(df['Dorm_or_commuter_student'])['COMM']
df['RESD'] = pd.get_dummies(df['Dorm_or_commuter_student'])['RESD']

### 'CollegeCode'

df[['AD','BD','SD']] = pd.get_dummies(df['CollegeCode'])

### 'Ethnicity'

df[['IndAlaskNat','Asian','BlackAfAmerican',
    'HispLatino','Multiple','NatHawaiiPacific','Non-ResidentAlien','Unknown','White']] = pd.get_dummies(df['Ethnicity'])


#################################################################
#################################################################

# Reassign ordinal variables for 'HD_Academic_Rating'.

df['HD_Academic_Rating'] = df['HD_Academic_Rating'].map(
            {
                7:np.nan,
                722:np.nan,
                "AR1":1,
                "AR1B":1,
                "AR2":2,
                "AR3":3,
                "AR4":4,
                "AR5":5,
                "ARX":0
            })

#################################################################
#################################################################

# Drop the original columns that we just one hot-encoded as they
# are no longer needed for the DataFrame.

df = df.drop(columns=['Dorm_or_commuter_student','CollegeCode','Ethnicity'])

#################################################################
#################################################################

# Drop the unknown races column, and rename "Multiple" for clarity purposes.

df = df.drop(columns='Unknown').rename(columns={"Multiple":"Multiple_races"})

#################################################################
#################################################################

# Test_Optional should be made into a T/F column.

df['Test_Optional'] = df['Test_Optional'].map({'TOPT':True})
df['Test_Optional'] = df['Test_Optional'].fillna(False)


#################################################################
#################################################################

# Re-organize the 'Legacy' column

### Any non NaN value means that there is some sort of 'legacy' for the student to follow here.
### A potential legacy student is assigned a '1', and non-legacy students are assigned a '0'.

df['Legacy'] = ~df['Legacy'].isnull().astype(int) + 2   

#################################################################
#################################################################

# Make the NaN values for campus visits 0's, as someone who
# has no visits to campus is logged as a NaN.

df['Number_of_campus_visits'] = df['Number_of_campus_visits'].fillna(0) 

#################################################################
#################################################################

# Write the DataFrame to a .csv file.

print("Write to file.")

df.to_csv('../../data/interim/Third_order_clean_confidential.csv')

#################################################################
#################################################################
