import pymysql

def get_db_connection():
    return pymysql.connect(
        host='localhost',
        user='root',          # default XAMPP user
        password='',          # default XAMPP password (blank)
        database='user_auth',
        cursorclass=pymysql.cursors.DictCursor
    )