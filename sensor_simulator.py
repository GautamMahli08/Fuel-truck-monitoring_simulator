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

MIN_RADIUS_METERS = 1000
MAX_RADIUS_METERS = 5000

def generate_gps_point():
    distance = random.uniform(MIN_RADIUS_METERS, MAX_RADIUS_METERS)
    angle = random.uniform(0, 2 * math.pi)
    dx = (distance * math.cos(angle)) / 111320
    dy = (distance * math.sin(angle)) / 111320
    return CENTER_LAT + dy, CENTER_LNG + dx

async def simulate_sensor(session, token):
    headers = {"Authorization": f"Bearer {token}"}
    fuel_levels = {sid: 100.0 for sid in SENSOR_IDS}

    while True:
        for sensor_id in SENSOR_IDS:
            try:
                lat, lng = generate_gps_point()
                valve_open = random.choices([True, False], weights=[0.2, 0.8])[0]  # Valve usually closed
                tilt = random.choices([True, False], weights=[0.1, 0.9])[0]         # Rarely tilts

                # Normal driving = slow fuel consumption
                fuel_drop = random.uniform(0.5, 2.5)

                # Simulate theft/tampering if valve is open
                if valve_open:
                    fuel_drop += random.uniform(10.0, 25.0)
                    print(f"🚨 [ALERT SIMULATED] Valve is OPEN during drop for {sensor_id}!")

                fuel_levels[sensor_id] = max(0, fuel_levels[sensor_id] - fuel_drop)

                # Simulate refueling if empty
                if fuel_levels[sensor_id] <= 0:
                    print(f"🔄 [Refueling] Fuel refilled for {sensor_id}")
                    fuel_levels[sensor_id] = 100.0

                payload = {
                    "sensor_id": sensor_id,
                    "fuel_level": round(fuel_levels[sensor_id], 2),
                    "valve_open": valve_open,
                    "latitude": lat,
                    "longitude": lng,
                    "tilt_detected": tilt,
                    "timestamp": datetime.utcnow().isoformat()
                }

                r = await session.post("http://localhost:8000/sensor/ingest", json=payload, headers=headers)
                r_data = await r.json()

                print(f"📡 Sent sensor data for {sensor_id}: {payload}")
                print(f"✅ Response: {r_data}\n")

            except aiohttp.ClientError as e:
                print(f"⚠️ Connection error: {e}. Retrying login...")
                break

        await asyncio.sleep(5)

async def main():
    while True:
        try:
            async with aiohttp.ClientSession() as session:
                print("🔐 Logging in...")
                resp = await session.post("http://localhost:8000/auth/login", json={
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
