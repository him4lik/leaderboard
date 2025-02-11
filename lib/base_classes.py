from datetime import datetime, timezone, time, timedelta
from django.db import models
from simple_history.admin import SimpleHistoryAdmin
from simple_history.models import HistoricalRecords
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import transaction
import datetime
from django import views
from django.shortcuts import render, HttpResponse, redirect, reverse


class BaseHistoryModel(models.Model):

    def changed_fields(self):
        if self.prev_record:
            delta = self.diff_against(self.prev_record)
            return delta.changed_fields
        return []

    def jsonify(self):
        return {
            'history_id': self.history_id,
            'changed_fields': self.changed_fields(),
            'changed_by': self.history_user.username if self.history_user else None,
            'history_date': str(self.history_date)
        }

    class Meta:
        abstract = True


class BaseModel(models.Model):
    history = HistoricalRecords(inherit=True, bases=[BaseHistoryModel])

    def set_field(self, data):
        change_flag = False
        for k,v in data.items():
            if getattr(self, k) != v:
                setattr(self, k, v)
                change_flag = True

        if change_flag:
            self.clean_strings()
            self.full_clean()
            self.save()

    def get_histories(self, start_date=None, end_date=None):
        histories = self.history.all()
        if start_date:
            histories = histories.filter(history_date__gte=start_date)
        if end_date:
            histories = histories.filter(history_date__lte=end_date)

        return histories.order_by('-history_date')

    def latest(self, dt=datetime.datetime.now()):
        if dt==None:
            dt=datetime.datetime.now()
        histories = self.history.all()
        if type(dt) is datetime.date:
            dt = dt + datetime.timedelta(days=1)
            dt = datetime.datetime(dt.year, dt.month, dt.day)
        dt = dt.replace(tzinfo=timezone.utc)
        sh_avail_date = datetime.datetime(2021, 1, 3).replace(tzinfo=timezone.utc)
        dt = max(dt, sh_avail_date)
        histories = histories.filter(history_date__lte=dt)

        return histories.order_by('-history_date').first()

    def oldest(self, dt=datetime.datetime.now()):
        histories = self.history.all()
        if type(dt) is datetime.date:
            dt = dt + datetime.timedelta(days=1)
            dt = datetime.datetime(dt.year, dt.month, dt.day)
        dt = dt.replace(tzinfo=timezone.utc)
        sh_avail_date = datetime.datetime(2021, 1, 3).replace(tzinfo=timezone.utc)
        dt = max(dt, sh_avail_date)
        histories = histories.filter(history_date__gte=dt)

        return histories.order_by('-history_date').last()

    def clean_strings(self):
        for f in self._meta.fields:
            if not type(f) in [models.CharField, models.TextField]: continue
            val = getattr(self, f.name)
            if val: setattr(self, f.name, ' '.join(val.split()))

    @classmethod
    def data_members_json(cls, instance=None):
        if instance:
            return cls.jsonify(instance)
        else:
            return {f.name: None for f in cls._meta.get_fields()}

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    class Meta:
        abstract = True

class CustomHistoryAdmin(SimpleHistoryAdmin):
    history_list_display = ['changed_fields']

    def changed_fields(self, obj):
        return ', '.join(obj.changed_fields())

    class Meta:
        abstract = True


class View(views.View):
    context = {}
    forms = [] 

class BaseView(views.View):

    def get_context_data(self, request):
        token = request.token
        context = {}
        forms = []

    def post_context_data(self, request):
        token = request.token
        context = {}
        forms = []

    def get(self, request):
        context = self.get_context_data(request)
        return render(request, self.template_name, context)

    def post(self, request):
        context = self.post_context_data(request)
        return render(request, self.template_name, context) 
