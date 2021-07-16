from fastapi import FastAPI

from api.config import CHROME_BINARY_PATH, CHROME_DRIVER_PATH

from .generator import PayloadGenerator

web_url = "https://newweb.nepalstock.com/company/detail/2917"
api_url = "https://newweb.nepalstock.com/api/nots/security/2917"

generator = PayloadGenerator(CHROME_BINARY_PATH, CHROME_DRIVER_PATH, web_url, api_url)
app = FastAPI()


@app.get("/")
async def root():
    payload_id = generator.get_payload_id()
    return {"payload_id": payload_id}


@app.get("/fetch")
async def fetch():
    payload_id = generator.fetch_payload_id()
    return {"payload_id": payload_id}
