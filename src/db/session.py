from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from pathlib import Path
import yaml

PROJECT_ROOT = Path(__file__).resolve().parents[2]

_engine = None
_SessionLocal = None


def get_db_config():
    config_path = PROJECT_ROOT / "config.yaml"
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)
    return config["database"]


def get_engine():
    global _engine
    if _engine is None:
        db = get_db_config()
        _engine = create_engine(
            f"postgresql+psycopg2://{db['user']}:{db['password']}@"
            f"{db['host']}:{db['port']}/{db['name']}",
            pool_pre_ping=True,
            future=True,
        )
    return _engine


def get_session():
    global _SessionLocal
    if _SessionLocal is None:
        _SessionLocal = sessionmaker(
            bind=get_engine(),
            autocommit=False,
            autoflush=False,
            future=True,
        )
    return _SessionLocal()
