from django.contrib import admin

from .models import PreparationPlan, PreparationTask

admin.site.register([PreparationPlan, PreparationTask])
