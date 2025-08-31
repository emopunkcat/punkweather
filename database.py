# database.py

import sqlalchemy as db
from datetime import datetime, timedelta

DATABASE_NAME = 'weather.db'
engine = db.create_engine(f'sqlite:///{DATABASE_NAME}')
metadata = db.MetaData()

# Define the table structure with the new column
weather_log = db.Table('weather_log', metadata,
    db.Column('id', db.Integer, primary_key=True),
    db.Column('timestamp', db.DateTime, nullable=False),
    db.Column('temperature', db.Float, nullable=False),
    db.Column('feels_like', db.Float, nullable=False),
    db.Column('might_rain_today', db.Boolean, nullable=False) # New column
)

def init_db():
    metadata.create_all(engine)

# Update this function to accept the new `rain_forecast` parameter
def add_weather_log(conn, temp, feels_like, rain_forecast):
    query = db.insert(weather_log).values(
        timestamp=datetime.now(),
        temperature=temp,
        feels_like=feels_like,
        might_rain_today=rain_forecast # Insert the new value
    )
    conn.execute(query)
    conn.commit()

# --- (The rest of the file, get_latest_weather and get_daily_trends, remains unchanged) ---
def get_latest_weather(conn):
    query = db.select(weather_log).order_by(db.desc('timestamp')).limit(1)
    result = conn.execute(query).fetchone()
    return result._asdict() if result else None

def get_daily_trends(conn, days=90):
    time_threshold = datetime.now() - timedelta(days=days)
    query = db.select(
        db.func.date(weather_log.c.timestamp).label('date'),
        db.func.avg(weather_log.c.temperature).label('avg_temp'),
        db.func.max(weather_log.c.temperature).label('max_temp'),
        db.func.min(weather_log.c.temperature).label('min_temp')
    ).where(
        weather_log.c.timestamp >= time_threshold
    ).group_by(
        db.func.date(weather_log.c.timestamp)
    ).order_by(
        db.func.date(weather_log.c.timestamp)
    )
    results = conn.execute(query).fetchall()
    return [row._asdict() for row in results]

def get_all_logs(conn):
    """Gets all weather readings from the database, newest first."""
    query = db.select(weather_log).order_by(db.desc('timestamp'))
    results = conn.execute(query).fetchall()
    return [row._asdict() for row in results]