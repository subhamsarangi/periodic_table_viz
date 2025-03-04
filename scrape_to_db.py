import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient
import os
import urllib.parse
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# MongoDB Connection Setup
username = urllib.parse.quote_plus(os.getenv("MONGO_USER"))
password = urllib.parse.quote_plus(os.getenv("MONGO_PASS"))
MONGO_HOST = urllib.parse.quote_plus(os.getenv("MONGO_HOST"))
mongo_uri = f"mongodb+srv://{username}:{password}@{MONGO_HOST}/?retryWrites=true&w=majority&appName=periodic"

client = MongoClient(mongo_uri)
db = client["periodic_table"]
elements_collection = db["elements"]

# URL of the Wikipedia periodic table page
url = "https://en.wikipedia.org/wiki/List_of_chemical_elements"
response = requests.get(url)
soup = BeautifulSoup(response.text, "html.parser")

# Find the table containing the periodic elements
table = soup.find("table", {"class": "wikitable"})
rows = table.find_all("tr")[1:]  # Skip header row

elements = []
for row in rows:
    cols = row.find_all("td")
    if len(cols) < 16:  # Ensure the row has all expected columns
        continue

    element_data = {
        "atomic_number": int(cols[0].text.strip()),
        "symbol": cols[1].text.strip(),
        "name": cols[2].text.strip(),
        "name_origin": cols[3].text.strip(),
        "group": cols[4].text.strip(),
        "period": cols[5].text.strip(),
        "block": cols[6].text.strip(),
        "atomic_weight": cols[7].text.strip(),
        "density": cols[8].text.strip() if cols[8].text.strip() else None,
        "melting_point": cols[9].text.strip() if cols[9].text.strip() else None,
        "boiling_point": cols[10].text.strip() if cols[10].text.strip() else None,
        "specific_heat_capacity": (
            cols[11].text.strip() if cols[11].text.strip() else None
        ),
        "electronegativity": cols[12].text.strip() if cols[12].text.strip() else None,
        "abundance": cols[13].text.strip() if cols[13].text.strip() else None,
        "origin": cols[14].text.strip(),
        "phase": cols[15].text.strip(),
    }
    elements.append(element_data)


# Insert elements into MongoDB
elements_collection.delete_many({})  # Clear existing data
elements_collection.insert_many(elements)

print("Scraped and stored periodic table data successfully!")
