# Import flask dependencies
from re import template
from flask import Blueprint, request, render_template, \
                  flash, g, session, redirect, url_for

# Import the database object from the main app module
from app import mysql
import MySQLdb.cursors

# import sha256_crypt to encrypt the password
from passlib.hash import sha256_crypt

from random import randint

from flask_jwt_extended import create_access_token, decode_token
import datetime

import re

from wtforms import validators
# Define the blueprint: 'user', set its url prefix: app.url/
user = Blueprint('user', __name__, url_prefix='/')

# Set the route and accepted methods
@user.route('/')
@user.route('/home/')
def home():
    return render_template("user/home.html")

@user.route('/turf', methods=['GET', 'POST'])
def turf():
    cur = mysql.connection.cursor()
    cur.execute('select * from admin where status=%s',('1'))
    turfData = cur.fetchall()
    cur.close()
    return render_template("user/Turf.html",turfDetails=turfData)



# @user.route('/home/', methods=['GET', 'POST'])
# @user.route('/', methods=['GET', 'POST'])
# def home():
#     if 'userLoggedin' in session:
#         cur = mysql.connection.cursor()
#         cur.execute('select * from admin where status=%s',('1'))
#         turfData = cur.fetchall()
#         cur.close()
#         return render_template("user/home.html",turfDetails=turfData)
#     else:
#         return redirect(url_for('user.login'))

@user.route('/test')
def test():
    return render_template('user/test.html')

@user.route('/login', methods=['GET', 'POST'])
def login():
    if 'userLoggedin' in session:
        return redirect(url_for('user.home'))
    else:
        msg = ""
        if request.method == 'POST' and 'email' in request.form and 'password' in request.form:
            details = request.form
            email = details['email'].strip()
            password = details['password'].strip()
            cur = mysql.connection.cursor()
            cur.execute('select userID,name,password from users where email = %s', (email,))
            logdata = cur.fetchone()
            cur.close()
            if logdata:
                if sha256_crypt.verify(password, logdata[2]):
                    session['userLoggedin'] = True
                    print(logdata)
                    session['loggedinuserid'] = logdata[0]
                    session['name'] = logdata[1]
                    return redirect(url_for('user.home'))
                msg = "Incorrect password !! "
            else:
                msg = "Incorrect username !!"
            return render_template('user/login.html', msgUser = msg)
        return render_template('user/login.html', msgUser = msg)


@user.route('/register', methods=['GET', 'POST'])
def register():
    msg = ''
    if request.method == 'POST' and 'name' in request.form and 'userid' in request.form and 'email' in request.form and 'phoneNo' in request.form and 'password' in request.form:
        name = request.form['name'].strip()
        userid = request.form['userid'].strip()
        email = request.form['email'].strip()
        phoneNo = request.form['phoneNo'].strip()
        password = request.form['password'].strip()
        password = sha256_crypt.hash(password)
        print(name)
        cursor = mysql.connection.cursor()
        print(name)
        cursor.execute('SELECT * FROM users WHERE userid = % s', (userid,))
        account = cursor.fetchone()
        if account:
            msg = 'Account already exists !'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address !'
        elif not re.match(r'[A-Za-z0-9]+', userid):
            msg = 'Username must contain only characters and numbers !'
        # elif not re.macth(r'[A-Za-z]+',name):
        #     msg ='name must contain charactors'
        # elif not userid or not password or not email:
        #     msg = 'Please fill out the form !'
        else:
            cursor.execute('INSERT INTO users VALUES (% s, % s, % s, % s,% s)', (name, email,phoneNo, password,userid))
            mysql.connection.commit()
            msg = "Thanks for registaring"
    elif request.method == 'POST':
        msg = 'Please fill out the form !'
    return render_template('user/register.html', msg=msg)


@user.route('/mybookings', methods=['GET','POST'])
def mybookings():
    bookingData = ""
    if 'userLoggedin' in session:
        cur = mysql.connection.cursor()
        cur.execute('select * from bookings where userid=%s',(session['loggedinuserid'],))
        bookingData = cur.fetchall()
        # print(bookingData)
    return render_template("user/mybookings.html", bookingData=bookingData)


@user.route('/profile')
def profile():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM users WHERE userid = %s',(session['loggedinuserid'],))
    data =cursor.fetchone()
    cursor.execute('select * from bookings where userid=%s',(session['loggedinuserid'],))
    bookingData = cursor.fetchall()
    return render_template('user/profile.html', data=data,bookingData=bookingData)
