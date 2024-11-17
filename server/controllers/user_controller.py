from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required,current_user
from server.models.user import User
from server.app import db
from werkzeug.security import check_password_hash, generate_password_hash

user_controller = Blueprint('user_controller', __name__)  




@user_controller.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        if not email or not password:
            flash('Please fill in all fields', 'error')
            return redirect(url_for('user_controller.login'))
        
        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            login_user(user)  
            return redirect(url_for('index')) 
        else:
            flash('Invalid email or password', 'error')
    return render_template('login.html')

@user_controller.route('/logout')
@login_required
def logout():
    logout_user() 
    return redirect(url_for('index')) 

@user_controller.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        fullname = request.form['fullname']
        password = request.form['password']
        cpassword = request.form['confirm-password']
        
        if not email or not fullname or not password or not cpassword:
            flash('Please fill in all fields', 'error')
            return redirect(url_for('user_controller.register'))

        if password != cpassword:
            flash('Passwords do not match', 'error')
            return redirect(url_for('user_controller.register'))

        user = User.query.filter_by(email=email).first()
        if user:
            flash('Email already exists', 'error')
            return redirect(url_for('user_controller.register'))

        new_user = User(username=fullname,email=email, password=generate_password_hash(password))
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('user_controller.login')) 
    return render_template('register.html')

@user_controller.route('/profile')
@login_required
def profile():
    return render_template('profile.html', user=current_user)
