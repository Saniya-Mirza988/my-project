
    # dropping of that index whimport pandas as pd

import pandas as pd

def getvaluecounts(df):
    return {k: int(v) for k, v in df['subject'].value_counts().items()}

def getlevelcount(df):
    return {k: int(v) for k, v in df.groupby('level')['num_subscribers'].count().items()}

def getsubjectsperlevel(df):
    grouped = df.groupby(['subject', 'level']).size()
    labels = [f"{subject}_{level}" for subject, level in grouped.index]
    values = [int(v) for v in grouped.values]
    return dict(zip(labels, values))

def yearwiseprofit(df):
    # Clean 'price' and 'num_subscribers' columns first
    df['price'] = df['price'].replace(['Free', 'TRUE', 'False'], 0)
    df['price'] = pd.to_numeric(df['price'], errors='coerce').fillna(0)
    df['num_subscribers'] = pd.to_numeric(df['num_subscribers'], errors='coerce').fillna(0)

    # Remove extreme values to avoid integer overflow (safe limits)
    df = df[(df['price'] < 1_000_000) & (df['num_subscribers'] < 100_000_000)]

    # Calculate revenue
    df['revenue'] = df['price'] * df['num_subscribers']

    # Convert timestamps safely
    df['published_timestamp'] = pd.to_datetime(df['published_timestamp'], errors='coerce')
    df = df.dropna(subset=['published_timestamp'])

    df['year'] = df['published_timestamp'].dt.year
    df['month'] = df['published_timestamp'].dt.month
    df['month_name'] = df['published_timestamp'].dt.month_name()

    # Group and prepare data
    yearwise_profit_map = df.groupby('year')['revenue'].sum().round(2).to_dict()
    subscribers_count_map = df.groupby('year')['num_subscribers'].sum().astype(int).to_dict()
    profit_monthwise = df.groupby('month_name')['revenue'].sum().round(2).to_dict()
    monthwise_subs = df.groupby('month_name')['num_subscribers'].sum().astype(int).to_dict()

    return yearwise_profit_map, subscribers_count_map, profit_monthwise, monthwise_subs

    
