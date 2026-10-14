"""
==========================================================
 BIRTHDAY REMINDER SYSTEM  -  PHASE 1 (Utility Assessment-I)
 Student : Tanvi Dahale          USN : CD26D015
 Guide   : Ms. Ashwini Yerlekar
 Course  : Python Programming Lab (Experiential Learning)
 Scope   : Problem understanding + core logic using
           functions, list and dictionary (in-memory)
==========================================================
Run  :  python phase1.py
"""
from datetime import date, datetime, timedelta

birthdays = []          # list of dictionaries -> one dictionary per person


def next_birthday(dob, today):
    """Return the next date on which this birthday occurs (today counts)."""
    year = today.year
    while True:
        try:
            nb = dob.replace(year=year)
        except ValueError:              # 29 Feb in a non-leap year
            nb = date(year, 2, 28)
        if nb >= today:
            return nb
        year += 1


def add_birthday(name, dob_text, relation):
    """Store one birthday record (date format DD-MM-YYYY)."""
    dob = datetime.strptime(dob_text, "%d-%m-%Y").date()
    birthdays.append({"name": name, "dob": dob, "relation": relation})
    print(f"  [+] Added : {name} ({dob.strftime('%d %b %Y')}) - {relation}")


def view_all():
    """Display every stored record in a table."""
    print(f"\n  {'No':<4}{'Name':<14}{'Date of Birth':<16}{'Relation'}")
    print("  " + "-" * 46)
    for i, b in enumerate(birthdays, 1):
        print(f"  {i:<4}{b['name']:<14}{b['dob'].strftime('%d-%m-%Y'):<16}{b['relation']}")


def search_birthday(keyword):
    """Return records whose name contains the keyword (case-insensitive)."""
    return [b for b in birthdays if keyword.lower() in b["name"].lower()]


def todays_birthdays(today):
    """Return people whose birthday is today."""
    return [b for b in birthdays if next_birthday(b["dob"], today) == today]


def upcoming_birthdays(days, today):
    """Return (record, days_left) for birthdays within the next `days` days."""
    result = []
    for b in birthdays:
        left = (next_birthday(b["dob"], today) - today).days
        if 0 < left <= days:
            result.append((b, left))
    return sorted(result, key=lambda item: item[1])


def dob_in(days_ahead, birth_year, today):
    """Helper for the demo: DOB whose birthday falls `days_ahead` days from today."""
    target = today + timedelta(days=days_ahead)
    try:
        return target.replace(year=birth_year).strftime("%d-%m-%Y")
    except ValueError:
        return target.replace(year=birth_year, day=28).strftime("%d-%m-%Y")


def main():
    today = date.today()
    print("=" * 60)
    print("   BIRTHDAY REMINDER SYSTEM - PHASE 1")
    print("   Today's date :", today.strftime("%d-%m-%Y (%A)"))
    print("=" * 60)

    print("\n[STEP 1] Adding birthday records")
    add_birthday("Aarav Sharma", dob_in(0, 2005, today), "Friend")
    add_birthday("Priya Dahale", dob_in(3, 1978, today), "Family")
    add_birthday("Rohan Patil", dob_in(6, 2004, today), "Classmate")
    add_birthday("Neha Joshi", dob_in(20, 2003, today), "Friend")
    add_birthday("Mr. Deshmukh", dob_in(150, 1975, today), "Colleague")

    print("\n[STEP 2] View all records")
    view_all()

    print("\n[STEP 3] Search by name -> 'priya'")
    found = search_birthday("priya")
    if found:
        for b in found:
            print(f"  Record Found : {b['name']} | {b['dob'].strftime('%d-%m-%Y')} | {b['relation']}")
    else:
        print("  Record Not Found")

    print("\n[STEP 4] Today's birthdays")
    for b in todays_birthdays(today):
        print(f"  *** Happy Birthday, {b['name']}! ({b['relation']}) ***")

    print("\n[STEP 5] Upcoming birthdays in next 7 days")
    for b, left in upcoming_birthdays(7, today):
        print(f"  {b['name']:<14} -> in {left} day(s) on {next_birthday(b['dob'], today).strftime('%d %b')}")

    print("\n[STEP 6] Search for a name that does not exist -> 'zoya'")
    print("  Record Found" if search_birthday("zoya") else "  Record Not Found")
    print("\nPhase 1 completed. (Data is kept in memory only.)")


if __name__ == "__main__":
    main()
