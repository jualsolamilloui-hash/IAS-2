from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_mysqldb import MySQL
import bcrypt

app = Flask(__name__)
app.secret_key = 'SECRET_KEY'
#DB CONNECTION
app.config['MYSQL_HOST'] = "localhost"
app.config['MYSQL_USER'] = "root"
app.config['MYSQL_PASSWORD'] = ""
app.config['MYSQL_DB'] = "ias2_db"
mysql = MySQL(app)


@app.route('/')
def home():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()
    cursor.close()
    return render_template("home.html", users=users)

@app.route('/auth')
def auth():
    return render_template('auth.html')

#SIGNUP
@app.route("/signup_process", methods=["POST"])
def signup_process():

    email = request.form["email"]
    password = request.form["password"]
    password_bytes = password.encode("utf-8")
    hashed_password = bcrypt.hashpw(password_bytes, bcrypt.gensalt())
    cursor = mysql.connection.cursor()
    # Check if email already exists
    cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
    account = cursor.fetchone()
    if account:
        flash("Account already exists!")
        return redirect("/auth")
    else:
        cursor.execute("INSERT INTO users(email, password) VALUES (%s, %s)", (email, hashed_password))
        mysql.connection.commit()
        cursor.close()

        flash("Account created successfully! Please login.")
        return redirect("/auth")


#LOGIN 
@app.route("/login_process", methods=["POST"])
def login_process():

    email = request.form["email"]
    password = request.form["password"].encode('utf-8')

    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM users WHERE email=%s", (email,))
    account = cursor.fetchone()

    if account:
        hashed_password = account[2].encode('utf-8')  # convert string to bytes
        if bcrypt.checkpw(password, hashed_password):
            session["user"] = account[1]
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