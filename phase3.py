"""
==========================================================
 BIRTHDAY REMINDER SYSTEM  -  PHASE 3 (Utility Assessment-III)  FINAL
 Student : Tanvi Dahale          USN : CD26D015
 Guide   : Ms. Ashwini Yerlekar
 Course  : Python Programming Lab (Experiential Learning)
 Scope   : Complete utility - OOP, file handling (JSON + CSV export),
           validation, reminders, edit/delete/search, statistics
           and automated test cases
==========================================================
Run demo + tests :  python phase3.py
Run menu (own)   :  python phase3.py --menu
"""
import csv
import json
import os
import sys
import tempfile
import unittest
from dataclasses import dataclass
from datetime import date, datetime, timedelta

DATE_FMT = "%d-%m-%Y"
DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "birthdays.json")
MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


# ------------------------------------------------------------------ date helper
def next_birthday(dob, today):
    """Next occurrence of dob on/after today (29 Feb -> 28 Feb in non-leap years)."""
    year = today.year
    while True:
        try:
            nb = dob.replace(year=year)
        except ValueError:
            nb = date(year, 2, 28)
        if nb >= today:
            return nb
        year += 1


# ------------------------------------------------------------------ class 1 : Person
@dataclass
class Person:
    name: str
    dob: date
    relation: str = "Friend"
    phone: str = ""

    def days_left(self, today):
        return (next_birthday(self.dob, today) - today).days

    def turning_age(self, today):
        return next_birthday(self.dob, today).year - self.dob.year

    def to_dict(self):
        return {"name": self.name, "dob": self.dob.strftime(DATE_FMT),
                "relation": self.relation, "phone": self.phone}

    @staticmethod
    def from_dict(d):
        return Person(d["name"], datetime.strptime(d["dob"], DATE_FMT).date(),
                      d.get("relation", "Friend"), d.get("phone", ""))


# ------------------------------------------------------------------ class 2 : Manager
class BirthdayManager:
    def __init__(self, filename=DATA_FILE):
        self.filename = filename
        self.people = []
        self.load()

    # ---- file handling
    def load(self):
        try:
            with open(self.filename, "r", encoding="utf-8") as f:
                self.people = [Person.from_dict(d) for d in json.load(f)]
        except FileNotFoundError:
            self.people = []
        except (json.JSONDecodeError, KeyError, ValueError):
            print("  [!] Data file is corrupted - starting with an empty list.")
            self.people = []

    def save(self):
        with open(self.filename, "w", encoding="utf-8") as f:
            json.dump([p.to_dict() for p in self.people], f, indent=4)

    def export_csv(self, path):
        with open(path, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["Name", "DOB", "Relation", "Phone"])
            for p in self.people:
                w.writerow([p.name, p.dob.strftime(DATE_FMT), p.relation, p.phone])
        return len(self.people)

    # ---- helpers
    def _find(self, name):
        return next((p for p in self.people if p.name.lower() == name.strip().lower()), None)

    @staticmethod
    def _valid_name(name):
        return len(name.strip()) >= 2 and all(c.isalpha() or c in " .'-" for c in name)

    # ---- CRUD (every method returns (success, message))
    def add(self, name, dob_text, relation="Friend", phone=""):
        if not self._valid_name(name):
            return False, f"Invalid name '{name}'"
        try:
            dob = datetime.strptime(dob_text, DATE_FMT).date()
        except ValueError:
            return False, f"Invalid date '{dob_text}' (use DD-MM-YYYY)"
        if dob > date.today():
            return False, "Date of birth cannot be in the future"
        if phone and not (phone.isdigit() and len(phone) == 10):
            return False, "Phone must be exactly 10 digits"
        if self._find(name):
            return False, f"Duplicate: '{name}' already exists"
        self.people.append(Person(name.strip(), dob, relation, phone))
        self.save()
        return True, f"Added & saved: {name.strip()}"

    def edit(self, name, new_dob=None, new_relation=None, new_phone=None):
        p = self._find(name)
        if p is None:
            return False, f"'{name}' not found"
        if new_dob:
            try:
                p.dob = datetime.strptime(new_dob, DATE_FMT).date()
            except ValueError:
                return False, f"Invalid date '{new_dob}'"
        if new_relation:
            p.relation = new_relation
        if new_phone is not None:
            p.phone = new_phone
        self.save()
        return True, f"Updated & saved: {p.name}"

    def delete(self, name):
        p = self._find(name)
        if p is None:
            return False, f"'{name}' not found"
        self.people.remove(p)
        self.save()
        return True, f"Deleted & saved: {p.name}"

    # ---- queries
    def search(self, keyword):
        k = keyword.lower()
        return [p for p in self.people if k in p.name.lower() or k in p.relation.lower()]

    def by_month(self, month):
        return sorted([p for p in self.people if p.dob.month == month], key=lambda p: p.dob.day)

    def todays(self, today=None):
        today = today or date.today()
        return [p for p in self.people if p.days_left(today) == 0]

    def upcoming(self, days=7, today=None):
        today = today or date.today()
        result = [(p, p.days_left(today)) for p in self.people
                  if 0 < p.days_left(today) <= days]
        return sorted(result, key=lambda x: x[1])

    def sorted_list(self, today=None):
        today = today or date.today()
        return sorted(self.people, key=lambda p: p.days_left(today))

    def stats(self, today=None):
        today = today or date.today()
        by_rel = {}
        for p in self.people:
            by_rel[p.relation] = by_rel.get(p.relation, 0) + 1
        by_month = {}
        for p in self.people:
            by_month[MONTHS[p.dob.month - 1]] = by_month.get(MONTHS[p.dob.month - 1], 0) + 1
        nearest = self.sorted_list(today)[0] if self.people else None
        return {"total": len(self.people), "by_relation": by_rel,
                "by_month": by_month, "nearest": nearest}


