from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, login_user, logout_user, current_user
from .models import User
from werkzeug.security import generate_password_hash, check_password_hash
from . import db

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/registration', methods=['GET', 'POST'])
def registration():
    if request.method == 'POST':
        login = request.form.get('login')
        password = request.form.get('password')
        passwordConfirm = request.form.get('passwordConfirm')

        if password != passwordConfirm:
            flash('Пароли не совпадают', category='error')

        if len(login) > 0 and len(password) > 0:          
            new_user = User(login=login, password_hash=generate_password_hash(password), role_id=1)
            db.session.add(new_user)
            db.session.commit()
            return redirect(url_for('home.home'))

    return render_template('registration.html')


@auth_bp.route('/authorization', methods=['GET', 'POST'])
def authorization():
    if request.method == 'POST':
        login = request.form.get('login')
        password = request.form.get('password')
        remember_me = request.form.get('remember_me')

        user = db.session.scalars(db.select(User).where(User.login == login)).one_or_none()
        if user:
            if check_password_hash(user.password_hash, password):
                if remember_me is None:
                    login_user(user)
                else:
                    login_user(user, remember=True)
                return redirect(url_for('home.home'))
            else:
                flash("Неверный логин или пароль", category="error")
        else:
            flash("Неверный логин или пароль", category="error")

    return render_template("authorization.html", user=current_user)


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home.home'))