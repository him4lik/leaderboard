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
