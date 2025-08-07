from fastapi.middleware.cors import CORSMiddleware

from fastapi import FastAPI, Query
import httpx

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


API_KEY="7eaa6dc9004535b989696c49323a410e"
@app.get("/weather")
async def get_weather(city: str = Query(...)):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        if response.status_code != 200:
            return {"error": "City not found"}
        data = response.json()
        return {
            "city": data["name"],
            "temperature": data["main"]["temp"],
            "humidity": data["main"]["humidity"],
            "description": data["weather"][0]["description"]
        }