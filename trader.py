import yfinance as yf
from datetime import datetime
import textwrap
from tabulate import tabulate

# Imports from other project modules
from gemini_client import get_swing_stocks, prompt_gemini_for_analysis
from stock_analyzer import StockAnalyzer

def analyze_watchlist(tickers: list) -> dict:
    """Analyzes a list of stock tickers using the StockAnalyzer class."""
    analysis_results = {}
    for ticker in tickers:
        try:
            analyzer = StockAnalyzer(ticker)
            tech_indicators = analyzer.get_technical_indicators()
            confidence = analyzer.get_confidence_score()
            
            if isinstance(tech_indicators, dict):
                analysis_results[ticker] = {
                    "Technical Indicators": tech_indicators,
                    "Confidence Score": confidence
                }
                print(f"  - Analysis for {ticker}: Success")
            else:
                analysis_results[ticker] = {
                    "Technical Indicators": "Data not available",
                    "Confidence Score": "N/A"
                }
                print(f"  - Analysis for {ticker}: Failed (Insufficient data)")
        except Exception as e:
            analysis_results[ticker] = { "Technical Indicators": "Analysis failed", "Confidence Score": "N/A"}
            print(f"  - Analysis for {ticker}: Error ({e})")
            
    return analysis_results

def generate_trading_context(target_stocks: list, live_prices: dict, analysis_data: dict) -> str:
    """Creates a detailed context string for the AI to process."""   
    # Basic portfolio snapshot
    nav = 10000.00
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    watchlist_with_prices = [f"{ticker} (Current Price: ${live_prices.get(ticker, 0):.2f})" for ticker in target_stocks]

    portfolio_string = (
        f"PORTFOLIO SNAPSHOT (Timestamp: {timestamp} UTC)\n"
        f"Net Asset Value (NAV): ${nav:,.2f}\n"
        f"Cash: ${nav:,.2f} (100%)\n"
        f"Watchlist: {', '.join(watchlist_with_prices)}"
    )

    # Add the detailed analysis section
    analysis_string = "\n\n[START PROPRIETARY ANALYSIS DATA]\n"
    for ticker in target_stocks:
        analysis_string += f"--- Analysis for {ticker} ---\n"
        data = analysis_data.get(ticker, {})
        analysis_string += f"Confidence Score: {data.get('Confidence Score', 'N/A')}\n"
        indicators = data.get('Technical Indicators')
        if isinstance(indicators, dict):
            for key, value in indicators.items():
                analysis_string += f"- {key}: {value}\n"
        else:
            analysis_string += f"- Technical Indicators: {indicators}\n"
        analysis_string += "\n"
    analysis_string += "[END PROPRIETARY ANALYSIS DATA]\n"
    
    return portfolio_string + analysis_string

def create_trading_prompt(context: str) -> str:
    """
    Constructs the final prompt for Gemini, instructing it to use the
    provided proprietary analysis and add a profitability estimate.
    """
    
    prompt_template = textwrap.dedent(f"""
    System Instructions
    You are a Senior Portfolio Manager at an elite quant fund. Your task is to synthesize the provided proprietary analysis with your own market knowledge to propose high-probability trade setups.

    [START CONTEXT AND DATA]
    {context}
    [END CONTEXT AND DATA]

    Your Task
    Analyze all the provided data for the stocks on the watchlist. Your primary goal is to use the "PROPRIETARY ANALYSIS DATA" section to inform your decisions. The "Confidence Score" and detailed technical indicators should be heavily weighted.
    You must also provide a "Profitability Chance" as a percentage (e.g., '65%'), representing your confidence in the trade reaching its profit target before the stop loss.

    Trade Selection Criteria
    - Hard Filters: The current price must be above the 50-day MA, and the 14-day RSI must be below 70. Use the values from the proprietary data.
    - Thesis: The "Thesis" must be concise (<= 20 words) and must justify the trade by referencing the provided proprietary data.

    Output Format
    Provide the output as a clean, text-wrapped table with these exact columns. Add the 'Profitability Chance' column before the 'Thesis'.
    For the "Stop Loss" and "Profit Target" columns, you must include the percentage change from the entry price. For example: "$250.00 (-10%)".
    Ticker | Action | Entry Range | Stop Loss | Profit Target | Profitability Chance | Thesis
    
    Do not include any other text, explanations, or formatting. If a stock fails the hard filters or has unavailable data, indicate this in the Thesis.
    """)
    
    return prompt_template.strip()

