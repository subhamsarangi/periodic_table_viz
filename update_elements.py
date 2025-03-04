import os
import urllib.parse
from dotenv import load_dotenv
from pymongo import MongoClient

# 1. Predefined positions mapping (symbol -> group, period)
positions = {
    "H": {"group": 1, "period": 1},
    "He": {"group": 18, "period": 1},
    "Li": {"group": 1, "period": 2},
    "Be": {"group": 2, "period": 2},
    "B": {"group": 13, "period": 2},
    "C": {"group": 14, "period": 2},
    "N": {"group": 15, "period": 2},
    "O": {"group": 16, "period": 2},
    "F": {"group": 17, "period": 2},
    "Ne": {"group": 18, "period": 2},
    "Na": {"group": 1, "period": 3},
    "Mg": {"group": 2, "period": 3},
    "Al": {"group": 13, "period": 3},
    "Si": {"group": 14, "period": 3},
    "P": {"group": 15, "period": 3},
    "S": {"group": 16, "period": 3},
    "Cl": {"group": 17, "period": 3},
    "Ar": {"group": 18, "period": 3},
    "K": {"group": 1, "period": 4},
    "Ca": {"group": 2, "period": 4},
    "Sc": {"group": 3, "period": 4},
    "Ti": {"group": 4, "period": 4},
    "V": {"group": 5, "period": 4},
    "Cr": {"group": 6, "period": 4},
    "Mn": {"group": 7, "period": 4},
    "Fe": {"group": 8, "period": 4},
    "Co": {"group": 9, "period": 4},
    "Ni": {"group": 10, "period": 4},
    "Cu": {"group": 11, "period": 4},
    "Zn": {"group": 12, "period": 4},
    "Ga": {"group": 13, "period": 4},
    "Ge": {"group": 14, "period": 4},
    "As": {"group": 15, "period": 4},
    "Se": {"group": 16, "period": 4},
    "Br": {"group": 17, "period": 4},
    "Kr": {"group": 18, "period": 4},
    "Rb": {"group": 1, "period": 5},
    "Sr": {"group": 2, "period": 5},
    "Y": {"group": 3, "period": 5},
    "Zr": {"group": 4, "period": 5},
    "Nb": {"group": 5, "period": 5},
    "Mo": {"group": 6, "period": 5},
    "Tc": {"group": 7, "period": 5},
    "Ru": {"group": 8, "period": 5},
    "Rh": {"group": 9, "period": 5},
    "Pd": {"group": 10, "period": 5},
    "Ag": {"group": 11, "period": 5},
    "Cd": {"group": 12, "period": 5},
    "In": {"group": 13, "period": 5},
    "Sn": {"group": 14, "period": 5},
    "Sb": {"group": 15, "period": 5},
    "Te": {"group": 16, "period": 5},
    "I": {"group": 17, "period": 5},
    "Xe": {"group": 18, "period": 5},
    "Cs": {"group": 1, "period": 6},
    "Ba": {"group": 2, "period": 6},
    # Lanthanides
    "La": {"group": 3, "period": 6},
    "Ce": {"group": 3, "period": 6},
    "Pr": {"group": 3, "period": 6},
    "Nd": {"group": 3, "period": 6},
    "Pm": {"group": 3, "period": 6},
    "Sm": {"group": 3, "period": 6},
    "Eu": {"group": 3, "period": 6},
    "Gd": {"group": 3, "period": 6},
    "Tb": {"group": 3, "period": 6},
    "Dy": {"group": 3, "period": 6},
    "Ho": {"group": 3, "period": 6},
    "Er": {"group": 3, "period": 6},
    "Tm": {"group": 3, "period": 6},
    "Yb": {"group": 3, "period": 6},
    "Lu": {"group": 3, "period": 6},
    "Hf": {"group": 4, "period": 6},
    "Ta": {"group": 5, "period": 6},
    "W": {"group": 6, "period": 6},
    "Re": {"group": 7, "period": 6},
    "Os": {"group": 8, "period": 6},
    "Ir": {"group": 9, "period": 6},
    "Pt": {"group": 10, "period": 6},
    "Au": {"group": 11, "period": 6},
    "Hg": {"group": 12, "period": 6},
    "Tl": {"group": 13, "period": 6},
    "Pb": {"group": 14, "period": 6},
    "Bi": {"group": 15, "period": 6},
    "Po": {"group": 16, "period": 6},
    "At": {"group": 17, "period": 6},
    "Rn": {"group": 18, "period": 6},
    "Fr": {"group": 1, "period": 7},
    "Ra": {"group": 2, "period": 7},
    # Actinides
    "Ac": {"group": 3, "period": 7},
    "Th": {"group": 3, "period": 7},
    "Pa": {"group": 3, "period": 7},
    "U": {"group": 3, "period": 7},
    "Np": {"group": 3, "period": 7},
    "Pu": {"group": 3, "period": 7},
    "Am": {"group": 3, "period": 7},
    "Cm": {"group": 3, "period": 7},
    "Bk": {"group": 3, "period": 7},
    "Cf": {"group": 3, "period": 7},
    "Es": {"group": 3, "period": 7},
    "Fm": {"group": 3, "period": 7},
    "Md": {"group": 3, "period": 7},
    "No": {"group": 3, "period": 7},
    "Lr": {"group": 3, "period": 7},
    "Rf": {"group": 4, "period": 7},
    "Db": {"group": 5, "period": 7},
    "Sg": {"group": 6, "period": 7},
    "Bh": {"group": 7, "period": 7},
    "Hs": {"group": 8, "period": 7},
    "Mt": {"group": 9, "period": 7},
    "Ds": {"group": 10, "period": 7},
    "Rg": {"group": 11, "period": 7},
    "Cn": {"group": 12, "period": 7},
    "Nh": {"group": 13, "period": 7},
    "Fl": {"group": 14, "period": 7},
    "Mc": {"group": 15, "period": 7},
    "Lv": {"group": 16, "period": 7},
    "Ts": {"group": 17, "period": 7},
    "Og": {"group": 18, "period": 7},
}


def main():
    # 2. Load environment variables
    load_dotenv()

    # 3. Build the Mongo URI
    username = urllib.parse.quote_plus(os.getenv("MONGO_USER"))
    password = urllib.parse.quote_plus(os.getenv("MONGO_PASS"))
    MONGO_HOST = urllib.parse.quote_plus(os.getenv("MONGO_HOST"))
    mongo_uri = f"mongodb+srv://{username}:{password}@{MONGO_HOST}/?retryWrites=true&w=majority&appName=periodic"

    # 4. Connect to MongoDB
    client = MongoClient(mongo_uri)
    db = client["periodic_table"]
    elements_coll = db["elements"]

    # 5. Update group/period in each element doc
    all_elements = elements_coll.find({})
    for doc in all_elements:
        sym = doc.get("symbol", "").strip()
        if sym in positions:
            gp = positions[sym]["group"]
            pd = positions[sym]["period"]
            elements_coll.update_one(
                {"_id": doc["_id"]}, {"$set": {"group": gp, "period": pd}}
            )
            print(f"Updated {sym} → group={gp}, period={pd}")
        else:
            print(f"Skipping {sym}, not found in positions map.")

    print("Done updating group/period for elements!")


if __name__ == "__main__":
    main()
