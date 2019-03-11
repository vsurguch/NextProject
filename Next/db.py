
from datetime import datetime
import sqlite3
import click
from flask import current_app, g
from flask.cli import with_appcontext
from werkzeug.security import generate_password_hash

from .utils import slots_in_range, datetime_from_str
# from .admin import add_slots

# database init/close
def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row

    return g.db


def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()


def init_db():
    db = get_db()

    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf8'))


# database routines
def insert(tablename, commit=True, **kwargs):
    db = get_db()
    fields = ', '.join(list(kwargs.keys()))
    values = list(kwargs.values())
    val_places = ', '.join(['?' for _ in range(len(values))])
    res = db.execute(f'INSERT INTO {tablename} ({fields}) VALUES ({val_places})', values)
    if commit:
        db.commit()
    return res

def remove(tablename, field, value, commit=True):
    db = get_db()
    res = db.execute(f'DELETE FROM {tablename} WHERE {field} = ?', (value,)).rowcount
    if commit:
        db.commit()
    return res


def commit():
    db = get_db()
    db.commit()


def select_one(tablename, search_field, search_value):
    db = get_db()
    res = db.execute(f'SELECT * FROM {tablename} WHERE {search_field} = ?', (search_value,)).fetchone()
    return res


def select_all(tablename, search_field=None, search_value=None, limit=-1, offset=0):
    db = get_db()
    if not search_field:
        res = db.execute(f'SELECT * FROM {tablename} LIMIT {limit} OFFSET {offset}').fetchall()
    else:
        res = db.execute(f'SELECT * FROM {tablename} WHERE {search_field} = ? LIMIT {limit} OFFSET {offset}',
                         (search_value,)).fetchall()
    return res


# specific requests
def add_superuser():
    insert('user', name='admin', email='email@email.com', password=generate_password_hash('admin'), superuser=1)


def add_slots(year, month, days, time_from, time_to, duration):
    slots = slots_in_range(year, month, days, time_from, time_to, duration)

    for slot in slots:
        insert('slots', commit=False, slot=slot)
    commit()


def get_slots(date_from, date_to):
    from_ = datetime_from_str(date_from).timestamp()
    to_ = datetime_from_str(date_to).timestamp()

    db_ = get_db()
    res = db_.execute('SELECT * FROM slots WHERE slot > ? AND slot < ?', (from_, to_)).fetchall()
    return res


def get_appointments(user_id=None, from_stamp=None, to_stamp=None, limit=-1, offset=0):
    db_ = get_db()
    clause = ''
    if user_id or from_stamp or to_stamp:
        add = ''
        userclause = ''
        fromclause = ''
        toclause = ''
        if user_id:
            userclause = f'a.user_id = {user_id}'
            add = 'AND'
        if from_stamp:
            fromclause = f' {add} a.date_time > {from_stamp}'
            add = 'AND'
        if to_stamp:
            toclause = f' {add} a.date_time <= {to_stamp}'
        clause = f'WHERE {userclause} {fromclause} {toclause}'

        print(clause)

    res = db_.execute(f'SELECT a.id AS id, a.date_time AS date, u.name AS name, u.phone as phone, u.email AS email '
                      f'FROM appointments AS a LEFT JOIN user AS u '
                      f'ON a.user_id=u.id {clause} LIMIT {limit} OFFSET {offset}')\
        .fetchall()
    return res


@click.command('init_db')
@with_appcontext
def init_db_command():
    init_db()
    click.echo('Initialized the db')

@click.command('add_superuser')
@with_appcontext
def add_superuser_command():
    add_superuser()
    click.echo('Superuser created')

@click.command('add_slots')
@click.argument('month')
@click.argument('year')
@click.argument('dates')
@with_appcontext
def add_slots_command(month, year, dates):
    print(month)
    print(year)
    dates_ = [int(date) for date in dates.split('-') if date != '']
    print(dates_)

    time_from = '9-00'
    time_to = '12-00'
    duration = 30

    add_slots(int(year), int(month), dates_, time_from, time_to, duration)

    test_slots = get_slots(f'{1}-{month}-{year}', f'{28}-{month}-{year}')

    for slot in test_slots:
        print(datetime.fromtimestamp(slot['slot']))


def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
    app.cli.add_command(add_superuser_command)
    app.cli.add_command(add_slots_command)
