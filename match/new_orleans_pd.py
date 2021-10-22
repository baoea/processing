from lib.date import combine_date_columns
from lib.path import data_file_path, ensure_data_dir
from datamatch import (
    ThresholdMatcher, JaroWinklerSimilarity, DateSimilarity, ColumnsIndex
)
from lib.post import extract_events_from_post
import pandas as pd
import sys
sys.path.append('../')


def match_pprr_against_post(pprr_ipm, post):
    dfa = pprr_ipm[['uid', 'first_name', 'last_name']]
    dfa.loc[:, 'hire_date'] = combine_date_columns(
        pprr_ipm, 'hire_year', 'hire_month', 'hire_day')
    dfa.loc[:, 'fc'] = dfa.first_name.fillna('').map(lambda x: x[:1])
    dfa.loc[:, 'lc'] = dfa.last_name.fillna('').map(lambda x: x[:1])
    dfa = dfa.drop_duplicates(subset=['uid']).set_index('uid')

    dfb = post[['uid', 'first_name', 'last_name']]
    dfb.loc[:, 'hire_date'] = combine_date_columns(
        post, 'hire_year', 'hire_month', 'hire_day')
    dfb.loc[:, 'fc'] = dfb.first_name.fillna('').map(lambda x: x[:1])
    dfb.loc[:, 'lc'] = dfb.last_name.fillna('').map(lambda x: x[:1])
    dfb = dfb.drop_duplicates(subset=['uid']).set_index('uid')

    matcher = ThresholdMatcher(ColumnsIndex(['fc', 'lc']), {
        'first_name': JaroWinklerSimilarity(),
        'last_name': JaroWinklerSimilarity(),
        'hire_date': DateSimilarity()
    }, dfa, dfb, show_progress=True)
    decision = 0.803
    matcher.save_pairs_to_excel(data_file_path(
        "match/pppr_ipm_new_orleans_pd_1946_2018_v_post_pprr_2020_11_06.xlsx"), decision)

    matches = matcher.get_index_pairs_within_thresholds(decision)
    return extract_events_from_post(post, matches, 'New Orleans PD')


def match_award_to_pprr_ipm(award, pprr_ipm):
    dfa = award[['uid', 'first_name', 'last_name']].drop_duplicates()\
        .set_index('uid', drop=True)
    dfa.loc[:, 'fc'] = dfa.first_name.fillna('').map(lambda x: x[:1])
    dfa.loc[:, 'lc'] = dfa.last_name.fillna('').map(lambda x: x[:1])

    dfb = pprr_ipm[['uid', 'first_name', 'last_name']].drop_duplicates()\
        .set_index('uid', drop=True)
    dfb.loc[:, 'fc'] = dfb.first_name.fillna('').map(lambda x: x[:1])
    dfb.loc[:, 'lc'] = dfb.last_name.fillna('').map(lambda x: x[:1])

    matcher = ThresholdMatcher(ColumnsIndex(['fc', 'lc']), {
        "first_name": JaroWinklerSimilarity(),
        "last_name": JaroWinklerSimilarity()
    }, dfa, dfb, show_progress=True)
    decision = 0.93
    matcher.save_pairs_to_excel(data_file_path(
        "match/new_orleans_pd_award_2016_2021_v_pprr_ipm_new_orleans_pd_1946_2018.xlsx"), decision)
    matches = matcher.get_index_pairs_within_thresholds(lower_bound=decision)

    match_dict = dict(matches)
    award.loc[:, 'uid'] = award.uid.map(lambda x: match_dict.get(x, x))
    return award


def match_lprr_to_pprr_ipm(lprr, pprr_ipm):
    dfa = lprr[['uid', 'first_name', 'last_name', 'middle_initial']]
    dfa.loc[:, 'fc'] = dfa.first_name.fillna('').map(lambda x: x[:1])
    dfa.loc[:, 'lc'] = dfa.last_name.fillna('').map(lambda x: x[:1])
    dfa = dfa.drop_duplicates(subset=['uid']).set_index('uid')

    dfb = pprr_ipm[['uid', 'first_name', 'last_name', 'middle_initial']]
    dfb.loc[:, 'fc'] = dfb.first_name.fillna('').map(lambda x: x[:1])
    dfb.loc[:, 'lc'] = dfb.last_name.fillna('').map(lambda x: x[:1])
    dfb = dfb.drop_duplicates(subset=['uid']).set_index('uid')

    matcher = ThresholdMatcher(ColumnsIndex(['fc', 'lc']), {
        'first_name': JaroWinklerSimilarity(),
        'last_name': JaroWinklerSimilarity(),
        'middle_initial': JaroWinklerSimilarity(),
    }, dfa, dfb, show_progress=True)
    decision = .80
    matcher.save_pairs_to_excel(data_file_path(
        'match/new_orleans_lprr_2000_2016_v_pprr_ipm_new_orleans_pd_1946_2018.xlsx'), decision)
    matches = matcher.get_index_clusters_within_thresholds(lower_bound=decision)
    match_dict = dict(matches)

    lprr.loc[:, 'uid'] = lprr.uid.map(lambda x: match_dict.get(x, x))
    return lprr


