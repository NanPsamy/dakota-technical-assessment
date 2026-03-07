from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Optional
from datetime import date
import random
import numpy as np
from faker import Faker

app = FastAPI(
    title="Dakota Energy Enrichment API",
    description="Synthetic data generation for energy market context",
    version="1.0.0"
)

fake = Faker()

class EnergyMarketContext(BaseModel):
    period: date
    area_code: str = Field(..., min_length=1, max_length=10)
    wti_crude_price_usd: float = Field(..., ge=0, le=200)
    brent_crude_price_usd: float = Field(..., ge=0, le=200)
    crude_spread: float = Field(..., ge=-50, le=50)
    refinery_utilization_rate: float = Field(..., ge=0, le=100)
    refinery_outage_index: float = Field(..., ge=0, le=10)
    gasoline_inventory_million_barrels: float = Field(..., ge=0, le=500)
    supply_disruption_index: float = Field(..., ge=0, le=10)
    regional_demand_index: float = Field(..., ge=0, le=10)
    vehicle_miles_traveled_index: float = Field(..., ge=0, le=10)
    avg_temperature_c: float = Field(..., ge=-50, le=50)
    heating_degree_days: float = Field(..., ge=0, le=10000)
    cooling_degree_days: float = Field(..., ge=0, le=10000)
    pipeline_utilization_rate: float = Field(..., ge=0, le=100)
    shipping_cost_index: float = Field(..., ge=0, le=10)
    energy_volatility_index: float = Field(..., ge=0, le=10)
    speculative_pressure_index: float = Field(..., ge=0, le=10)
    hurricane_risk_index: float = Field(..., ge=0, le=10)
    geopolitical_risk_index: float = Field(..., ge=0, le=10)

def generate_synthetic_data(period: date, area_code: str) -> EnergyMarketContext:
    """Generate realistic synthetic energy market data"""
    # Base prices with some randomness
    base_wti = 70 + random.uniform(-20, 30)
    base_brent = base_wti + random.uniform(1, 5)

    # Seasonal adjustments
    month = period.month
    if month in [6, 7, 8]:  # Summer driving season
        demand_multiplier = 1.2
        temp_base = 25
    elif month in [12, 1, 2]:  # Winter
        demand_multiplier = 0.9
        temp_base = 0
    else:
        demand_multiplier = 1.0
        temp_base = 15

    # Generate data with correlations
    refinery_rate = random.uniform(70, 95)
    demand_index = random.uniform(3, 8) * demand_multiplier
    inventory = random.uniform(200, 400)

    # Temperature and degree days
    temp = temp_base + random.uniform(-10, 10)
    hdd = max(0, 18 - temp) * 30  # Simplified
    cdd = max(0, temp - 22) * 30

    return EnergyMarketContext(
        period=period,
        area_code=area_code,
        wti_crude_price_usd=round(base_wti, 2),
        brent_crude_price_usd=round(base_brent, 2),
        crude_spread=round(base_brent - base_wti, 2),
        refinery_utilization_rate=round(refinery_rate, 2),
        refinery_outage_index=round(random.uniform(0, 2), 3),
        gasoline_inventory_million_barrels=round(inventory, 2),
        supply_disruption_index=round(random.uniform(0, 3), 3),
        regional_demand_index=round(demand_index, 3),
        vehicle_miles_traveled_index=round(demand_index * 0.8, 3),
        avg_temperature_c=round(temp, 2),
        heating_degree_days=round(hdd, 2),
        cooling_degree_days=round(cdd, 2),
        pipeline_utilization_rate=round(random.uniform(60, 95), 2),
        shipping_cost_index=round(random.uniform(2, 6), 3),
        energy_volatility_index=round(random.uniform(1, 5), 3),
        speculative_pressure_index=round(random.uniform(0, 4), 3),
        hurricane_risk_index=round(random.uniform(0, 3), 3),  # Higher in Gulf areas
        geopolitical_risk_index=round(random.uniform(0, 5), 3)
    )

@app.get("/")
async def root():
    return {"message": "Dakota Energy Enrichment API", "version": "1.0.0"}

@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.get("/enrich/{area_code}")
async def enrich_data(area_code: str, period: date = None):
    """Generate synthetic enrichment data for a given area and period"""
    if not period:
        # Default to current week if not specified
        import datetime
        today = date.today()
        period = today - datetime.timedelta(days=today.weekday())

    try:
        data = generate_synthetic_data(period, area_code)
        return data.dict()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating data: {str(e)}")

@app.post("/enrich/batch")
async def enrich_batch(request: dict):
    """Generate enrichment data for multiple periods/areas"""
    periods = request.get("periods", [])
    area_codes = request.get("area_codes", [])

    if not periods or not area_codes:
        raise HTTPException(status_code=400, detail="Provide periods and area_codes")

    results = []
    for period_str in periods:
        for area in area_codes:
            try:
                period = date.fromisoformat(period_str)
                data = generate_synthetic_data(period, area)
                results.append(data.dict())
            except ValueError:
                continue  # Skip invalid dates

    return {"data": results}