#!/usr/bin/env python3
"""
╔══════════════════════════════════════════╗
║   Student Management System  v2.0        ║
║   Built with Pure Python 3               ║
╚══════════════════════════════════════════╝
"""

import json
import os
import sys
from datetime import datetime

# ── Paths ────────────────────────────────────────────────────────────────────
BASE_DIR  = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, "data", "students.json")

# ── Terminal Colors ───────────────────────────────────────────────────────────
R  = "\033[91m"   # Red
G  = "\033[92m"   # Green
Y  = "\033[93m"   # Yellow
B  = "\033[94m"   # Blue
C  = "\033[96m"   # Cyan
M  = "\033[95m"   # Magenta
W  = "\033[97m"   # White
BO = "\033[1m"    # Bold
RS = "\033[0m"    # Reset

def c(text, *codes): return "".join(codes) + str(text) + RS

# ── Utilities ─────────────────────────────────────────────────────────────────
def clear():    os.system("clear")
def pause():    input(c("\n  ↵  Press Enter to continue...", Y))
def line(ch="─", n=62, col=C): print(c(ch * n, col))

def ask(label, default=None):
    hint = f" [{default}]" if default is not None else ""
    val  = input(c(f"  ➤  {label}{hint}: ", Y)).strip()
    return val if val else default

def confirm(msg):
    return input(c(f"  ➤  {msg} (y/n): ", R)).strip().lower() == "y"

def header(title):
    clear()
    line("═")
    print(c(f"   🎓  {title}", BO + C))
    line("═")
    print()

# ── Data Layer ────────────────────────────────────────────────────────────────
def load():
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    if not os.path.exists(DATA_FILE):
        return {}
    with open(DATA_FILE) as f:
        return json.load(f)

def save(data):
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

def gen_id(data):
    if not data:
        return "S001"
    num = max(int(k[1:]) for k in data)
    return f"S{num+1:03d}"

# ── Grade Helpers ─────────────────────────────────────────────────────────────
def average(grades):
    return round(sum(grades) / len(grades), 2) if grades else None

def letter(avg):
    if avg is None: return "N/A"
    if avg >= 90:   return c("A", G, BO)
    if avg >= 80:   return c("B", G)
    if avg >= 70:   return c("C", Y)
    if avg >= 60:   return c("D", Y)
    return c("F", R)

def grade_bar(avg):
    if avg is None: return c("No grades", Y)
    filled = int(avg / 5)
    bar    = "█" * filled + "░" * (20 - filled)
    col    = G if avg >= 70 else Y if avg >= 60 else R
    return c(bar, col) + c(f" {avg:.1f}%", BO)

# ── Display ───────────────────────────────────────────────────────────────────
def print_table(data):
    if not data:
        print(c("  No students found.\n", Y))
        return

    # Header row
    print(c(f"  {'ID':<6} {'Name':<22} {'Age':<5} {'Course':<20} {'Avg':<8} {'Grade'}", BO + W))
    line("─", 70, col=B)

    for sid, s in data.items():
        avg = average(s.get("grades", []))
        avg_str = f"{avg:.1f}" if avg else "—"
        let = letter(avg).replace("\033[", "").split("m")[-1].replace(RS,"")  # plain for table
        # Re-colorize avg
        avg_col = G if avg and avg >= 70 else Y if avg and avg >= 60 else R if avg else W
        print(
            f"  {c(sid, C, BO):<15} "
            f"{s['name'][:21]:<22} "
            f"{s['age']:<5} "
            f"{s['course'][:19]:<20} "
            f"{c(avg_str, avg_col):<18} "
            f"{letter(avg)}"
        )

    line("─", 70, col=B)
    print(c(f"  Total: {len(data)} student(s)\n", G))

# ── 1. Add Student ─────────────────────────────────────────────────────────────
def add_student():
    header("Add New Student")
    data = load()

    name = ask("Full Name")
    if not name:
        print(c("  ✗  Name is required.\n", R)); return

    try:
        age = int(ask("Age"))
        assert 5 <= age <= 100
    except:
        print(c("  ✗  Invalid age (must be 5–100).\n", R)); return

    course = ask("Course / Programme")
    if not course:
        print(c("  ✗  Course is required.\n", R)); return

    email  = ask("Email", "")
    phone  = ask("Phone", "")

    grade_raw = ask("Grades (comma-separated, e.g. 85,90,78) — skip: leave blank", "")
    grades = []
    if grade_raw:
        try:
            grades = [float(g.strip()) for g in grade_raw.split(",")]
            assert all(0 <= g <= 100 for g in grades)
        except:
            print(c("  ✗  Invalid grades. Each must be 0–100.\n", R)); return

    sid = gen_id(data)
    data[sid] = {
        "name":     name,
        "age":      age,
        "course":   course,
        "email":    email,
        "phone":    phone,
        "grades":   grades,
        "enrolled": datetime.today().strftime("%Y-%m-%d")
    }
    save(data)

    avg = average(grades)
    print(c(f"\n  ✓  Student added! ID: {sid}", G, BO))
    if avg:
        print(c(f"  📊  Grade: {avg:.1f}% → {letter(avg)}", W))
    print()

