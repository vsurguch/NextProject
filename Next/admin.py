
# from .db import get_db, insert, commit
# from .utils import slots_in_range, datetime_from_str
import json
from sqlite3 import IntegrityError
from datetime import datetime
from flask import Blueprint, request, session, render_template
from .auth import superuser_required
from .db import select_all, select_one, get_appointments, remove, insert
from .utils import date_format

bp = Blueprint('admin', __name__, url_prefix='/admin')

@bp.route('/list', methods=['GET', 'POST'])
@superuser_required
def list():
    if request.method == 'POST':
        name = request.form.get('name')
        from_str = request.form.get('from')
        to_str = request.form.get('to')
        from_stamp = datetime.strptime(from_str, '%d/%m/%y').timestamp() if from_str and from_str != '' else None
        to_stamp = datetime.strptime(to_str, '%d/%m/%y').timestamp() if to_str and to_str != '' else None

        user = select_one('user', 'name', name) if name else None
        user_id = user['id'] if user else None
        raw_appointments = get_appointments(user_id=user_id, from_stamp=from_stamp, to_stamp=to_stamp)
    else:
        raw_appointments = get_appointments()

    appointments = []
    for item in raw_appointments:
        appointment = {
            'id': item['id'],
            'name': item['name'],
            'date': datetime.strftime(datetime.fromtimestamp(item['date']), '%d/%m/%Y %H:%M'),
            'phone': item['phone'],
            'email': item['email'],
        }
        appointments.append(appointment)
    context = {
        'appointments': appointments
    }
    return render_template('admin/list.html', context=context)


@bp.route('/delete_appointment', methods=['DELETE'])
@superuser_required
def delete_appointment():
    result = {'removed': 0}
    if request.method == 'DELETE':
        id = request.form.get('id')
        slot = select_one('appointments', 'id', id)['date_time']
        res = remove('appointments', 'id', id)
        result['removed'] = res
        try:
            insert('slots', slot=slot)
        except IntegrityError:
            pass

    return json.dumps(result)


# def test_add_slots():
#     year = 2019
#     month = 2
#     days = [1, 3, 5, 8]
#     time_from = '9-00'
#     time_to = '12-00'
#     duration = 30
#
#     # add_slots(year, month, days, time_from, time_to, duration)


# def test_get_slots():
#     date_from = '01-02-2019'
#     date_to = '05-03-2019'
#     from datetime import datetime
#     slots = get_slots(date_from, date_to)
#     for slot in slots:
#         print(datetime.fromtimestamp(slot['slot']))



