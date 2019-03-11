
from threading import Thread
from flask_mail import Mail, Message
from flask import current_app


def send_mail_func(app, msg):
    mail = Mail()
    with app.app_context():
        mail.send(msg)

def send_mail(recipient, subject, text):
    app = current_app._get_current_object()
    sender = 'vsurguch@yahoo.com'
    msg = Message(subject=subject, recipients=[recipient], sender=sender, body=text)
    thr = Thread(target=send_mail_func, args=[app, msg])
    thr.start()
    return thr



