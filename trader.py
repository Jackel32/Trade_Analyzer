import os
import google.generativeai as genai
import yfinance as yf
import pandas as pd
from datetime import datetime
import textwrap
from tabulate import tabulate

def get_api_key():
    """Fetches the Gemini API key from environment variables."""
    api_key = "AIzaSyDACYbCDEAtTELSFcTahQsezKfh4ul5Bfw" #os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable not set. Please set it to your API key.")
    return api_key

def get_top_5_swing_stocks() -> list:
    """
    Sends an initial prompt to Gemini to get a list of 5 stocks suitable
    for a short-term (3-7 day) swing trade.
    """
    print("STEP 1: Asking Gemini for the top 5 stocks for a short-term trade...")
    
    prompt = textwrap.dedent("""
    You are a Senior Market Analyst. Your task is to identify 5 US-listed stocks that are strong candidates for a short-term swing trade (holding for 3-7 days).

    Selection Criteria:
    - High liquidity (Market Cap > $10B and high average daily volume).
    - Strong recent price momentum (e.g., trading above key moving averages).
    - High relative volume or a recent bullish technical pattern (like a flag or consolidation breakout).
    - Potential for a near-term catalyst (sector rotation, news, etc.).

    Provide your response as a single line of comma-separated ticker symbols, and nothing else.
    Example: AAPL,MSFT,NVDA,GOOG,JPM
    """)
    
    try:
        api_key = get_api_key()
        genai.configure(api_key=api_key)
        
        model = genai.GenerativeModel('gemini-2.5-flash')
        response = model.generate_content(prompt)
        
        # Parse the comma-separated list
        tickers = [ticker.strip() for ticker in response.text.strip().split(',')]
        
        if len(tickers) != 5:
            raise ValueError("AI did not return a list of 5 tickers.")
            
        print(f"   > Received watchlist: {', '.join(tickers)}\n")
        return tickers
        
    except Exception as e:
        print(f"Could not get stock list from Gemini: {e}")
        # Return a default list if the API fails
        return ['MSFT', 'KO', 'JPM', 'JNJ', 'BRK-B']

def generate_portfolio_context(target_stocks: list, live_prices: dict) -> str:
    """
    Creates a string representation of a portfolio including live prices
    for the AI to analyze.
    """
    print("STEP 3: Simulating cash portfolio with LIVE prices...")
    
    nav = 10000.00
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Build the string with live price data
    watchlist_with_prices = []
    for ticker in target_stocks:
        price = live_prices.get(ticker, 'N/A')
        watchlist_with_prices.append(f"{ticker} (Current Price: ${price:.2f})")

    portfolio_string = (
        f"PORTFOLIO SNAPSHOT (Timestamp: {timestamp} UTC)\n"
        f"Net Asset Value (NAV): ${nav:,.2f}\n"
        f"Cash: ${nav:,.2f} (100%)\n"
        f"Current Positions: None\n"
        f"Watchlist for New Positions: {', '.join(watchlist_with_prices)}"
    )
    
    print("   > Portfolio context complete.\n")
    return portfolio_string

