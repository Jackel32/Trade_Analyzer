import os
import google.generativeai as genai
import textwrap

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

def prompt_gemini_for_analysis(prompt: str):
    """Sends the prompt to the Gemini API and prints the response."""
    try:
        api_key = get_api_key()
        genai.configure(api_key=api_key)

        model = genai.GenerativeModel('gemini-2.5-flash')
        response = model.generate_content(prompt)

        return response.text

    except Exception as e:
        print(f"An error occurred while contacting the Gemini API: {e}")
        return None
