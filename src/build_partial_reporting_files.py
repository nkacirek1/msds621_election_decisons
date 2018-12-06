from transform_data import *


# build empty df with proper columns
columns = ['STATE', 'RACE',
           'S1_DEM_RATIO', 'S2_DEM_RATIO', 'S3_DEM_RATIO',
           # 'S4_DEM_RATIO', 'S5_DEM_RATIO', 'S6_DEM_RATIO',
           'S1_REP_RATIO', 'S2_REP_RATIO', 'S3_REP_RATIO',
           # 'S4_REP_RATIO', 'S5_REP_RATIO', 'S6_REP_RATIO',
           'S1_COR(DD)', 'S2_COR(DD)', 'S3_COR(DD)',
           # 'S4_COR(DD)', 'S5_COR(DD)', 'S6_COR(DD)',
           'S1_COR(RR)', 'S2_COR(RR)', 'S3_COR(RR)',
           # 'S4_COR(RR)', 'S5_COR(RR)', 'S6_COR(RR)',
           'TIGHT_RACE', 'WINNER']

df = pd.DataFrame(columns=columns)

abs_path = sys.argv[1]  # absolute path to dir containing the repo

percents = [d for d in os.listdir(abs_path + 'msds621_election_decisons/partial_data/')
            if not d.startswith('.')]

path_pairs = []
for perc in percents:
    path_pairs.extend(get_partial_filepaths(abs_path, perc))

    for p in path_pairs:
        print(p[1])
        new_df_row = process_one_district(p[0], p[1], p[2], p[2][0], p[3])
        df = df.append(new_df_row)

    df.to_csv(abs_path + 'msds621_election_decisons/partial_data/' + perc + '/' + perc + '_reporting.csv', index=False)