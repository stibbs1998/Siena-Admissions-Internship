# This script is used to generate departmental reports on where else students decide to go.

import numpy as np
import pandas as pd
import altair as alt
import sys
import os,subprocess

import warnings
warnings.filterwarnings('ignore')

from progressbar import ProgressBar
pbar = ProgressBar()

df = pd.read_csv('../../data/processed/CriticalPath_Data_EM_Confidential_lessNoise.csv').drop(columns='Unnamed: 0')
path = '../../reports/demo_reports/'

#########################################################
# The following dictionary is used to group all similar #
# majors together #######################################
#########################################################

ourmajors = {"Physics":["PHYS","PYEN","PYED"], "Biology":["BIBS","BIBA","BIED","BICM"],
            "Chemistry":["CHEM","CHED","CHEN","BICM"],"Math":["MTED","MTBS","MTBA"],
            "Sociology":["SWRK","SOCI"],"Pre-Laws":["HIST","PHIL","POSC","CLAS","AMST"],
            "Languages":["FREN","FRED","SPAN","SPED"], "Pyschology":["PSYC"],
            "Undeclared":["UNSE","UNSC","UNBU","UNBE","UNAR","UNAE"],
            "Religion":["RELG"],"Health-Studies":["HLST","HSAD","HSHS","HSHP"],
            "Finance":["FNED","FINC"],"Environmental-Studies":["ENVS","ENVA"],
            "English":["ENGL","ENED"],"Computer-Science":['CSIS'],
            "Data-Science":["DASC"],"Communications":["COMM"], "Actuarial-Science":["ACSC","ACBS"],
            "Marketing":["MRKT"],"Management":["MGMT"], "Arts":["CREA"],"Nursing":["NRBL"], "HYED":["HYED"]
            }

# The same footer is used for each .tex file

footer = r'''\end{document}'''

########################################################
# For each 'branch' in the `ourmajors` dictionary, #####
# create a plot for the top 10 schools overall in ######
# competition, and then by each 'submajor' do the same #
######################################################## 

