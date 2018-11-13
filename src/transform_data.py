from SmallVoteLib import *
import os
import sys


def merge(old, new):
    """
    Helper method that merges 2016 election data frame with incoming 2018 election data frame
    """
    merged_df = pd.merge(old, new, how='outer',
                         on=(['STATE', 'COUNTY', 'PRECINCT']))[['STATE', 'COUNTY',
                                                                'PRECINCT', 'CLINTON',
                                                                'TRUMP', 'DEM', 'REP']]
    merged_df = merged_df.rename({'STATE_x': 'STATE', 'DEM': 'NEW_DEM', 'REP': 'NEW_REP'}, axis=1)

    # check if both are 0
    mask = (merged_df.NEW_DEM == 0) & (merged_df.NEW_REP == 0)
    merged_df.loc[mask, 'NEW_REP'] = np.nan
    merged_df.loc[mask, 'NEW_DEM'] = np.nan

    return merged_df


def strata_maker(df, num_strata):
    """
    Orders the precincts by dem_ratio and partitions into NUM_STRATA equal groups
    Assigns Stratum 1 as the most democratic one
    Returns the dataframe with the added strata column
    """
    df = df[df.CLINTON.notnull()]
    df = df[df.CLINTON != 0]
    df['DEM_RATIO'] = df.CLINTON / (df.CLINTON + df.TRUMP)
    df = df.sort_values('DEM_RATIO', ascending=True)

    labels = [i for i in range(1, num_strata+1)]
    # Produce labels for the strata names
    df['STRATA'] = pd.qcut(df['DEM_RATIO'], num_strata, labels=labels).astype(str)
    return df


def process_one_district(old_file, new_file, race, racetype):
    """
    :param old_file: filename of older vote totals (earlier year)
    :param new_file: filename of new vote totals (later year)
    :param race: D#, SEN, GOV
    :param racetype: D, G, or S
    :return: a pandas df of a single row
    """
    old_df = pd.read_csv(old_file, dtype={'COUNTY': str, 'PRECINCT': str})
    new_df = pd.read_csv(new_file, dtype={'COUNTY': str, 'PRECINCT': str})

    combined = merge(old_df, new_df)  # merge
    with_strata = strata_maker(combined, 3)  # add strata

    votes_obj = Votes(with_strata)  # create the vote object

    return votes_obj.wide_strata_summary(race, racetype)  # will give a row per district


def mostrecent(files):
    """Helper to get more recently scrapped file"""
    if len(files) > 0:
        int_names = [int(f.split('.')[0]) for f in files]
        most_recent = max(int_names)
        index = int_names.index(most_recent)
    else:
        raise RuntimeError('File %s not found' % files)
    return files[index]


def get_filepaths(path, alert):
    """
    For a specified alert
    :return: the filepaths for a given alertname
    """
    data2016 = path + 'msds621_election_decisons/data/data2016/'
    scrape_2018 = path + 'msds621_election_decisons/data/scrape_2018/'

    paths = []

    races = [d for d in os.listdir(data2016 + alert) if not d.startswith('.')]

    for r in races:
        results_2016 = data2016 + alert + '/' + r + '/results2016.csv'

        files = [d for d in os.listdir(scrape_2018 + alert + '/' + r + '/') if
                 not d.startswith('.')]
        last_scrape = scrape_2018 + alert + '/' + r + '/' + mostrecent(files)

        paths.append((results_2016, last_scrape, r))

    return paths


if __name__ == '__main__':

    # build empty df with proper columns
    columns = ['STATE', 'RACE', 'S1_DEM_RATIO', 'S2_DEM_RATIO', 'S3_DEM_RATIO',
               'S1_REP_RATIO', 'S2_REP_RATIO', 'S3_REP_RATIO', 'S1_COR(DD)',
               'S2_COR(DD)', 'S3_COR(DD)', 'S1_COR(RR)', 'S2_COR(RR)', 'S3_COR(RR)',
               'WINNER']
    df = pd.DataFrame(columns=columns)

    abs_path = sys.argv[1]  # /Users/nicolekacirek/Desktop/USF/Fall_Module_2/Machine_Learning/

    alerts = [d for d in os.listdir(abs_path + 'msds621_election_decisons/data/data2016/') if not d.startswith('.')]

    path_pairs = []
    for a in alerts:
        path_pairs.extend(get_filepaths(abs_path, a))

    # path_pairs = get_filepaths(abs_path, 'NC_SOS')

    for p in path_pairs:
        new_df_row = process_one_district(p[0], p[1], p[2], p[2][0])
        df = df.append(new_df_row)

    df.to_csv(abs_path + 'msds621_election_decisons/data/final.csv', index=False)

