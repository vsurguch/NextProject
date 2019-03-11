
from flask import (
    Blueprint, g, session, request, render_template, redirect, flash, url_for
)
from sqlite3 import IntegrityError
from datetime import datetime, time, timedelta
from calendar import monthrange

from .db import insert, remove, get_slots

from .utils import months, date_format
from .auth import login_required

bp = Blueprint('appointment', __name__, url_prefix='/appointment')


@bp.route('/select_date', methods=['GET', 'POST'])
@login_required
def select_date():

    today = datetime.today()

    if 'next' in request.args:
        next_month_year = request.args['next'].split('-')
        next_month = next_month_year[0]
        next_year = next_month_year[1]
        month = int(next_month)
        year = int(next_year)
    else:
        month = today.month
        year = today.year

    month_name = months[month]
    first, ndays = monthrange(year, month)
    weeks = (first + ndays) // 7 + int(bool((first + ndays) % 7))

    if month == 1:
        prev_month_year = f'{12}-{year-1}'
        next_month_year = f'{2}-{year}'
    elif month == 12:
        prev_month_year = f'{11}-{year}'
        next_month_year = f'{1}-{year+1}'
    else:
        prev_month_year = f'{month-1}-{year}'
        next_month_year = f'{month+1}-{year}'

    if month == today.month and year == today.year:
        prev_active = False
    else:
        prev_active = True

    # get available dates
    raw_slots = get_slots(f'{1}-{month}-{year}', f'{ndays}-{month}-{year}')
    days = set()
    for row in raw_slots:
        day = datetime.fromtimestamp(row['slot']).day
        if day not in days:
            days.add(day)
    # dates = [datetime.fromtimestamp(row['slot']).day for row in raw_slots]
    # print(days)

    # build calendar
    get_date = lambda row, cell: row * 7 + cell - first + 1
    rows = [[('{}'.format(get_date(row, cell)), get_date(row, cell) in days) if
             (get_date(row, cell) > 0 and get_date(row, cell)<=ndays)
             else '' for cell in range(7) ]
            for row in range(weeks)]

    return render_template('appointment/select_date.html',
                           appointment_id=str(123),
                           rows=rows,
                           month=month,
                           year=year,
                           prev_month_year=prev_month_year,
                           next_month_year=next_month_year,
                           month_name=month_name,
                           prev_active=prev_active)


@bp.route('/select_time', methods=['GET', 'POST'])
@login_required
def select_time():
    print(request.form)
    if ('date' in request.form) and ('month' in request.form):
        date = int(request.form['date'])
        month = int(request.form['month'])
        year = int(request.form['year'])
        selected_date = datetime(year=year, month=month, day=date, hour=9, minute=0)
        session['selected_date'] = selected_date

        # get available times
        raw_slots = get_slots(f'{date}-{month}-{year}', f'{date+1}-{month}-{year}')
        times = []
        for row in raw_slots:
            hour = datetime.fromtimestamp(row['slot']).hour
            minute = datetime.fromtimestamp(row['slot']).minute
            time_slot = time(hour=hour, minute=minute)
            times.append(time_slot)

        slot_min = 30
        start_time = time(hour=9, minute=00)
        end_time = time(hour=16, minute=0)
        get_time = lambda hour, slot: time(hour=hour, minute=(slot_min * slot))
        check_active = lambda time_slot: time_slot in times
        rows = [[('{}'.format(get_time(hour, slot).strftime('%H - %M')), check_active(get_time(hour, slot)))
                 if (get_time(hour, slot) >= start_time and get_time(hour, slot) <= end_time) else ''
                 for slot in range(60 // slot_min)] for hour in range(start_time.hour, end_time.hour+1)]

        return render_template('appointment/select_time.html',
                               rows = rows,
                               selected_date = selected_date.strftime('%d/%m/%Y'))
    else:
        return redirect(url_for('appointment.select_date'))



@bp.route('/appoint_info', methods=['GET', 'POST'])
@login_required
def appoint_info():
    if 'slot' in request.args and 'selected_date' in session:
        time_data = request.args['slot'].split(' - ')
        selected_date = session['selected_date']
        session['selected_date'] = selected_date.replace(hour=int(time_data[0]), minute=int(time_data[1]))
        new_selected_date = session['selected_date']
        username = g.user['name']
        userphone = g.user['phone']
        useremail = g.user['email']
        return render_template('appointment/appoint_info.html',
                               selected_date = new_selected_date.strftime('%d/%m/%Y'),
                               selected_time=new_selected_date.strftime('%H:%M'),
                               username=username, userphone=userphone, useremail=useremail)
    else:
        return redirect('appointment.select_time')



@bp.route('/confirmation', methods=['GET', 'POST'])
@login_required
def confirmation():
    user_id = g.user['id']
    selected_date = session.get('selected_date')
    date = date_format(selected_date)
    stamp = selected_date.timestamp()

    try:
        insert('appointments', date_time=stamp, user_id=user_id)
        context = {
            'date': date,
            'time': selected_date.strftime('%H:%M')
        }
        res = remove('slots', 'slot', stamp)
    except IntegrityError:
        context = {
            'error_msg': 'Ошибка. Возможно данное время уже занято. Попробуйте выбрать другое время.',
        }

    return render_template('appointment/confirmation.html', context=context)





