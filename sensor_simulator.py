import os
import asyncio
import aiohttp
import random
import math
from datetime import datetime

BASE_URL = "https://fuel-truck-monitoring-backend-1.onrender.com"
USERNAME = os.getenv("SIMULATOR_USER")
PASSWORD = os.getenv("SIMULATOR_PASS")
SENSOR_IDS = list(set(["SENSOR_ID11", "SENSOR_ID22", "SENSOR_ID44", "SENSOR_ID55", "SENSOR_ID66","SENSOR_ID77","SENSOR_ID88","SENSOR_ID99","SENSOR_ID100","SENSOR_ID21","SENSOR_ID22","SENSOR_ID123","SENSOR_ID24"]))
CENTER_LAT = 23.6913
CENTER_LNG = 85.2722
RADIUS_METERS = 300

def generate_gps_point():
    angle = random.uniform(0, 2 * math.pi)
    dx = RADIUS_METERS * math.cos(angle) / 111320
    dy = RADIUS_METERS * math.sin(angle) / 111320
    return CENTER_LAT + dy, CENTER_LNG + dx

async def simulate_sensor(session, token):
    headers = {"Authorization": f"Bearer {token}"}
    fuel_level = 100.0

    while True:
        try:
            lat, lng = generate_gps_point()
            valve_open = random.choice([True, False])
            tilt = random.choice([True, False])
            fuel_drop = random.uniform(10.1, 30.0)
            fuel_level = max(0, fuel_level - fuel_drop)

            payload = {
                "sensor_id": SENSOR_ID,
                "fuel_level": round(fuel_level, 2),
                "valve_open": valve_open,
                "latitude": lat,
                "longitude": lng,
                "tilt_detected": tilt,
                "timestamp": datetime.utcnow().isoformat()
            }

            r = await session.post(f"{BASE_URL}/sensor/ingest", json=payload, headers=headers)
            r_data = await r.json()

            print(f"📡 Sent: {payload}")
            print(f"🚨 Server: {r_data}\n")

            await asyncio.sleep(6)

        except aiohttp.ClientError as e:
            print(f"⚠️ Connection error: {e}")
            break

async def main():
    while True:
        try:
            async with aiohttp.ClientSession() as session:
                print("🔐 Logging in...")
                resp = await session.post(f"{BASE_URL}/auth/login", json={
                    "email": USERNAME,
                    "password": PASSWORD
                })
                login_data = await resp.json()
                if "token" not in login_data:
                    print("❌ Login failed:", login_data)
                    return

                token = login_data["token"]
                print("✅ Logged in. Starting simulation...\n")

                await simulate_sensor(session, token)

        except Exception as e:
            print(f"❌ Critical error: {e}. Retrying in 5s...\n")
            await asyncio.sleep(5)

asyncio.run(main())