def match_pprr_csd_to_pprr_ipm(pprr_csd, pprr_ipm):
    dfa = pprr_csd[['uid', 'first_name', 'last_name', 'agency']]
    dfa.loc[:, 'hire_date'] = combine_date_columns(
        pprr_csd, 'hire_year', 'hire_month', 'hire_day')
    dfa.loc[:, 'fc'] = dfa.first_name.fillna('').map(lambda x: x[:1])
    dfa.loc[:, 'lc'] = dfa.last_name.fillna('').map(lambda x: x[:1])
    dfa = dfa.drop_duplicates(subset=['uid']).set_index('uid')

    dfb = pprr_ipm[['uid', 'first_name', 'last_name', 'agency']]
    dfb.loc[:, 'hire_date'] = combine_date_columns(
        pprr_ipm, 'hire_year', 'hire_month', 'hire_day')
    dfb.loc[:, 'fc'] = dfb.first_name.fillna('').map(lambda x: x[:1])
    dfb.loc[:, 'lc'] = dfb.last_name.fillna('').map(lambda x: x[:1])
    dfb = dfb.drop_duplicates(subset=['uid']).set_index('uid')

    matcher = ThresholdMatcher(ColumnsIndex(['fc', 'lc', 'agency']), {
        'first_name': JaroWinklerSimilarity(),
        'last_name': JaroWinklerSimilarity(),
        'hire_date': DateSimilarity(),
    }, dfa, dfb, show_progress=True)
    decision = 1
    matcher.save_pairs_to_excel(data_file_path(
        'match/pprr_new_orleans_csd_2014_v_pprr_ipm_new_orleans_pd_1946_2018.xlsx'), decision)
    matches = matcher.get_index_pairs_within_thresholds(lower_bound=decision)
    match_dict = dict(matches)

    pprr_csd.loc[:, 'uid'] = pprr_csd.uid.map(lambda x: match_dict.get(x, x))
    return pprr_csd


# def merge(pprr_ipm, pprr_csd):
#     df = pd.merge(pprr_ipm, pprr_csd, on=['uid'], how='outer')\
#         .drop(columns=[
#             'birth_year_x', 'birth_month', 'birth_day', 'department_desc_y',
#             'rank_code', 'rank_desc_y', 'hire_year_y', 'hire_month_y', 'hire_day_y',
#             'term_year', 'term_month', 'term_day', 'data_production_year_y', 'agency_y',
#             'data_production_year_x', 'first_name_y', 'last_name_y'
#         ])\
#         .rename(columns={
#             'rank_desc_x': 'rank_desc',
#             'department_desc_x': 'department_desc',
#             'agency_x': 'agency',
#             'hire_year_x': 'hire_year',
#             'hire_month_x': 'hire_month',
#             'hire_day_x': 'hire_day',
#             'birth_year_y': 'birth_year'
#         })\
#         .drop_duplicates(subset=['left_year', 'left_month', 'left_day', 'uid'])
#     return df


if __name__ == '__main__':
    pprr_ipm = pd.read_csv(data_file_path('clean/pprr_new_orleans_ipm_iapro_1946_2018.csv'))
    pprr_csd = pd.read_csv(data_file_path('clean/pprr_new_orleans_csd_2014.csv'))
    post = pd.read_csv(data_file_path('clean/pprr_post_2020_11_06.csv'))
    award = pd.read_csv(data_file_path('clean/award_new_orleans_pd_2016_2021.csv'))
    lprr = pd.read_csv(data_file_path('clean/lprr_new_orleans_csc_2000_2016.csv'))
    post = post[post.agency == 'new orleans pd'].reset_index(drop=True)
    event_df = match_pprr_against_post(pprr_ipm, post)
    award = match_award_to_pprr_ipm(award, pprr_ipm)
    lprr = match_lprr_to_pprr_ipm(lprr, pprr_ipm)
    pprr_csd = match_pprr_csd_to_pprr_ipm(pprr_csd, pprr_ipm)
    ensure_data_dir('match')
    award.to_csv(data_file_path(
        'match/award_new_orleans_pd_2016_2021.csv'), index=False)
    event_df.to_csv(data_file_path(
        'match/post_event_new_orleans_pd.csv'), index=False)
    lprr.to_csv(data_file_path(
        'match/lprr_new_orleans_csc_2000_2016.csv'), index=False)
    pprr_csd.to_csv(data_file_path(
        'match/pprr_new_orleans_csd_2014.csv'), index=False)
