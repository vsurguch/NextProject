from datetime import datetime, time, timedelta

months = {
    1: 'Январь', 2: 'Февраль', 3: 'Март', 4: 'Апрель', 5: 'Май', 6: 'Июнь', 7: 'Июль', 8: 'Август', 9: 'Сентябрь',
    10: 'Октябрь', 11: 'Ноябрь', 12: 'Декабрь' }
months_declinated = {
    1: 'января', 2: 'февраля', 3: 'марта', 4: 'апреля', 5: 'мая', 6: 'июня', 7: 'июля', 8: 'августа', 9: 'сентября',
    10: 'октября', 11: 'ноября', 12: 'декабря' }


def date_format(date_time):
    return date_time.strftime('%d _ %Y г.').replace('_', months_declinated[date_time.month])

def datetime_from_str(date_string):
    return datetime.strptime(date_string, '%d-%m-%Y')


def slots_in_range(year, month, days, time_from, time_to, duration):
    slots = []
    from_ = datetime.strptime(time_from, '%H-%M')
    to_ = datetime.strptime(time_to, '%H-%M')
    slots_per_day = (to_ - from_) // timedelta(minutes=duration)
    # print('slots_per_day', slots_per_day)
    for day in days:
        proto_slot = datetime(year=year, month=month, day=day, hour=from_.hour, minute=from_.minute)
        for i in range(slots_per_day):
            slot = proto_slot.timestamp() + i * timedelta(minutes=duration).total_seconds()
            slots.append(slot)

    return slots


def test_slots_in_range():
    year = 2019
    month = 2
    days = [1, 2]
    time_from = '9-00'
    time_to = '14-00'
    duration = 15

    slots = slots_in_range(year, month, days, time_from, time_to, duration)
    slots_formatted = [datetime.fromtimestamp(slot) for slot in slots]
    for s in slots_formatted:
        print(s)

# if __name__ == '__main__':
#     test_slots_in_range()
