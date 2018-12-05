from SmallVoteLib import *
import os
import sys
import re


def merge(old, new):
    """
    Helper method that merges 2016 election full_data frame with incoming 2018 election full_data frame
    """
    merged_df = pd.merge(old, new, how='outer',
                         on=(['STATE', 'COUNTY', 'PRECINCT']))[['STATE', 'COUNTY',
                                                                'PRECINCT', 'PAST_DEM',
                                                                'PAST_REP', 'DEM', 'REP']]
    merged_df = merged_df.rename({'STATE_x': 'STATE', 'DEM': 'NEW_DEM', 'REP': 'NEW_REP'}, axis=1)

    # check if both are 0
    mask = (merged_df.NEW_DEM == 0) & (merged_df.NEW_REP == 0)
    merged_df.loc[mask, 'NEW_REP'] = np.nan
    merged_df.loc[mask, 'NEW_DEM'] = np.nan

    return merged_df


def process_one_district(old_file, new_file, race, racetype, midterm_year):
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

    votes_obj = Votes(combined, midterm_year)  # create the vote object

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


def get_old_filepaths(path, alert):
    """
    For a specified alert
    :return: the filepaths for a given alertname and the race
    """
    data2016 = path + 'msds621_election_decisons/full_data/efs/data2016/'
    scrape_2018 = path + 'msds621_election_decisons/full_data/efs/scrape_2018/'

    paths = []

    races = [d for d in os.listdir(data2016 + alert) if not d.startswith('.')]

    for r in races:
        results_2016 = data2016 + alert + '/' + r + '/results2016.csv'

        files = [d for d in os.listdir(scrape_2018 + alert + '/' + r + '/') if
                 not d.startswith('.')]
        last_scrape = scrape_2018 + alert + '/' + r + '/' + mostrecent(files)

        paths.append((results_2016, last_scrape, r))

    return paths


def get_new_filepaths(path, state):
    """
    For a specified alert
    :return: a list of tuples - (president_results, midterm_results, race)
    """

    data_path = path + 'msds621_election_decisons/full_data/'

    paths = []

    for d in os.listdir(data_path + state + '/Presidential'):
        if not d.startswith('.'):
            pres_path = os.path.abspath(data_path+ state + '/Presidential/' + d)
            race, year = re.split('[._]', d)[0:2]
            midt_race = race + '_2014.csv'
            midt_path = os.path.abspath(data_path+ state + '/Midterm/' + midt_race)
            paths.append((pres_path, midt_path, race))

    return paths


def get_partial_filepaths():
    """
    get the filepaths for the partially reporting files
    :return: a list of tuples - (president_results, midterm_results, race)
    """
    return None


if __name__ == '__main__':

    # build empty df with proper columns
    columns = ['STATE', 'RACE',
               'S1_DEM_RATIO', 'S2_DEM_RATIO', 'S3_DEM_RATIO',
               'S4_DEM_RATIO', 'S5_DEM_RATIO', 'S6_DEM_RATIO',
               'S1_REP_RATIO', 'S2_REP_RATIO', 'S3_REP_RATIO',
               'S4_REP_RATIO', 'S5_REP_RATIO', 'S6_REP_RATIO',
               'S1_COR(DD)', 'S2_COR(DD)', 'S3_COR(DD)',
               'S4_COR(DD)', 'S5_COR(DD)', 'S6_COR(DD)',
               'S1_COR(RR)', 'S2_COR(RR)', 'S3_COR(RR)',
               'S4_COR(RR)', 'S5_COR(RR)', 'S6_COR(RR)',
               'TIGHT_RACE', 'WINNER']
    df = pd.DataFrame(columns=columns)

    abs_path = sys.argv[1]  # absolute path to dir containing the repo

    alerts = [d for d in os.listdir(abs_path + 'msds621_election_decisons/full_data/efs/data2016/') if not d.startswith('.')]

    path_pairs = []
    for a in alerts:
        path_pairs.extend(get_old_filepaths(abs_path, a))

    for p in path_pairs:
        new_df_row = process_one_district(p[0], p[1], p[2], p[2][0], 2018)
        df = df.append(new_df_row)

    # repeat for the new states full_data
    ignore = ['efs', 'Build', 'final.csv', 'full_final.csv']
    states = [d for d in os.listdir(abs_path + 'msds621_election_decisons/full_data/')
              if not d.startswith('.') and d not in ignore]

    path_pairs = []
    for s in states:
        path_pairs.extend(get_new_filepaths(abs_path, s))

    for p in path_pairs:
        new_df_row = process_one_district(p[0], p[1], p[2], p[2][0], 2014)
        df = df.append(new_df_row)

    df.to_csv(abs_path + 'msds621_election_decisons/full_data/full_final.csv', index=False)

