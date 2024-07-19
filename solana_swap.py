import requests
import sys
import json
import base64
from solders.keypair import Keypair
from solders.transaction import VersionedTransaction
from solana.rpc.api import Client
from solana.rpc.types import TxOpts
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Constants
KEY = Keypair.from_base58_string(os.getenv('SOLANA_PRIVATE_KEY'))
SLIPPAGE = 50
QUOTE_TOKEN = 'So11111111111111111111111111111111111111112'

def get_quote(token, amount):
    url = f'https://quote-api.jup.ag/v6/quote?inputMint={QUOTE_TOKEN}&outputMint={token}&amount={amount}&slippageBps={SLIPPAGE}'
    return requests.get(url).json()

def create_swap_transaction(quote, public_key):
    url = 'https://quote-api.jup.ag/v6/swap'
    headers = {"Content-Type": "application/json"}
    data = json.dumps({"quoteResponse": quote, "userPublicKey": public_key})
    return requests.post(url, headers=headers, data=data).json()

def send_transaction(tx_bytes, client):
    tx = VersionedTransaction.from_bytes(tx_bytes)
    signed_tx = VersionedTransaction(tx.message, [KEY])
    tx_id = client.send_raw_transaction(bytes(signed_tx), TxOpts(skip_preflight=True)).value
    return tx_id

def main():
    token = sys.argv[1]
    amount = sys.argv[2]

    client = Client("https://api.mainnet-beta.solana.com")

    quote = get_quote(token, amount)
    tx_res = create_swap_transaction(quote, str(KEY.pubkey()))
    swap_tx = base64.b64decode(tx_res['swapTransaction'])
    tx_id = send_transaction(swap_tx, client)

    print(f"https://solscan.io/token/{str(tx_id)}")

if __name__ == "__main__":
    main()
