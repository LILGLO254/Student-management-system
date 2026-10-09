from hmac import compare_digest
from functools import wraps
from flask import Flask,abort, redirect, render_template, request, session, url_for
from database import create_connection
from mysql.connector import Error, IntegrityError
from werkzeug.security import check_password_hash, generate_password_hash


app = Flask(__name__, static_folder="styles", static_url_path="/styles")
app.secret_key = "school-management-demo-key"



def login_required(*allowed_roles):
    def decorator(view_function):
        @wraps(view_function)
        def wrapper(*args, **kwargs):
            user=session.get("user")

    


            if not session.get("user"):
                return redirect(url_for("login"))

            
            role = str(user.get("role", "student")).lower()
            if role not in allowed_roles:
                abort(403)
            return view_function(*args, **kwargs)
        return wrapper
    return decorator

@app.errorhandler(403)
def forbidden(error):
    return render_template("403.html"), 403 







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
        identifier = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        connection = create_connection()
        if connection:
            try:
                cursor = connection.cursor(dictionary=True)
                cursor.execute(
                    "SELECT username, email, password, role FROM users "
                    "WHERE LOWER(email) = %s OR LOWER(username) = %s LIMIT 1",
                    (identifier, identifier),
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
                    "role": user["role"] or "student",
                }
                session.permanent = request.form.get("remember") == "on"
                return redirect(url_for("dashboard"))
        error = "That email and password combination is not recognized."

    return render_template(
        "login.html", error=error, registered=request.args.get("registered") == "1"
    )

@app.route("/admin/dashboard")
@login_required("admin")    
def admin_dashboard():
    return render_template("admin_dashboard.html",user=session.get("user"))

@app.route("/lecturer/dashboard")
@login_required("lecturer")
def lecturer_dashboard():
    return render_template("lecturer_dashboard.html",user=session.get("user"))

@app.route("/student/dashboard")
@login_required("student")
def student_dashboard():
    return render_template("student_dashboard.html",user=session.get("user"))



@app.route("/dashboard")
def dashboard():
   user = session.get("user")

   if not user:
       return redirect(url_for("login"))

   role =str(user.get("role", "student")).strip().lower()

   if role == "admin":
        return redirect(url_for("admin_dashboard"))

   elif role == "lecturer":
        return redirect(url_for("lecturer_dashboard"))

   elif role == "student":
        return redirect(url_for("student_dashboard"))

   abort(403)



    

@app.route("/logout")
def logout():
    session.clear()
    return render_template("logout.html")

if __name__ == "__main__":
    connection = create_connection()
    if connection:
        connection.close()
    app.run(debug=True)
