import json

from datetime import datetime, date, time


def day_timerange(day=date.today()):
    return (datetime.combine(day, time.min),
            datetime.combine(day, time.max))


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
