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


def createBookingList(start_time, end_time, bookedDetails):
    turfTimeDetails=[]
    today = datetime.datetime.now().replace(microsecond=0, second=0, minute=0) + datetime.timedelta(hours=2)
    end_date=today + datetime.timedelta(days=7)
    cur_time = today.time()
    cur_time=datetime.datetime.combine(datetime.date.min, cur_time) - datetime.datetime.min
    while(today<end_date):
        #print("Date : ",today.date())
        while cur_time>=start_time and cur_time<=end_time:   
            status=0     
            #print(cur_time)
            for booked in bookedDetails:
                if booked[0]==today.date() and booked[1]==cur_time:
                    status=1
                    break
            turfTimeDetails.append((today.date(),cur_time,status))  
            cur_time += datetime.timedelta(hours=1)
        cur_time=start_time
        today += datetime.timedelta(days=1)
    return turfTimeDetails

@user.route('/book/<turfID>', methods=['GET', 'POST'])
def book(turfID):
    if 'userLoggedin' in session:
        turfTimeDetails=[]
        cur = mysql.connection.cursor()
        cur.execute('select name, address, contactNo1, contactNo2, starttime, endtime, rate from admin where turfid=%s and status=%s',(turfID,'1',))
        turfData = cur.fetchall()
        #print(turfData)
        if turfData:
            cur.execute('select bookDate, bookTime, status from bookings where turfid = %s', (turfID,))
            bookedDetails = cur.fetchall()
            #print(bookedDetails)
            start_time=turfData[0][4]
            end_time=turfData[0][5]
            turfTimeDetails=createBookingList(start_time, end_time, bookedDetails)
            # print(turfTimeDetails)
        else:
            return redirect("user.home") 
        cur.close()        
        return render_template("user/book.html", turfTimeDetails=turfTimeDetails,turfData=turfData, turfID=turfID)
    else: 
        return redirect(url_for('user.home')) 

@user.route('/bookingConfirmation', methods=['POST'])
def bookingConfirmation():
    userid=request.form['turf_id']
    bookingDate=request.form['turf_booking_date']
    bookingTime=request.form['turf_booking_time']
    return '<div class="modal fade" id="staticBackdrop" data-bs-backdrop="static" data-bs-keyboard="false" tabindex="-1" aria-labelledby="staticBackdropLabel" aria-hidden="true">\
    <div class="modal-dialog">\
        <div class="modal-content">\
        <div class="modal-header">\
            <h5 class="modal-title" id="staticBackdropLabel">Confirm</h5>\
            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>\
        </div>\
        <div class="modal-body">\
            Do you want to confirm booking on '+bookingDate+' at '+bookingTime+'\
        </div>\
        <div class="modal-footer">\
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>\
            <button onclick="confirmBooking('+userid+',\''+bookingDate+'\',\''+bookingTime+'\')" class="btn btn-warning">Confirm Booking</button>\
        </div>\
        </div>\
    </div>\
    </div>'

@user.route('/confirmUserBooking', methods=['POST'])
def confirmUserBooking():
    turf_id=request.form['turf_id']
    bookingDate=request.form['turf_booking_date']
    bookingTime=request.form['turf_booking_time']
    cursor = mysql.connection.cursor()
    cursor.execute('INSERT INTO bookings VALUES (%s, %s, %s, %s, %s)', (turf_id,session['loggedinuserid'], bookingDate,bookingTime, 1))
    mysql.connection.commit()
    return '<div class="modal fade" id="staticBackdrop2" data-bs-backdrop="static" data-bs-keyboard="false" tabindex="-1" aria-labelledby="staticBackdropLabel" aria-hidden="true">\
    <div class="modal-dialog">\
        <div class="modal-content">\
        <div class="modal-header">\
            <h5 class="modal-title" id="staticBackdropLabel">Booking Confirmed</h5>\
            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>\
        </div>\
        <div class="modal-body">\
            Your booking on '+bookingDate+' at '+bookingTime+' has been confirmed.\
        </div>\
        <div class="modal-footer">\
            <a href="http://127.0.0.1:5000/profile" type="button" class="btn btn-success">Okay</a>\
        </div>\
        </div>\
    </div>\
    </div>'




@user.route('/profile')
def profile():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM users WHERE userid = %s',(session['loggedinuserid'],))
    data =cursor.fetchone()
    cursor.execute('select * from bookings where userid=%s',(session['loggedinuserid'],))
    bookingData = cursor.fetchall()
    return render_template('user/profile.html', data=data,bookingData=bookingData)


@user.route('/edit_profile',methods=['GET','POST'])
def edit_profile():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM users WHERE userid = %s',(session['loggedinuserid'],))
    data =cursor.fetchone()
    return render_template('user/edit_profile.html', data=data)

@user.route('/update_profile',methods=['GET','POST'])
def update_profile():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phoneNo = request.form['phoneNo']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("UPDATE users SET name = %s, email = %s, phoneNo= %s WHERE userid = %s ",(name,email,phoneNo,session['loggedinuserid']))
        mysql.connection.commit()
        print("data updated")
    return redirect(url_for('user.profile'))

