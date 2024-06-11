from typing import Union

from fastapi import FastAPI
from pydantic import BaseModel
from motor.motor_asyncio import AsyncIOMotorClient

app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}