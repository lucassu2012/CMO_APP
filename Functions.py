import numpy as np
import mapclassify
import pandas as pd
from sklearn import preprocessing, gaussian_process, metrics


# %% adjust
# adjust display settings
# pd.reset_option("display.width")
# pd.reset_option("display.max_columns")
# pd.get_option("display.width")
# pd.get_option("display.max_columns")
pd.set_option("display.width", 240)
pd.set_option("display.max_columns", 9)


# %% define calculation functions
def cal_nr_terminal_ratio(df, regex='device_count', suffix=''):
    # np.add(df[regex + '_4g_ios' + suffix],
    #        df[regex + '_4g_ad' + suffix])
    ter_4g_total = np.nansum([df[regex + '_4g_ios' + suffix],
                              df[regex + '_4g_ad' + suffix]],
                             axis=0)
    ter_5g_ip12 = np.nansum([df[regex + '_ip12_5g' + suffix],
                             df[regex + '_ip12_fb' + suffix],
                             df[regex + '_ip12_lk' + suffix]],
                            axis=0)
    ter_5g_ad = np.nansum([df[regex + '_ad_5g' + suffix],
                           df[regex + '_ad_fb' + suffix],
                           df[regex + '_ad_lk' + suffix]],
                          axis=0)
    ter_5g_total = np.nansum([ter_5g_ip12, ter_5g_ad], axis=0)
    ter_total = np.nansum([ter_4g_total + ter_5g_total], axis=0)
    r = np.divide(ter_5g_total, ter_total)
    return np.round(r * 100, 0)


def cal_nr_register_ratio(df, regex='device_count', suffix=''):
    ter_5g_ip12 = np.nansum([df[regex + '_ip12_5g' + suffix],
                             df[regex + '_ip12_fb' + suffix],
                             df[regex + '_ip12_lk' + suffix]],
                            axis=0)
    ter_5g_ad = np.nansum([df[regex + '_ad_5g' + suffix],
                           df[regex + '_ad_fb' + suffix],
                           df[regex + '_ad_lk' + suffix]],
                          axis=0)
    ter_5g_total = np.nansum([ter_5g_ip12, ter_5g_ad], axis=0)
    ter_5g_reg = np.nansum([df[regex + '_ip12_5g' + suffix],
                            df[regex + '_ad_5g' + suffix]],
                           axis=0)
    r = np.divide(ter_5g_reg, ter_5g_total)
    return np.round(r * 100, 0)


def cal_nr_function_ratio(df, regex='device_count', suffix=''):
    ter_5g_ip12 = np.nansum([df[regex + '_ip12_5g' + suffix],
                             df[regex + '_ip12_fb' + suffix],
                             df[regex + '_ip12_lk']],
                            axis=0)
    ter_5g_ad = np.nansum([df[regex + '_ad_5g' + suffix],
                           df[regex + '_ad_fb' + suffix],
                           df[regex + '_ad_lk' + suffix]],
                          axis=0)
    ter_5g_total = np.nansum([ter_5g_ip12, ter_5g_ad], axis=0)
    ter_5g_fun_ip12 = np.nansum([df[regex + '_ip12_5g' + suffix],
                                 df[regex + '_ip12_fb' + suffix]],
                                axis=0)
    ter_5g_fun_ad = np.nansum([df[regex + '_ad_5g' + suffix],
                               df[regex + '_ad_fb' + suffix]],
                              axis=0)
    ter_5g_fun = np.nansum([ter_5g_fun_ip12, ter_5g_fun_ad], axis=0)
    r = np.divide(ter_5g_fun, ter_5g_total)
    return np.round(r * 100, 0)


def cal_nr_fallback_ratio(df, regex='device_count', suffix=''):
    ter_5g_fun_ip12 = np.nansum([df[regex + '_ip12_5g' + suffix],
                                 df[regex + '_ip12_fb' + suffix]],
                                axis=0)
    ter_5g_fun_ad = np.nansum([df[regex + '_ad_5g' + suffix],
                               df[regex + '_ad_fb' + suffix]],
                              axis=0)
    ter_5g_fun = np.nansum([ter_5g_fun_ip12, ter_5g_fun_ad], axis=0)
    ter_5g_fb = np.nansum([df[regex + '_ip12_fb' + suffix],
                           df[regex + '_ad_fb' + suffix]],
                          axis=0)
    r = np.divide(ter_5g_fb, ter_5g_fun)
    return np.round(r * 100, 0)


