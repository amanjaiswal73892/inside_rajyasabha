import pandas as pd
import re

# This file contains the helper functions used for plotting graphs

def append_files(df, startvalue='2009', endvalue='2013'):
    """ This is used to index the dataset and slicing with datetime."""
    df = df.copy(deep=True)
    df.index = pd.to_datetime(df.answer_date)

    return df.loc[startvalue:endvalue, :]



def get_answered_by(x):
    """This function uses regex to extract which minister answered a question"""
    if len(re.findall(r'\(([ . A-Z a-z ]*)\)', x)) == 0:

        return "Unknown"
    return re.findall('\(([ . A-Z a-z ]*)\)', x)[0]


def sortby_datetime(df: pd.DataFrame):
    """This function is used to sort the dataframe by answer_date"""
    df = df.copy(deep=True)
    df.loc[:, 'answer_date'] = pd.to_datetime(df.answer_date)
    df = df.sort_values(by='answer_date')
    return df


def getDataFrameWithPartyName(df: pd.DataFrame) -> pd.DataFrame:
    """This function is used to extract the party affiliations of the members"""
    rsMembers = pd.read_csv('Dataset/RajyaSabhaMembers1952To2013.csv')
    df['question_by'] = df.question_by.str.upper()
    rsMembers['Member Name'] = rsMembers['Member Name'].str.upper()
    dataFrame = pd.merge(df, rsMembers[['Member Name', 'Gender', 'State Name', 'Party Name', ]],
                         left_on=['question_by'], right_on=['Member Name'], how='left')
    return dataFrame

