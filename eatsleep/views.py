from datetime import date, datetime

from django.conf import settings
from django.views.generic import View
from django.http import HttpResponse
from django.shortcuts import render

from eatsleep.models import FoodLog, TargetCalories
from eatsleep.utils import format_foodlog_chart_json


class EatSleepView(View):
    context = {'version': settings.VERSION}
    template = 'base.html'

    def esv_render(self, request):
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
            percent = '%.2f' % ((total_calories/target_obj['calories']) * 100)
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
                'date': datetime.strftime(date_target, '%B %d, %Y')
            })
        print self.context['date']
        return self.esv_render(request)
