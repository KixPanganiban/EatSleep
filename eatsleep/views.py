import json

from datetime import date, datetime

from django.conf import settings
from django.views.generic import View
from django.http import HttpResponse
from django.shortcuts import render, redirect

from eatsleep.models import FoodLog, TargetCalories, SleepLog
from eatsleep.utils import format_foodlog_chart_json


class EatSleepView(View):
    context = {'version': settings.VERSION}
    template = 'base.html'

    def esv_render(self, request):
        request.session['error'] = None
        return render(request, self.template, self.context)


class Overview(EatSleepView):
    template = 'overview.html'

    def get(self, request):
        date_target_raw = request.GET.get('date', None)
        if not date_target_raw:
            date_target = date.today()
        else:
            try:
                date_target = datetime.strptime(
                    date_target_raw,
                    '%m-%d-%Y').date()
            except ValueError:
                date_target = date.today()
        total_calories = FoodLog.get_total_day_calories(date_target)
        target_obj = TargetCalories.get_day_target(date_target)
        try:
            percent = '%.2f' % (
                (total_calories / target_obj['calories']) * 100)
        except ZeroDivisionError:
            percent = '00.00'
        status = "Bad"
        if target_obj['type'] == 'lt':
            if float(percent) < 100.00:
                status = "Good"
        elif target_obj['type'] == 'ex':
            if float(percent) == 100.00:
                status = "Good"
        elif target_obj['type'] == 'gt':
            if float(percent) > 100.00:
                status = "Good"
        foodlogs = FoodLog.get_day_entries(date_target)
        self.context.update(
            {
                'title': 'Overview',
                'progress': {
                    'total': total_calories,
                    'target': target_obj,
                    'percent': percent,
                    'status': status
                },
                'foodlogs': foodlogs,
                'chart_foodlogs': format_foodlog_chart_json(foodlogs),
                'date': datetime.strftime(date_target, '%B %d, %Y'),
                'error': request.session['error'] if request.session['error']
                else None,
                'sleeplogs': SleepLog.get_sevenday_entries(),
                'chart_sleeplogs': json.dumps(
                    SleepLog.get_sevenday_entries_durations(
                        date_target))
            })
        return self.esv_render(request)


class Log(View):

    def handle_error(self, request, error):
        request.session['error'] = error
        return redirect('/overview/')

    def post(self, request):
        try:
            if not request.POST['type']:
                return self.handle_error(request, 'Broken form submission.')
            if request.POST.get('type') == 'food':
                for val in ['name', 'calories', 'date_submit', 'time_submit']:
                    if val not in request.POST:
                        return self.handle_error(request,
                                                 'Required field missing.')
                FoodLog(name=request.POST['name'],
                        calories=float(request.POST['calories']),
                        datetime=datetime.combine(
                            datetime.strptime(
                                request.POST['date_submit'],
                                '%m/%d/%Y').date(),
                            datetime.strptime(
                                request.POST['time_submit'],
                                '%H:%M').time()
                )).save()
            return redirect('/overview/')
        except Exception:
            return self.handle_error(request, 'Something went wrong.')
