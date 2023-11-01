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

@admin.route('/')
def home():
    return("Home")