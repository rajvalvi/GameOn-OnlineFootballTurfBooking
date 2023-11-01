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
@user.route('/user_home')
def home():
    return("userr home")