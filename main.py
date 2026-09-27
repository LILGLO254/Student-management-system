from hmac import compare_digest

from flask import Flask, redirect, render_template, request, session, url_for
from database import create_connection
from werkzeug.security import check_password_hash


app = Flask(__name__, static_folder="styles", static_url_path="/styles")
app.secret_key = "school-management-demo-key"


@app.route("/")




def home():
    if session.get("user"):
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if session.get("user"):
        return redirect(url_for("dashboard"))

    error = None
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        connection = create_connection()
        if connection:
            try:
                cursor = connection.cursor(dictionary=True)
                cursor.execute(
                    "SELECT username, email, password, role FROM users "
                    "WHERE LOWER(email) = %s OR LOWER(username) = %s LIMIT 1",
                    (email, email),
                )
                user = cursor.fetchone()
            finally:
                connection.close()

            stored_password = user["password"] if user else ""
            password_matches = (
                check_password_hash(stored_password, password)
                if stored_password.startswith(("pbkdf2:", "scrypt:"))
                else compare_digest(stored_password, password)
            )
            if user and password_matches:
                session["user"] = {
                    "name": user["username"],
                    "role": user["role"] or "School user",
                }
                session.permanent = request.form.get("remember") == "on"
                return redirect(url_for("dashboard"))
        error = "That email and password combination is not recognized."

    return render_template("login.html", error=error)


@app.route("/dashboard")
def dashboard():
    if not session.get("user"):
        return redirect(url_for("login"))
    return render_template("dashboard.html", user=session["user"])


@app.route("/logout")
def logout():
    session.clear()
    return render_template("logout.html")

if __name__ == "__main__":
    connection = create_connection()
    if connection:
        connection.close()
    app.run(debug=True)

