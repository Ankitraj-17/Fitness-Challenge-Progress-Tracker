from datetime import datetime

from fitness_utils import append_activity_rows, compute_trend, load_activity_logs, load_summary, save_summary, summarize_by_period


class Participant:
    def __init__(self, name):
        self.name = name
        self.activity_log = sorted([e for e in load_activity_logs() if e["name"] == name], key=lambda e: e["date"])
        self._unsaved = []

    def log_activity(self, steps, exercise, calories, date=None):
        entry = {"name": self.name, "date": date or datetime.now().strftime("%Y-%m-%d"), "steps": int(steps), "exercise": exercise, "calories": float(calories)}
        self.activity_log.append(entry); self._unsaved.append(entry)
        print(f"✓ {self.name}: {steps} steps, {exercise}, {calories} cal")

    def calculate_progress(self):
        if not self.activity_log:
            return {"name": self.name, "total_steps": 0, "total_calories": 0.0, "average_daily_steps": 0, "records": 0, "trend": {"change": 0, "percent_change": 0.0}}
        steps = [e["steps"] for e in self.activity_log]; calories = [e["calories"] for e in self.activity_log]
        best = max(self.activity_log, key=lambda e: e["steps"])
        return {
            "name": self.name,
            "total_steps": sum(steps),
            "total_calories": round(sum(calories), 2),
            "average_daily_steps": int(sum(steps) / len(steps)),
            "records": len(self.activity_log),
            "best_day": {"date": best["date"], "steps": best["steps"]},
            "trend": compute_trend(steps),
        }

    def show_stats(self):
        s = self.calculate_progress()
        print(f"\n{self.name}: {s['total_steps']} steps, avg {s['average_daily_steps']}/day, best {s['best_day']['date']} ({s['best_day']['steps']} steps)")
        t = s["trend"]; print(f"Trend: {t['change']} steps ({t['percent_change']}%)")
        wk, mo = self.weekly_stats(), self.monthly_stats()
        if wk: lw = sorted(wk)[-1]; print(f"Latest week {lw}: {wk[lw]['steps']} steps")
        if mo: lm = sorted(mo)[-1]; print(f"Latest month {lm}: {mo[lm]['steps']} steps")

    def weekly_stats(self):
        return summarize_by_period(self.activity_log, "week")

    def monthly_stats(self):
        return summarize_by_period(self.activity_log, "month")

    def export_data(self):
        if self._unsaved:
            append_activity_rows(self._unsaved); self._unsaved = []
        summary = load_summary(); summary[self.name] = self.calculate_progress(); save_summary(summary)
