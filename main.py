import os
import urllib.parse

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from starlette.requests import Request
from pymongo import MongoClient
from pymongo.server_api import ServerApi

app = FastAPI()

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins (change this for security)
    allow_credentials=True,
    allow_methods=["*"],  # Allows all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],  # Allows all headers
)

load_dotenv()

username = urllib.parse.quote_plus(os.getenv("MONGO_USER"))
password = urllib.parse.quote_plus(os.getenv("MONGO_PASS"))
MONGO_HOST = urllib.parse.quote_plus(os.getenv("MONGO_HOST"))
mongo_uri = f"mongodb+srv://{username}:{password}@{MONGO_HOST}/?retryWrites=true&w=majority&appName=periodic"

client = MongoClient(mongo_uri, server_api=ServerApi("1"))

try:
    client.admin.command("ping")
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)

db = client["periodic_table"]

elements_collection = db["elements"]

# Mount static directory (for CSS & JS)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Set up Jinja2 templates (for HTML rendering)
templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
async def serve_homepage(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/elements")
async def get_all_elements():
    elements = list(elements_collection.find({}, {"_id": 0}))
    return elements


@app.get("/element/{symbol}")
async def get_element(symbol: str):
    element = elements_collection.find_one({"symbol": symbol}, {"_id": 0})
    if element:
        return element
    return {"error": "Element not found"}


@app.get("/filter_options")
async def get_filter_options():
    # Retrieve distinct group and period values from the collection
    groups = sorted(list(elements_collection.distinct("group")))
    periods = sorted(list(elements_collection.distinct("period")))
    return {"groups": groups, "periods": periods}
