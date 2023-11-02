# Import flask dependencies
from flask import Blueprint, request, render_template, \
                  flash, g, session, redirect, url_for

# Import random module
from random import randint

# Import the database object from the main app module
from app import mysql

# import sha256_crypt to encrypt the password
from passlib.hash import sha256_crypt

# Define the blueprint: 'auth', set its url prefix: app.url/auth
super_admin = Blueprint('super_admin', __name__, url_prefix='/super_admin', template_folder='../templates/super_admin', static_folder='../static/super_admin')


# Set the route and accepted methods
@super_admin.route('/home', methods=['GET', 'POST'])
@super_admin.route('/', methods=['GET', 'POST'])
def home():
    if 'superAdminLoggedin' in session:
        cur = mysql.connection.cursor()
        msg=''
        if request.method == 'POST':
            details = request.form
            turfID=randint(100000000,9999999999)
            name=details['name'].strip()
            address=details['address'].strip()
            password=sha256_crypt.hash(details['password'].strip())
            email=details['email'].strip()
            contactNo1=details['contactNo1']
            contactNo2=details['contactNo2']
            logo = 'profile.jpg'
            status = 1
            cur.execute("insert into admin(turfid,name,address,password,email,contactNo1, contactNo2, logo ,status) values(%s,%s,%s,%s,%s,%s,%s,%s,%s)",(turfID,name,address,password,email,contactNo1,contactNo2,logo,status))
            mysql.connection.commit()
            msg="Turf added successfully"
        cur.execute('select turfid,name,address,email,contactNo1, contactNo2, status from admin')
        adminData = cur.fetchall()
        cur.close()
        return render_template("homeSA.html",turfDetails=adminData,turfMsg=msg)
    else:
        return redirect(url_for('super_admin.login'))

# super admin login route
@super_admin.route('/login', methods=['GET', 'POST'])
def login():
    if 'superAdminLoggedin' in session:
        return redirect(url_for('super_admin.home'))
    else:
        msg = ""
        if request.method == 'POST' and 'usernameSA' in request.form and 'passwordSA' in request.form:
            details = request.form
            username = details['usernameSA'].strip()
            password = details['passwordSA'].strip()
            cur = mysql.connection.cursor()
            cur.execute('select * from superAdmin where username = %s', (username,))
            logdata = cur.fetchone()
            cur.close()
            if logdata:
                if sha256_crypt.verify(password, logdata[2]):
                    session['superAdminLoggedin'] = True
                    # print(logdata)
                    session['name'] = logdata[0]
                    return redirect(url_for('super_admin.home'))
                msg = "Incorrect password !! "
            else:
                msg = "Incorrect username !!"
            return render_template('loginSA.html', msgSA = msg)
        return render_template('loginSA.html', msgSA = msg)

# super admin logout url
@super_admin.route('/logout')
def logout():
    session.pop('superAdminLoggedin', None)
    session.pop('name', None)
    return redirect(url_for('super_admin.login'))

# Change turf status(enable/disable)
@super_admin.route('/changeStatus/<int:turfID>/<int:oldStatus>')
def changeStatus(turfID,oldStatus):
    if 'superAdminLoggedin' in session:
        cur = mysql.connection.cursor()
        if oldStatus==0:
            cur.execute("update admin set status=%s where turfid=%s",('1',turfID))
        else:
            cur.execute("update admin set status=%s where turfid=%s",('0',turfID))
        mysql.connection.commit()
        cur.close()
        return redirect(url_for('super_admin.home'))
    else:
        return redirect(url_for('super_admin.login'))

# Delete turf from the list
@super_admin.route('/deleteTurf/<int:turfID>',methods = ['GET','POST'])
def delete_turf(turfID):
    if 'superAdminLoggedin' in session:
        cursor=mysql.connection.cursor()
        cursor.execute('DELETE FROM admin WHERE turf_id ={0}'.format(turfID))
        mysql.connection.commit()
        return redirect(url_for("super_admin.home"))
    else:
        return redirect(url_for('super_admin.login'))

# edit turf info
@super_admin.route('/editTurf/<int:turfID>', methods = ['GET', 'POST'])
def edit_turf(turfID):
    if 'superAdminLoggedin' in session:
        cursor = mysql.connection.cursor()
        cursor.execute('SELECT * FROM turf_info WHERE turf_id ={0}'.format(id))
        data =cursor.fetchone()
        return render_template('edit_turf.html',res=data)
    else:
        return redirect(url_for('super_admin.login'))
    

    