for key in pbar(ourmajors.keys()):
    codes = ourmajors[key]
    for code in codes:

        # Create a plot of top 10 schools to which students go otherwise for code/major, colored by number of campus visits
        
        source = df[['College_chosen_by_non-matrics','Unique_student_ID','Number_of_campus_visits','Major']].where(df.Major==code)
        top = source.groupby('College_chosen_by_non-matrics').count().reset_index().sort_values("Major",ascending=False)['College_chosen_by_non-matrics'][:10].values
        source = source.where(source['College_chosen_by_non-matrics'].isin(top))
        source.Number_of_campus_visits = source.Number_of_campus_visits.fillna(0)
        source = source.dropna()
        source.Number_of_campus_visits = source.Number_of_campus_visits.astype(int)
        source.Number_of_campus_visits[source.Number_of_campus_visits > 1] = '2+'
        source.Number_of_campus_visits = source.Number_of_campus_visits.astype(str)
        
        if len(source)>0:
            chart = alt.Chart(source.reset_index()).mark_bar().encode(
                y=alt.Y("College_chosen_by_non-matrics:N", axis=alt.Axis(title=''),
                        sort=alt.EncodingSortField(field="count:Q",op='count',order="descending")),
                x=alt.X("count(College_chosen_by_non-matrics)", axis=alt.Axis(title='')),
                color="Number_of_campus_visits:N",
                order=alt.Order(
                      'Number_of_campus_visits',
                      sort='ascending'
                    )
                ).properties(title=f"Top Colleges for Competition: {code}")
            chart.save(f"{path}{key}_{code}_other_choices_by_visits.png")

    # Create a plot of top 10 schools to which students go otherwise for each `branch`

    source = df[['College_chosen_by_non-matrics','Unique_student_ID','Number_of_campus_visits','Major']].where(df.Major.isin(codes))
    top = source.groupby('College_chosen_by_non-matrics').count().reset_index().sort_values("Major",ascending=False)['College_chosen_by_non-matrics'][:10].values
    source = source.where(source['College_chosen_by_non-matrics'].isin(top))
    source.Number_of_campus_visits = source.Number_of_campus_visits.fillna(0)
    source = source.dropna()
    source.Number_of_campus_visits = source.Number_of_campus_visits.astype(int)
    source.Number_of_campus_visits[source.Number_of_campus_visits > 1] = '2+'
    source.Number_of_campus_visits = source.Number_of_campus_visits.astype(str)

    chart = alt.Chart(source.reset_index()).mark_bar().encode(
            y=alt.Y("College_chosen_by_non-matrics:N", axis=alt.Axis(title=''),
                    sort=alt.EncodingSortField(field="count:Q",op='count',order="descending")),
            x=alt.X("count(College_chosen_by_non-matrics)", axis=alt.Axis(title='# Students')),
            color=alt.Color("Number_of_campus_visits:N",scale=alt.Scale(domain=['0','1','2+'],range=['black','green','gold'])),
            order=alt.Order(
                  'Number_of_campus_visits',
                  sort='ascending'
                )
            ).properties(title=f"Top Colleges for Competition: {key}")

    chart.save(f"{path}{key}_ALL_other_choices_by_visits.png")

    ############################################
    # Now write the report for this Department #
    ############################################
    
    header = r'''\documentclass{article}
    \usepackage{fullpage}
    \usepackage{graphicx}
    \usepackage{float}
    \title{%s Department}
    \author{Siena College}
    \date{\today}
    \begin{document}
    \maketitle
    ''' % key
    
    main = "Here is the Enrolled/Applied/Accepted breakdown for your department: \n"
        
    num_applied = len(df[['Major','Admission_status']].where(df.Major.isin(codes)).dropna())
    num_accepted = len(df[['Major','Admission_status']].where((df.Major.isin(codes)) & (df.Admission_status!='Applied')).dropna())
    num_enrolled = len(df[['Major','Admission_status']].where((df.Major.isin(codes)) & (df.Admission_status=='Enrolled')).dropna())
    
    main = main + r'''
    \begin{center}
    \begin{tabular}{ c | c c c }
     Code & Enrolled & Accepted & Applied \\ 
     Total & %s & %s & %s'''  % (num_enrolled,num_accepted,num_applied)
    
    if len(codes)>1:
        for code in codes:
            num_applied = len(df[['Major','Admission_status']].where((df.Major==code)).dropna())
            num_accepted = len(df[['Major','Admission_status']].where((df.Major==code) & (df.Admission_status!='Applied')).dropna())
            num_enrolled = len(df[['Major','Admission_status']].where((df.Major==code) & (df.Admission_status=='Enrolled')).dropna())
            
            main = main + r''' \\ 
            %s & %s & %s & %s''' % (code,num_enrolled,num_accepted,num_applied)
            
    main = main + '''
    \end{tabular}
    \end{center}'''

    main = main + "These colleges are the top competition for your department: \n"

    filename = f'{key}_ALL_other_choices_by_visits.png'

    main = main +  r'''\begin{figure}[H]
    \centering
    \includegraphics[width = 0.99\textwidth]{%s}{\hspace{0.2 in}}
    \caption{Top competition overall for the department.}
    \end{figure}
    ''' % (path+filename)

    if len(codes) > 1:

        for code in codes:
            
            if len(df[['Major']].where(df.Major==code).dropna()) > 0:

                filename = f'{key}_{code}_other_choices_by_visits.png'

                main = main + r'''\begin{figure}[H]
                \centering
                \includegraphics[width = 0.99\textwidth]{%s}{\hspace{0.2 in}}
                \caption{Top competition specifically for those who declared major is %s.}
                \end{figure}
                ''' % (path+filename,code)

    content = header + main + footer

    # Write to the .tex file

    with open(f'{path}{key}_by_visits.tex','w') as f:
         f.write(content)


#####################################################
# Compile the .tex files and delete the extra files #
#####################################################

for filename in os.listdir(path):
    if '.tex' in filename:  
        proc = subprocess.Popen(['pdflatex', path+filename])
        proc.communicate()

os.system("mv *.pdf " + path)
os.system("rm *.aux *.log")

