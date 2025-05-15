import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import time

def get_dam_data():
    # Set up Selenium WebDriver (no webdriver-manager)
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    # Path to manually installed ChromeDriver
    chromedriver_path = "/Users/sagnikchakravarty/Downloads/chromedriver-mac-arm64/chromedriver"  # Make sure this is the correct path

    service = Service(executable_path=chromedriver_path)
    driver = webdriver.Chrome(service=service, options=options)

    try:
        # Visit the IEX Market Snapshot page
        url = "https://www.iexindia.com/market-data/day-ahead-market/market-snapshot"
        driver.get(url)
        time.sleep(10)  # Allow JS to load the table

        # Parse HTML
        soup = BeautifulSoup(driver.page_source, "html.parser")
    finally:
        driver.quit()

    # Locate table
    table = soup.find("table")
    if not table:
        raise Exception("Could not find data table on the page.")

    rows = table.find_all("tr")

    # Column headers
    headers = ["Date", "Time Block", "Purchase Bid (MW)", "Sell Bid (MW)",
               "MCV (MW)", "Final Scheduled Volume (MW)", "MCP (Rs/MWh)"]

    data = []
    today = pd.Timestamp.today().strftime("%d-%m-%Y")

    for row in rows[1:]:
        cols = [td.text.strip() for td in row.find_all("td")]
        if len(cols) == 6:
            time_block = cols[0]
            purchase_bid = cols[1]
            sell_bid = cols[2]
            mcv = cols[3]
            scheduled_volume = cols[4]
            mcp = cols[5]

            data.append([
                today,
                time_block,
                purchase_bid,
                sell_bid,
                mcv,
                scheduled_volume,
                mcp
            ])

    # Return DataFrame (no Excel save)
    df = pd.DataFrame(data, columns=headers)
    return df

# Run script
if __name__ == "__main__":
    try:
        df = get_dam_data()
        print(df.head())
    except Exception as e:
        print("Error loading DAM data:", e)


