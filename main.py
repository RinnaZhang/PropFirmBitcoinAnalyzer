import requests
from bs4 import BeautifulSoup
import pandas as pd
import re  # To handle extracting numbers from strings

# Step 1: Scrape Prop Trading Firms Data from Forex Prop Reviews
url = 'https://forexpropreviews.com/proprietary-trading-firm-comparison-spreadsheet/'

response = requests.get(url)
if response.status_code == 200:
    print("Successfully fetched the webpage!")
else:
    print("Failed to retrieve the webpage")

soup = BeautifulSoup(response.content, 'html.parser')

firms = []
table = soup.find('table', class_='has-fixed-layout')

# Function to extract the numeric percentage from text
def extract_percentage(text):
    # Use regex to extract the first numeric percentage found
    match = re.search(r'(\d+(\.\d+)?)%', text)
    if match:
        return float(match.group(1))  
    else:
        return None  

# Function to extract the minimum trading days
def extract_min_trading_days(text):
    if text.lower().startswith('no'):
        return 0  
    
    # Check if the text contains "Standard:", then extract the number following it
    if "Standard" in text:
        match = re.search(r'\d+', text)  
        if match:
            return int(match.group(0))  
    
    return int(text.split()[0])  

# Function to clean "Maximum Trading Days" for better readability
def clean_max_trading_days(text):
    return text.replace('Phase 1:', 'Phase 1: ').replace('Phase 2:', 'Phase 2: ')

# Extract table rows
for row in table.find_all('tr')[1:]:
    columns = row.find_all('td')
    
    firms.append({
        'Prop Firm': columns[0].text.strip(),
        'Profit Targets': columns[1].text.strip(),
        'Max Daily Drawdown': extract_percentage(columns[2].text.strip()), 
        'Max Drawdown': extract_percentage(columns[3].text.strip()),  
        'Minimum Trading Days': extract_min_trading_days(columns[4].text.strip()),  
        'Maximum Trading Days': clean_max_trading_days(columns[5].text.strip()),  
        'Profit Split': columns[6].text.strip()
    })

df_firms = pd.DataFrame(firms)

# Step 2: Fetch Bitcoin Exchange Rate from Blockchain API
blockchain_api_url = 'https://blockchain.info/ticker'
btc_response = requests.get(blockchain_api_url)

if btc_response.status_code == 200:
    btc_data = btc_response.json()
    btc_usd_rate = btc_data['USD']['last']
    print(f"Current Bitcoin to USD exchange rate: {btc_usd_rate}")
else:
    print("Failed to retrieve Bitcoin exchange rate")
    btc_usd_rate = None

# Add Bitcoin exchange rate as a column
df_firms['Bitcoin to USD Exchange Rate'] = btc_usd_rate

# Step 3: Ask the user for their preferences
print("\nPlease enter your preferences:")

# Get user preferences
max_drawdown_preference = float(input("Enter the maximum drawdown percentage you're willing to tolerate (e.g., 12): "))
profit_split_preference = input("Enter the minimum profit split percentage you're looking for (e.g., 80%): ")

min_profit_split = float(profit_split_preference.strip('%'))

min_trading_days = int(input("Enter the maximum number of minimum trading days you're willing to trade (e.g., 5): "))

# Step 4: Filter the firms based on the user's input
filtered_firms = df_firms[
    (df_firms['Max Drawdown'] <= max_drawdown_preference) &
    (df_firms['Profit Split'].str.contains(f'{int(min_profit_split)}%')) &  
    (df_firms['Minimum Trading Days'] <= min_trading_days)
]

# Format and display the best matching firms
if not filtered_firms.empty:
    pd.set_option('display.max_colwidth', None)  
    pd.set_option('display.colheader_justify', 'left')  
    pd.set_option('display.expand_frame_repr', False)  
    
    print("\nThe best matching firms based on your preferences are:\n")
    display_columns = ['Prop Firm', 'Max Drawdown', 'Minimum Trading Days', 'Profit Split', 'Bitcoin to USD Exchange Rate']
    print(filtered_firms[display_columns].to_string(index=False)) 
else:
    print("\nNo firms matched your criteria.")

# Save the filtered firms to a CSV file
filtered_firms.to_csv('filtered_prop_firms.csv', index=False)