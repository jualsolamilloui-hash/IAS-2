from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_mysqldb import MySQL
import bcrypt
from cryptography.fernet import Fernet
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')

# DB CONNECTION
app.config['MYSQL_HOST'] = "localhost"
app.config['MYSQL_USER'] = "root"
app.config['MYSQL_PASSWORD'] = ""
app.config['MYSQL_DB'] = "ias2_db"
mysql = MySQL(app)

# Encryption setup
key = os.getenv('FERNET_KEY').encode()
cipher = Fernet(key)

def encrypt_email(email):
    """Encrypt email and return a base64 string (safe for storage)."""
    return cipher.encrypt(email.encode()).decode('utf-8')

def decrypt_email(encrypted_email):
    return cipher.decrypt(encrypted_email.encode()).decode('utf-8')

@app.route('/')
def home():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT id, email, password FROM users")
    users_raw = cursor.fetchall()
    users = []
    for user in users_raw:
        # user = (id, encrypted_email, password)
        try:
            decrypted_email = decrypt_email(user[1])
            # Append a TUPLE: (id, decrypted_email, password)
            users.append((user[0], decrypted_email, user[2]))
        except Exception as e:
            # If decryption fails, print error (check your console)
            print(f"Decryption error for user {user[0]}: {e}")
            # Optionally, you could still include the user with placeholder email
            # users.append((user[0], "[decryption failed]", user[2]))
            continue
    cursor.close()
    return render_template("home.html", users=users)

@app.route('/auth')
def auth():
    return render_template('auth.html')

# SIGNUP
@app.route("/signup_process", methods=["POST"])
def signup_process():
    email = request.form["email"]
    password = request.form["password"]

    # Encrypt the email before storing
    encrypted_email = encrypt_email(email)

    password_bytes = password.encode("utf-8")
    hashed_password = bcrypt.hashpw(password_bytes, bcrypt.gensalt())

    cursor = mysql.connection.cursor()
    # We cannot search by encrypted email because encryption is non‑deterministic.
    # Instead, we check for duplicates by fetching all users and decrypting.
    cursor.execute("SELECT email FROM users")
    existing_encrypted = cursor.fetchall()
    for row in existing_encrypted:
        if decrypt_email(row[0]) == email:
            flash("Account already exists!")
            cursor.close()
            return redirect("/auth")

    # Insert new user
    cursor.execute(
        "INSERT INTO users (email, password) VALUES (%s, %s)",
        (encrypted_email, hashed_password)
    )
    mysql.connection.commit()
    cursor.close()
    flash("Account created successfully! Please login.")
    return redirect("/auth")

# LOGIN
@app.route("/login_process", methods=["POST"])
def login_process():
    email = request.form["email"]
    password = request.form["password"].encode('utf-8')

    cursor = mysql.connection.cursor()
    cursor.execute("SELECT id, email, password FROM users")
    users = cursor.fetchall()
    cursor.close()

    user_found = None
    for user in users:
        # user = (id, encrypted_email, hashed_password)
        try:
            decrypted_email = decrypt_email(user[1])
            if decrypted_email == email:
                user_found = user
                break
        except Exception:
            # In case decryption fails for any reason, skip this user
            continue

    if user_found:
        # user_found[2] is the hashed password (as bytes from DB, but stored as string)
        hashed_password = user_found[2].encode('utf-8')
        if bcrypt.checkpw(password, hashed_password):
            session["user"] = decrypted_email   # store the decrypted email in session
            return redirect("/")
        else:
            flash("Invalid email or password!")
            return redirect("/auth")
    else:
        flash("Invalid email or password!")
        return redirect("/auth")

@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect("/auth")

@app.route('/products')
def products():
    return render_template("prod.html")

@app.route('/up_products')
def up_products():
    return render_template("prod.html")

if __name__ == '__main__':
    app.run(debug=True)