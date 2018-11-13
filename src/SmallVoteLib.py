#!/usr/bin/env python3

import pandas as pd
import numpy as np


np.seterr(invalid='ignore')


class Votes:
    """
    - A votes object is instantiated with a data frame object (that already contains
    strata assignments that have been correctly collapsed)
    - The list of strata in the object are added as an attribute for easier reference later on
    The first handful of methods are to calculate statistics we need for the latter portion
    of methods, which are concerned with prediction and printing of these statistics and predictions
    """

    def __init__(self, df):
        # Adding column to original data frame
        df['TOTAL_2016_VOTES'] = df['CLINTON'] + df['TRUMP']
        df['TOTAL_2018_VOTES'] = df['NEW_DEM'] + df['NEW_REP']
        self.df = df[df['TOTAL_2016_VOTES'] != 0]
        self.strata_lst = list(df.STRATA.unique())
        self.df = self.df[(df.NEW_DEM.notnull()) & (df.CLINTON.notnull())]  # Valid incoming data

    def getPrecinctCounts(self):
        """
        computes the number of precincts in each strata
        """
        return self.df.groupby('STRATA').count()['NEW_DEM']

    def totalReportingByStrata(self):
        """
        Computes the number of precincts reporting in 2018 by stratum.
        returns:
            A pandas data frame including stratum number and number of precincts reporting
        """
        stratum_num = np.asarray([self.df[self.df['STRATA'] == i]['NEW_DEM'].count() for i in self.strata_lst])
        tbl = pd.DataFrame({'Stratum': self.strata_lst, 'Total_Precincts_Reporting': stratum_num})
        return tbl.set_index('Stratum')

    def percentReportingByStrata(self):
        """
        Computes the percentage of precincts reporting in 2018 by stratum.
        returns:
            A pandas data frame including stratum number and percentage of precincts reporting
        """
        strata_counts = self.df.groupby('STRATA').count()['STATE']
        stratum_perc = np.asarray([self.df[self.df['STRATA'] == i]['NEW_DEM'].count() for i in self.strata_lst]) / \
                       np.asarray([el for el in strata_counts if el > 0]) * 100
        tbl = pd.DataFrame({'Stratum': self.strata_lst,
                            'Percent_Precincts_Reporting': np.round(stratum_perc, 1)})
        return tbl.set_index('Stratum')

    def totalVotesByStrata2018(self):
        """
        Computes the total number of votes in 2018 by stratum.
        returns:
            A pandas data frame including stratum number and total votes
        """
        total_votes = self.df.groupby('STRATA').sum()['TOTAL_2018_VOTES']
        total_votes = total_votes.astype(int)
        tbl = pd.DataFrame({'Stratum': self.strata_lst,
                            'Total_Votes': np.asarray([el for el in total_votes if el > 0])})
        return tbl.set_index('Stratum')

    def totalDemocraticVotesByStrata2018(self):
        """
            Computes the total number of democratic votes in 2018 by stratum.
            returns:
            A pandas data frame including stratum number and total democratic votes
            """
        total_votes = self.df.groupby('STRATA').sum()['NEW_DEM']
        total_votes = total_votes.astype(int)
        tbl = pd.DataFrame({'Stratum': self.strata_lst,
                            'Total_Votes': np.asarray([el for el in total_votes if el > 0])})
        return tbl.set_index('Stratum')

    def totalVotesByStrata2016(self):
        """
        Computes the total number of votes in 2016 by stratum.
        returns:
            A pandas data frame including stratum number and total votes
        """
        total_votes = self.df.groupby('STRATA').sum()['TOTAL_2016_VOTES']
        total_votes = total_votes.astype(int)
        tbl = pd.DataFrame({'Stratum': self.strata_lst,
                            'Total_Votes': np.asarray([el for el in total_votes if el > 0])})
        return tbl.set_index('Stratum')

    def percentVotesByStrata(self):
        """
        Computes the percent of votes reported in 2016 by stratum.
        returns:
            A pandas data frame including stratum number and total votes
        """
        total_votes = self.totalVotesByStrata2016()['Total_Votes']
        total_2016_votes = self.df.groupby('STRATA').sum()['TOTAL_2016_VOTES']
        total_votes_perc = np.asarray([el for el in total_2016_votes if el > 0]) / \
                           np.asarray([el for el in total_votes if el > 0])
        tbl = pd.DataFrame({'Stratum': self.strata_lst,
                            'Percent_Votes': np.round(total_votes_perc * 100, 1)})
        return tbl.set_index('Stratum')

    def democraticRatioByStrata(self):
        """
        Computes the ratio (avg percent voting Democratic in 2018)/(avg percent voting Democratic in 2016) by stratum.
        returns:
            A pandas data frame including stratum number and respective voting ratios
        """
        df_copy = self.df.copy()
        df_copy['Clinton_Ratio'] = df_copy.CLINTON / (df_copy.CLINTON + df_copy.TRUMP)
        df_copy['Dem_Ratio'] = df_copy.NEW_DEM / (df_copy.NEW_DEM + df_copy.NEW_REP)
        df_copy['RP_Dem'] = df_copy['Dem_Ratio'] / df_copy['Clinton_Ratio']
        ratio_by_strata = df_copy.groupby('STRATA').mean()['RP_Dem']  # Computing average by strata
        ratio_by_strata = [el for el in ratio_by_strata if el > 0]
        tbl = pd.DataFrame({'Stratum': self.strata_lst,
                            'Dem_Ratio': np.asarray(ratio_by_strata)})
        return tbl.set_index('Stratum')

    def republicanRatioByStrata(self):
        """
        Computes the ratio (avg percent voting Republican in 2018)/(avg percent voting Republican in 2016) by stratum.
        returns:
            A pandas data frame including stratum number and respective voting ratios
        """
        df_copy = self.df.copy()
        df_copy['Trump_Ratio'] = df_copy.TRUMP / (df_copy.CLINTON + df_copy.TRUMP)
        df_copy['Rep_Ratio'] = df_copy.NEW_REP / (df_copy.NEW_DEM + df_copy.NEW_REP)
        df_copy['RP_Rep'] = df_copy['Rep_Ratio'] / df_copy['Trump_Ratio']
        ratio_by_strata = df_copy.groupby('STRATA').mean()['RP_Rep']
        ratio_by_strata = [el for el in ratio_by_strata if el > 0]
        tbl = pd.DataFrame({'Stratum': self.strata_lst,
                            'Rep_Ratio': np.asarray(ratio_by_strata)})
        return tbl.set_index('Stratum')

    def corr_by_race(self, num=True, dem=True):
        if num and dem:
            return self.df['CLINTON'].corr(self.df['NEW_DEM'])

        elif num and not dem:
            return self.df['TRUMP'].corr(self.df['NEW_REP'])

        elif not num and dem:
            dem_2016_perc = self.df['CLINTON'] / self.df['TOTAL_2016_VOTES']
            dem_2018_perc = self.df['NEW_DEM'] / self.df['TOTAL_2018_VOTES']
            return dem_2016_perc.corr(dem_2018_perc)

        else:
            rep_2016_perc = self.df['TRUMP'] / self.df['TOTAL_2016_VOTES']
            rep_2018_perc = self.df['NEW_REP'] / self.df['TOTAL_2018_VOTES']
            return rep_2016_perc.corr(rep_2018_perc)

    def corr_by_strata(self, num=True, dem=True):
        if num and dem:
            corrs = self.df.groupby('STRATA')[['CLINTON', 'NEW_DEM']].corr().iloc[0::2, -1]
            corrs_only = [corrs.iloc[[i]][0] for i in range(len(corrs))]
            tbl = pd.DataFrame({'Stratum': self.strata_lst,
                                'C(DD#)': corrs_only})
            return tbl.set_index('Stratum')

        elif num and not dem:
            corrs = self.df.groupby('STRATA')[['TRUMP', 'NEW_REP']].corr().iloc[0::2, -1]
            corrs_only = [corrs.iloc[[i]][0] for i in range(len(corrs))]
            tbl = pd.DataFrame({'Stratum': self.strata_lst,
                                'C(RR#)': corrs_only})
            return tbl.set_index('Stratum')

        elif not num and dem:
            tmp_df = self.df
            tmp_df['DEM_2016_PERC'] = self.df['CLINTON'] / self.df['TOTAL_2016_VOTES']
            tmp_df['DEM_2018_PERC'] = self.df['NEW_DEM'] / self.df['TOTAL_2018_VOTES']
            corrs = tmp_df.groupby('STRATA')[['DEM_2016_PERC', 'DEM_2018_PERC']].corr().iloc[0::2, -1]
            corrs_only = [corrs.iloc[[i]][0] for i in range(len(corrs))]
            tbl = pd.DataFrame({'Stratum': self.strata_lst,
                                'C(DD%)': corrs_only})
            return tbl.set_index('Stratum')

        else:
            tmp_df = self.df
            tmp_df['REP_2016_PERC'] = self.df['TRUMP'] / self.df['TOTAL_2016_VOTES']
            tmp_df['REP_2018_PERC'] = self.df['NEW_REP'] / self.df['TOTAL_2018_VOTES']
            corrs = tmp_df.groupby('STRATA')[['REP_2016_PERC', 'REP_2018_PERC']].corr().iloc[0::2, -1]
            corrs_only = [corrs.iloc[[i]][0] for i in range(len(corrs))]
            tbl = pd.DataFrame({'Stratum': self.strata_lst,
                                'C(RR%)': corrs_only})
            return tbl.set_index('Stratum')

    def strataSummary(self, printable=False):
        """
        Creates and returns a pandas dataframe including all summary metrics by strata.
        params:
            printable - boolean indicating if you want a nicely printed output (default=False)
                        If True, all cell values will be formatted as strings
        returns:
            pandas dataframe with all summary metrics
        """
        strata_tbl = pd.DataFrame({'#Prec': self.getPrecinctCounts(),
                                   '#Reporting': self.totalReportingByStrata()['Total_Precincts_Reporting'],
                                   '%PctRepd': self.percentReportingByStrata()['Percent_Precincts_Reporting'],
                                   '#Votes16': self.totalVotesByStrata2016()['Total_Votes'],
                                   '%Votes16': self.percentVotesByStrata()['Percent_Votes'],
                                   '#Votes18': self.totalVotesByStrata2018()['Total_Votes'],
                                   '#DVotes18': self.totalDemocraticVotesByStrata2018()['Total_Votes'],
                                   'DRatio': self.democraticRatioByStrata()['Dem_Ratio'],
                                   'RRatio': self.republicanRatioByStrata()['Rep_Ratio'],
                                   'Stratum': self.strata_lst,
                                   'C(DD#)': self.corr_by_strata()['C(DD#)'],
                                   'C(RR#)': self.corr_by_strata(dem=False)['C(RR#)'],
                                   'C(DD%)': self.corr_by_strata(num=False)['C(DD%)'],
                                   'C(RR%)': self.corr_by_strata(num=False, dem=False)['C(RR%)']})
        strata_tbl = strata_tbl.set_index('Stratum')
        if printable:
            # Formatting table to look nice
            strata_tbl['#Prec'] = strata_tbl['#Prec'].map('{:.0f}'.format)
            strata_tbl['#Votes16'] = strata_tbl['#Votes16'].map('{:,}'.format)
            strata_tbl['%Votes16'] = strata_tbl['%Votes16'].map('{:.1f}%'.format)
            strata_tbl['%PctRepd'] = strata_tbl['%PctRepd'].map('{:.1f}%'.format)
            strata_tbl['#Votes18'] = strata_tbl['#Votes18'].map('{:,}ls'.format)
            strata_tbl['#DVotes18'] = strata_tbl['#DVotes18'].map('{:,}ls'.format)
            strata_tbl['DRatio'] = strata_tbl['DRatio'].map('{:.2f}'.format)
            strata_tbl['RRatio'] = strata_tbl['RRatio'].map('{:.2f}'.format)
            strata_tbl['C(DD#)'] = strata_tbl['C(DD#)'].map('{:.2f}'.format)
            strata_tbl['C(RR#)'] = strata_tbl['C(RR#)'].map('{:.2f}'.format)
            strata_tbl['C(DD%)'] = strata_tbl['C(DD%)'].map('{:.2f}'.format)
            strata_tbl['C(RR%)'] = strata_tbl['C(RR%)'].map('{:.2f}'.format)
        return strata_tbl

    def wide_strata_summary(self):
        return None