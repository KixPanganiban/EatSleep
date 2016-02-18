from datetime import date as date_, timedelta, datetime

from django.db import models

from eatsleep.utils import multi_day_timerange, day_timerange


class FoodLog(models.Model):
    datetime = models.DateTimeField()
    name = models.CharField(max_length=32)
    calories = models.DecimalField(decimal_places=2, max_digits=6)
    comment = models.TextField(null=True, blank=True)

    def __unicode__(self):
        return "[%s] %s (%.2f calories)" % (self.datetime, self.name,
                                            self.calories)

    @classmethod
    def get_total_day_calories(cls, day=date_.today()):
        query = cls.objects.filter(datetime__range=day_timerange(day))
        if query.count() == 0:
            return 0.0
        return float(
            reduce(lambda m, n: m + n, map(lambda q: q.calories, query)))

    @classmethod
    def get_day_entries(cls, day=date_.today()):
        return cls.objects.filter(datetime__range=day_timerange(day))\
            .order_by('datetime')


class SleepLog(models.Model):
    datetime = models.DateTimeField()
    duration = models.DecimalField(decimal_places=2, max_digits=6)

    def __unicode__(self):
        return "[%s] %.2f hours" % (self.datetime, self.duration)

    @classmethod
    def get_sevenday_entries(cls, day=date_.today()):
        return cls.objects.filter(
            datetime__range=multi_day_timerange(
                day-timedelta(days=7),
                day))

    @classmethod
    def get_sevenday_entries_durations(cls, day=date_.today()):
        entries = []
        curr_day = day - timedelta(days=6)
        while (curr_day <= day):
            query_set = cls.objects.filter(
                datetime__range=day_timerange(curr_day))
            if query_set.count() > 0:
                items = query_set
            else:
                items = [0]
            entries.append((datetime.strftime(curr_day, '%m-%d-%Y'),
                           reduce(
                                  lambda m, n: m + n,
                                  map(
                                      lambda l: float(l.duration)
                                      if isinstance(l, SleepLog)
                                      else 0.0,
                                      items))))
            curr_day += timedelta(days=1)
        return entries


class WorkoutLog(models.Model):
    datetime = models.DateTimeField()
    name = models.CharField(max_length=32)
    calories = models.DecimalField(decimal_places=2, max_digits=6)
    comment = models.TextField(null=True, blank=True)


class TargetCalories(models.Model):
    date = models.DateField()
    calories = models.DecimalField(decimal_places=2, max_digits=6)
    type = models.CharField(choices=(('lt', 'Less Than'),
                                     ('ex', 'Exactly'),
                                     ('gt', 'Greater Than')),
                            max_length=2)

    def __unicode__(self):
        return "%s onwards: %s %.2f calories" % (self.date, self.type,
                                                 self.calories)

    @classmethod
    def get_day_target(cls, day=date_.today()):
        target_day = day
        match_count = cls.objects.filter(date=target_day).count()
        while (match_count < 1):
            target_day = target_day - timedelta(days=1)
            match_count = cls.objects.filter(date=target_day).count()

            if cls.objects.filter(date__lte=target_day).count() == 0:
                break

        try:
            obj = cls.objects.get(date=target_day)
        except cls.DoesNotExist:
            return {'type': 'ex', 'calories': 00.00}
        return {'type': obj.type, 'calories': float(obj.calories)}
