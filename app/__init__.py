from flask import Flask, render_template

from flask_mysqldb import MySQL

from flask_jwt_extended import JWTManager



app = Flask(__name__)

mysql = MySQL(app)

jwt = JWTManager(app)

# Configurations
app.config.from_object('config')         

# -----------------------  SUPER ADMIN PAGES --------------------------
from app.super_admin.app_superadmin import super_admin as super_admin
app.register_blueprint(super_admin)

# --------------------------  ADMIN PAGES -----------------------------
from app.admin.app_admin import admin as admin
app.register_blueprint(admin)

# --------------------------  USER PAGES -----------------------------
from app.user.app_user import user as user
app.register_blueprint(user)

# --------------------------  ERROR PAGES -----------------------------

# @app.errorhandler(404)
# def page_not_found( error ) :
#     return render_template("error.html", error_msg = "404, Sorry Page not found"), 404


# @app.errorhandler(400)
# def bad_request( error ) :
#     return render_template("error.html",
#                            error_msg = "Yeahhh, the server couldn't understand what you asked for, Sorry"), 400
