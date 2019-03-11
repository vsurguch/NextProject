import functools
from datetime import datetime

from flask import (
    Blueprint, g, flash, redirect, render_template, request, session, url_for, current_app
)
from werkzeug.security import check_password_hash, generate_password_hash
from .db import get_db
from .email import send_mail


def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            session['requested_url'] = request.url
            return redirect(url_for('auth.login'))
        return view(**kwargs)
    return wrapped_view

def superuser_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None or g.user['superuser']==False:
            session['requested_url'] = request.url
            return redirect(url_for('auth.login'))
        return view(**kwargs)
    return wrapped_view


bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        name = request.form['name']
        password = request.form['password']
        password2 = request.form['confirm']
        email = request.form['email']
        phone = request.form['phone']
        db = get_db()

        error = None

        if not name:
            error = 'Необходимо задать имя пользователя'
        elif not password:
            error = 'Необходимо задать пароль'
        elif password != password2:
            error = 'Пароли не совпадают'
        elif not email:
            error = 'Необходимо задать e-mail'
        elif db.execute(
            'SELECT id FROM user WHERE email = ?', (email,)
        ).fetchone() is not None:
            error = 'Пользователь уже зарегистрирован'

        if error is None:
            db.execute(
                'INSERT INTO user (name, email, phone, password) VALUES (?, ?, ?, ?)',
                (name, email, phone, generate_password_hash(password))
            )
            db.commit()
            return redirect(url_for('auth.login'))

        flash(error)

    return render_template('auth/register.html')


@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        db = get_db()
        error = None

        if email is None:
            error = 'Incorrect email'
        else:
            user = db.execute('SELECT * FROM user WHERE email = ?', (email,)).fetchone()
            if user is None or (not check_password_hash(user['password'], password)):
                error = 'Incorrect password'

        if error is None:
            requested_url = session.get('requested_url')
            session.clear()
            session['user_id'] = user['id']

            if requested_url:
                return redirect(requested_url)
            else:
                return redirect(url_for('main.index'))

        flash(error)

    return render_template('auth/login.html')


@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')
    if user_id is not None:
        g.user = get_db().execute('SELECT * FROM user WHERE id = ?', (user_id,)).fetchone()
    else:
        g.user = None


@bp.route('/logout')
def logout():
    session.clear()
    g.user = None
    return redirect(url_for('main.index'))


@bp.route('/remind', methods=('GET', 'POST'))
def remind():
    if request.method == 'POST':
        email = request.form['email']
        code = 123
        expires = datetime.now()
        domain = current_app.config['DOMAIN_NAME']
        link = domain+url_for('auth.password_change', email=email, code=code)

        send_mail(email, 'Password change', link)

        db = get_db()
        db.execute('INSERT INTO pwchange (email, code, expires) VALUES (?, ?, ?)', (email, code, expires))
        db.commit()
        msg = 'Зайдите в почту и перейдите по ссылке изменения пароля.'
        flash(msg)
        return redirect(url_for('auth.login'))

    return render_template('auth/remind.html')


@bp.route('/password_change', methods=('GET', 'POST'))
def password_change():
    db = get_db()
    if request.method == 'GET':
        email = request.args['email']
        code = request.args['code']
        record = db.execute('SELECT * FROM pwchange WHERE email = ?', (email,)).fetchone()

        # print(record['expires'])

        error = None
        if record is None:
            error = 'Этот пользователь не запрашивал  изменение пароля'
        elif record['code'] != code:
            error = 'Не совпадает код подтверждения'

        if error is not None:
            flash(error)
            return redirect(url_for('auth.remind'))

        session['email_to_change'] = email

    elif request.method == 'POST':
        password = request.form['password']
        password2 = request.form['confirm']

        if password != password2:
            error = 'Пароль не совпадает'
            flash(error)
            return redirect(url_for('auth.password_change'))

        db.execute(
            'UPDATE user SET password=? WHERE email = ?',
            (generate_password_hash(password), session['email_to_change'])
        )
        # db.execute() # delete pwchange record
        db.commit()

        return redirect(url_for('auth.login'))

    return render_template('auth/password_change.html')


@bp.route('/edit', methods=('GET', 'POST'))
@login_required
def edit():
    if request.method == 'POST':
        old_email = g.user['email']
        user_id = g.user['id']
        email = request.form['email']
        name = request.form['name']
        phone = request.form['phone']
        password = request.form['password']
        password2 = request.form['confirm']
        db = get_db()

        error = None

        if not name:
            error = 'Необходимо задать имя пользователя'
        elif not email:
            error = 'Необходимо задать e-mail'
        elif not password:
            error = 'Необходимо задать пароль'
        elif (password != password2):
            error = 'Пароль не совпадает'
        elif (old_email != email) and db.execute(
                'SELECT id FROM user WHERE email = ?', (email,)
        ).fetchone() is not None:
            error = 'Пользователь с этим e-mail уже зарегистрирован'

        if error is None:
            db.execute(
                'UPDATE user SET name=?, email=?, phone=?, password=? WHERE id = ?',
                (name, email, phone, generate_password_hash(password), user_id)
            )
            db.commit()
            return redirect(url_for('main.index'))

        flash(error)

    return render_template('auth/profile.html')






