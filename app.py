import atexit
from flask import Flask, render_template, jsonify
from apscheduler.schedulers.background import BackgroundScheduler
import database as db
from weather import fetch_and_log_weather, celsius_to_fahrenheit

# --- App Setup ---
app = Flask(__name__)
db.init_db()

# --- Routes ---
@app.route('/')
def home():
    """Serves the homepage with the latest data and chart trends."""
    with db.engine.connect() as connection:
        latest = db.get_latest_weather(connection)
        trends = db.get_daily_trends(connection, days=90)

    # Process latest data for display card
    weather_card_data = None
    if latest:
        weather_card_data = {
            "city": "Raleigh",
            "timestamp": latest['timestamp'].strftime("%Y-%m-%d %H:%M:%S"),
            "temperature": f"{celsius_to_fahrenheit(latest['temperature']):.1f}°F",
            "feels_like": f"{celsius_to_fahrenheit(latest['feels_like']):.1f}°F",
        }

    # Process daily trend data for the chart
    chart_data = {
        "labels": [t['date'] for t in trends],
        "avg_temps": [round(celsius_to_fahrenheit(t['avg_temp']), 2) for t in trends],
        "max_temps": [round(celsius_to_fahrenheit(t['max_temp']), 2) for t in trends],
        "min_temps": [round(celsius_to_fahrenheit(t['min_temp']), 2) for t in trends],
    }
    
    return render_template('index.html', weather=weather_card_data, chart_data=chart_data)

@app.route('/history')
def history_page():
    """Serves an HTML page with all historical data in a table."""
    with db.engine.connect() as connection:
        all_logs = db.get_all_logs(connection)
    
    # Convert temperatures to Fahrenheit for display
    for log in all_logs:
        log['temperature'] = celsius_to_fahrenheit(log['temperature'])
        log['feels_like'] = celsius_to_fahrenheit(log['feels_like'])
        
    return render_template('history.html', logs=all_logs)

# --- API Endpoints ---
@app.route('/api/weather')
def api_weather():
    """Serves the latest weather reading as JSON."""
    with db.engine.connect() as connection:
        latest = db.get_latest_weather(connection)
    
    if latest:
        latest['temperature'] = round(celsius_to_fahrenheit(latest['temperature']), 2)
        latest['feels_like'] = round(celsius_to_fahrenheit(latest['feels_like']), 2)
        latest['timestamp'] = latest['timestamp'].isoformat() # Use ISO format for APIs
        return jsonify(latest)
    else:
        return jsonify({"error": "Weather data not available"}), 503

@app.route('/api/simple')
def api_simple():
    """Serves just the current temp and rain forecast."""
    with db.engine.connect() as connection:
        latest = db.get_latest_weather(connection)
    
    if latest:
        response_data = {
            "current_temperature": f"{celsius_to_fahrenheit(latest['temperature']):.1f}°F",
            "might_rain_today": latest['might_rain_today']
        }
        return jsonify(response_data)
    else:
        return jsonify({"error": "Weather data not available"}), 503

@app.route('/api/db/all')
def api_get_all_data():
    """Serves all historical data from the database."""
    with db.engine.connect() as connection:
        all_logs = db.get_all_logs(connection)
    
    # Convert datetime objects to strings for JSON serialization
    for log in all_logs:
        log['timestamp'] = log['timestamp'].isoformat()
        
    return jsonify(all_logs)

# --- Scheduler Setup for Production (Gunicorn) ---
print("Starting scheduler...")
# Fetch data immediately on startup to populate the DB
fetch_and_log_weather()
    
# Configure and start the background scheduler
scheduler = BackgroundScheduler()
scheduler.add_job(func=fetch_and_log_weather, trigger="interval", minutes=5)
scheduler.start()

# Ensure the scheduler is shut down when the app exits
atexit.register(lambda: scheduler.shutdown())