import os
import pandas as pd
import logging
from sqlalchemy import create_engine,text
from sqlalchemy.types import DateTime, Date
from dotenv import load_dotenv
import airportsdata

# Load environment variables
ENV_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".env"))
load_dotenv(ENV_PATH)

# Get DB credentials from .env
DB_USER = os.getenv("POSTGRES_USER")
DB_PASS = os.getenv("POSTGRES_PASSWORD")
DB_HOST = os.getenv("POSTGRES_HOST")
DB_PORT = os.getenv("POSTGRES_PORT", "5432")
DB_NAME = os.getenv("POSTGRES_DB")


# Connection string
DATABASE_URL = f"postgresql+psycopg2://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
SCHEMA = "public"


def push_fligth_schedule_to_postgres(df: pd.DataFrame = None, csv_path: str = None):
    logger = logging.getLogger("schedule")

    DESIRED_COLUMNS = [
        "flight_date", "flight_date_utc", "flight_number_iata", "flight_number_icao",
        "tail_number", "airline", "status", "depart_from", "depart_from_iata",
        "depart_from_icao", "scheduled_departure_local", "scheduled_departure_local_tz",
        "scheduled_departure_utc", "actual_departure_local", "actual_departure_local_tz",
        "actual_departure_utc", "arrive_at", "arrive_at_iata", "arrive_at_icao",
        "scheduled_arrival_local", "scheduled_arrival_local_tz", "scheduled_arrival_utc",
        "actual_arrival_local", "actual_arrival_local_tz", "actual_arrival_utc", "duration"
    ]

    TABLE_NAME = "flight_schedule"

    if df is None:
        if not csv_path or not os.path.exists(csv_path):
            logger.error("No DataFrame or CSV provided.")
            return
        logger.info("Reading CSV from: %s", csv_path)
        df = pd.read_csv(csv_path)

    # Keep only necessary columns
    df = df[[col for col in DESIRED_COLUMNS if col in df.columns]]

    # Convert datetime columns
    for col in df.columns:
        if "date" in col or "time" in col:
            df[col] = pd.to_datetime(df[col], errors="coerce")

    # Define SQLAlchemy type mapping
    dtype_mapping = {
        "flight_date": Date(),
        "flight_date_utc": Date(),
        "scheduled_departure_local": DateTime(),
        "scheduled_departure_utc": DateTime(),
        "actual_departure_local": DateTime(),
        "actual_departure_utc": DateTime(),
        "scheduled_arrival_local": DateTime(),
        "scheduled_arrival_utc": DateTime(),
        "actual_arrival_local": DateTime(),
        "actual_arrival_utc": DateTime()
    }

    logger.info("Connecting to PostgreSQL...")
    engine = create_engine(DATABASE_URL)

    with engine.begin() as conn:
        db_name = conn.execute(text("SELECT current_database()")).scalar()
        schema_name = conn.execute(text("SELECT current_schema()")).scalar()
        logger.info("Connected to DB: %s | Schema: %s", db_name, schema_name)

        logger.info("Creating table '%s.%s' if not exists...", SCHEMA, TABLE_NAME)
        conn.execute(text(f"""
        CREATE TABLE IF NOT EXISTS {SCHEMA}.{TABLE_NAME} (
            flight_date DATE,
            flight_date_utc DATE,
            flight_number_iata TEXT,
            flight_number_icao TEXT,
            tail_number TEXT,
            airline TEXT,
            status TEXT,
            depart_from TEXT,
            depart_from_iata TEXT,
            depart_from_icao TEXT,
            scheduled_departure_local TIMESTAMP,
            scheduled_departure_local_tz TEXT,
            scheduled_departure_utc TIMESTAMP,
            actual_departure_local TIMESTAMP,
            actual_departure_local_tz TEXT,
            actual_departure_utc TIMESTAMP,
            arrive_at TEXT,
            arrive_at_iata TEXT,
            arrive_at_icao TEXT,
            scheduled_arrival_local TIMESTAMP,
            scheduled_arrival_local_tz TEXT,
            scheduled_arrival_utc TIMESTAMP,
            actual_arrival_local TIMESTAMP,
            actual_arrival_local_tz TEXT,
            actual_arrival_utc TIMESTAMP,
            duration TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (flight_date_utc, flight_number_iata, airline, depart_from_iata, arrive_at_iata, scheduled_departure_utc, scheduled_arrival_utc)
        );
        """))

        temp_table_name = f"temp_{TABLE_NAME}"
        logger.info("Creating and populating temp table '%s.%s'...", SCHEMA, temp_table_name)
        df.to_sql(
            name=temp_table_name,
            con=engine,
            schema=SCHEMA,
            if_exists="replace",
            index=False,
            method="multi",
            chunksize=5000,
            dtype=dtype_mapping
        )

        logger.info("Performing UPSERT...")
        upsert_sql = f"""
        INSERT INTO {SCHEMA}.{TABLE_NAME} ({", ".join(DESIRED_COLUMNS)})
        SELECT {", ".join(DESIRED_COLUMNS)} FROM {SCHEMA}.{temp_table_name}
        ON CONFLICT (flight_date_utc, flight_number_iata, airline, depart_from_iata, arrive_at_iata, scheduled_departure_utc, scheduled_arrival_utc)
        DO UPDATE SET
            tail_number = EXCLUDED.tail_number,
            airline = EXCLUDED.airline,
            status = EXCLUDED.status,
            actual_departure_local = EXCLUDED.actual_departure_local,
            actual_departure_local_tz = EXCLUDED.actual_departure_local_tz,
            actual_departure_utc = EXCLUDED.actual_departure_utc,
            actual_arrival_local = EXCLUDED.actual_arrival_local,
            actual_arrival_local_tz = EXCLUDED.actual_arrival_local_tz,
            actual_arrival_utc = EXCLUDED.actual_arrival_utc,
            duration = EXCLUDED.duration,
            updated_at = CURRENT_TIMESTAMP
        """
        conn.execute(text(upsert_sql))

        logger.info("Dropping temp table '%s.%s'...", SCHEMA, temp_table_name)
        conn.execute(text(f"DROP TABLE IF EXISTS {SCHEMA}.{temp_table_name};"))

    logger.info("Upsert complete: %d rows into '%s.%s'", len(df), SCHEMA, TABLE_NAME)


def push_airports_to_postgress():
    # Target table
    TABLE_NAME = "airports"
    # Load airport data using IATA codes
    airports = airportsdata.load('IATA')

    # Convert the nested dictionary into a DataFrame
    df = pd.DataFrame.from_dict(airports, orient='index')

    engine = create_engine(DATABASE_URL)

    with engine.begin() as conn:
        df.to_sql(
            name=TABLE_NAME,
            con=engine,
            schema=SCHEMA,
            if_exists="replace",
            index=False
        )

    print(f"Data pushed to table '{TABLE_NAME}' in database '{DB_NAME}' successfully!")
   