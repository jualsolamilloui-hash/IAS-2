from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = 'my_secret_key'  # Change this to a random secret key in production

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/auth')
def auth():
    return render_template('auth.html')

@app.route('/signup', methods=['POST'])
def signup():
    return redirect(url_for('home'))

@app.route('/login', methods=['POST'])
def login():
        return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)