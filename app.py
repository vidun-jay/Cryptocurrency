#!/usr/bin/python
# -*- coding: utf-8 -*-

from flask import Flask, render_template, flash, redirect, url_for, session, request, logging
from passlib.hash import sha256_crypt
from flask_mysqldb import MySQL
from sqlhelper import *
from forms import *
from functools import wraps

app = Flask(__name__)

# configuring SQL stuff
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'password'
app.config['MYSQL_DB'] = 'crypto'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

mysql = MySQL(app)

def isLoggedIn(f): # doesn't let people just type the / location like '/dashboard' without logging in
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash("Unathorized, please log in.", 'danger')
            return redirect(url_for('login'))

    return wrap

def loginUser(username):
    users = Table("users", "name", "email", "username", "password")
    user = users.getone("username", username)

    session['logged_in'] = True
    session['username'] = username
    session['name'] = user.get('name')
    session['email'] = user.get('email')

@app.route("/register", methods = ['GET', 'POST'])
def register():
    form = RegisterForm(request.form)
    users = Table("users", "name", "email", "username", "password")

    if request.method == 'POST' and form.validate(): # when register button is pressed, get data entered
        username = form.username.data
        email = form.email.data
        name = form.name.data

        # check if user exists already
        if isnewuser(username):
            password = sha256_crypt.encrypt(form.password.data)
            users.insert(name,email,username,password) # add it to database
            loginUser(username)
            return redirect(url_for('dashboard'))
        else:
            flash('User already exists!', 'danger')
            return redirect(url_for('register'))

    return render_template('register.html', form=form)

@app.route("/login", methods = ['GET', 'POST'])
def login():
    if request.method == 'POST': # check if login button has been pressed
        username = request.form['username']
        candidate = request.form['password']

        users = Table("users", "name", "email", "username", "password")
        user = users.getone("username", username)
        finalPass = user.get("password")

        if finalPass is None:
            flash("Username is not found", 'danger')
            return redirect(url_for('login'))
        else:
            if sha256_crypt.verify(candidate, finalPass):
                loginUser(username)
                flash("You are now logged in!", 'success')
                return redirect(url_for('dashboard'))
            else:
                flash("Invalid password", 'danger')
                return redirect(url_for('login'))

    return render_template('login.html')

@app.route("/logout")
@isLoggedIn
def logout():
    session.clear()
    flash("Logged out successfully", "success")
    return redirect(url_for('login'))

@app.route("/dashboard")
@isLoggedIn
def dashboard():
    return render_template('dashboard.html', session=session)

@app.route("/")
def index():
    # send_money("vidunvj", "MeatyMeterWeiner", 4.2)
    return render_template('index.html')

if __name__ == '__main__':
    app.secret_key = 'secret123'
    app.run(debug = True)