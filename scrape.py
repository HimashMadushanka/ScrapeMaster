import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

data = []

# number of pages (adjust to reach ~2000 rows)
for page in range(1, 101):   # try 100 pages
    url = f"https://ikman.lk/en/ads/sri-lanka?page={page}"
    
    headers = {
        "User-Agent": "Mozilla/5.0"
    }
    
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")
    
    ads = soup.find_all("li", class_="normal--2QYVk gtm-normal-ad")
    
    for ad in ads:
        title = ad.find("h2")
        price = ad.find("div", class_="price--3SnqI")
        location = ad.find("div", class_="description--2-ez3")
        
        data.append({
            "Title": title.text.strip() if title else "",
            "Price": price.text.strip() if price else "",
            "Location": location.text.strip() if location else ""
        })
    
    print(f"Page {page} scraped")
    
    time.sleep(2)  # avoid blocking

# Convert to DataFrame
df = pd.DataFrame(data)

# Save to CSV
df.to_csv("ikman_data.csv", index=False)

print("✅ CSV file saved!")