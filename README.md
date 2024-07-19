
# Solana Swap and Token Overview Bot

This repository contains two Python scripts designed to interact with the Solana blockchain, perform token swaps, and analyze new token listings. The scripts leverage various APIs to provide comprehensive insights and functionalities for users interested in Solana-based tokens.

## Features

### `solana_swap.py`

- **Token Swap Functionality**: Automate token swaps on the Solana blockchain using Jupiter Aggregator's API.
- **Transaction Management**: Generate and send transactions seamlessly.
- **Error Handling**: Robust error handling for reliable execution.

### `birdeye_bot.py`

- **Token Discovery**: Scan and list new tokens on the Solana blockchain using BirdEye's public API.
- **Data Filtering**: Filter tokens based on liquidity, market cap, trading volume, and other criteria.
- **Automated Data Processing**: Continuously fetch and process token data to identify new launches and promising tokens.
- **Detailed Token Analysis**: Fetch and display comprehensive token information, including recent trade activity and unique wallet counts.

## Installation

1. Clone the repository:
   \`\`\`bash
   git clone https://github.com/yourusername/solana-swap-token-overview.git
   cd solana-swap-token-overview
   \`\`\`

2. Install required dependencies:
   \`\`\`bash
   pip install -r requirements.txt
   \`\`\`

3. Set up your \`dontshare.py\` file with the following variables:
   \`\`\`python
   key = 'your_solana_private_key'
   birdeye = 'your_birdeye_api_key'
   \`\`\`

## Usage

### Token Swap

To perform a token swap, run:
\`\`\`bash
python solana_swap.py <token_mint_address> <amount>
\`\`\`
Replace \`<token_mint_address>\` with the mint address of the token you want to swap to and \`<amount>\` with the amount of the quote token.

### Token Overview

To run the token discovery and filtering process:
\`\`\`bash
python birdeye_bot.py
\`\`\`
This will fetch, filter, and analyze new token listings on Solana.

## Configuration

You can customize the filtering criteria in the \`birdeye_bot.py\` script to suit your specific needs.
