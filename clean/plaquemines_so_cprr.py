from lib.columns import clean_column_names
from lib.path import data_file_path
from lib.uid import gen_uid
from lib.clean import clean_names, standardize_desc_cols, clean_dates
from lib.rows import duplicate_row
import pandas as pd
import re
import sys
sys.path.append('../')


def gen_middle_initial(df):
    df.loc[df.middle_name.isna(
    ), 'middle_name'] = df.loc[df.middle_name.isna(), 'middle_initial']
    df.loc[:, 'middle_initial'] = df.middle_name.fillna(
        '').map(lambda x: x[:1])
    return df


def assign_agency(df):
    df.loc[:, 'data_production_year'] = 2019
    df.loc[:, 'agency'] = 'Plaquemines SO'
    return df


def split_row_with_multiple_names(df):
    df.loc[:, 'against'] = df.against.str.lower().str.strip().fillna('')\
        .str.replace('smith tam', 'smith/tam', regex=False)\
        .str.replace(r'(\w+) / (\w+)', r'\1/\2', regex=True)\
        .str.replace(r'^robin thomas grant solis gerald cormier jennifer daigle$',
                     'robin thomas/grant solis/gerald cormier/jennifer daigle', regex=True)\
        .str.replace(r'^danny rees brandon leblanc anthony dugas$',
                     'danny rees/brandon leblanc/anthony dugas', regex=True)\
        .str.replace(r'^corbett reddoch holly hardin ryan hebert chris lambert ryan lejeune$',
                     'corbett reddoch/holly hardin/ryan hebert/chris lambert/ryan lejeune',
                     regex=True)\
        .str.replace(r'^holly hardin daniel swear$', 'holly hardin/daniel swear', regex=True)

    i = 0
    for idx in df[df.against.str.contains('/')].index:
        s = df.loc[idx + i, 'against']
        parts = re.split(r"\s*(?:\/)\s*", s)
        df = duplicate_row(df, idx + i, len(parts))
        for j, name in enumerate(parts):
            df.loc[idx + i + j, 'against'] = name
        i += len(parts) - 1
    return df


def clean_and_split_names(df):
    df.loc[:, 'against'] = df.against\
        .str.replace('daniel scott lott', 'daniel lott scott', regex=False)\
        .str.replace('natalie d. fitzgerald', ' natalie fitzgerald d', regex=False)
    names = df.against.str.extract(r'(\w+) ?(\w+)? ?(.+)?')
    df.loc[:, 'first_name'] = names[0]\
        .str.replace('ppso', "plaquemines parish sheriff's office", regex=False)
    df.loc[:, 'last_name'] = names[1]
    df.loc[:, 'middle_name'] = names.loc[:, 2].str.strip().fillna('')\
        .map(lambda s: '' if len(s) < 2 else s)
    df.loc[:, 'middle_initial'] = names.loc[:, 2].str.strip().fillna('')\
        .map(lambda s: '' if len(s) > 2 else s)
    return df.fillna('').drop(columns='against')


def drop_rows_missing_names(df):
    return df[~((df.first_name == '') & (df.last_name == ''))]


def clean_receive_dates(df):
    df.loc[:, 'receive_date'] = df.date\
        .str.replace('11/16/2 0', '11/16/20', regex=False)
    return df.drop(columns='date')


def clean_and_split_rows_with_multiple_charges(df):
    df.loc[:, 'charges'] = df.policy.str.lower().str.strip().fillna('')\
        .str.replace('ppdc', 'plaquemines parish detention center', regex=False)\
        .str.replace('info', 'information', regex=False)\
        .str.replace(r'domestic issue-off duty', 'off duty domestic issue', regex=False)

    i = 0
    for idx in df[df.charges.str.contains(',')].index:
        s = df.loc[idx + i, 'charges']
        parts = re.split(r"\s*(?:\,)\s*", s)
        df = duplicate_row(df, idx + i, len(parts))
        for j, name in enumerate(parts):
            df.loc[idx + i + j, 'charges'] = name
        i += len(parts) - 1

    return df


def extract_actions(df):
    df.loc[:, 'conclusion'] = df.conclusion.str.lower().str.strip()\
        .str.replace(r'(\w+) / (\w+)', r'\1; \2', regex=True)
    
    actions = df.conclusion.str.extract(r'(30 day suspension|verbal counsel| ?suspended|arrested; suspended|terminated)')
    
    df.loc[:, 'action'] = actions[0]\
        .str.replace(r'^ (\w+)$', r'\1', regex=True)
    return df


def clean_disposition(df):
    df.loc[:, 'disposition'] = df.conclusion\
        .str.replace(r'(30 day suspension|verbal counsel| ?suspended|arrested; suspended|terminated|;)', '', regex=True)\
        .str.replace(r'\, $', '', regex=True)\
        .str.replace(r'\, (.+)', r'; \1', regex=True)\
        .str.replace(r'^unsustained$', 'not sustained', regex=True)
    return df.drop(columns='conclusion')


def clean19():
    df = pd.read_csv(data_file_path(
        'raw/plaquemines_so/plaquemines_so_cprr_2019.csv'
    ))
    df = clean_column_names(df)
    df = df.rename(columns={
        'rule_violation': 'charges'
    })
    return df\
        .pipe(gen_middle_initial)\
        .pipe(assign_agency)\
        .pipe(clean_names, ['first_name', 'last_name', 'middle_name', 'middle_initial'])\
        .pipe(gen_uid, ['agency', 'first_name', 'last_name', 'middle_name', 'middle_initial'])\
        .pipe(gen_uid, ['agency', 'tracking_number'], 'complaint_uid')


def clean20():
    df = pd.read_csv(data_file_path('raw/plaquemines_so/plaquemines_so_cprr_2016_2020.csv'))\
        .pipe(clean_column_names)\
        .drop(columns=['complainant'])\
        .rename(columns={
            'ppso_iad': 'tracking_number',
        })\
        .pipe(split_row_with_multiple_names)\
        .pipe(clean_and_split_names)\
        .pipe(standardize_desc_cols, ['tracking_number'])\
        .pipe(clean_receive_dates)\
        .pipe(clean_dates, ['receive_date'])\
        .pipe(clean_and_split_rows_with_multiple_charges)\
        .pipe(extract_actions)\
        .pipe(clean_disposition)\
        .pipe(drop_rows_missing_names)
    return df


if __name__ == '__main__':
    df = clean19()
    df.to_csv(data_file_path('clean/cprr_plaquemines_so_2019.csv'), index=False)
