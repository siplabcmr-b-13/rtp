import os
import json
import random
import smtplib
import ssl
from flask import (
    Flask, request, render_template, redirect, url_for,
    session, flash
)
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')

EMAIL_ADDRESS = os.getenv('EMAIL_ADDRESS')
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')
SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587
USERS_FILE = 'users.json'


def load_users():
    if not os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'w') as f:
            json.dump({"users": []}, f)
    with open(USERS_FILE, 'r') as f:
        return json.load(f)


def save_users(data):
    with open(USERS_FILE, 'w') as f:
        json.dump(data, f, indent=4)


def find_user(email):
    data = load_users()
    return next((u for u in data['users'] if u['email'] == email), None)


def send_otp_email(to_email, otp):
    subject = "Your OTP Code"
    body = f"Your OTP is: {otp}"
    msg = f"Subject: {subject}\n\n{body}"
    ctx = ssl.create_default_context()
    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls(context=ctx)
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        server.sendmail(EMAIL_ADDRESS, to_email, msg)


def calc_calories(weight, height, age, gender, activity):
    # BMR
    if gender == 'male':
        bmr = 10 * weight + 6.25 * height - 5 * age + 5
    else:
        bmr = 10 * weight + 6.25 * height - 5 * age - 161
    factors = {
        'sedentary': 1.2,
        'lightly active': 1.375,
        'moderately active': 1.55,
        'very active': 1.725,
        'extra active': 1.9
    }
    return bmr * factors.get(activity, 1.2)


def total_req_calories(user, workout_hours, job_hours, today_activity):
    base = calc_calories(user['weight'], user['height'],
                         user['age'], user['gender'], today_activity)
    workout_mins = workout_hours * 60
    workout_cal = workout_mins * user['weight'] * 0.0175 * 6
    job_cal = job_hours * 60 * user['weight'] * 0.0175 * 1.5
    return round(base + workout_cal + job_cal, 2)


@app.route('/')
def index():
    if session.get('user'):
        return redirect(url_for('dashboard'))
    return redirect(url_for('signin'))


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        form = request.form
        if 'otp' not in form:
            data = {
                'email': form['email'],
                'username': form['username'],
                'age': int(form['age']),
                'gender': form['gender'],
                'weight': float(form['weight']),
                'height': float(form['height'])
            }
            session['signup_data'] = data
            otp = str(random.randint(100000, 999999))
            session['signup_otp'] = otp
            send_otp_email(data['email'], otp)
            flash('OTP sent to your Gmail.')
            return render_template('signup.html',
                                   show_otp=True,
                                   signup_data=data)
        else:
            if form['otp'] == session.get('signup_otp'):
                data = session.pop('signup_data')
                if find_user(data['email']):
                    flash('User already exists.')
                    return redirect(url_for('signup'))
                all_users = load_users()
                all_users['users'].append(data)
                save_users(all_users)
                session['user'] = data['email']
                session.pop('signup_otp', None)
                return redirect(url_for('dashboard'))
            else:
                flash('Wrong OTP, try again.')
                return render_template('signup.html',
                                       show_otp=True,
                                       signup_data=session.get('signup_data'))
    return render_template('signup.html', show_otp=False)


@app.route('/signin', methods=['GET', 'POST'])
def signin():
    if request.method == 'POST':
        form = request.form
        if 'otp' not in form:
            email = form['email']
            if not find_user(email):
                flash('No such user, please sign up.')
                return redirect(url_for('signup'))
            session['signin_email'] = email
            otp = str(random.randint(100000, 999999))
            session['signin_otp'] = otp
            send_otp_email(email, otp)
            flash('OTP sent to your mail.')
            return render_template('signin.html',
                                   show_otp=True,
                                   signin_email=email)
        else:
            if form['otp'] == session.get('signin_otp'):
                session['user'] = session.pop('signin_email')
                session.pop('signin_otp', None)
                return redirect(url_for('dashboard'))
            else:
                flash('Wrong OTP.')
                return render_template('signin.html',
                                       show_otp=True,
                                       signin_email=session.get('signin_email'))
    return render_template('signin.html', show_otp=False)


@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if not session.get('user'):
        return redirect(url_for('signin'))
    user = find_user(session['user'])
    result = None
    if request.method == 'POST':
        workout_hours = float(request.form['workout_time'])
        job_hours = float(request.form['job_time'])
        today_activity = request.form['today_activity']
        result = total_req_calories(user, workout_hours, job_hours, today_activity)
    return render_template('dashboard.html', user=user, result=result)


@app.route('/edit_profile', methods=['POST'])
def edit_profile():
    if not session.get('user'):
        return redirect(url_for('signin'))
    usr = find_user(session['user'])
    for f in ['username', 'age', 'gender', 'weight', 'height']:
        val = request.form[f]
        if f in ['age']:
            usr[f] = int(val)
        elif f in ['weight', 'height']:
            usr[f] = float(val)
        else:
            usr[f] = val
    data = load_users()
    data['users'] = [u if u['email'] != usr['email'] else usr for u in data['users']]
    save_users(data)
    flash('Profile updated.')
    return redirect(url_for('dashboard'))


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('signin'))


if __name__ == '__main__':
    app.run(debug=True)
