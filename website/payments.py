from flask import Blueprint, render_template, redirect, request, flash, url_for
from flask_login import current_user
import uuid
from datetime import datetime, timedelta
from . import config, db, decorators
from .models import Payments, User
from yookassa import Configuration, Payment
from yookassa.domain.notification import WebhookNotificationEventType, WebhookNotificationFactory
from yookassa.domain.common import SecurityHelper

Configuration.account_id = config.YOOKASSA_ID
Configuration.secret_key = config.YOOKASSA_SECRET_KEY

payments_bp = Blueprint("payments", __name__)


@payments_bp.route("/pay-once", methods=["GET", "POST"])
@decorators.role_required('user')
def pay_once():

    return render_template("pay-once.html")


@payments_bp.route("/pay-subscription", methods=["GET", "POST"])
@decorators.role_required('user')
def pay_subscription():

    return render_template("pay-subscription.html")


type_to_description = {
    "1": {
        "10": "10 раскладов на gpttaro",
        "30": "30 раскладов на gpttaro",
        "50": "50 раскладов на gpttaro"
    },
    "2": {
        "7": "Подписка на 7 дней, безлимитное количество раскладов",
        "14": "Подписка на 14 дней, безлимитное количество раскладов",
        "30": "Подписка на 14 дней, безлимитное количество раскладов"
    }
}

@payments_bp.route("/payment-creation/")
def payment_creation():
    value = request.args.get("value")
    type = request.args.get("type")
    quantity = request.args.get("quantity")

    idempotence_key = str(uuid.uuid4())
    payment = Payment.create({
        "amount": {
            "value": f"{value}",
            "currency": "RUB"
        },
        "payment_method_data": {
            "type": "bank_card"
        },
        "confirmation": {
            "type": "redirect",
            "return_url": "https://gpttaro.online/"
        },
        "capture": True,
        "description": f"{type_to_description[type][quantity]}",
        "metadata": {
            "type": type,
            "quantity": quantity
        }
    }, idempotence_key)

    confirmation_url = payment.confirmation.confirmation_url
    print(payment['id'])

    new_payment = Payments(id=payment['id'], user_id=current_user.id, status=payment['status'], amount=payment['amount']['value'])

    try:
        db.session.add(new_payment)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        flash(f"{e}", category="error")
        return redirect(url_for("payments.pay_once"))

    return redirect(confirmation_url)


@payments_bp.route("/payments-handler")
def payments_handler():
    event_json = request.json
    ip = request.remote_addr
    print(request)
    print(event_json)
    if not SecurityHelper().is_ip_trusted(ip):
        return 400

    try:
        notification_object = WebhookNotificationFactory().create(event_json)
        response_object = notification_object.object
        if notification_object.event == WebhookNotificationEventType.PAYMENT_SUCCEEDED:
            print(response_object)
            payment = db.session.scalars(db.select(Payments).where(Payments.id == response_object.id))
            payment.status = response_object.status

            if response_object.metadata.type == "1":
                payment.user.balance += response_object.metadata.quantity
            if response_object.metadata.type == "2":
                payment.user.subscription_end = datetime.now() + timedelta(days=int(response_object.metadata.quantity))

            try:
                db.session.commit()
            except Exception as e:
                db.session.rollback()

        elif notification_object.event == WebhookNotificationEventType.PAYMENT_WAITING_FOR_CAPTURE:
            some_data = {
                'paymentId': response_object.id,
                'paymentStatus': response_object.status,
            }
        elif notification_object.event == WebhookNotificationEventType.PAYMENT_CANCELED:
            some_data = {
                'paymentId': response_object.id,
                'paymentStatus': response_object.status,
            }
        elif notification_object.event == WebhookNotificationEventType.REFUND_SUCCEEDED:
            some_data = {
                'refundId': response_object.id,
                'refundStatus': response_object.status,
                'paymentId': response_object.payment_id,
            }
        elif notification_object.event == WebhookNotificationEventType.DEAL_CLOSED:
            some_data = {
                'dealId': response_object.id,
                'dealStatus': response_object.status,
            }
        elif notification_object.event == WebhookNotificationEventType.PAYOUT_SUCCEEDED:
            some_data = {
                'payoutId': response_object.id,
                'payoutStatus': response_object.status,
                'dealId': response_object.deal.id,
            }
        elif notification_object.event == WebhookNotificationEventType.PAYOUT_CANCELED:
            some_data = {
                'payoutId': response_object.id,
                'payoutStatus': response_object.status,
                'dealId': response_object.deal.id,
            }
        else:
            return 400

        payment_info = Payment.find_one(some_data['paymentId'])
        if payment_info:
            payment_status = payment_info.status
            print(payment_status)
        else:
            return 400

    except Exception:
        return 400

    return 200
