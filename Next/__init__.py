

from flask import Flask, render_template, template_rendered
from flask_mail import Mail
from . import db, main, appoint, auth, lk, admin


app = Flask(__name__)
app.config.from_object('config_next')

# def log_template_rendered(sender, template, context, **extras):
#     print(f'Rendered template {template.name} with context {context}')
#
# template_rendered.connect(log_template_rendered, app)

db.init_app(app)

mail = Mail()
mail.init_app(app)

app.register_blueprint(auth.bp)
app.register_blueprint(appoint.bp)
app.register_blueprint(main.bp)
app.register_blueprint(lk.bp)
app.register_blueprint(admin.bp)