def create_trading_prompt(portfolio_data: str) -> str:
    """Constructs the full, detailed prompt for the Gemini API for STOCK TRADING."""

    prompt_template = textwrap.dedent(f"""
    System Instructions

    You are a Senior Portfolio Manager at an elite quant fund. Your task is to analyze the user's watchlist and propose entry strategies for equity positions. The user is currently holding all cash.

    [START PORTFOLIO DATA]
    {portfolio_data}
    [END PORTFOLIO DATA]

    Data Categories for Analysis

    Fundamental Data Points:
    Earnings Per Share (EPS), Revenue, Net Income, EBITDA, Price-to-Earnings (P/E) Ratio, Price/Sales Ratio, Gross & Operating Margins, Free Cash Flow Yield, Insider Transactions, Forward Guidance, PEG Ratio, Sell-side blended multiples.

    Price & Volume Historical Data Points:
    Daily Open, High, Low, Close, Volume (OHLCV), Historical Volatility, Moving Averages (50/100/200-day), Average True Range (ATR), Relative Strength Index (RSI), MACD, Bollinger Bands, VWAP, Pivot Points.

    Alternative, Macro, ETF Flow, and Analyst Data Points:
    Social Sentiment, News Headlines, Credit-card spending, GDP, 10-year yields, VIX, SPY/QQQ flows, Sector flows, Consensus target price, Recent upgrades/downgrades, Earnings estimate revisions.

    Trade Selection Criteria

    Number of Trades: Exactly 5 (one for each stock on the watchlist)
    Goal: Propose high-probability trade setups with clear entry and exit points.

    Hard Filters (discard trades not meeting these):
    Average Daily Volume > 1,000,000 shares.
    For BUY ideas, the 14-day RSI must be below 70 (not overbought).
    For BUY ideas, the current price must be above the 50-day moving average.

    Selection Rules

    Rank trades by a proprietary model_score favoring strong fundamentals and positive price momentum.
    Ensure diversification: maximum of 2 trades per GICS sector.
    In case of ties, prefer higher momentum_z and flow_z scores.

    Output Format

    Provide output strictly as a clean, text-wrapped table including only the following columns:
    Ticker
    Action
    Entry Range
    Stop Loss
    Profit Target
    Thesis (≤ 20 words, plain language)

    Additional Guidelines

    The "Action" should be "Buy".
    The "Thesis" should be concise and justify the trade based on technicals or fundamentals.
    Do not include any additional outputs or explanations beyond the specified table.
    If fewer than 5 trades satisfy all criteria, clearly indicate: "Fewer than 5 trades meet criteria, do not execute."
    """)
    
    print("STEP 3: Full prompt for STOCK trading has been constructed.")
    return prompt_template.strip()

# --- This function remains the same ---
def prompt_gemini_for_analysis(prompt: str):
    """Sends the prompt to the Gemini API and prints the response."""
    print("STEP 4: Sending prompt to Gemini for analysis...")
    print("-" * 50)
    
    try:
        api_key = get_api_key()
        genai.configure(api_key=api_key)
        
        model = genai.GenerativeModel('gemini-2.5-flash')
        response = model.generate_content(prompt)
        
        print("Response from Gemini:\n")
        try:
            lines = response.text.strip().split('\n')
            
            # The first non-empty line is the header
            headers = [h.strip() for h in lines[0].split('|')]
            
            # Find the data rows (all lines after the separator)
            data = []
            for line in lines[2:]: # Skips header and separator line '---|---'
                row = [r.strip() for r in line.split('|')]
                data.append(row)
            
            if not data:
                 raise ValueError("No data rows could be parsed from the response.")

            # Print the formatted table
            print(tabulate(data, headers=headers, tablefmt="grid"))
            
        except Exception as parse_error:
            # If parsing fails for any reason, just print the raw text
            print(f"Could not parse the table (Error: {parse_error}). Printing raw output:")
            print(response.text)
    except Exception as e:
        print(f"An error occurred while contacting the Gemini API: {e}")

if __name__ == "__main__":
    # 1. Get the dynamic list of top 5 stocks
    top_stocks = get_top_5_swing_stocks()
    
    if top_stocks:
        print("STEP 2: Fetching LIVE market prices for the watchlist...")
        try:
            data = yf.download(tickers=top_stocks, period='1d', interval='1m')
            # Get the very last price available for each stock
            live_prices = data['Close'].iloc[-1].to_dict()
            print("   > Live prices fetched successfully.\n")
        except Exception as e:
            print(f"Could not fetch live prices: {e}. Exiting.")
            exit()

        # 3. Generate the portfolio context with those stocks and their live prices
        portfolio_context = generate_portfolio_context(top_stocks, live_prices)
    
        # 4. Create the detailed analysis prompt
        analysis_prompt = create_trading_prompt(portfolio_context)
        
        # 5. Get and print the final trade plan table
        prompt_gemini_for_analysis(analysis_prompt)