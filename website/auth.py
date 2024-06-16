from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, login_user, logout_user, current_user
import hashlib, hmac
from .models import User
from . import db

auth_bp = Blueprint("auth", __name__)


def check_response(data):
    modified_data = data.copy()
    del modified_data['hash']
    data_list = []
    for key in sorted(modified_data.keys()):
        if modified_data[key] is not None:
            data_list.append(key + "=" + modified_data[key])
    data_string = bytes('\n'.join(data_list), 'utf-8')

    secret_key = hashlib.sha256(current_app.config['TELEGRAM_BOT_TOKEN'].encode('utf-8')).digest()
    hmac_string = hmac.new(secret_key, data_string, hashlib.sha256).hexdigest()
    if hmac_string == data['hash']:
        return True
    return False


@auth_bp.route("/auth/telegram", methods=["GET"])
def auth_telegram():
    data = {
        'id': request.args.get('id', None),
        'first_name': request.args.get('first_name', None),
        'last_name': request.args.get('last_name', None),
        'username': request.args.get('username', None),
        'photo_url': request.args.get('photo_url', None),
        'auth_date': request.args.get('auth_date', None),
        'hash': request.args.get('hash', None)
    }

    if check_response(data):
        user = db.session.scalars(
            db.select(User).where(User.id == data['id'])
        ).one_or_none()
        if user is None:
            new_user = User(id=int(data['id']), first_name=data['first_name'], last_name=data['last_name'], username=data['username'], photo_url=data['photo_url'], auth_date=data['auth_date'], hash=data['hash'], role_id=1)
            try:
                db.session.add(new_user)
                db.session.commit()
                login_user(new_user, remember=True)
                return redirect(url_for('home.home'))
            except Exception as e:
                db.session.rollback()
                flash(f"{e}", category="error")
                return render_template("home.html")
        else:
            login_user(user, remember=True)
            return redirect(url_for('home.home'))
    else:
        flash("Неверные данные", category="error")
        return render_template("home.html", user=current_user)


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("home.home"))
