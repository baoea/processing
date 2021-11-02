import sys
sys.path.append('../')
from datamatch import JaroWinklerSimilarity, ThresholdMatcher, ColumnsIndex
from lib.path import data_file_path
import pandas as pd 


def match_cprr_with_post(cprr, post):
    dfa = cprr[['first_name', 'last_name', 'uid', 'agency']]
    dfa.loc[:, 'fc'] = dfa.first_name.map(lambda x: x[:1])
    dfa.loc[:, 'lc'] = dfa.last_name.fillna('').map(lambda x: x[:1])
    dfa = dfa.drop_duplicates(subset=['uid']).set_index('uid')

    dfb = post[['first_name', 'last_name', 'uid', 'agency']]
    dfb.loc[:, 'fc'] = dfb.first_name.map(lambda x: x[:1])
    dfb.loc[:, 'lc'] = dfb.last_name.fillna('').map(lambda x: x[:1])
    dfb = dfb.drop_duplicates(subset=['uid']).set_index('uid')

    matcher = ThresholdMatcher(ColumnsIndex(['fc', 'lc']), {
        'first_name': JaroWinklerSimilarity(),
        'last_name': JaroWinklerSimilarity(),
    }, dfa, dfb)
    decision = .96
    matcher.save_pairs_to_excel(data_file_path(
        'match/cprr_tangipahoa_da_2021_v_post_2020_11_06.xlsx'), decision)
    matches = matcher.get_index_pairs_within_thresholds(lower_bound=decision)
    match_dict = dict(matches)

    cprr.loc[:, 'uid'] = cprr.uid.map(lambda x: match_dict.get(x, x))
    return cprr


if __name__ == '__main__':
    cprr = pd.read_csv(data_file_path('clean/cprr_tangipahoa_da_2021.csv'))
    post = pd.read_csv(data_file_path('clean/pprr_post_2020_11_06.csv'))
    cprr = match_cprr_with_post(cprr, post)
    cprr.to_csv(data_file_path(
        'match/cprr_tangipahoa_da_2021.csv'), index=False)