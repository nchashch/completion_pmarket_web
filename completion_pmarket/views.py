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

def portfolio(request):
    pass

def market(request):
    outcomes_list = []
    if request.GET:
        market = request.GET['m']
        outcomes_list = Outcome.objects.order_by('-outcome_date').filter(market=market)
    template = loader.get_template('market.html')
    context = {
        'outcomes_list': outcomes_list,
    }
    return HttpResponse(template.render(context, request))

def outcome(request):
    pass

def position(request):
    pass

def order(request):
    pass