# ------------------------------------------------------------------ display
def show_table(people, today):
    print(f"\n  {'No':<4}{'Name':<16}{'DOB':<13}{'Relation':<13}"
          f"{'Phone':<12}{'Turns':<7}{'Days'}")
    print("  " + "-" * 72)
    for i, p in enumerate(people, 1):
        print(f"  {i:<4}{p.name:<16}{p.dob.strftime(DATE_FMT):<13}{p.relation:<13}"
              f"{(p.phone or '-'):<12}{p.turning_age(today):<7}{p.days_left(today)}")


def show_reminders(mgr, days, today):
    print("\n  +--------------------------------------------------+")
    print("  |              BIRTHDAY REMINDERS                  |")
    print("  +--------------------------------------------------+")
    todays = mgr.todays(today)
    if todays:
        for p in todays:
            print(f"   TODAY    : {p.name} turns {p.turning_age(today)}"
                  f"  - wish them now! ({p.relation})")
    else:
        print("   TODAY    : No birthdays today")
    up = mgr.upcoming(days, today)
    if up:
        for p, d in up:
            print(f"   UPCOMING : {p.name:<14} in {d} day(s) - turns {p.turning_age(today)}")
    else:
        print(f"   UPCOMING : None in next {days} days")


def say(result):
    ok, msg = result
    print(("  [+] " if ok else "  [x] ") + msg)


# ------------------------------------------------------------------ interactive menu
def menu():
    mgr = BirthdayManager()
    today = date.today()
    show_reminders(mgr, 7, today)
    while True:
        print("\n===== BIRTHDAY REMINDER SYSTEM =====")
        print("1.Add 2.View 3.Search 4.Edit 5.Delete 6.Reminders "
              "7.Month-wise 8.Statistics 9.Export CSV 0.Exit")
        ch = input("Enter choice: ").strip()
        if ch == "1":
            say(mgr.add(input("Name: "), input("DOB (DD-MM-YYYY): "),
                        input("Relation: ") or "Friend", input("Phone (optional): ")))
        elif ch == "2":
            show_table(mgr.sorted_list(today), today)
        elif ch == "3":
            show_table(mgr.search(input("Search keyword: ")), today)
        elif ch == "4":
            say(mgr.edit(input("Name to edit: "), input("New DOB (blank=skip): ") or None,
                         input("New relation (blank=skip): ") or None))
        elif ch == "5":
            say(mgr.delete(input("Name to delete: ")))
        elif ch == "6":
            show_reminders(mgr, int(input("Days ahead: ") or 7), today)
        elif ch == "7":
            show_table(mgr.by_month(int(input("Month number (1-12): "))), today)
        elif ch == "8":
            print(mgr.stats(today))
        elif ch == "9":
            print("  Exported", mgr.export_csv("birthdays_export.csv"), "records")
        elif ch == "0":
            print("Goodbye! Never miss a birthday again.")
            break
        else:
            print("  Invalid choice")


# ------------------------------------------------------------------ test cases
class TestBirthdayManager(unittest.TestCase):
    TODAY = date(2026, 10, 9)

    def setUp(self):
        self.tmp = tempfile.NamedTemporaryFile(suffix=".json", delete=False)
        self.tmp.close()
        os.remove(self.tmp.name)
        self.mgr = BirthdayManager(self.tmp.name)

    def tearDown(self):
        if os.path.exists(self.tmp.name):
            os.remove(self.tmp.name)

    def test_01_add_valid_record(self):
        self.assertTrue(self.mgr.add("Aarav", "09-10-2005")[0])

    def test_02_reject_duplicate(self):
        self.mgr.add("Aarav", "09-10-2005")
        self.assertFalse(self.mgr.add("aarav", "01-01-2000")[0])

    def test_03_reject_invalid_date(self):
        self.assertFalse(self.mgr.add("Kunal", "31-02-2001")[0])

    def test_04_reject_future_date(self):
        self.assertFalse(self.mgr.add("Baby", "01-01-2099")[0])

    def test_05_reject_bad_phone(self):
        self.assertFalse(self.mgr.add("Riya", "05-05-2000", "Friend", "12345")[0])

    def test_06_data_persists_in_file(self):
        self.mgr.add("Priya", "12-10-1978")
        self.assertEqual(len(BirthdayManager(self.tmp.name).people), 1)

    def test_07_today_and_upcoming(self):
        self.mgr.add("Today", "09-10-2005")
        self.mgr.add("Soon", "12-10-1990")
        self.mgr.add("Later", "01-03-1990")
        self.assertEqual([p.name for p in self.mgr.todays(self.TODAY)], ["Today"])
        self.assertEqual([p.name for p, d in self.mgr.upcoming(7, self.TODAY)], ["Soon"])

    def test_08_leap_day_birthday(self):
        self.mgr.add("Leap", "29-02-2000")
        self.assertEqual(next_birthday(date(2000, 2, 29), date(2027, 1, 1)), date(2027, 2, 28))

    def test_09_edit_and_delete(self):
        self.mgr.add("Neha", "29-10-2003")
        self.assertTrue(self.mgr.edit("Neha", new_relation="Family")[0])
        self.assertEqual(self.mgr.search("family")[0].name, "Neha")
        self.assertTrue(self.mgr.delete("Neha")[0])
        self.assertFalse(self.mgr.delete("Neha")[0])

    def test_10_turning_age(self):
        self.mgr.add("Aarav", "09-10-2005")
        self.assertEqual(self.mgr.people[0].turning_age(self.TODAY), 21)


