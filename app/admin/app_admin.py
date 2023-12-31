# Import flask dependencies
from flask import Flask, Blueprint, redirect,  request, render_template, \
                  flash, g, session, url_for,Response

# Import the database object from the main app module
from app import mysql

# import sha256_crypt to encrypt the password
from passlib.hash import sha256_crypt
import datetime 
from datetime import date 


# Define the blueprint: 'admin', set its url prefix: app.url/admin
admin = Blueprint('admin', __name__, url_prefix='/admin', template_folder='../templates/admin', static_folder='../static/admin')

@admin.route('/login', methods=['GET', 'POST'])
def login():
    if 'adminLoggedin' in session:
        return redirect(url_for('admin.home'))
    else:
        msg = ""
        if request.method == 'POST' and 'adminEmail' in request.form and 'adminPassword' in request.form:
            details = request.form
            admin_email = details['adminEmail'].strip()
            admin_password = details['adminPassword'].strip()
            cur = mysql.connection.cursor()
            cur.execute('select * from admin where email = %s', (admin_email,))
            logdata = cur.fetchone()
            cur.close()
            print (type(logdata[9]))
            if logdata:
                if logdata[7]!=1:

                    if logdata[9]!= 1:
                        msg="Account in-active. Kindly send a mail to onlineturfbooking@gmail.com :)"
                    elif sha256_crypt.verify(admin_password, logdata[3]):
                        session['adminLoggedin'] = True
                if logdata[9]!=1:
                    msg="Account in-active. Kindly send a mail to onlineturfbooking@gmail.com :)"
                elif sha256_crypt.verify(admin_password, logdata[3]):
                    session['adminLoggedin'] = True

                    # print(logdata)
                    session['adminName'] = logdata[1]
                    session['adminID'] = logdata[0]
                    return redirect(url_for('admin.AdminTimeSlots'))
                else:
                    msg = "Incorrect password !! "
            else:
                msg = "Incorrect email !!"
            return render_template('adminLogin.html', msgAdmin = msg)
        return render_template('adminLogin.html', msgAdmin = msg)

# admin logout url
@admin.route('/logout')
def logout():
    session.pop('adminLoggedin', None)
    session.pop('adminName', None)
    return redirect(url_for('admin.login'))

# Set the route and accepted methods
@admin.route('/home', methods=['GET', 'POST'])
@admin.route('/', methods=['GET', 'POST'])
def home():
    # session['adminLoggedin'] = True
    # session['adminName'] = "Test Turf"
    # session['adminID'] = 3739226622
    if 'adminLoggedin' in session:
        return render_template("admin_layout.html")
    else:
        return redirect(url_for('admin.login'))


# Booking for admin side 
def createBookingList(start_time, end_time, bookedDetails):
    turfTimeDetails=[]
    today = datetime.datetime.now().replace(microsecond=0, second=0, minute=0) + datetime.timedelta(hours=2)
    end_date=today + datetime.timedelta(days=3)
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

