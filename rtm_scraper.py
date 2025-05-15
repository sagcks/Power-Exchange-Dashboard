import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import time

def get_rtm_data():
    # Setup Chrome WebDriver manually (assuming it's already installed in /usr/local/bin/)
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    service = Service(executable_path="/Users/sagnikchakravarty/Downloads/chromedriver-mac-arm64/chromedriver")
    driver = webdriver.Chrome(service=service, options=options)

    # Load IEX RTM market snapshot
    url = "https://www.iexindia.com/market-data/real-time-market/market-snapshot"
    driver.get(url)
    time.sleep(10)
    soup = BeautifulSoup(driver.page_source, "html.parser")
    driver.quit()

    table = soup.find("table")
    rows = table.find_all("tr")

    headers = ["Date", "Session ID", "Time Block", "Purchase Bid (MW)", "Sell Bid (MW)",
               "MCV (MW)", "Final Scheduled Volume (MW)", "MCP (Rs/MWh)"]

    data = []
    today = pd.Timestamp.today().strftime("%d-%m-%Y")
    last_session_id = ""

    for row in rows[1:]:
        cols = [td.text.strip() for td in row.find_all("td")]
        if len(cols) < 6:
            continue

        if len(cols) == 7:
            last_session_id = cols[0]
            time_block = cols[1]
            purchase_bid = cols[2]
            sell_bid = cols[3]
            mcv = cols[4]
            scheduled_volume = cols[5]
            mcp = cols[6]
        elif len(cols) == 6:
            time_block = cols[0]
            purchase_bid = cols[1]
            sell_bid = cols[2]
            mcv = cols[3]
            scheduled_volume = cols[4]
            mcp = cols[5]
        else:
            continue  # Skip unexpected rows

        # Add row only if session ID is known
        if last_session_id:
            data.append([
                today,
                last_session_id,
                time_block,
                purchase_bid,
                sell_bid,
                mcv,
                scheduled_volume,
                mcp
            ])

    df = pd.DataFrame(data, columns=headers)
    return df



