from flask import Blueprint, render_template, request, flash, redirect, url_for, current_app, session
from flask_login import current_user
import os, random, json
from openai import OpenAI
from . import config, decorators, db
from .models import User

client = OpenAI(api_key=config.OPENAI_API_KEY)

home_bp = Blueprint("home", __name__)


def random_card(cards_number):
    current_dir = os.path.dirname(__file__)
    image_folder = os.path.join(current_dir, "static", "cards")
    all_cards = os.listdir(image_folder)
    selected_cards = [
        {"name": f.replace(".webp", ""), "reversed": bool(random.getrandbits(1))}
        for f in random.sample(all_cards, cards_number)
    ]
    return selected_cards


@home_bp.route("/", methods=["POST", "GET"])
def home():
    if not current_user.is_authenticated:
        if 'balance' not in session:
            session['balance'] = 2
    return render_template("home.html", user=current_user, session=session)


@home_bp.route("/answer", methods=["GET", "POST"])
def answer():
    if not current_user.is_authenticated:
        if session.get('balance') == 0:
            response = {
                "status": "error",
                "message": "У Вас закончился баланс!"
            }
            return json.dumps(response), 400
        else:
            session['balance'] = session['balance'] - 1
            balance = session['balance']
    else:
        user = db.session.scalars(db.select(User).where(User.id == current_user.id)).one_or_none()
        if user.balance == 0:
            response = {
                "status": "error",
                "message": "У Вас закончился баланс!"
            }
            return json.dumps(response), 400
        else:
            user.balance = user.balance - 1
            balance = user.balance
            db.session.commit()
    data = request.get_json()
    message = data["message"]
    cards = data["cards_number"]
    random_cards = random_card(int(cards))

    def generate():
        yield json.dumps({"cards": random_cards, "balance": balance})
        stream = client.chat.completions.create(
            model="gpt-3.5-turbo-16k",
            messages=[
                {
                    "role": "system",
                    "content": "Задача прочитать карты Таро по представленным названиям, объяснить их значение, а затем ответить на вопрос в контексте этих карт. name: название карты, reversed: перевернута карта или нет. Пожалуйста, исключите любой диалог, который не является прямым ответом на вопрос или прямым разъяснением значения карт. Вам не требуется приветствовать пользователя или предоставлять неспецифическую информацию. Просто сконцентрируйтесь на интерпретации данных карт Таро и на ответе на специфический вопрос в контексте расклада. Ожидается, что вы будете обладать детальным знанием каждой карты таро в класическом колоде Райдер-Уайт и сможете адаптировать эти уникальные значения к заданному вопросу. Общайтесь на русском языке.",
                },
                {"role": "user", "content": f"{random_cards}, {message}"},
            ],
            stream=True,
        )

        for chunk in stream:
            if chunk.choices[0].delta.content is not None:
                yield chunk.choices[0].delta.content

    return generate(), {"Content-Type": "text/plain"}


@home_bp.route("/adminpanel", methods=["GET", "POST"])
@decorators.role_required('admin')
def adminpanel():
    return render_template('adminpanel.html')


@home_bp.route("/deleteuser", methods=["POST"])
def delete_user():
    username = request.form.get("username")
    user = db.session.scalars(db.select(User).where(User.username == username)).one_or_none()
    if not user:
        flash("Неверный username", category="error")
        return redirect(url_for("home.adminpanel"))
    try:
        db.session.delete(user)
        db.session.commit()
        flash(f"{user.username} удалён", category="error")
    except Exception as e:
        flash(f"{e}", category="error")
        db.session.rollback()

    return redirect(url_for("home.adminpanel"))


@home_bp.route("/edituser", methods=["POST"])
def edit_user():
    username = request.form.get("username")
    user = db.session.scalars(db.select(User).where(User.username == username)).one_or_none()

    if not user:
        flash("Неверный username", category="error")
        return redirect(url_for("home.adminpanel"))

    new_balance = request.form.get("balance")

    try:
        user.balance = request.form.get("balance")
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        flash(f"{e}", category="error")

    return redirect(url_for("home.adminpanel"))


@home_bp.route("/addicon", methods=["POST"])
def add_icon():
    icon = request.files["file"]
    icon_name = 'icon.webp'
    icon.save(os.path.join(current_app.config['UPLOAD_FOLDER'], icon_name))

    return redirect(url_for("home.adminpanel"))


@home_bp.route('/oferta', methods=["GET"])
def oferta():
    return render_template('oferta.html')
