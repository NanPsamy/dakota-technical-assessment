from pydantic import BaseModel, Field
from datetime import date

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