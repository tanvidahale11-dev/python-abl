"""
==========================================================
 BIRTHDAY REMINDER SYSTEM  -  PHASE 2 (Utility Assessment-II)
 Student : Tanvi Dahale          USN : CD26D015
 Guide   : Ms. Ashwini Yerlekar
 Course  : Python Programming Lab (Experiential Learning)
 Scope   : Module development + FILE HANDLING (JSON),
           input validation, duplicate check, delete, sort
==========================================================
Run demo       :  python phase2.py
Run menu (own) :  python phase2.py --menu
"""
import json
import os
import sys
from datetime import date, datetime, timedelta

DATE_FMT = "%d-%m-%Y"
FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "birthdays_phase2.json")


# ---------------------------------------------------------------- MODULE 1 : date logic
def next_birthday(dob, today):
    year = today.year
    while True:
        try:
            nb = dob.replace(year=year)
        except ValueError:              # 29 Feb in non-leap year
            nb = date(year, 2, 28)
        if nb >= today:
            return nb
        year += 1


def days_left(record, today):
    dob = datetime.strptime(record["dob"], DATE_FMT).date()
    return (next_birthday(dob, today) - today).days


# ---------------------------------------------------------------- MODULE 2 : file handling
def load_data():
    """Read records from the JSON file (empty list if file missing/corrupt)."""
    try:
        with open(FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return []
    except json.JSONDecodeError:
        print("  [!] File is corrupted. Starting with an empty list.")
        return []


def save_data(records):
    """Write all records permanently to the JSON file."""
    with open(FILE, "w", encoding="utf-8") as f:
        json.dump(records, f, indent=4)


# ---------------------------------------------------------------- MODULE 3 : validation
def is_valid_name(name):
    return len(name.strip()) >= 2 and all(c.isalpha() or c in " .'-" for c in name)


def parse_date(text):
    """Return a date object or None if text is not a valid, non-future DD-MM-YYYY date."""
    try:
        d = datetime.strptime(text, DATE_FMT).date()
    except ValueError:
        return None
    return d if d <= date.today() else None


# ---------------------------------------------------------------- MODULE 4 : operations
def add_birthday(records, name, dob_text, relation="Friend"):
    if not is_valid_name(name):
        print(f"  [x] Invalid name: '{name}'")
        return False
    if parse_date(dob_text) is None:
        print(f"  [x] Invalid date for {name}: '{dob_text}' (use DD-MM-YYYY, not in future)")
        return False
    if any(r["name"].lower() == name.lower() for r in records):
        print(f"  [x] Duplicate entry: {name} already exists")
        return False
    records.append({"name": name.strip(), "dob": dob_text, "relation": relation})
    save_data(records)                  # saved immediately -> permanent
    print(f"  [+] Added & saved : {name} ({dob_text}) - {relation}")
    return True


def delete_birthday(records, name):
    for r in records:
        if r["name"].lower() == name.lower():
            records.remove(r)
            save_data(records)
            print(f"  [-] Deleted & saved : {r['name']}")
            return True
    print(f"  [x] '{name}' not found")
    return False


def search_birthday(records, keyword):
    k = keyword.lower()
    return [r for r in records if k in r["name"].lower() or k in r["relation"].lower()]


def view_all(records, today):
    """Show records sorted by the nearest upcoming birthday."""
    print(f"\n  {'No':<4}{'Name':<16}{'DOB':<13}{'Relation':<11}{'Days Left'}")
    print("  " + "-" * 54)
    for i, r in enumerate(sorted(records, key=lambda r: days_left(r, today)), 1):
        print(f"  {i:<4}{r['name']:<16}{r['dob']:<13}{r['relation']:<11}{days_left(r, today)}")


def upcoming(records, days, today):
    return sorted([(r, days_left(r, today)) for r in records if days_left(r, today) <= days],
                  key=lambda x: x[1])


# ---------------------------------------------------------------- MODULE 5 : user interface
def menu():
    records = load_data()
    today = date.today()
    while True:
        print("\n===== BIRTHDAY REMINDER (Phase 2) =====")
        print("1.Add  2.View all  3.Search  4.Delete  5.Upcoming  6.Exit")
        ch = input("Enter choice: ").strip()
        if ch == "1":
            add_birthday(records, input("Name: "), input("DOB (DD-MM-YYYY): "), input("Relation: ") or "Friend")
        elif ch == "2":
            view_all(records, today)
        elif ch == "3":
            for r in search_birthday(records, input("Search: ")):
                print("  ", r["name"], r["dob"], r["relation"])
        elif ch == "4":
            delete_birthday(records, input("Name to delete: "))
        elif ch == "5":
            for r, d in upcoming(records, int(input("Within days: ") or 7), today):
                print(f"   {r['name']} in {d} day(s)")
        elif ch == "6":
            print("Goodbye!")
            break
        else:
            print("  Invalid choice")


# ---------------------------------------------------------------- DEMO (runs in one go)
def dob_in(days_ahead, birth_year, today):
    t = today + timedelta(days=days_ahead)
    try:
        return t.replace(year=birth_year).strftime(DATE_FMT)
    except ValueError:
        return t.replace(year=birth_year, day=28).strftime(DATE_FMT)


def demo():
    today = date.today()
    if os.path.exists(FILE):
        os.remove(FILE)                 # fresh start for the demo only
    print("=" * 62)
    print("   BIRTHDAY REMINDER SYSTEM - PHASE 2 (File Handling)")
    print("   Today's date :", today.strftime("%d-%m-%Y (%A)"))
    print("=" * 62)

    records = load_data()
    print("\n[1] Adding records (each one is saved to the file)")
    add_birthday(records, "Aarav Sharma", dob_in(0, 2005, today), "Friend")
    add_birthday(records, "Priya Dahale", dob_in(3, 1978, today), "Family")
    add_birthday(records, "Rohan Patil", dob_in(6, 2004, today), "Classmate")
    add_birthday(records, "Neha Joshi", dob_in(20, 2003, today), "Friend")
    add_birthday(records, "Mr. Deshmukh", dob_in(150, 1975, today), "Colleague")

    print("\n[2] Validation checks")
    add_birthday(records, "Aarav Sharma", "01-01-2005", "Friend")     # duplicate
    add_birthday(records, "R2D2", "01-01-2000", "Friend")             # bad name
    add_birthday(records, "Kunal", "31-02-2001", "Friend")            # bad date
    add_birthday(records, "Future Kid", "01-01-2099", "Friend")       # future date

    print("\n[3] View all (sorted by nearest birthday)")
    view_all(records, today)

    print("\n[4] Search -> 'friend'")
    for r in search_birthday(records, "friend"):
        print(f"   Found : {r['name']} | {r['dob']} | {r['relation']}")

    print("\n[5] Upcoming birthdays within 7 days")
    for r, d in upcoming(records, 7, today):
        print(f"   {r['name']:<14} -> " + ("TODAY!" if d == 0 else f"in {d} day(s)"))

    print("\n[6] Delete record -> 'Neha Joshi'")
    delete_birthday(records, "Neha Joshi")
    delete_birthday(records, "Zoya")

    print("\n[7] Proof of permanent storage: clear memory and reload from file")
    records.clear()
    print("   Records in memory after clear :", len(records))
    records = load_data()
    print("   Records after reloading file  :", len(records))
    print("   File saved at :", os.path.basename(FILE))
    print("\nPhase 2 completed.")


if __name__ == "__main__":
    menu() if "--menu" in sys.argv else demo()
