import os
from pydantic import BaseModel, Field
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config(BaseModel):
    STARTING_CAPITAL: float = Field(default=50000.0, description="Initial capital")
    DB_PATH: str = Field(default="data/forge_tl.duckdb", description="Path to DuckDB database")
    RAW_DATA_DIR: str = Field(default="data/raw", description="Directory for raw data")
    PROCESSED_DATA_DIR: str = Field(default="data/processed", description="Directory for processed data")
    PARQUET_DIR: str = Field(default="data/parquet", description="Directory for parquet exports")

def load_config() -> Config:
    return Config(
        STARTING_CAPITAL=float(os.getenv("FORGE_STARTING_CAPITAL", 50000.0)),
        DB_PATH=os.getenv("FORGE_DB_PATH", "data/forge_tl.duckdb"),
        RAW_DATA_DIR=os.getenv("FORGE_RAW_DATA_DIR", "data/raw"),
        PROCESSED_DATA_DIR=os.getenv("FORGE_PROCESSED_DATA_DIR", "data/processed"),
        PARQUET_DIR=os.getenv("FORGE_PARQUET_DIR", "data/parquet")
    )

config = load_config()

# Ensure directories exist
os.makedirs(config.RAW_DATA_DIR, exist_ok=True)
os.makedirs(config.PROCESSED_DATA_DIR, exist_ok=True)
os.makedirs(config.PARQUET_DIR, exist_ok=True)
