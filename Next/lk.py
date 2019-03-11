
import datetime
from flask import Blueprint, request, render_template, session, redirect, url_for, g
from .db import select_one
from .utils import date_format
from .auth import login_required


bp = Blueprint('lk', __name__, url_prefix='/lk')

@bp.route('/', methods=['GET',])
@login_required
def lk():
    user_id = g.user['id']

    appointment = select_one('appointments', 'user_id', user_id)
    context = {
        'superuser': g.user['superuser']
    }
    if appointment:
        stamp = appointment['date_time']
        date_time = datetime.datetime.fromtimestamp(stamp)
        date= date_format(date_time)
    else:
        date = ''

    return render_template('lk/lk.html', context=context)