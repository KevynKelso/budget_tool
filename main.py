#!/usr/bin/env python3
from pathlib import Path
from os.path import dirname
import pandas as pd
from datetime import date, timedelta

NUM_LOOKBACK_WEEKS = 52


def get_most_recent_sunday():
    today = date.today()
    offset = (today.weekday() + 1) % 7
    most_recent_sunday = today - timedelta(days=offset)
    
    return most_recent_sunday

def get_transactions_by_week(csv_files: list[str]):
    df_list = [pd.read_csv(f) for f in csv_files]
    df = pd.concat(df_list, ignore_index=True)
    df['datetime'] = pd.to_datetime(df['Transaction Date'])

    # Split transactions into weeks, sorted by most recent week
    # last_sunday = get_most_recent_sunday() - timedelta(days=7)
    last_sunday = get_most_recent_sunday()
    last_last_sunday = last_sunday - timedelta(days=7)
    last_sunday_ts = pd.Timestamp(last_sunday)
    last_last_sunday_ts = pd.Timestamp(last_last_sunday)
    weekly_transactions = df[(df['datetime'] >= last_last_sunday_ts) & (df['datetime'] < last_sunday_ts)]
    transaction_weeks = [weekly_transactions]
    for _ in range(NUM_LOOKBACK_WEEKS):
        last_sunday = last_last_sunday
        last_last_sunday = last_sunday - timedelta(days=7)
        last_sunday_ts = pd.Timestamp(last_sunday)
        last_last_sunday_ts = pd.Timestamp(last_last_sunday)
        weekly_transactions = df[(df['datetime'] >= last_last_sunday_ts) & (df['datetime'] < last_sunday_ts)]
        if (len(weekly_transactions)):
            transaction_weeks.append(weekly_transactions)

    return transaction_weeks


def main():
    csv_files = list(Path(dirname(__file__)).glob("*.csv", case_sensitive=False))
    transaction_weeks = get_transactions_by_week(csv_files)
    for tw in transaction_weeks:
        print(tw)

if __name__ == '__main__':
    main()