def cal_ip12_terminal_ratio(df, regex='device_count', suffix=''):
    ter_5g_ip12 = np.nansum([df[regex + '_ip12_5g' + suffix],
                             df[regex + '_ip12_fb' + suffix],
                             df[regex + '_ip12_lk' + suffix]],
                            axis=0)
    ter_5g_ad = np.nansum([df[regex + '_ad_5g' + suffix],
                           df[regex + '_ad_fb' + suffix],
                           df[regex + '_ad_lk' + suffix]],
                          axis=0)
    ter_5g_total = np.nansum([ter_5g_ip12, ter_5g_ad], axis=0)
    r = np.divide(ter_5g_ip12, ter_5g_total)
    return np.round(r * 100, 0)


def cal_ip12_register_ratio(df, regex='device_count', suffix=''):
    ter_5g_ip12 = np.nansum([df[regex + '_ip12_5g' + suffix],
                             df[regex + '_ip12_fb' + suffix],
                             df[regex + '_ip12_lk' + suffix]],
                            axis=0)
    r = np.divide(df[regex + '_ip12_5g' + suffix], ter_5g_ip12)
    return np.round(r * 100, 0)


def cal_ip12_function_ratio(df, regex='device_count', suffix=''):
    ter_5g_ip12 = np.nansum([df[regex + '_ip12_5g' + suffix],
                             df[regex + '_ip12_fb' + suffix],
                             df[regex + '_ip12_lk' + suffix]],
                            axis=0)
    ter_5g_fun_ip12 = np.nansum([df[regex + '_ip12_5g' + suffix],
                                 df[regex + '_ip12_fb' + suffix]],
                                axis=0)
    r = np.divide(ter_5g_fun_ip12, ter_5g_ip12)
    return np.round(r * 100, 0)


def cal_ip12_fallback_ratio(df, regex='device_count', suffix=''):
    ter_5g_fun_ip12 = np.nansum([df[regex + '_ip12_5g' + suffix],
                                 df[regex + '_ip12_fb' + suffix]],
                                axis=0)
    r = np.divide(df[regex + '_ip12_fb' + suffix], ter_5g_fun_ip12)
    return np.round(r * 100, 0)


def cal_nr_speed_gain_ratio(df, regex='device_count', suffix=''):
    ter_4g_total = np.nansum([df[regex + '_4g_ios' + suffix],
                              df[regex + '_4g_ad' + suffix]],
                             axis=0)
    ter_4g_speed = np.divide(np.nansum([df[regex + '_4g_ios' + suffix] * df['avg_dl_4g_ios' + suffix],
                                        df[regex + '_4g_ad' + suffix] * df['avg_dl_4g_ad' + suffix]],
                                       axis=0),
                             ter_4g_total, where=ter_4g_total != 0)
    ter_5g_total = np.nansum([df[regex + '_ip12_5g' + suffix], df[regex + '_ad_5g' + suffix]],
                             axis=0)
    ter_5g_speed = np.divide(np.nansum([df[regex + '_ip12_5g' + suffix] * df['avg_dl_ip12_5g' + suffix],
                                        df[regex + '_ad_5g' + suffix] * df['avg_dl_ad_5g' + suffix]],
                                       axis=0),
                             ter_5g_total, where=ter_5g_total != 0)
    g = np.divide(ter_5g_speed, ter_4g_speed, where=ter_4g_speed != 0)
    g[g == 0] = np.nan
    return np.round(g * 100, 0)


def cal_ip12_speed_gain_ratio(df, regex='device_count', suffix=''):
    g = np.divide(df['avg_dl_ip12_5g' + suffix],
                  df['avg_dl_4g_ios' + suffix])
    return np.round(g * 100, 0)


def cal_nr_total_samples(df, regex='device_count', suffix=''):
    ter_5g_ip12 = np.nansum([df[regex + '_ip12_5g' + suffix],
                             # df[regex + '_ip12_fb' + suffix],
                             # df[regex + '_ip12_lk' + suffix]
                             ],
                            axis=0)
    ter_5g_ad = np.nansum([df[regex + '_ad_5g' + suffix],
                           # df[regex + '_ad_fb' + suffix],
                           # df[regex + '_ad_lk' + suffix]
                           ],
                          axis=0)
    ter_5g_total = np.nansum([ter_5g_ip12, ter_5g_ad], axis=0)
    return np.round(ter_5g_total, 0)


def cal_ip12_total_samples(df, regex='device_count', suffix=''):
    ter_5g_ip12 = np.nansum([df[regex + '_ip12_5g' + suffix],
                             # df[regex + '_ip12_fb' + suffix],
                             # df[regex + '_ip12_lk' + suffix]
                             ],
                            axis=0)
    return np.round(ter_5g_ip12, 0)


