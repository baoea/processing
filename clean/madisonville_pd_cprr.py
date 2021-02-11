from lib.path import data_file_path, ensure_data_dir
from lib.columns import clean_column_names
from lib.clean import clean_names, clean_dates, standardize_desc_cols
import pandas as pd
import sys
sys.path.append("../")


def swap_names(df):
    # swap first_name and last_name in first row
    v = df.loc[0, "first_name"]
    df.loc[0, "first_name"] = df.loc[0, "last_name"]
    df.loc[0, "last_name"] = v
    return df


def extract_complainant_gender(df):
    df.loc[:, "complainant_sex"] = "female"
    df.loc[df.complainant_name == "Mr. Joe Mahon, Jr.",
           "complainant_sex"] = "male"
    df.loc[:, "complainant_name"] = df.complainant_name.str.replace(
        r"^Mr\.\s+", "")
    return df


def assign_agency(df):
    df.loc[:, "data_production_year"] = "2020"
    df.loc[:, "agency"] = "Madisonville PD"
    return df


def clean():
    df = pd.read_csv(data_file_path(
        "madisonville_pd/madisonville_pd_cprr_2010-2020.csv"))
    df = clean_column_names(df)
    df.columns = [
        'rank_desc', 'last_name', 'first_name', 'occur_date', 'tracking_number', 'complainant_name']
    df = df\
        .pipe(swap_names)\
        .pipe(extract_complainant_gender)\
        .pipe(clean_names, ["first_name", "last_name", "complainant_name"])\
        .pipe(clean_dates, ["occur_date"])\
        .pipe(standardize_desc_cols, ["rank_desc"])\
        .pipe(assign_agency)
    return df


if __name__ == "__main__":
    df = clean()
    ensure_data_dir("clean")
    df.to_csv(data_file_path(
        "clean/cprr_madisonville_pd_2010_2020.csv"), index=False)
