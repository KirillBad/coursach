from flask import Blueprint, render_template, request
from flask_login import current_user
import os, random, json
from openai import OpenAI
from . import config

client = OpenAI(api_key=config.OPENAI_API_KEY)

home_bp = Blueprint("home", __name__)


def random_card(card_number):
    current_dir = os.path.dirname(__file__)
    image_folder = os.path.join(current_dir, "static", "cards")
    all_cards = os.listdir(image_folder)
    selected_cards = [
        f.replace(".png", "") for f in random.sample(all_cards, card_number)
    ]
    return selected_cards


@home_bp.route("/", methods=["POST", "GET"])
def home():
    return render_template("home.html", user=current_user)


@home_bp.route("/answer", methods=["GET", "POST"])
def answer():
    data = request.get_json()
    message = data["message"]
    cards = data["card_number"]
    random_cards = random_card(int(cards))

    def generate():
        yield json.dumps({"cards": random_cards})
        stream = client.chat.completions.create(
            model="gpt-3.5-turbo-16k",
            messages=[
                {
                    "role": "system",
                    "content": "Задача прочитать карты Таро по представленным названиям, объяснить их значение, а затем ответить на вопрос в контексте этих карт. Пожалуйста, исключите любой диалог, который не является прямым ответом на вопрос или прямым разъяснением значения карт. Вам не требуется приветствовать пользователя или предоставлять неспецифическую информацию. Просто сконцентрируйтесь на интерпретации данных карт Таро и на ответе на специфический вопрос в контексте расклада. Ожидается, что вы будете обладать детальным знанием каждой карты таро в класическом колоде Райдер-Уайт и сможете адаптировать эти уникальные значения к заданному вопросу.",
                },
                {"role": "user", "content": f"{random_cards}, {message}"},
            ],
            stream=True,
        )

        for chunk in stream:
            if chunk.choices[0].delta.content is not None:
                yield chunk.choices[0].delta.content

    return generate(), {"Content-Type": "text/plain"}
