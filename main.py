from fastapi import FastAPI
from API.routers import symbol_data
from API.routers import symbol_hmm
from API.routers import symbol_volatility

app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}

app.include_router(symbol_data.router)
app.include_router(symbol_hmm.router)
app.include_router(symbol_volatility.router)