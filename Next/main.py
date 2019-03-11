
from flask import (
    Blueprint, g, flash, redirect, render_template, request, session, url_for
)
# from .admin import test_get_slots, test_add_slots

bp = Blueprint('main', __name__, url_prefix='')

@bp.route('/index', methods=('GET', 'POST'))
def index():
    # test_add_slots()
    # test_get_slots()
    return render_template('main/index.html')

@bp.route('/contacts', methods=('GET', 'POST'))
def contacts():
    return render_template('main/index.html')

@bp.route('/get_to', methods=('GET', 'POST'))
def get_to():
    return render_template('main/index.html')