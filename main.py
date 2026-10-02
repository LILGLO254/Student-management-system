from hmac import compare_digest

from flask import Flask, redirect, render_template, request, session, url_for
from database import create_connection
from mysql.connector import Error, IntegrityError
from werkzeug.security import check_password_hash, generate_password_hash


app = Flask(__name__, static_folder="styles", static_url_path="/styles")
app.secret_key = "school-management-demo-key"


@app.route("/")

def home():
    if session.get("user"):
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))


@app.route("/register", methods=["GET", "POST"])
def register():
    if session.get("user"):
        return redirect(url_for("dashboard"))

    error = None
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")
        strength_checks = (
            len(password) >= 8,
            any(character.islower() for character in password),
            any(character.isupper() for character in password),
            any(character.isdigit() for character in password),
            any(not character.isalnum() for character in password),
        )

        if not username or not email:
            error = "Enter a username and email address."
        elif len(username) > 100 or len(email) > 150:
            error = "The username or email address is too long."
        elif sum(strength_checks) < 4:
            error = "Choose a stronger password using at least 8 characters and 3 character types."
        elif password != confirm_password:
            error = "The passwords do not match."
        else:
            connection = create_connection()
            if connection is None:
                error = "Registration is temporarily unavailable. Please try again."
            else:
                cursor = None
                try:
                    cursor = connection.cursor()
                    cursor.execute(
                        "SELECT user_id FROM users "
                        "WHERE LOWER(username) = LOWER(%s) OR LOWER(email) = %s LIMIT 1",
                        (username, email),
                    )
                    if cursor.fetchone():
                        error = "That username or email is already registered."
                    else:
                        cursor.execute(
                            "INSERT INTO users (username, email, password, role) "
                            "VALUES (%s, %s, %s, %s)",
                            (username, email, generate_password_hash(password), "student"),
                        )
                        connection.commit()
                        return redirect(url_for("login", registered=1))
                except IntegrityError:
                    connection.rollback()
                    error = "That username or email is already registered."
                except Error:
                    connection.rollback()
                    error = "Registration is temporarily unavailable. Please try again."
                finally:
                    if cursor is not None:
                        cursor.close()
                    connection.close()

    return render_template("registration.html", error=error)


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

    return render_template(
        "login.html", error=error, registered=request.args.get("registered") == "1"
    )


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

