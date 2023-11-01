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

@super_admin.route('/home')
def home():
    return("super admin home")