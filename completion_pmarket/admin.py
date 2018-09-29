from django.contrib import admin
from .models import Portfolio, Market, Outcome, Position, Order

admin.site.register(Portfolio)
admin.site.register(Market)
admin.site.register(Outcome)
admin.site.register(Position)
admin.site.register(Order)