# ── 2. View All ────────────────────────────────────────────────────────────────
def view_all():
    header("All Students")
    print_table(load())

# ── 3. Search ──────────────────────────────────────────────────────────────────
def search():
    header("Search Students")
    data  = load()
    query = ask("Search by ID / Name / Course").lower()
    if not query: return

    results = {
        sid: s for sid, s in data.items()
        if query in sid.lower()
        or query in s["name"].lower()
        or query in s["course"].lower()
        or query in s.get("email","").lower()
    }

    print(c(f"\n  Found {len(results)} result(s):\n", G if results else Y))
    print_table(results)

# ── 4. Student Detail ──────────────────────────────────────────────────────────
def detail():
    header("Student Detail")
    data = load()

    sid = ask("Enter Student ID").upper()
    if sid not in data:
        print(c(f"  ✗  Student '{sid}' not found.\n", R)); return

    s      = data[sid]
    grades = s.get("grades", [])
    avg    = average(grades)

    print()
    line("┄", 46, C)
    def row(k, v): print(c(f"  {k:<14}", C) + c(str(v), W))
    row("ID",        sid)
    row("Name",      s["name"])
    row("Age",       s["age"])
    row("Course",    s["course"])
    row("Email",     s["email"] or "—")
    row("Phone",     s["phone"] or "—")
    row("Enrolled",  s.get("enrolled","—"))
    row("Grades",    ", ".join(str(g) for g in grades) if grades else "—")
    row("Average",   f"{avg:.1f}%" if avg else "N/A")
    row("Grade",     letter(avg))
    print(c(f"\n  📊  ", W) + grade_bar(avg))
    line("┄", 46, C)
    print()

# ── 5. Update ──────────────────────────────────────────────────────────────────
def update():
    header("Update Student")
    data = load()

    sid = ask("Enter Student ID").upper()
    if sid not in data:
        print(c(f"  ✗  Student '{sid}' not found.\n", R)); return

    s = data[sid]
    print(c(f"\n  Editing: {s['name']} ({sid})  — leave blank to keep current\n", C))

    name   = ask("Name",   s["name"])
    age_s  = ask("Age",    str(s["age"]))
    course = ask("Course", s["course"])
    email  = ask("Email",  s["email"])
    phone  = ask("Phone",  s["phone"])

    try:
        age = int(age_s); assert 5 <= age <= 100
    except:
        print(c("  ✗  Invalid age.\n", R)); return

    data[sid].update({"name": name, "age": age, "course": course,
                      "email": email, "phone": phone})
    save(data)
    print(c(f"\n  ✓  Student {sid} updated successfully!\n", G))

# ── 6. Grades ──────────────────────────────────────────────────────────────────
def manage_grades():
    header("Manage Grades")
    data = load()

    sid = ask("Enter Student ID").upper()
    if sid not in data:
        print(c(f"  ✗  Student '{sid}' not found.\n", R)); return

    s = data[sid]
    cur = s.get("grades", [])
    print(c(f"\n  Student : {s['name']}", C))
    print(c(f"  Current : {cur if cur else 'No grades yet'}\n", W))

    print(c("  Options:", BO))
    print("   1. Replace all grades")
    print("   2. Append new grades")
    print("   3. Clear all grades\n")

    choice = ask("Choose (1/2/3)", "1")

    if choice == "3":
        if confirm("Clear all grades?"):
            data[sid]["grades"] = []
            save(data)
            print(c("\n  ✓  Grades cleared.\n", G))
        return

    raw = ask("Enter grades (comma-separated)")
    try:
        new_grades = [float(g.strip()) for g in raw.split(",")]
        assert all(0 <= g <= 100 for g in new_grades)
    except:
        print(c("  ✗  Invalid grades. Each must be 0–100.\n", R)); return

    if choice == "2":
        data[sid]["grades"] = cur + new_grades
    else:
        data[sid]["grades"] = new_grades

    avg = average(data[sid]["grades"])
    save(data)
    print(c(f"\n  ✓  Grades saved!", G, BO))
    print(c(f"  📊  Average: {avg:.1f}% → ", W) + letter(avg))
    print(f"       {grade_bar(avg)}\n")

# ── 7. Delete ──────────────────────────────────────────────────────────────────
def delete():
    header("Delete Student")
    data = load()

    sid = ask("Enter Student ID").upper()
    if sid not in data:
        print(c(f"  ✗  Student '{sid}' not found.\n", R)); return

    s = data[sid]
    print(c(f"\n  About to delete: {s['name']} ({sid})\n", Y))

    if confirm("This cannot be undone. Continue?"):
        del data[sid]
        save(data)
        print(c(f"\n  ✓  Student {sid} deleted.\n", G))
    else:
        print(c("\n  Cancelled.\n", C))

