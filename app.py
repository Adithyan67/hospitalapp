from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3, requests

app = Flask(__name__)
app.secret_key = "supersecret"
DB = "clinic.db"

HOLIDAY_API = "https://date.nager.at/api/v3/PublicHolidays/2025/IN"

def get_db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn

def is_holiday(date):
    res = requests.get(HOLIDAY_API).json()
    return any(h["date"] == date for h in res)

# ✅ Home route redirects to /appointments
@app.route("/")
def home():
    return redirect(url_for("appointments"))

@app.route("/appointments")
def appointments():
    doctor_filter = request.args.get("doctor")
    date_filter = request.args.get("date")

    conn = get_db()
    q = """SELECT a.id, d.name as doctor, p.name as patient, a.date, a.time
           FROM appointments a
           JOIN doctors d ON a.doctor_id=d.id
           JOIN patients p ON a.patient_id=p.id
           WHERE 1=1 """
    params = []
    if doctor_filter:
        q += " AND d.id=?"
        params.append(doctor_filter)
    if date_filter:
        q += " AND a.date=?"
        params.append(date_filter)

    cur = conn.execute(q, params)
    appts = cur.fetchall()
    doctors = conn.execute("SELECT * FROM doctors").fetchall()
    conn.close()
    return render_template("appointments.html", appointments=appts, doctors=doctors)

@app.route("/appointments/new", methods=["GET", "POST"])
def new_appointment():
    conn = get_db()
    doctors = conn.execute("SELECT * FROM doctors").fetchall()
    patients = conn.execute("SELECT * FROM patients").fetchall()

    if request.method == "POST":
        doctor_id = request.form["doctor_id"]
        patient_id = request.form["patient_id"]
        date = request.form["date"]
        time = request.form["time"]

        if is_holiday(date):
            flash("❌ Cannot book on a public holiday.")
            return redirect(url_for("new_appointment"))

        cur = conn.execute(
            "SELECT 1 FROM appointments WHERE doctor_id=? AND date=? AND time=?",
            (doctor_id, date, time)
        )
        if cur.fetchone():
            flash("❌ This slot is already booked.")
            return redirect(url_for("new_appointment"))

        conn.execute(
            "INSERT INTO appointments (doctor_id, patient_id, date, time) VALUES (?,?,?,?)",
            (doctor_id, patient_id, date, time)
        )
        conn.commit()
        conn.close()
        flash("✅ Appointment booked!")
        return redirect(url_for("appointments"))

    return render_template("new_appointment.html", doctors=doctors, patients=patients)

if __name__ == "__main__":
    # Run the Flask app
    app.run(debug=True)
