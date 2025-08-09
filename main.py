#!/usr/bin/env python3
from pathlib import Path
from os.path import dirname
import pandas as pd
from datetime import date, timedelta
import numpy as np
import matplotlib.pyplot as plt

NUM_LOOKBACK_WEEKS = 52


def get_most_recent_sunday():
    today = date.today()
    offset = (today.weekday() + 1) % 7
    most_recent_sunday = today - timedelta(days=offset)
    
    return most_recent_sunday

def get_transactions_by_week(csv_files: list[str]):
    """Split data into weekly buckets sorted from most recent to least recent.

    Args:
        csv_files: list of csv files containing transactions.

    Returns: list of dataframes
        
    """
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
    # weekly data
    # - total spent
    # - how that compares to the average week
    # - total spent by category
    # - how that compares to the average week
    # - spending graphs by category
    # - total transactions
    # - how that compares on average
    weekly_data = pd.DataFrame(columns=["date", "total_spent", "percent_change"])
    sum = 0
    for tw in transaction_weeks:
        print(tw)
        total_spent = abs(tw[tw['Amount'] < 0]['Amount'].sum())
        if total_spent <= 0:
            continue
        sum += total_spent
        weekly_data.loc[len(weekly_data)] = [tw["Transaction Date"].max(), total_spent, 0]

    avg = sum / len(transaction_weeks)
    weekly_data["percent_change"] = weekly_data.apply(
        lambda row: ((row["total_spent"] - avg) / avg) * 100,
        axis=1,
    )

    print(weekly_data)
    weekly_data_reversed = weekly_data.iloc[::-1]
    plt.plot(weekly_data_reversed["date"], weekly_data_reversed["total_spent"])
    plt.xlabel("Date")
    plt.ylabel("$")
    plt.title("Spending Trends")
    plt.gcf().autofmt_xdate()
    plt.grid()
    plt.show()
    plt.savefig("trends.png")

if __name__ == '__main__':
    main()
