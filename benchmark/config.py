from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")


def env_int(name: str, default: int) -> int:
    return int(os.getenv(name, str(default)))


@dataclass(frozen=True)
class Settings:
    seed: int = env_int("BENCHMARK_SEED", 20260830)
    orders: int = env_int("BENCHMARK_ORDERS", 100_000)
    repetitions: int = env_int("BENCHMARK_REPETITIONS", 10)
    batch_size: int = env_int("BENCHMARK_BATCH_SIZE", 2_000)
    mssql_host: str = os.getenv("MSSQL_HOST", "localhost")
    mssql_port: int = env_int("MSSQL_PORT", 1433)
    mssql_user: str = os.getenv("MSSQL_USER", "sa")
    mssql_password: str = os.getenv("MSSQL_SA_PASSWORD", "OnlineShop_Test_2026!")
    mssql_database: str = os.getenv("MSSQL_DATABASE", "OnlineShopDB")
    postgres_host: str = os.getenv("POSTGRES_HOST", "localhost")
    postgres_port: int = env_int("POSTGRES_PORT", 5432)
    postgres_user: str = os.getenv("POSTGRES_USER", "postgres")
    postgres_password: str = os.getenv("POSTGRES_PASSWORD", "OnlineShop_Test_2026!")
    postgres_database: str = os.getenv("POSTGRES_DB", "OnlineShopDB")
    mongo_host: str = os.getenv("MONGO_HOST", "localhost")
    mongo_port: int = env_int("MONGO_PORT", 27017)
    mongo_user: str = os.getenv("MONGO_INITDB_ROOT_USERNAME", "root")
    mongo_password: str = os.getenv(
        "MONGO_INITDB_ROOT_PASSWORD", "OnlineShop_Test_2026!"
    )
    mongo_database: str = os.getenv("MONGO_DATABASE", "OnlineShopDB")

    @property
    def customer_count(self) -> int:
        return max(1_000, self.orders // 5)

    @property
    def product_count(self) -> int:
        return max(1_000, self.orders // 10)

    @property
    def category_count(self) -> int:
        return 50

    @property
    def mongo_uri(self) -> str:
        return (
            f"mongodb://{self.mongo_user}:{self.mongo_password}@"
            f"{self.mongo_host}:{self.mongo_port}/?authSource=admin"
        )
