import requests
import pandas as pd
from bs4 import BeautifulSoup

# URL of the Wikipedia page
url = "https://en.wikipedia.org/wiki/List_of_chemical_elements"

# Request page content
response = requests.get(url)
soup = BeautifulSoup(response.text, "html.parser")

# Find the first table
table = soup.find("table", {"class": "wikitable"})

# Read table into DataFrame
df = pd.read_html(str(table))[0]

# Rename columns for better readability
df.columns = [
    "Atomic Number",
    "Symbol",
    "Element",
    "Origin of Name",
    "Group",
    "Period",
    "Block",
    "Atomic Weight",
    "Density",
    "Melting Point",
    "Boiling Point",
    "Specific Heat Capacity",
    "Electronegativity",
    "Abundance in Earth's Crust",
    "Origin",
    "Phase",
]

# Drop unwanted footnotes and clean the data
df = df.replace(r"\[.*?\]", "", regex=True)

# Show the first few rows
print(df.head())

# Save to CSV
df.to_csv("periodic_table.csv", index=False)
print("Data saved to periodic_table.csv")