def cal_nr_average_speed(df, regex='device_count', suffix=''):
    ter_5g_total = np.nansum([df[regex + '_ip12_5g' + suffix],
                              df[regex + '_ad_5g' + suffix]],
                             axis=0)
    ter_5g_speed = np.divide(np.nansum([df[regex + '_ip12_5g' + suffix] * df['avg_dl_ip12_5g' + suffix],
                                        df[regex + '_ad_5g' + suffix] * df['avg_dl_ad_5g' + suffix]],
                                       axis=0),
                             ter_5g_total, where=(ter_5g_total != 0))
    # ter_5g_speed[ter_5g_speed == 0] = np.nan
    return np.round(ter_5g_speed, 0)


def cal_ip12_average_speed(df, regex='device_count', suffix=''):
    ter_ip12_speed = df['avg_dl_ip12_5g' + suffix]
    return np.round(ter_ip12_speed, 0)


def cal_4g_average_speed(df, regex='device_count', suffix=''):
    ter_4g_total = np.nansum([df[regex + '_4g_ios' + suffix],
                              df[regex + '_4g_ad' + suffix]],
                             axis=0)
    ter_4g_speed = np.divide(np.nansum([df[regex + '_4g_ios' + suffix] * df['avg_dl_4g_ios' + suffix],
                                        df[regex + '_4g_ad' + suffix] * df['avg_dl_4g_ad' + suffix]],
                                       axis=0),
                             ter_4g_total, where=(ter_4g_total != 0))
    # ter_4g_speed[ter_4g_speed == 0] = np.nan
    return np.round(ter_4g_speed, 0)


def cal_tns_tns(df, regex='device_count', suffix=''):
    ter_4g_total = np.nansum([df[regex + '_4g_ios' + suffix],
                              df[regex + '_4g_ad' + suffix]],
                             axis=0)
    ter_4g_speed = np.divide(np.nansum([df[regex + '_4g_ios' + suffix] * df['avg_dl_4g_ios' + suffix],
                                        df[regex + '_4g_ad' + suffix] * df['avg_dl_4g_ad' + suffix]],
                                       axis=0),
                             ter_4g_total, where=(ter_4g_total != 0))
    # ter_4g_speed[ter_4g_speed == 0] = np.nan
    return np.round(ter_4g_speed, 0)


# %%
def palette_n_dict(gdf, col, bin_num=5, bin_decimal=2, palette='RdYlGn_r', classifiers='Quantiles'):
    # print('classifiers supports:')
    # print(mapclassify.classifiers.CLASSIFIERS)
    mc = mapclassify.__getattribute__(classifiers)(gdf[col].dropna(), k=bin_num - 1)
    bins = (np.ceil(mc.bins * 10 ** bin_decimal) / 10 ** bin_decimal).tolist()
    bin_min = np.floor(gdf[col].min() * 10 ** bin_decimal) / 10 ** bin_decimal
    palette_n = {palette: [bin_min] + bins}
    return palette_n


# %% functions
def remove_outlier(coords, val, std_threshold):
    # calculate summary statistics
    val_mean, val_std = np.mean(val), np.std(val)
    # identify outliers
    val_cut_off = val_std * std_threshold
    val_lower = max(val.min(), val_mean - val_cut_off)
    val_upper = min(val.max(), val_mean + val_cut_off)
    # identify outliers
    non_outliers = np.where((val > val_lower) & (val < val_upper))[0]
    return coords[non_outliers], val[non_outliers]


def add_kpi_cat(kpi_df, kpi_dict, kpi_thd, cat_default):
    """
    :param kpi_df
    :param kpi_dict: {'2c_value': ['Inhabitants_Density', 'Average_income'],
                      '2b_value': ['Enterprise_Density'],
                      '2h_value': ['Building_Density', 'Average_income']}
    :param kpi_thd: kpi_thd = pd.DataFrame({'Inhabitants_Density': [50, 10],
                                            'Average_income': [25000, 20000],
                                            'Enterprise_Density': [15, 1],
                                            'Building_Density': [20, 5],
                                            })
                    kpi_thd.index = ['H', 'M']
    :param cat_default: 'L'
    """
    df = kpi_df.copy()
    for x in kpi_dict.keys():
        kpi = kpi_dict[x]
        df[x] = np.select(
            condlist=[(df[kpi] >= row[1][kpi]).all(axis=1) for row in kpi_thd.iterrows()],
            choicelist=kpi_thd.index,
            default=cat_default)
    return df