class PrettyResult(unittest.TestResult):
    """Prints one clean line per test case."""
    def _line(self, test, status):
        name = test._testMethodName
        print(f"   T{name[5:7]}  {name[8:].replace('_', ' '):<26} {status}")

    def addSuccess(self, test):
        super().addSuccess(test)
        self._line(test, "PASS")

    def addFailure(self, test, err):
        super().addFailure(test, err)
        self._line(test, "FAIL")

    def addError(self, test, err):
        super().addError(test, err)
        self._line(test, "ERROR")


def run_tests():
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(TestBirthdayManager)
    result = PrettyResult()
    suite.run(result)
    return result


# ------------------------------------------------------------------ demo
def dob_in(days_ahead, birth_year, today):
    t = today + timedelta(days=days_ahead)
    try:
        return t.replace(year=birth_year).strftime(DATE_FMT)
    except ValueError:
        return t.replace(year=birth_year, day=28).strftime(DATE_FMT)


def demo():
    today = date.today()
    demo_file = os.path.join(tempfile.gettempdir(), "birthday_demo.json")
    if os.path.exists(demo_file):
        os.remove(demo_file)
    mgr = BirthdayManager(demo_file)
    print("=" * 66)
    print("   BIRTHDAY REMINDER SYSTEM - PHASE 3 (FINAL UTILITY)")
    print("   Student: Tanvi Dahale | USN: CD26D015")
    print("   Today's date :", today.strftime("%d-%m-%Y (%A)"))
    print("=" * 66)

    print("\n[1] Adding records")
    for n, d, y, rel, ph in [("Aarav Sharma", 0, 2005, "Friend", "9876543210"),
                             ("Priya Dahale", 3, 1978, "Family", "9822012345"),
                             ("Rohan Patil", 6, 2004, "Classmate", ""),
                             ("Neha Joshi", 20, 2003, "Friend", "9890011223"),
                             ("Mr. Deshmukh", 150, 1975, "Colleague", "")]:
        say(mgr.add(n, dob_in(d, y, today), rel, ph))

    print("\n[2] Validation (invalid inputs are rejected)")
    say(mgr.add("Aarav Sharma", "01-01-2005"))
    say(mgr.add("Kunal", "31-02-2001"))
    say(mgr.add("Riya", "05-05-2000", "Friend", "12345"))

    show_reminders(mgr, 7, today)

    print("\n[3] All records (sorted by nearest birthday)")
    show_table(mgr.sorted_list(today), today)

    print("\n[4] Search 'friend'")
    show_table(mgr.search("friend"), today)

    print("\n[5] Edit & delete")
    say(mgr.edit("Rohan Patil", new_relation="Best Friend", new_phone="9765432100"))
    say(mgr.delete("Mr. Deshmukh"))

    print("\n[6] Month-wise list (October)")
    show_table(mgr.by_month(10), today)

    print("\n[7] Statistics")
    s = mgr.stats(today)
    print("   Total records :", s["total"])
    print("   By relation   :", s["by_relation"])
    print("   By month      :", s["by_month"])
    print("   Nearest       :", s["nearest"].name, f"({s['nearest'].days_left(today)} day(s))")

    print("\n[8] Export to CSV")
    csv_path = os.path.join(tempfile.gettempdir(), "birthdays_export.csv")
    print("   Records exported :", mgr.export_csv(csv_path), "->", os.path.basename(csv_path))

    print("\n[9] Running automated test cases")
    result = run_tests()
    print(f"\n   Tests run: {result.testsRun} | Failures: {len(result.failures)}"
          f" | Errors: {len(result.errors)}")
    print("   RESULT :", "ALL TESTS PASSED" if result.wasSuccessful() else "SOME TESTS FAILED")


if __name__ == "__main__":
    menu() if "--menu" in sys.argv else demo()
