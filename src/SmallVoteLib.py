#!/usr/bin/env python3

from winners import *
import pandas as pd
import numpy as np


np.seterr(invalid='ignore')


class Votes:
    """
    - A votes object is instantiated with a full_data frame object (that already contains
    strata assignments that have been correctly collapsed)
    - The list of strata in the object are added as an attribute for easier reference later on
    The first handful of methods are to calculate statistics we need for the latter portion
    of methods, which are concerned with prediction and printing of these statistics and predictions
    """

    def __init__(self, df, midterm_year):
        # Adding column to original full_data frame
        df['TOTAL_2016_VOTES'] = df['PAST_DEM'] + df['PAST_REP']
        self.df = df[df['TOTAL_2016_VOTES'] != 0]
        self.df = self.df[(df.NEW_DEM.notnull()) & (df.PAST_DEM.notnull())]  # Valid incoming full_data
        self.midterm_year = midterm_year
        self.df = self.strata_maker(self.df, 3)  # add strata
        self.strata_lst = list(self.df.STRATA.unique())

    def strata_maker(self, df, num_strata):
        """
        Orders the precincts by dem_ratio and partitions into NUM_STRATA equal groups
        Assigns Stratum 1 as the most democratic one
        Returns the dataframe with the added strata column
        """
        df = df[df.PAST_DEM.notnull()]
        df = df[df.PAST_DEM != 0]
        df['DEM_RATIO'] = df.PAST_DEM / (df.PAST_DEM + df.PAST_REP)
        df = df.sort_values('DEM_RATIO', ascending=True)

        labels = [i for i in range(1, num_strata + 1)]
        # Produce labels for the strata names
        df['STRATA'] = pd.qcut(df['DEM_RATIO'], num_strata, labels=labels).astype(str)
        return df

    def democraticRatioByStrata(self):
        """
        Computes the ratio (avg percent voting Democratic in 2018)/(avg percent voting Democratic in 2014) by stratum.
        returns:
            A list of the ratios by strata
        """
        df_copy = self.df.copy()
        df_copy.loc[df_copy.PAST_REP == 0.0, 'PAST_REP'] = 1.0
        df_copy['PAST_DEM_Ratio'] = df_copy.PAST_DEM / (df_copy.PAST_DEM + df_copy.PAST_REP)
        df_copy['Dem_Ratio'] = df_copy.NEW_DEM / (df_copy.NEW_DEM + df_copy.NEW_REP)
        df_copy['RP_Dem'] = df_copy['Dem_Ratio'] / df_copy['PAST_DEM_Ratio']
        ratio_by_strata = df_copy.groupby('STRATA').mean()['RP_Dem']  # Computing average by strata
        ratio_by_strata_final = [el for el in ratio_by_strata if el > 0]
        if len(ratio_by_strata) < 3:
            print(df_copy)
            print(df_copy.STRATA.unique())
            print(ratio_by_strata)
            print(ratio_by_strata_final)
        return ratio_by_strata_final

    def republicanRatioByStrata(self):
        """
        Computes the ratio (avg percent voting Republican in 2018)/(avg percent voting Republican in 2014) by stratum.
        returns:
             A list of the ratios by strata
        """
        df_copy = self.df.copy()
        df_copy.loc[df_copy.PAST_REP == 0.0, 'PAST_REP'] = 1.0
        df_copy['PAST_REP_Ratio'] = df_copy.PAST_REP / (df_copy.PAST_DEM + df_copy.PAST_REP)
        df_copy['Rep_Ratio'] = df_copy.NEW_REP / (df_copy.NEW_DEM + df_copy.NEW_REP)
        df_copy['RP_Rep'] = df_copy['Rep_Ratio'] / df_copy['PAST_REP_Ratio']
        ratio_by_strata = df_copy.groupby('STRATA').mean()['RP_Rep']
        ratio_by_strata = [el for el in ratio_by_strata if el > 0]
        return ratio_by_strata

    def corr_by_strata(self, dem=True):
        if dem:
            corrs = self.df.groupby('STRATA')[['PAST_DEM', 'NEW_DEM']].corr().iloc[0::2, -1]
            corrs_only = [corrs.iloc[[i]][0] for i in range(len(corrs))]
            return corrs_only

        else:
            corrs = self.df.groupby('STRATA')[['PAST_REP', 'NEW_REP']].corr().iloc[0::2, -1]
            corrs_only = [corrs.iloc[[i]][0] for i in range(len(corrs))]
            return corrs_only

    def tight_race(self):
        """
        A race is considered to be "tight" if the difference between the 2018 Dem/Rep
        vote totals is < 10% of the total votes
        :return: True/False
        """
        df_copy = self.df.copy()
        df_copy['TOTAL_2018_VOTES'] = df_copy.NEW_DEM + df_copy.NEW_REP

        percent_diff = abs(df_copy.NEW_DEM.sum() - df_copy.NEW_REP.sum()) / df_copy.TOTAL_2018_VOTES.sum()
        if percent_diff < 0.1:
            return True
        else:
            return False

    def wide_strata_summary(self, race, race_type):
        """
        CO the full_data frame per district for ml project
        """
        dem_ratios = self.democraticRatioByStrata()
        rep_ratios = self.republicanRatioByStrata()
        dd_cor = self.corr_by_strata()
        rr_cor = self.corr_by_strata(dem=False)
        race = self.df['STATE'].unique()[0] + '_' + race
        won = won_2018[race] if self.midterm_year == 2018 else won_2014[race]

        strata_tbl = pd.DataFrame({
            'STATE': self.df['STATE'].unique()[0],
            'RACE': race_type,
            'S1_DEM_RATIO': dem_ratios[0],
            'S2_DEM_RATIO': dem_ratios[1],
            'S3_DEM_RATIO': dem_ratios[2],
            # 'S4_DEM_RATIO': dem_ratios[3],
            # 'S5_DEM_RATIO': dem_ratios[4],
            # 'S6_DEM_RATIO': dem_ratios[5],
            'S1_REP_RATIO': rep_ratios[0],
            'S2_REP_RATIO': rep_ratios[1],
            'S3_REP_RATIO': rep_ratios[2],
            # 'S4_REP_RATIO': rep_ratios[3],
            # 'S5_REP_RATIO': rep_ratios[4],
            # 'S6_REP_RATIO': rep_ratios[5],
            'S1_COR(DD)': dd_cor[0],
            'S2_COR(DD)': dd_cor[1],
            'S3_COR(DD)': dd_cor[2],
            # 'S4_COR(DD)': dd_cor[3],
            # 'S5_COR(DD)': dd_cor[4],
            # 'S6_COR(DD)': dd_cor[5],
            'S1_COR(RR)': rr_cor[0],
            'S2_COR(RR)': rr_cor[1],
            'S3_COR(RR)': rr_cor[2],
            # 'S4_COR(RR)': rr_cor[3],
            # 'S5_COR(RR)': rr_cor[4],
            # 'S6_COR(RR)': rr_cor[5],
            'TIGHT_RACE': self.tight_race(),
            'WINNER': won
        }, index=[0])

        return strata_tbl
