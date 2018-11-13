from SmallVoteLib import *
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


def process_one_district(old_file, new_file, district):
    """
    :param old_file: filename of older vote totals (earlier year)
    :param new_file: filename of new vote totals (later year)
    :param district: integer district number
    :return: a pandas df of a single row
    """
    old_df = pd.read_csv(old_file, dtype={'COUNTY': str, 'PRECINCT': str})
    new_df = pd.read_csv(new_file, dtype={'COUNTY': str, 'PRECINCT': str})

    combined = merge(old_df, new_df)  # merge
    with_strata = strata_maker(combined, 3)  # add strata

    votes_obj = Votes(with_strata)  # create the vote object

    return votes_obj.wide_strata_summary(district)  # will give a row per district


if __name__ == '__main__':

    # set up columns for final df
    columns = ['STATE', 'DISTRICT', 'S1_DEM_RATIO', 'S2_DEM_RATIO', 'S3_DEM_RATIO',
               'S1_REP_RATIO', 'S2_REP_RATIO', 'S3_REP_RATIO', 'S1_COR(DD)',
               'S2_COR(DD)', 'S3_COR(DD)', 'S1_COR(RR)', 'S2_COR(RR)', 'S3_COR(RR)']

    df = pd.DataFrame(columns=columns)
    new_df_row = process_one_district(sys.argv[1], sys.argv[2], 1)
    df = df.append(new_df_row)
    print(df)
