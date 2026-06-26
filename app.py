import os
from flask import Flask, render_template, request, redirect, session
import psycopg2
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "your_secret_key_change_this"


def get_db_connection():
    conn = psycopg2.connect(
        host="aws-1-ap-south-1.pooler.supabase.com",
        database="postgres",
        user="postgres.abjynasbpfumnixpnhkk",
        password="sajib khan ss",  # set this in your environment, don't hardcode it
        port="5432",
    )
    return conn


@app.route('/')
def login():
    return render_template('login.html')


@app.route('/home')
def home():
    if 'user_id' not in session:
        return redirect('/')

    conn = get_db_connection()
    c = conn.cursor()
    c.execute(
        "SELECT * FROM courses WHERE user_id = %s ORDER BY id DESC",
        (session['user_id'],)
    )
    courses = c.fetchall()
    c.close()
    conn.close()
    return render_template('home.html', courses=courses)


@app.route('/add', methods=['GET', 'POST'])
def add():
    if 'user_id' not in session:
        return redirect('/')

    if request.method == 'POST':
        course_name = request.form['course_name']
        semester = request.form['semester']

        conn = get_db_connection()
        c = conn.cursor()
        c.execute(
            """
            INSERT INTO courses (user_id, course_name, semester)
            VALUES (%s, %s, %s)
            """,
            (session['user_id'], course_name, semester)
        )
        conn.commit()
        c.close()
        conn.close()
        return redirect('/home')

    return render_template('add.html')


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

    return render_template('login.html', error='Invalid credentials')


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
            (username, generate_password_hash(password))
        )
        conn.commit()
        c.close()
        conn.close()
        return redirect('/')
    except Exception:
        return render_template('login.html', error='Username already exists')


@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')


@app.route('/delete/<int:course_id>')
def delete(course_id):
    if 'user_id' not in session:
        return redirect('/')

    conn = get_db_connection()
    c = conn.cursor()
    c.execute(
        """
        DELETE FROM courses
        WHERE id = %s AND user_id = %s
        """,
        (course_id, session['user_id'])
    )
    conn.commit()
    c.close()
    conn.close()
    return redirect('/home')

@app.route('/resources/<int:course_id>')
def resources(course_id):
    if 'user_id' not in session:
        return redirect('/')

    conn = get_db_connection()
    c = conn.cursor()

    c.execute(
        """
        SELECT title, description, resource_type, resource_link
        FROM resources
        WHERE course_id = %s
        """,
        (course_id,)
    )

    resources = c.fetchall()

    c.close()
    conn.close()

    return render_template(
        'resources.html',
        resources=resources
    )

if __name__ == '__main__':
    app.run(debug=True)