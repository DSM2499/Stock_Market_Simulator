from fastapi import FastAPI, Body
from fastapi.middleware.cors import CORSMiddleware
from pydantic import RootModel, BaseModel
from typing import Dict, List
from api.data_store import DataStore

app = FastAPI()
store = DataStore()

app.add_middleware(
    CORSMiddleware,
    allow_origins = ["*"],
    allow_credentials = True,
    allow_methods = ["*"],
    allow_headers = ["*"],
)

class OHLCEntry(BaseModel):
    day: int
    open: float
    high: float
    low: float
    close: float
    volume: int

class OHLCUpdate(RootModel[Dict[str, List[OHLCEntry]]]):
    pass

class WealthEntry(BaseModel):
    agent_id: int
    strategy: str
    day: int
    cash: float
    wealth: float
    is_market_maker: bool

    class config:
        extra = "allow"

class SentimentEntry(BaseModel):
    day: int
    minute: int
    stock: str
    sentiment: float

# POST Endpoints

@app.post('/update/ohlc')
def update_ohlc(data: OHLCUpdate):
    store.update_ohlc(data.root)
    return {"status": "ok"}

@app.post('/update/wealth')
def update_wealth(data: List[WealthEntry]):
    entries = [entry.model_dump() for entry in data]
    store.update_wealth(entries)
    return {"status": "ok"}

@app.post('/update/sentiment')
def update_sentiment(data: List[SentimentEntry]):
    entries = [entry.model_dump() for entry in data]
    store.update_sentiment(entries)
    return {"status": "ok"}

# GET Endpoints

@app.get('/data/ohlc')
def get_ohlc():
    return store.get_ohlc()

@app.get('/data/wealth')
def get_wealth():
    return store.get_wealth()

@app.get('/data/sentiment')
def get_sentiment():
    return store.get_sentiment()
