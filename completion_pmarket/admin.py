from django.contrib import admin
from .models import Portfolio
from .models import Market
from .models import Outcome
from .models import Position
from .models import Order

admin.site.register(Portfolio)
admin.site.register(Market)
admin.site.register(Outcome)
admin.site.register(Position)
admin.site.register(Order)
