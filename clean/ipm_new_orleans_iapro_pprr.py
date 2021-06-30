from lib.path import data_file_path, ensure_data_dir
from lib.columns import clean_column_names
from lib.clean import (
    clean_races, float_to_int_str, standardize_desc_cols, clean_sexes, clean_names, clean_dates
)
from lib.uid import gen_uid
import pandas as pd
import sys
sys.path.append("../")


def remove_badge_number_zeroes_prefix(df):
    df.loc[:, 'badge_no'] = df.badge_no.str.replace(r'^0+', '', regex=True)
    return df


def clean_employee_type(df):
    df.loc[:, 'employee_type'] = df.employee_type.str.lower().str.replace(
        r'commisioned', 'commissioned')
    return df

def strip_time_from_dates(df, cols):
    for col in cols:
        df.loc[:, col] = df[col].str.replace(r' \d+:\d+$', '', regex=True)
    return df


def generate_middle_initial(df):
    df.loc[:, 'middle_initial'] = df.middle_name.map(lambda x: x[:1])
    return df


def assign_agency(df):
    df.loc[:, 'data_production_year'] = '2018'
    df.loc[:, 'agency'] = 'New Orleans PD'
    return df


def clean_current_supervisor(df):
    df.loc[:, 'employee_id'] = df.employee_id.astype(str)
    officer_number_dict = df.set_index('employee_id').uid.to_dict()
    df.loc[:, 'current_supervisor'] = df.current_supervisor.map(
        lambda x: officer_number_dict.get(x, ''))
    return df


def remove_unnamed_officers(df):
    df.loc[:, 'last_name'] = df.last_name.str.replace(r'^unknown.*', '')\
        .str.replace(r'^none$', '').str.replace(r'not an nopd officer', '')
    return df[df.last_name != ''].reset_index(drop=True)


def clean():
    df = pd.read_csv(data_file_path(
        "ipm/new_orleans_iapro_pprr_1946-2018.csv"), sep='\t')
    df = df.dropna(axis=1, how="all")
    df = clean_column_names(df)
    df = df.drop(columns=[
        'employment_number', 'working_status', 'shift_hours', 'exclude_reason'
    ])
    df = df.rename(columns={
        'badge_number': 'badge_no',
        'title': 'rank_desc',
        'employment_ended_on': 'left_date',
        'officer_department': 'department_desc',
        'officer_division': 'division_desc',
        'officer_sub_division_a': 'sub_division_a_desc',
        'officer_sub_division_b': 'sub_division_b_desc',
        'assigned_to_unit_on': 'dept_date',
        'hired_on': 'hire_date',
        'officer_sex': 'sex',
        'officer_race': 'race',
        'middle_initial': 'middle_name',
        'officer_number': 'employee_id'
    })
    return df\
        .pipe(float_to_int_str, ["years_employed", "current_supervisor", 'birth_year'])\
        .pipe(remove_badge_number_zeroes_prefix)\
        .pipe(standardize_desc_cols, [
            "rank_desc", "employment_status", "officer_inactive", "department_desc"
        ])\
        .pipe(clean_employee_type)\
        .pipe(clean_sexes, ['sex'])\
        .pipe(clean_races, ['race'])\
        .pipe(assign_agency)\
        .pipe(gen_uid, ['agency', 'employee_id'])\
        .pipe(strip_time_from_dates, ['hire_date', 'left_date', 'dept_date'])\
        .pipe(clean_dates, ['hire_date', 'left_date', 'dept_date'])\
        .pipe(clean_names, ['first_name', 'middle_name', 'last_name'])\
        .pipe(remove_unnamed_officers)\
        .pipe(generate_middle_initial)\
        .pipe(clean_current_supervisor)


if __name__ == '__main__':
    df = clean()
    ensure_data_dir('clean')
    df.to_csv(data_file_path(
        'clean/pprr_new_orleans_pd_1946_2018.csv'), index=False)
