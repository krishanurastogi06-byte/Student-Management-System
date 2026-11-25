
from flask import Flask, render_template, request, redirect, session, flash, url_for
import sqlite3
import calendar

app = Flask(__name__)
app.secret_key = "student123"


# Database Connection
def get_db_connection():
    conn = sqlite3.connect("students.db")
    conn.row_factory = sqlite3.Row
    return conn


# Create Database
def create_database():
    conn = get_db_connection()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            course TEXT NOT NULL,
            created_at TEXT
        )
    """)

    columns = [
        row["name"]
        for row in conn.execute("PRAGMA table_info(students)").fetchall()
    ]

    if "created_at" not in columns:
        conn.execute("ALTER TABLE students ADD COLUMN created_at TEXT")

    conn.commit()
    conn.close()


# Home Page
@app.route("/")
def home():
    return redirect(url_for("login"))


# Admin Login
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if username == "admin" and password == "admin123":
            session["admin"] = username
            return redirect(url_for("dashboard"))
        else:
            flash("Invalid username or password!")

    return render_template("login.html")


# Dashboard
@app.route("/dashboard")
def dashboard():
    if "admin" not in session:
        return redirect(url_for("login"))

    conn = get_db_connection()

    total_students = conn.execute(
        "SELECT COUNT(*) FROM students"
    ).fetchone()[0]

    total_courses = conn.execute(
        "SELECT COUNT(DISTINCT course) FROM students"
    ).fetchone()[0]

    course_data = conn.execute("""
        SELECT course, COUNT(*) AS total
        FROM students
        GROUP BY course
    """).fetchall()

    monthly_data = conn.execute("""
        SELECT CAST(strftime('%m', created_at) AS INTEGER) AS month,
               COUNT(*) AS total
        FROM students
        WHERE strftime('%Y', created_at) = strftime('%Y', 'now')
        GROUP BY month
    """).fetchall()

    recent_students = conn.execute("""
        SELECT * FROM students
        ORDER BY id DESC LIMIT 5
    """).fetchall()

    conn.close()

    month_counts = {
        row["month"]: row["total"]
        for row in monthly_data if row["month"] is not None
    }

    months = [calendar.month_abbr[i] for i in range(1, 13)]
    monthly_counts = [month_counts.get(i, 0) for i in range(1, 13)]

    course_labels = [row["course"] for row in course_data]
    course_counts = [row["total"] for row in course_data]

    return render_template(
        "dashboard.html",
        total_students=total_students,
        total_courses=total_courses,
        months=months,
        monthly_counts=monthly_counts,
        course_labels=course_labels,
        course_counts=course_counts,
        recent_students=recent_students
    )


# Add Student
@app.route("/add_student", methods=["GET", "POST"])
def add_student():
    if "admin" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        course = request.form["course"]

        conn = get_db_connection()

        conn.execute("""
            INSERT INTO students (name, email, course, created_at)
            VALUES (?, ?, ?, CURRENT_TIMESTAMP)
        """, (name, email, course))

        conn.commit()
        conn.close()

        flash("Student added successfully!")
        return redirect(url_for("view_students"))

    return render_template("add_student.html")


# View and Search Students
@app.route("/view_students")
def view_students():
    if "admin" not in session:
        return redirect(url_for("login"))

    search = request.args.get("search", "").strip()

    conn = get_db_connection()

    students = conn.execute("""
        SELECT * FROM students
        WHERE name LIKE ? OR email LIKE ? OR course LIKE ?
        ORDER BY id DESC
    """, (f"%{search}%", f"%{search}%", f"%{search}%")).fetchall()

    conn.close()

    return render_template(
        "view_students.html",
        students=students,
        search=search
    )


# Student Profile
@app.route("/student_profile/<int:id>")
def student_profile(id):
    if "admin" not in session:
        return redirect(url_for("login"))

    conn = get_db_connection()

    student = conn.execute(
        "SELECT * FROM students WHERE id = ?", (id,)
    ).fetchone()

    conn.close()

    if student is None:
        return "Student not found", 404

    return render_template(
        "student_profile.html",
        student=student
    )


# Edit Student
@app.route("/edit_student/<int:id>", methods=["GET", "POST"])
def edit_student(id):
    if "admin" not in session:
        return redirect(url_for("login"))

    conn = get_db_connection()

    student = conn.execute(
        "SELECT * FROM students WHERE id = ?", (id,)
    ).fetchone()

    if student is None:
        conn.close()
        return "Student not found", 404

    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        course = request.form["course"]

        conn.execute("""
            UPDATE students
            SET name = ?, email = ?, course = ?
            WHERE id = ?
        """, (name, email, course, id))

        conn.commit()
        conn.close()

        flash("Student updated successfully!")
        return redirect(url_for("view_students"))

    conn.close()

    return render_template(
        "edit_student.html",
        student=student
    )


# Delete Student
@app.route("/delete_student/<int:id>")
def delete_student(id):
    if "admin" not in session:
        return redirect(url_for("login"))

    conn = get_db_connection()

    conn.execute(
        "DELETE FROM students WHERE id = ?", (id,)
    )

    conn.commit()
    conn.close()

    flash("Student deleted successfully!")
    return redirect(url_for("view_students"))


# Logout
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


# Run Application
if __name__ == "__main__":
    create_database()
    app.run(debug=True)
