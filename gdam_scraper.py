import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import time

def get_gdam_data():
    # Set Chrome options for headless operation
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    # Path to your manually downloaded ChromeDriver
    chromedriver_path = "/Users/sagnikchakravarty/Downloads/chromedriver-mac-arm64/chromedriver"  # 🔁 Change this line

    service = Service(executable_path=chromedriver_path)
    driver = webdriver.Chrome(service=service, options=options)

    try:
        url = "https://www.iexindia.com/market-data/green-day-ahead-market/market-snapshot"
        driver.get(url)
        time.sleep(10)  # Wait for JavaScript to load

        soup = BeautifulSoup(driver.page_source, "html.parser")
    finally:
        driver.quit()

    table = soup.find("table")
    if not table:
        raise Exception("Could not find data table on the page.")

    rows = table.find_all("tr")

    headers = [
        "Date", "Hour", "Time Block", "Purchase Bid (MW)",
        "Sell Bid Total (MWh)", "Sell Bid Solar (MWh)", "Sell Bid Non-Solar (MWh)", "Sell Bid Hydro (MWh)",
        "MCV Total (MWh)", "MCV Solar (MWh)", "MCV Non-Solar (MWh)", "MCV Hydro (MWh)",
        "Final Scheduled Total (MWh)", "Final Scheduled Solar (MWh)", "Final Scheduled Non-Solar (MWh)", "Final Scheduled Hydro (MWh)",
        "MCP (Rs/MWh)"
    ]

    data = []
    last_date = ""
    last_hour = ""

    for row in rows[1:]:
        cols = [td.text.strip() for td in row.find_all("td")]

        if len(cols) == 17:
            last_date = cols[0]
            last_hour = cols[1]
        elif len(cols) == 16:
            cols.insert(0, last_date)
            last_hour = cols[1]
        elif len(cols) == 15:
            cols.insert(0, last_date)
            cols.insert(1, last_hour)

        if len(cols) == 17:
            data.append(cols)

    df = pd.DataFrame(data, columns=headers)
    return df

# Example usage
if __name__ == "__main__":
    try:
        df = get_gdam_data()
        print(df.head())
    except Exception as e:
        print("Error loading GDAM data:", e)



