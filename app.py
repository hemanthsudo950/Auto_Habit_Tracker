from flask import Flask, render_template, request, redirect, jsonify
import sqlite3
import datetime
import threading
import time
import winsound  # For sound alarm

app = Flask(__name__)
DB_FILE = 'habits.db'


# --- Initialize Database ---
def init_db():
    with sqlite3.connect(DB_FILE) as conn:
        conn.execute('''CREATE TABLE IF NOT EXISTS habits (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            name TEXT NOT NULL,
                            status TEXT DEFAULT 'Pending',
                            time_period TEXT,
                            reminder_time TEXT
                        )''')
        conn.commit()


# --- Default habits with auto reminder times ---
DEFAULT_HABITS = {
    "morning": [
        ("Exercise", "06:30"),
        ("Drink Water", "07:00"),
        ("Cycling", "07:30")
    ],
    "afternoon": [
        ("Read Book", "13:00"),
        ("Lunch", "12:30"),
        ("Time to Rest", "14:30")
    ],
    "night": [
        ("Dinner", "20:00"),
        ("Drink Water", "21:00"),
        ("Sleep Early", "22:30")
    ]
}


# --- Insert default habits if missing ---
def add_default_habits():
    with sqlite3.connect(DB_FILE) as conn:
        cur = conn.cursor()
        for period, habits in DEFAULT_HABITS.items():
            for habit_name, time_str in habits:
                cur.execute("SELECT * FROM habits WHERE name=? AND time_period=?", (habit_name, period))
                if not cur.fetchone():
                    cur.execute(
                        "INSERT INTO habits (name, time_period, reminder_time) VALUES (?, ?, ?)",
                        (habit_name, period, time_str)
                    )
        conn.commit()


# --- Alarm sound ---
def play_alarm():
    try:
        winsound.Beep(1200, 800)
    except:
        print("Alarm sound unavailable")


# --- Background reminder checker ---
def reminder_loop():
    while True:
        now = datetime.datetime.now().strftime("%H:%M")

        with sqlite3.connect(DB_FILE) as conn:
            cur = conn.cursor()
            cur.execute("SELECT id, name, reminder_time FROM habits WHERE reminder_time IS NOT NULL AND status='Pending'")
            reminders = cur.fetchall()

        for habit_id, habit_name, reminder_time in reminders:
            if reminder_time == now:
                print(f"🔔 Reminder: Time for '{habit_name}'!")
                play_alarm()

        time.sleep(60)


# --- ROUTES ---
@app.route('/')
def home():
    add_default_habits()
    with sqlite3.connect(DB_FILE) as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM habits ORDER BY id ASC")
        habits = cur.fetchall()
    return render_template('index.html', habits=habits)


@app.route('/add', methods=['POST'])
def add_habit():
    name = request.form.get('habit')
    time_str = request.form.get('time')

    if not name or not name.strip():
        return jsonify({'success': False, 'error': 'Habit name cannot be empty'}), 400

    try:
        with sqlite3.connect(DB_FILE) as conn:
            conn.execute("INSERT INTO habits (name, time_period, reminder_time) VALUES (?, ?, ?)",
                         (name, "custom", time_str))
            conn.commit()
        return jsonify({'success': True, 'message': f'Habit "{name}" added successfully!'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/complete/<int:habit_id>', methods=['POST'])
def complete_habit(habit_id):
    with sqlite3.connect(DB_FILE) as conn:
        conn.execute("UPDATE habits SET status='Completed' WHERE id=?", (habit_id,))
        conn.commit()
    return jsonify(success=True)


# --- DELETE habit endpoint ---
@app.route('/delete/<int:habit_id>', methods=['POST'])
def delete_habit(habit_id):
    with sqlite3.connect(DB_FILE) as conn:
        conn.execute("DELETE FROM habits WHERE id=?", (habit_id,))
        conn.commit()
    return jsonify({'success': True})

# --- Run App ---
if __name__ == '__main__':
    init_db()
    add_default_habits()
    threading.Thread(target=reminder_loop, daemon=True).start()
    app.run(debug=True)
