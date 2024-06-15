from flask import Blueprint, render_template, request, flash, redirect, url_for, current_app, session
from flask_login import current_user
from werkzeug.security import generate_password_hash
import os, random, json
from openai import OpenAI
from . import config, decorators, db
from .models import User

payments_bp = Blueprint("payments", __name__)

@payments_bp.route("/pay-once", methods=["GET", "POST"])
def pay_once():

    return render_template("pay-once.html")


@payments_bp.route("/pay-subscription", methods=["GET", "POST"])
def pay_subscription():

    return render_template("pay-subscription.html")