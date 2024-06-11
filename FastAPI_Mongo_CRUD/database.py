from motor.motor_asyncio import AsyncIOMotorClient
from fastapi import FastAPI
from dotenv import load_dotenv
import logging
import os

load_dotenv()
logging.basicConfig(level=logging.INFO)

async def db_lifespan(app: FastAPI):
    # Startup
    app.mongodb_client = AsyncIOMotorClient(os.getenv("MONGODB_URL"), tls=True, tlsAllowInvalidCertificates=True)
    app.employeeData = app.mongodb_client.employeeData
    ping_response = await app.employeeData.command("ping")
    if int(ping_response["ok"]) != 1:
        raise Exception("Problem connecting to database cluster.")
    else:
        logging.info("Connected to database cluster.")

    yield

    # Shutdown
    logging.info("Closing connection to database cluster.")
    app.mongodb_client.close()