# ── 8. Statistics ──────────────────────────────────────────────────────────────
def statistics():
    header("Statistics")
    data = load()

    if not data:
        print(c("  No data available.\n", Y)); return

    total   = len(data)
    courses = {}
    avgs    = []

    for s in data.values():
        courses[s["course"]] = courses.get(s["course"], 0) + 1
        avg = average(s.get("grades", []))
        if avg is not None:
            avgs.append(avg)

    overall = round(sum(avgs)/len(avgs), 1) if avgs else None

    print(c(f"  Total Students   : ", C) + c(total, W, BO))
    print(c(f"  Courses Offered  : ", C) + c(len(courses), W, BO))
    if avgs:
        print(c(f"  Highest Average  : ", C) + c(f"{max(avgs):.1f}%", G, BO))
        print(c(f"  Lowest Average   : ", C) + c(f"{min(avgs):.1f}%", R, BO))
        print(c(f"  Overall Average  : ", C) + c(f"{overall:.1f}%", Y, BO))

    # Grade distribution
    buckets = {"A (90-100)":0, "B (80-89)":0, "C (70-79)":0,
               "D (60-69)":0, "F (<60)":0, "No grades":0}
    for s in data.values():
        avg = average(s.get("grades",[]))
        if avg is None:            buckets["No grades"] += 1
        elif avg >= 90:            buckets["A (90-100)"] += 1
        elif avg >= 80:            buckets["B (80-89)"] += 1
        elif avg >= 70:            buckets["C (70-79)"] += 1
        elif avg >= 60:            buckets["D (60-69)"] += 1
        else:                      buckets["F (<60)"] += 1

    print(c("\n  Grade Distribution:\n", BO + W))
    for grade, cnt in buckets.items():
        if cnt == 0: continue
        bar = "█" * cnt
        col = G if grade.startswith("A") else G if grade.startswith("B") else \
              Y if grade.startswith("C") else Y if grade.startswith("D") else R
        print(f"   {grade:<14} {c(bar, col)} {cnt}")

    print(c("\n  Students per Course:\n", BO + W))
    for course, cnt in sorted(courses.items(), key=lambda x: -x[1]):
        bar = "█" * cnt
        print(f"   {course[:18]:<20} {c(bar, B)} {cnt}")
    print()

# ── 9. Top Students ────────────────────────────────────────────────────────────
def top_students():
    header("Top Students")
    data = load()

    ranked = []
    for sid, s in data.items():
        avg = average(s.get("grades", []))
        if avg is not None:
            ranked.append((sid, s, avg))

    if not ranked:
        print(c("  No graded students found.\n", Y)); return

    ranked.sort(key=lambda x: -x[2])
    top_n = min(10, len(ranked))

    print(c(f"  Top {top_n} Students by Average:\n", BO + W))
    for i, (sid, s, avg) in enumerate(ranked[:top_n], 1):
        medal = ["🥇","🥈","🥉"][i-1] if i <= 3 else f"  {i}."
        print(f"  {medal}  {c(s['name'][:22]+'  ', BO+W)}{c(sid, C)}  {grade_bar(avg)}")
    print()

# ── Main Menu ──────────────────────────────────────────────────────────────────
MENU = [
    ("1", "Add Student",        add_student),
    ("2", "View All Students",  view_all),
    ("3", "Search Student",     search),
    ("4", "Student Detail",     detail),
    ("5", "Update Student",     update),
    ("6", "Manage Grades",      manage_grades),
    ("7", "Top Students",       top_students),
    ("8", "Statistics",         statistics),
    ("9", "Delete Student",     delete),
    ("0", "Exit",               None),
]

def show_menu():
    clear()
    print(c("""
  ╔══════════════════════════════════════════╗
  ║    🎓  Student Management System  v2.0   ║
  ╚══════════════════════════════════════════╝""", BO + C))

    data  = load()
    count = len(data)
    print(c(f"  📁  Students in database: {count}\n", W))

    icons = ["➕","📋","🔍","👤","✏️ ","📊","🏆","📈","🗑️ ","🚪"]
    for i, (key, label, _) in enumerate(MENU):
        col = R if key == "0" else G
        print(f"  {c(f'[{key}]', col, BO)}  {icons[i]}  {label}")
    print()

def main():
    while True:
        show_menu()
        choice = input(c("  Choose: ", BO + W)).strip()
        action = {key: fn for key, _, fn in MENU}.get(choice)

        if choice == "0":
            clear()
            print(c("\n  Goodbye! 👋\n", C, BO))
            sys.exit(0)
        elif action:
            action()
            pause()
        else:
            print(c("\n  ✗  Invalid option.\n", R))
            pause()

if __name__ == "__main__":
    main()
