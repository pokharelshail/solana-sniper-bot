import pandas as pd
import datetime
import requests
import time
import json
import pprint
import re as reggie
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Constants
BASE_URL = "https://birdeye.so/token/"
API_KEY = os.getenv('BIRDEYE_API_KEY')
MIN_LIQUIDITY = 50000
MIN_24HR_VOLUME = 50000
MARKET_CAP_MAX = 1000000000
NUM_TOKENS_2SEARCH = 100
MAX_SELL_PERCENTAGE = 50
MIN_TRADES_LAST_HOUR = 100
MIN_UNQ_WALLETS2hr = 100
MIN_VIEW24h = 100

def get_tokens():
    url = "https://public-api.birdeye.so/public/tokenlist"
    headers = {"x-chain": "solana", "X-API-KEY": API_KEY}
    tokens = []
    offset = 0
    limit = 50
    total_tokens = 0

    while total_tokens < NUM_TOKENS_2SEARCH:
        try:
            print(f'scanning solana for new tokens, total scanned: {total_tokens}...')
            params = {"sort_by": "v24hChangePercent", "sort_type": "desc", "offset": offset, "limit": limit}
            response = requests.get(url, headers=headers, params=params)

            if response.status_code == 200:
                response_data = response.json()
                new_tokens = response_data.get('data', {}).get('tokens', [])
                tokens.extend(new_tokens)
                total_tokens += len(new_tokens)
                offset += limit
            else:
                print(f"Error {response.status_code}: trying again in 10 seconds...")
                time.sleep(10)
                continue

            time.sleep(0.1)
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}. Retrying in 10 seconds...")
            time.sleep(10)
            continue

    return tokens

def filter_tokens(tokens):
    df = pd.DataFrame(tokens)
    df['token_url'] = df['address'].apply(lambda x: BASE_URL + x)
    df = df.dropna(subset=['liquidity', 'v24hUSD'])
    df = df[df['liquidity'] >= MIN_LIQUIDITY]
    df = df[df['v24hUSD'] >= MIN_24HR_VOLUME]
    df = df[(df['mc'] >= 50) & (df['mc'] <= MARKET_CAP_MAX)]
    df['lastTradeUnixTime'] = pd.to_datetime(df['lastTradeUnixTime'], unit='s').dt.tz_localize('UTC')
    ten_minutes_ago = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(minutes=59)
    df = df[df['lastTradeUnixTime'] >= ten_minutes_ago]
    df.to_csv("data/filtered_pricechange_with_urls.csv", index=False)
    pd.set_option('display.max_columns', None)
    return df

def new_launches(data):
    new_launches = data[data['v24hChangePercent'].isna()]
    csv_filename = 'data/new_launches.csv'
    new_launches.to_csv(csv_filename, index=False)
    return new_launches

def token_overview(address):
    overview_url = f"{BASE_URL}/token_overview?address={address}"
    headers = {"X-API-KEY": API_KEY}
    response = requests.get(overview_url, headers=headers)
    result = {}

    if response.status_code == 200:
        overview_data = response.json().get('data', {})
        buy1h = overview_data.get('buy1h', 0)
        sell1h = overview_data.get('sell1h', 0)
        trade1h = buy1h + sell1h

        buy_percentage = (buy1h / trade1h * 100) if trade1h else 0
        sell_percentage = (sell1h / trade1h * 100) if trade1h else 0

        if sell_percentage > MAX_SELL_PERCENTAGE or trade1h < MIN_TRADES_LAST_HOUR:
            return None
        if overview_data.get('uniqueWallet24h', 0) < MIN_UNQ_WALLETS2hr or overview_data.get('view24h', 0) < MIN_VIEW24h:
            return None
        if overview_data.get('liquidity', 0) < MIN_LIQUIDITY:
            return None

        result.update({
            'address': address,
            'buy1h': buy1h,
            'sell1h': sell1h,
            'trade1h': trade1h,
            'buy_percentage': buy_percentage,
            'sell_percentage': sell_percentage,
            'liquidity': overview_data.get('liquidity', 0),
        })

        extensions = overview_data.get('extensions', {})
        description = extensions.get('description', '') if extensions else ''
        urls = find_urls(description)
        links = [{'telegram': u} for u in urls if 't.me' in u]
        links.extend([{'twitter': u} for u in urls if 'twitter.com' in u])
        links.extend([{'website': u} for u in urls if 't.me' not in u and 'twitter.com' not in u])
        result['description'] = links

        return result
    else:
        print(f"Failed to retrieve token overview for address {address}: HTTP status code {response.status_code}")
        return None

def find_urls(string):
    return reggie.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', string)

def process_new_launches():
    df = pd.read_csv('data/new_launches.csv')
    dfs_to_concat = []

    for index, row in df.iterrows():
        while True:
            try:
                token_data = token_overview(row['address'])
                if token_data:
                    token_data['address'] = row['address']
                    token_data['url'] = f"https://dexscreener.com/solana/{token_data['address']}"
                    token_data.pop('priceChangesXhrs', None)
                    temp_df = pd.DataFrame([token_data])
                    dfs_to_concat.append(temp_df)
                break
            except Exception as e:
                print(f"Failed to process token {row['address']}: {e}")
                time.sleep(5)

    if dfs_to_concat:
        results_df = pd.concat(dfs_to_concat, ignore_index=True)
        csv_file_path = 'data/hyper-sorted-sol.csv'
        results_df.to_csv(csv_file_path, index=False)
        print('-' * 80)
        print(results_df)
    else:
        print('-' * 80)
        print("After filtering, there are no tokens meeting the criteria."
              "Try changing your parameters or increasing NUM_TOKENS_2SEARCH.")

def main():
    if new_data:
        print('getting new data...')
        tokens = get_tokens()
        filtered_tokens = filter_tokens(tokens)
        new_launches(filtered_tokens)
    else:
        filtered_tokens = pd.read_csv('data/filtered_pricechange_with_urls.csv')
    
    process_new_launches()

if __name__ == "__main__":
    main()
