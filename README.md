# 🌿 Automatic Habit Tracker

A simple Flask + SQLite web app for tracking daily habits, with default morning/afternoon/night routines, custom habit creation, and time-based reminders (both server-side beeps and in-browser popup notifications).

![Python](https://img.shields.io/badge/python-3.x-blue)
![Flask](https://img.shields.io/badge/flask-web%20app-black)
![SQLite](https://img.shields.io/badge/database-SQLite-lightgrey)

## Features

- ✅ Add, complete, and delete habits
- ⏰ Set a reminder time for any habit
- 🌅 Comes preloaded with default morning, afternoon, and night habits
- 🔔 Background thread checks reminder times and plays an audio alarm
- 💻 In-browser popup + toast notifications when a habit's time comes up
- 📊 Live stats (total / completed habits)
- 🎨 Clean, animated UI with a welcome screen on first visit

## Tech Stack

- **Backend:** Python, Flask
- **Database:** SQLite (`habits.db`)
- **Frontend:** HTML, CSS, vanilla JavaScript (Font Awesome for icons)

## Project Structure

Flask expects templates and static files in specific folders. Arrange the project like this:

```
habit-tracker/
├── app.py
├── habits.db          # created automatically on first run
├── templates/
│   └── index.html
└── static/
    ├── style.css
    └── beep-125033.mp3
```

> **Note:** `index.html` must go in a `templates/` folder and `style.css` must go in a `static/` folder for Flask's `render_template` and `url_for('static', ...)` to find them.

## Getting Started

### Prerequisites

- Python 3.7+
- pip

### Installation

1. Clone the repo:
   ```bash
   git clone https://github.com/<your-username>/habit-tracker.git
   cd habit-tracker
   ```

2. Install dependencies:
   ```bash
   pip install flask
   ```

3. Make sure the folder structure above is in place (move `index.html` into `templates/`, and `style.css` / `beep-125033.mp3` into `static/`).

4. Run the app:
   ```bash
   python app.py
   ```

5. Open your browser to:
   ```
   http://127.0.0.1:5000
   ```

The SQLite database (`habits.db`) and default habits are created automatically the first time the app runs.

## ⚠️ Windows-only alarm sound

The background reminder loop currently uses Python's built-in `winsound` module to play an audible beep, which **only works on Windows**. On macOS/Linux, `app.py` will fail to import.

If you want this to run cross-platform, replace the `winsound` import and `play_alarm()` function with something portable, e.g. [`playsound`](https://pypi.org/project/playsound/) or `pygame.mixer`, and point it at `static/beep-125033.mp3`:

```python
from playsound import playsound

def play_alarm():
    try:
        playsound('static/beep-125033.mp3')
    except Exception:
        print("Alarm sound unavailable")
```

(You'll also need `pip install playsound`.)

## How Reminders Work

- **Server-side:** a background thread checks every 60 seconds whether the current time matches any pending habit's `reminder_time`, and plays a system beep if so.
- **Client-side:** the page independently polls every 60 seconds and shows an in-browser popup + plays a WebAudio beep when a habit's time is reached, using `localStorage` to avoid repeating the same popup twice in one day.

## Routes

| Route | Method | Description |
|---|---|---|
| `/` | GET | Home page, loads/display habits |
| `/add` | POST | Add a new habit (`habit`, `time` form fields) |
| `/complete/<id>` | POST | Mark a habit as completed |
| `/delete/<id>` | POST | Delete a habit |
