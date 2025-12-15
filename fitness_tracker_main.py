from participant_class import Participant
from fitness_utils import aggregate_activities, ensure_storage, load_activity_logs, plot_progress, summarize_daily_steps, validate_entry

participants = {}

def bootstrap_from_history():
    ensure_storage()
    for name in {e["name"] for e in load_activity_logs()}:
        participants[name] = Participant(name)

@validate_entry
def log(name, steps, exercise, calories):
    if name not in participants:
        participants[name] = Participant(name); print(f"✓ Added {name}")
    participants[name].log_activity(steps, exercise, calories); participants[name].export_data(); print("✓ Saved")

def pick_name():
    return input("Name: ").strip()

def list_participants():
    print("Participants:", ", ".join(sorted(participants)) or "none")

def summarize_all():
    if not participants: print("No data."); return
    steps = [e["steps"] for e in aggregate_activities(participants.values())]
    print(f"Total steps all participants: {summarize_daily_steps(steps)}")

def main():
    bootstrap_from_history()
    menu = "\n1 Add  2 Log  3 Stats  4 Plot  5 List  6 Summary  7 Exit\nChoice: "
    while True:
        c = input(menu).strip()
        if c == "1":
            n = pick_name()
            if not n: print("Name cannot be empty"); continue
            if n in participants: print("Exists"); continue
            participants[n] = Participant(n); participants[n].export_data(); print("✓ Added")
        elif c == "2":
            n = pick_name()
            try:
                steps = int(input("Steps: ")); calories = float(input("Calories: "))
            except ValueError:
                print("Steps int, calories number."); continue
            ex = input("Exercise: ").strip()
            try: log(n, steps, ex, calories)
            except ValueError as e: print(f"Invalid: {e}")
        elif c == "3":
            n = pick_name(); participants[n].show_stats() if n in participants else print("Not found")
        elif c == "4":
            n = pick_name(); plot_progress(participants[n]) if n in participants else print("Not found")
        elif c == "5":
            list_participants()
        elif c == "6":
            summarize_all()
        elif c == "7":
            break
        else:
            print("Choose 1-7")

if __name__ == "__main__":
    main()
