#!/usr/bin/env python3

from winners import won
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
        df['TOTAL_2016_VOTES'] = df['PAST_DEM'] + df['PAST_REP']
        df['TOTAL_2018_VOTES'] = df['NEW_DEM'] + df['NEW_REP']
        self.df = df[df['TOTAL_2016_VOTES'] != 0]
        self.strata_lst = list(df.STRATA.unique())
        self.df = self.df[(df.NEW_DEM.notnull()) & (df.PAST_DEM.notnull())]  # Valid incoming data

    def democraticRatioByStrata(self):
        """
        Computes the ratio (avg percent voting Democratic in 2018)/(avg percent voting Democratic in 2016) by stratum.
        returns:
            A list of the ratios by strata
        """
        df_copy = self.df.copy()
        df_copy['PAST_DEM_Ratio'] = df_copy.PAST_DEM / (df_copy.PAST_DEM + df_copy.PAST_REP)
        df_copy['Dem_Ratio'] = df_copy.NEW_DEM / (df_copy.NEW_DEM + df_copy.NEW_REP)
        df_copy['RP_Dem'] = df_copy['Dem_Ratio'] / df_copy['PAST_DEM_Ratio']
        ratio_by_strata = df_copy.groupby('STRATA').mean()['RP_Dem']  # Computing average by strata
        ratio_by_strata = [el for el in ratio_by_strata if el > 0]
        return ratio_by_strata

    def republicanRatioByStrata(self):
        """
        Computes the ratio (avg percent voting Republican in 2018)/(avg percent voting Republican in 2016) by stratum.
        returns:
             A list of the ratios by strata
        """
        df_copy = self.df.copy()
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

    def wide_strata_summary(self, race, race_type):
        """
        Build the data frame per district for ml project
        """
        dem_ratios = self.democraticRatioByStrata()
        rep_ratios = self.republicanRatioByStrata()
        dd_cor = self.corr_by_strata()
        rr_cor = self.corr_by_strata(dem=False)
        race = self.df['STATE'].unique()[0] + '_' + race

        strata_tbl = pd.DataFrame({
            'STATE': self.df['STATE'].unique()[0],
            'RACE': race_type,
            'S1_DEM_RATIO': dem_ratios[0],
            'S2_DEM_RATIO': dem_ratios[1],
            'S3_DEM_RATIO': dem_ratios[2],
            'S1_REP_RATIO': rep_ratios[0],
            'S2_REP_RATIO': rep_ratios[1],
            'S3_REP_RATIO': rep_ratios[2],
            'S1_COR(DD)': dd_cor[0],
            'S2_COR(DD)': dd_cor[1],
            'S3_COR(DD)': dd_cor[2],
            'S1_COR(RR)': rr_cor[0],
            'S2_COR(RR)': rr_cor[1],
            'S3_COR(RR)': rr_cor[2],
            'WINNER': won[race]
        }, index=[0])

        return strata_tbl
