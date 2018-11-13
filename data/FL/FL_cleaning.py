import pandas as pd
import os

column_list = ['County_Code', 'County', 'Election_Number', 'Election_Date', 'Election_Name', 'Precinct',
                       'Polling_Location', 'Total_Registered_Voters', 'Total_Registered_Republicans',
                       'Total_Registered_Democrats', 'Total_Registered_All_Other_Parties', 'Contest_Name', 'District',
                       'Contest_Code', 'Candidate', 'Candidate_Party', 'Candidate_Florida_ID_Number', 'DOE', 'Vote_Total']
column_list = [c.upper() for c in column_list]


def create_past(filename):
    df_past = pd.read_csv(filename, sep='\t', header=None)
    df_past.columns = column_list
    df_past = df_past[['COUNTY', 'PRECINCT', 'CONTEST_NAME', 'CANDIDATE', 'CANDIDATE_PARTY', 'VOTE_TOTAL']]
    df_past = df_past[df_past['CONTEST_NAME']=='President of the United States']
    df_past = df_past.drop(columns=['CONTEST_NAME','CANDIDATE'])
    df_past = df_past[df_past['CANDIDATE_PARTY'] == 'DEM'].merge(df_past[df_past['CANDIDATE_PARTY'] == 'REP'], on=['COUNTY','PRECINCT'])
    df_past = df_past.rename({'VOTE_TOTAL_x':'PAST_DEM', 'VOTE_TOTAL_y':'PAST_REP'}, axis=1)
    df_past = df_past.drop(columns=['CANDIDATE_PARTY_x', 'CANDIDATE_PARTY_y'])
    df_past['STATE'] = 'FL'
    df_past = df_past[['STATE', 'COUNTY', 'PRECINCT', 'PAST_DEM', 'PAST_REP']]
    return df_past


def create_present(filename):
    df_present = pd.read_csv(filename, sep='\t', header=None)
    df_present.columns = column_list
    df_present = df_present[['COUNTY', 'PRECINCT', 'CONTEST_NAME', 'CANDIDATE', 'CANDIDATE_PARTY', 'VOTE_TOTAL']]
    df_present = df_present[df_present['CONTEST_NAME']=='U.S. Representative']
    df_present = df_present.drop(columns=['CONTEST_NAME','CANDIDATE'])
    df_present = df_present[df_present['CANDIDATE_PARTY'] == 'DEM'].merge(df_present[df_present['CANDIDATE_PARTY'] == 'REP'], on=['COUNTY','PRECINCT'])
    df_present = df_present.rename({'VOTE_TOTAL_x':'NEW_DEM', 'VOTE_TOTAL_y':'NEW_REP'}, axis=1)
    df_present = df_present.drop(columns=['CANDIDATE_PARTY_x', 'CANDIDATE_PARTY_y'])
    df_present['STATE'] = 'FL'
    df_present = df_present[['STATE', 'COUNTY', 'PRECINCT', 'NEW_DEM', 'NEW_REP']]
    return df_present

file_list_12 = []
for name in os.walk('/Users/sarahmelancon/Desktop/FL12/'):
    for f in name[2]:
        if f.endswith('.txt'):
            file_list_12.append(f)

file_list_12 = sorted(file_list_12)
file_list_12 = [(f.split('_')[0], '/Users/sarahmelancon/Desktop/FL12/' + f) for f in file_list_12]

file_list_14 = []
for name in os.walk('/Users/sarahmelancon/Desktop/FL14/'):
    for f in name[2]:
        if f.endswith('.txt'):
            file_list_14.append(f)

file_list_14 = sorted(file_list_14)
file_list_14 = [(f.split('_')[0], '/Users/sarahmelancon/Desktop/FL14/' + f) for f in file_list_14]

for file in file_list_12:
    print('2012: ' + file[0])
    df = create_past(file[1])
    df.to_csv(file[0] + '_12', index=False)

for file in file_list_14:
    print('2014: ' + file[0])
    try:    
        df = create_present(file[1])
        df.to_csv(file[0] + '_14', index=False)
    except:
        print(file[0] + ' did not work')

