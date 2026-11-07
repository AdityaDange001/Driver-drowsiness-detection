
import os
import json
import sqlite3

from flask import Flask, render_template_string

app = Flask(__name__)

DATABASE_PATH = "drowsiness.db"
STATUS_PATH = "system_status.json"

HTML_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta http-equiv="refresh" content="5">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">

    <title>Driver Drowsiness Dashboard</title>

    <style>
        * {
            box-sizing: border-box;
        }

        body {
            margin: 0;
            padding: 25px;
            font-family: Arial, sans-serif;
            background: #f1f5f9;
            color: #172033;
        }

        h1 {
            text-align: center;
            margin-bottom: 8px;
        }

        .subtitle {
            text-align: center;
            color: #64748b;
            margin-bottom: 30px;
        }

        .cards {
            display: grid;
            grid-template-columns: repeat(
                auto-fit, minmax(210px, 1fr)
            );
            gap: 18px;
            max-width: 1100px;
            margin: auto;
        }

        .card {
            background: white;
            padding: 24px;
            border-radius: 14px;
            box-shadow: 0 3px 12px #00000010;
            overflow-wrap: anywhere;
        }

        .card h3 {
            color: #64748b;
            font-size: 15px;
        }

        .number {
            font-size: 30px;
            font-weight: bold;
        }

        .red {
            color: #dc2626;
        }

        .orange {
            color: #ea580c;
        }

        .green {
            color: #15803d;
        }

        .history {
            max-width: 1100px;
            margin: 25px auto;
            padding: 24px;
            background: white;
            border-radius: 14px;
            overflow-x: auto;
        }

        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 15px;
        }

        th, td {
            text-align: left;
            padding: 13px;
            border-bottom: 1px solid #e2e8f0;
        }

        th {
            background: #f8fafc;
        }

        .footer {
            text-align: center;
            color: #64748b;
            margin-top: 25px;
            font-size: 13px;
        }
    </style>
</head>

<body>
    <h1>Driver Drowsiness Detection</h1>
    <p class="subtitle">
        Monitoring Dashboard | Auto-refresh every 5 seconds
    </p>

    <div class="cards">

        <div class="card">
            <h3>Current Detection Status</h3>
            <div class="number">{{ live_status.status }}</div>
            <p>Last Updated: {{ live_status.updated_at }}</p>
        </div>

        <div class="card">
            <h3>Total Drowsiness Warnings</h3>
            <div class="number red">{{ drowsiness_count }}</div>
        </div>

        <div class="card">
            <h3>Total Yawning Events</h3>
            <div class="number orange">{{ yawning_count }}</div>
        </div>

        <div class="card">
            <h3>Total Recorded Events</h3>
            <div class="number green">{{ total_events }}</div>
        </div>

    </div>

    <div class="history">
        <h2>Recent Event History</h2>

        {% if events %}
        <table>
            <thead>
                <tr>
                    <th>ID</th>
                    <th>Event Type</th>
                    <th>Date &amp; Time</th>
                </tr>
            </thead>

            <tbody>
                {% for event in events %}
                <tr>
                    <td>{{ event[0] }}</td>
                    <td>{{ event[1] }}</td>
                    <td>{{ event[2] }}</td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
        {% else %}
        <p>No events recorded yet.</p>
        {% endif %}
    </div>

    <p class="footer">
        Student project prototype • Refreshes every 5 seconds
    </p>
</body>
</html>
"""


def get_dashboard_data():
    connection = sqlite3.connect(DATABASE_PATH)

    try:
        cursor = connection.cursor()

        cursor.execute("""
            SELECT id, event_type, event_time
            FROM events
            ORDER BY id DESC
            LIMIT 100
        """)
        events = cursor.fetchall()

        cursor.execute("""
            SELECT COUNT(*) FROM events
            WHERE event_type = 'Drowsiness Warning'
        """)
        drowsiness_count = cursor.fetchone()[0]

        cursor.execute("""
            SELECT COUNT(*) FROM events
            WHERE event_type = 'Yawning Detected'
        """)
        yawning_count = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM events")
        total_events = cursor.fetchone()[0]

        return (
            events,
            drowsiness_count,
            yawning_count,
            total_events
        )
    finally:
        connection.close()


def get_live_status():
    default_status = {
        "status": "Waiting for detection",
        "updated_at": "Not started"
    }

    if not os.path.exists(STATUS_PATH):
        return default_status

    try:
        with open(STATUS_PATH, "r", encoding="utf-8") as file:
            data = json.load(file)

        if isinstance(data, dict):
            default_status.update(data)

        return default_status

    except (json.JSONDecodeError, OSError):
        return default_status


@app.route("/")
def dashboard():
    (
        events,
        drowsiness_count,
        yawning_count,
        total_events
    ) = get_dashboard_data()

    live_status = get_live_status()

    return render_template_string(
        HTML_PAGE,
        events=events,
        drowsiness_count=drowsiness_count,
        yawning_count=yawning_count,
        total_events=total_events,
        live_status=live_status
    )


if __name__ == "__main__":
    print("Dashboard starting...")
    print("Open http://127.0.0.1:5000 in your browser")

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=False
    )
