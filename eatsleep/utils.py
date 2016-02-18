import json

from datetime import datetime, date, time


def multi_day_timerange(day_a=date.today(), day_b=date.today()):
    return (datetime.combine(day_a, time.min),
            datetime.combine(day_b, time.max))


def day_timerange(day=date.today()):
    return multi_day_timerange(day, day)


def format_foodlog_chart_json(items):
    preformatted = {}
    output = []
    for item in items:
        if item in output:
            preformatted[item.name] += float(item.calories)
        else:
            preformatted[item.name] = float(item.calories)
    for key, val in preformatted.iteritems():
        output.append((key, val))
    output_json = json.dumps(output)
    return output_json[0:len(output_json)-1]
