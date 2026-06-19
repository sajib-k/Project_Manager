from flask import Flask, render_template, request, redirect, session
import psycopg2
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "your_secret_key_change_this"


# DATABASE CONNECTION
def get_db_connection():
    conn = psycopg2.connect(
        host="aws-1-ap-south-1.pooler.supabase.com",
        database="postgres",
        user="postgres.abjynasbpfumnixpnhkk",
        password="sajib khan ss",
        port="5432"
    )
    return conn

# LOGIN PAGE
@app.route('/')
def login():
    return render_template('login.html')


# HOME PAGE
@app.route('/home')
def home():

    if 'user_id' not in session:
        return redirect('/')

    conn = get_db_connection()
    c = conn.cursor()

    c.execute(
        "SELECT * FROM projects WHERE user_id = %s",
        (session['user_id'],)
    )

    projects = c.fetchall()

    c.close()
    conn.close()

    return render_template('home.html', projects=projects)


# ADD PROJECT
@app.route('/add', methods=['GET', 'POST'])
def add():

    if 'user_id' not in session:
        return redirect('/')

    if request.method == 'POST':

        project_name = request.form['project_name']
        description = request.form['description']
        project_link = request.form['project_link']
        project_image = request.form['project_image']

        conn = get_db_connection()
        c = conn.cursor()

        c.execute(
            """
            INSERT INTO projects
            (
                user_id,
                project_name,
                description,
                project_link,
                project_image
            )
            VALUES (%s, %s, %s, %s, %s)
            """,
            (
                session['user_id'],
                project_name,
                description,
                project_link,
                project_image
            )
        )

        conn.commit()
        c.close()
        conn.close()

        return redirect('/home')

    return render_template('add.html')


# LOGIN POST
@app.route('/login', methods=['POST'])
def login_post():

    username = request.form['username']
    password = request.form['password']

    conn = get_db_connection()
    c = conn.cursor()

    c.execute(
        "SELECT id, password FROM users WHERE username = %s",
        (username,)
    )

    user = c.fetchone()

    c.close()
    conn.close()

    if user and check_password_hash(user[1], password):
        session['user_id'] = user[0]
        return redirect('/home')

    return render_template(
        'login.html',
        error='Invalid credentials'
    )


# SIGNUP
@app.route('/signup', methods=['POST'])
def signup_post():

    username = request.form['username']
    password = request.form['password']

    try:
        conn = get_db_connection()
        c = conn.cursor()

        c.execute(
            """
            INSERT INTO users (username, password)
            VALUES (%s, %s)
            """,
            (
                username,
                generate_password_hash(password)
            )
        )

        conn.commit()

        c.close()
        conn.close()

        return redirect('/')

    except Exception:
        return render_template(
            'login.html',
            error='Username already exists'
        )


# LOGOUT
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')


# DELETE PROJECT
@app.route('/delete/<int:project_id>')
def delete(project_id):

    if 'user_id' not in session:
        return redirect('/')

    conn = get_db_connection()
    c = conn.cursor()

    c.execute(
        """
        DELETE FROM projects
        WHERE id = %s AND user_id = %s
        """,
        (
            project_id,
            session['user_id']
        )
    )

    conn.commit()

    c.close()
    conn.close()

    return redirect('/home')


# RUN APP
if __name__ == '__main__':
    app.run(debug=True)