from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from .models import Market, Outcome

# Create your views here.
def index(request):
    markets_list = Market.objects.order_by('-start_date')[:5]
    template = loader.get_template('index.html')
    context = {
        'markets_list': markets_list,
    }
    return HttpResponse(template.render(context, request))
