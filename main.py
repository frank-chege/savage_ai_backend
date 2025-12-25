from fastapi import FastAPI, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
import httpx
import os
from dotenv import load_dotenv
import uvicorn

load_dotenv()

app = FastAPI()

# Enable CORS for Lovable
app.add_middleware(
    CORSMiddleware,
    allow_origins=["savage-ai.lovable.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

PAYSTACK_SECRET = os.getenv("PAYSTACK_SECRET")
HEADERS = {
    "Authorization": f"Bearer {PAYSTACK_SECRET}",
    "Content-Type": "application/json",
}


@app.post("/pay")
async def initiate_push(payload: dict = Body(...)):
    phone = payload.get("phone")
    if not phone:
        raise HTTPException(status_code=400, detail="Phone required")

    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://api.paystack.co/charge",
            json={
                "email": f"user_{phone}@savage.ai",
                "amount": "2000",  # KES 20
                "currency": "KES",
                "mobile_money": {"phone": phone, "provider": "mpesa"},
            },
            headers=HEADERS,
        )
        return response.json()


@app.get("/verify/{reference}")
async def verify_payment(reference: str):
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"https://api.paystack.co/charge/{reference}", headers=HEADERS
        )
        return response.json()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
