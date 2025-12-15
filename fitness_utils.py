import csv, json
from collections import Counter, defaultdict
from datetime import datetime
from functools import wraps
from pathlib import Path

import matplotlib.pyplot as plt

DATA_DIR = Path(__file__).parent
ACTIVITY_FILE, SUMMARY_FILE = DATA_DIR / "activity_logs.csv", DATA_DIR / "participant_summary.json"

def ensure_storage():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if not ACTIVITY_FILE.exists() or ACTIVITY_FILE.stat().st_size == 0:
        with open(ACTIVITY_FILE, "w", newline="") as f:
            csv.writer(f).writerow(["name", "date", "steps", "exercise", "calories"])
    SUMMARY_FILE.touch(exist_ok=True)

def validate_entry(func):
    @wraps(func)
    def wrapper(name, steps, exercise, calories, *a, **k):
        if not str(name).strip() or steps < 0 or calories < 0:
            raise ValueError("Invalid entry: name required, steps/calories >=0")
        return func(name, steps, exercise, calories, *a, **k)
    return wrapper

summarize_daily_steps = lambda steps: sum(steps) if steps else 0  # noqa: E731
aggregate_activities = lambda ps: [e for p in ps for e in getattr(p, "activity_log", [])]  # noqa: E731

def load_activity_logs():
    ensure_storage()
    out = []
    with open(ACTIVITY_FILE, newline="") as f:
        for r in csv.DictReader(f):
            try:
                out.append(
                    {
                        "name": r["name"],
                        "date": r.get("date") or datetime.now().strftime("%Y-%m-%d"),
                        "steps": int(r.get("steps", 0)),
                        "exercise": r.get("exercise", ""),
                        "calories": float(r.get("calories", 0)),
                    }
                )
            except (TypeError, ValueError):
                continue
    return out

def append_activity_rows(rows):
    ensure_storage()
    with open(ACTIVITY_FILE, "a", newline="") as f:
        csv.writer(f).writerows([[r["name"], r["date"], r["steps"], r["exercise"], r["calories"]] for r in rows])

def load_summary():
    ensure_storage()
    try:
        return json.loads(SUMMARY_FILE.read_text() or "{}")
    except json.JSONDecodeError:
        return {}

def save_summary(summary):
    ensure_storage(); SUMMARY_FILE.write_text(json.dumps(summary, indent=2))

def summarize_by_period(logs, period):
    buckets = defaultdict(lambda: {"steps": 0, "calories": 0, "entries": 0})
    for e in logs:
        try:
            d = datetime.strptime(e["date"], "%Y-%m-%d").date()
        except ValueError:
            continue
        key = f"{d.isocalendar().year}-W{d.isocalendar().week:02d}" if period == "week" else f"{d.year}-{d.month:02d}"
        buckets[key]["steps"] += e["steps"]; buckets[key]["calories"] += e["calories"]; buckets[key]["entries"] += 1
    for v in buckets.values():
        v["average_steps"] = int(v["steps"] / v["entries"]) if v["entries"] else 0
    return dict(buckets)

def compute_trend(steps):
    if len(steps) < 2:
        return {"change": 0, "percent_change": 0.0}
    change = steps[-1] - steps[0]
    return {"change": change, "percent_change": round((change / steps[0] * 100) if steps[0] else 0.0, 2)}

def plot_progress(participant):
    if not participant.activity_log:
        print("No activity to plot yet."); return
    try:
        steps = [e["steps"] for e in participant.activity_log]
        dates = [e["date"] for e in participant.activity_log]
        counts = Counter(e["exercise"] for e in participant.activity_log)
        plt.figure(figsize=(12, 5))
        plt.subplot(1, 2, 1); plt.plot(dates, steps, "b-o"); plt.xticks(rotation=45, ha="right"); plt.ylabel("Steps"); plt.xlabel("Date"); plt.title("Progress Over Time")
        plt.subplot(1, 2, 2); plt.bar(counts.keys(), counts.values(), color="orange"); plt.ylabel("Count"); plt.xlabel("Exercise Type"); plt.title("Activity Counts by Type")
        plt.tight_layout(); plt.show()
    except Exception as e:
        print(f"Error displaying plot: {e}\nCheck matplotlib backend.")
