import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings('ignore')

#################################################################
#################################################################


## Read in data files

df = pd.read_csv("../../data/raw/CriticalPath_Data_EM_Confidential.csv")
_2017 = pd.read_csv('../../data/raw/201730_Fresh_Not_Enrolled_College_Choice.csv').set_index("SARADAP_PIDM")
_2018 = pd.read_csv('../../data/raw/201830_Fresh_Not_Enrolled_College_Choice.csv').set_index("SARADAP_PIDM")
_2019 = pd.read_csv('../../data/raw/201930_Fresh_Not_Enrolled_College_Choice.csv').rename(columns={"PIDM":"SARADAP_PIDM"}).set_index("SARADAP_PIDM")

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

# ## Columns to dump as said by Ned:
# * tuition_waiver...
# * outside_aid - not aquired till late in the process
# * athletic_based_inst_aid
# * internal_academic_rating

#################################################################
#################################################################

df = df.drop(columns=['Tuition_waivers_and_exchanges','Outside_aid','Athletic_based_inst_aid','Internal_Academic_rating'])

#################################################################
#################################################################

# Make all columns begining with "Ints" a T/F

for col in df.columns.values:
    if col.startswith("Ints"):
        df[col] = df[col].map(dict(zip(df[col].unique(), [0,1])))

#################################################################
#################################################################

# Remove all columns with less than 3000 entry points.  These are almost all collected after enrollment has occured

df = df[df.columns.values[df.count()>3000]]

#################################################################
#################################################################

# One hot-encode the following columns:

# 'Dorm_or_commuter_student'

df['COMM'] = pd.get_dummies(df['Dorm_or_commuter_student'])['COMM']
df['RESD'] = pd.get_dummies(df['Dorm_or_commuter_student'])['RESD']

# 'CollegeCode'

df[['AD','BD','SD']] = pd.get_dummies(df['CollegeCode'])

# 'HD_Academic_Rating'

df[['AR1','AR1B','AR2','AR3','AR4','AR5']] = pd.get_dummies(df['HD_Academic_Rating']).drop(columns=['7','722','ARX'])

# 'Ethnicity'

df[['IndAlaskNat','Asian','BlackAfAmerican',
    'HispLatino','Multiple','NatHawaiiPacific','Non-ResidentAlien','Unknown','White']] = pd.get_dummies(df['Ethnicity'])

#################################################################
#################################################################


# Drop the original columns that we just one hot-encoded

df = df.drop(columns=['Dorm_or_commuter_student','CollegeCode','HD_Academic_Rating','Ethnicity'])

df = df.drop(columns='Unknown').rename(columns={"Multiple":"Multiple_races"})

#################################################################
#################################################################

# Drop these columns as they repeat information from other columns

df =  df.drop(columns=['Admission_status','HS_Numeric_rank'])

df['Test_Optional'] = df['Test_Optional'].map({'TOPT':True})
df['Test_Optional'] = df['Test_Optional'].fillna(False)


#################################################################
#################################################################

# Re-organize the 'Legacy' column

df['Legacy'] = ~df['Legacy'].isnull().astype(int) + 2  # any legacy student is assigned a 1, otherwise a 0

#################################################################
#################################################################

# Write file to .csv 

df.to_csv('../../data/interim/Third_order_clean_confidential.csv')

#################################################################
#################################################################