def parse_and_print_response(response_text: str):
    """Parses the Gemini response text and prints it as a formatted table."""
    print("\n" + "="*50)
    print("               Final Trade Plan")
    print("="*50)
    
    if not response_text:
        print("Received an empty response from the API.")
        return
        
    try:
        cleaned_text = response_text.replace('`', '').replace('---', '').strip()
        lines = [line for line in cleaned_text.split('\n') if line.strip()]
        
        headers = [h.strip() for h in lines[0].split('|')]
        data = [
            [r.strip() for r in line.split('|')]
            for line in lines[1:]
            if len([r.strip() for r in line.split('|')]) == len(headers)
        ]
        
        if not data:
            raise ValueError("No data rows could be parsed from the response.")

        print(tabulate(data, headers=headers, tablefmt="grid"))
        
    except Exception as parse_error:
        print(f"\nCould not parse the table (Error: {parse_error}).")
        print("--- Raw Gemini Output ---")
        print(response_text)
    print("="*50 + "\n")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Stock Trading Bot")
    parser.add_argument("ticker", type=str, nargs="?", help="Stock ticker symbol (e.g., AAPL)")
    parser.add_argument("price", type=float, nargs="?", help="Purchase price of the stock")
    args = parser.parse_args()

    if args.ticker and args.price:
        # If ticker and price are provided, calculate sell prices
        analyzer = StockAnalyzer(args.ticker)
        sell_prices = analyzer.get_sell_prices(args.price)
        print(f"Sell prices for {args.ticker}:")
        print(f"  - Stop Loss: {sell_prices['stop_loss']}")
        print(f"  - Take Profit: {sell_prices['take_profit']}")
    else:
        # Original functionality
        # 1. Get watchlist from Gemini
        print("STEP 1: Asking Gemini for 25 potential swing trade stocks...")
        initial_watchlist = get_swing_stocks()
        print("-" * 50)

        # 2. Filter and Analyze the watchlist
        print("STEP 2: Filtering and analyzing watchlist with local tools...")

        filtered_stocks = []
        analysis_data = {}

        for ticker in initial_watchlist:
            if len(filtered_stocks) >= 5:
                print("\n  > Analysis complete. Found 5 suitable stocks.")
                break

            analyzer = StockAnalyzer(ticker)

            # Check for high-profitability chance
            confidence_str = analyzer.get_confidence_score()
            try:
                confidence_val = float(confidence_str.strip('%'))
                if confidence_val < 85.0:
                    print(f"  - Skipping {ticker} (Confidence: {confidence_str} < 85%)")
                    continue
            except (ValueError, TypeError):
                print(f"  - Skipping {ticker} (Could not parse confidence score)")
                continue

            # Check technical indicators
            tech_indicators = analyzer.get_technical_indicators()
            if not isinstance(tech_indicators, dict):
                print(f"  - Skipping {ticker} (Insufficient technical data)")
                continue

            # Add to filtered list
            print(f"  + Adding {ticker} to final list (Confidence: {confidence_str})")
            filtered_stocks.append(ticker)
            analysis_data[ticker] = {
                "Technical Indicators": tech_indicators,
                "Confidence Score": confidence_str
            }

        if len(filtered_stocks) < 3:
            print("\nCould not find at least 3 high-probability stocks. Exiting.")
            exit()

        print(f"\nFinal Watchlist: {', '.join(filtered_stocks)}")
        print("-" * 50)

        # 3. Fetch live prices
        print("STEP 3: Fetching live market prices...")
        try:
            data = yf.download(tickers=filtered_stocks, period='2d', interval='1m', progress=False, auto_adjust=True)
            live_prices = data['Close'].iloc[-1].to_dict()
            print("  - Success: Live prices fetched.")
        except Exception as e:
            print(f"  - Error: Could not fetch live prices: {e}. Exiting.")
            exit()
        print("-" * 50)

        # 4. Generate context
        print("STEP 4: Generating full context for Gemini...")
        full_context = generate_trading_context(filtered_stocks, live_prices, analysis_data)

        # 5. Create prompt
        print("STEP 5: Constructing final, detailed prompt...")
        analysis_prompt = create_trading_prompt(full_context)
        print("-" * 50)

        # 6. Send to Gemini
        print("STEP 6: Sending final prompt to Gemini for trade plan...")
        final_response_text = prompt_gemini_for_analysis(analysis_prompt)

        # 7. Parse and print final result
        parse_and_print_response(final_response_text)
