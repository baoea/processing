import re

import pandas as pd

from .clean import float_to_int_str, names_to_title_case


def clean_column_names(df: pd.DataFrame) -> pd.DataFrame:
    """Removes unnamed columns and convert column names to snake case

    Args:
        df (pd.DataFrame):
            the frame to process

    Returns:
        the updated frame
    """
    df = df[[col for col in df.columns if not col.startswith("Unnamed:")]]
    df.columns = [
        re.sub(r"[\s\W]+", "_", col.strip()).lower().strip("_")
        for col in df.columns]
    return df


def set_values(df: pd.DataFrame, value_dict: dict) -> pd.DataFrame:
    """Set entire column to a value.

    Multiple columns can be specified each as a single key in value_dict

    Examples:
        >>> df = set_values(df, {
        ...     "agency": "Brusly PD",
        ...     "data_production_year": 2020
        ... })

    Args:
        df (pd.DataFrame):
            the frame to process
        value_dict (dict):
            the mapping between column name and what value should be set
            for that column.

    Returns:
        the updated frame
    """
    for col, val in value_dict.items():
        df.loc[:, col] = val
    return df


def rearrange_personnel_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Performs final processing step for a personnel table

    This performs the following tasks:
    - discard rows with empty uid
    - discard columns not present in PERSONNEL_COLUMNS
    - drop row duplicates
    - convert name columns to title case
    - convert numeric columns to int or str

    Args:
        df (pd.DataFrame):
            the frame to process

    Returns:
        the updated frame
    """
    existing_cols = set(df.columns)
    df = df[df.uid.notna() & (df.uid != '')]
    df = df[[col for col in PERSONNEL_COLUMNS if col in existing_cols]]\
        .drop_duplicates(ignore_index=True)
    return df\
        .pipe(names_to_title_case, ["first_name", "last_name", "middle_name", "middle_initial"])\
        .pipe(float_to_int_str, ["birth_year", "birth_month", "birth_day"])\
        .sort_values('uid')


def rearrange_event_columns(df):
    """Performs final processing step for an event table

    This performs the following tasks:
    - discard columns not present in EVENT_COLUMNS
    - drop row duplicates
    - convert numeric columns to int or str

    Args:
        df (pd.DataFrame):
            the frame to process

    Returns:
        the updated frame
    """
    existing_cols = set(df.columns)
    return float_to_int_str(
        df[[
            col for col in EVENT_COLUMNS if col in existing_cols
        ]].drop_duplicates(ignore_index=True),
        [
            "badge_no",
            "employee_id",
            "year",
            "month",
            "day",
            "years_employed",
            "department_code",
            "rank_code"
        ]).sort_values(['agency', 'kind', 'event_uid'])


def rearrange_complaint_columns(df):
    """Performs final processing step for a complaint table

    This performs the following tasks:
    - discard columns not present in COMPLAINT_COLUMNS
    - drop row duplicates
    - convert numeric columns to int or str

    Args:
        df (pd.DataFrame):
            the frame to process

    Returns:
        the updated frame
    """
    existing_cols = set(df.columns)
    return float_to_int_str(
        df[[col for col in COMPLAINT_COLUMNS if col in existing_cols]]
        .drop_duplicates(ignore_index=True),
        [
            "paragraph_code",
        ]).sort_values(['agency', 'complaint_uid'])


def rearrange_appeal_hearing_columns(df):
    """Performs final processing step for an appeal hearing table

    This performs the following tasks:
    - discard columns not present in APPEAL_HEARING_COLUMNS
    - drop row duplicates
    - convert counsel name to title case

    Args:
        df (pd.DataFrame):
            the frame to process

    Returns:
        the updated frame
    """
    existing_cols = set(df.columns)
    df = df[[
            col for col in APPEAL_HEARING_COLUMNS
            if col in existing_cols
            ]].drop_duplicates(ignore_index=True)
    return names_to_title_case(df, ["counsel"]).sort_values(['agency', 'appeal_uid'])


def rearrange_use_of_force(df):
    """Performs final processing step for a uof table

    This performs the following tasks:
    - discard columns not present in USE_OF_FORCE_COLUMNS
    - drop row duplicates
    - convert numeric columns to int or str

    Args:
        df (pd.DataFrame):
            the frame to process

    Returns:
        the updated frame
    """
    existing_cols = set(df.columns)
    return float_to_int_str(
        df[[
            col for col in USE_OF_FORCE_COLUMNS
            if col in existing_cols
        ]].drop_duplicates(ignore_index=True),
        [
            'citizen_age', 'citizen_age_1', 'officer_current_supervisor', 'officer_age',
            'officer_years_exp', 'officer_years_with_unit'
        ]).sort_values(['agency', 'uof_uid'])


def rearrange_stop_and_search_columns(df):
    """Performs final processing step for a stop and search table

    This performs the following tasks:
    - discard columns not present in STOP_AND_SEARCH_COLUMNS
    - drop row duplicates
    - convert numeric columns to int or str

    Args:
        df (pd.DataFrame):
            the frame to process

    Returns:
        the updated frame
    """
    existing_cols = set(df.columns)
    df = df[df.uid.notna() & (df.uid != '')]
    df = df[[col for col in STOP_AND_SEARCH_COLUMNS if col in existing_cols]]\
        .drop_duplicates(ignore_index=True)
    return df\
        .pipe(names_to_title_case, ["first_name", "last_name", "middle_name"])\
        .pipe(float_to_int_str, ["stop_and_search_year", "stop_and_search_month", "stop_and_search_day"])\
        .sort_values(['agency', 'stop_and_search_uid'])
