import math
import django
from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from .models import Market, Outcome
from .forms import BuyForm, SellForm
from datetime import datetime

def create_market(name, b, number_of_outcomes, start_date, end_date):
    market = Market(name = name, b = b, number_of_outcomes = number_of_outcomes, start_date = start_date, end_date = end_date)
    market.save()
    for _ in range(number_of_outcomes):
        P = 1/number_of_outcomes
        outcome = Outcome(market = market, outcome_date = datetime.now(), outstanding = 0, probability = P)
        outcome.save()

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
    market = None
    if request.GET:
        market = request.GET['pk']
        outcomes_list = Outcome.objects.order_by('-outcome_date').filter(market=market)
        try:
            market = Market.objects.get(pk=market)
        except django.core.exceptions.ObjectDoesNotExist:
            market = []
    template = loader.get_template('market.html')
    context = {
        'outcomes_list': outcomes_list,
        'market': market,
    }
    return HttpResponse(template.render(context, request))

def outcome(request):
    outcome = []
    if request.GET:
        outcome = request.GET['pk']
        try:
            outcome = Outcome.objects.get(pk=outcome)
            market = Market.objects.get(pk=outcome.market.pk)
        except django.core.exceptions.ObjectDoesNotExist:
            outcome = []
            market = []
    template = loader.get_template('outcome.html')
    request.session['market'] = market.pk
    request.session['outcome'] = outcome.pk
    buy_form = BuyForm()
    sell_form = SellForm()
    context = {
        'buy_form': buy_form,
        'sell_form': sell_form,
        'outcome': outcome,
        'market': market,
    }
    return HttpResponse(template.render(context, request))

def position(request):
    context = {}
    template = loader.get_template('position.html')
    return HttpResponse(template.render(context, request))

def cost_function(b, amounts):
    return b * math.log(sum((math.e ** (a / b) for a in amounts)))

def probabilities(b, amounts):
    s = sum((math.e ** (a/b) for a in amounts))
    return [math.e ** (a/b) / s for a in amounts]

def order(request):
    amount = 0
    market_pk = request.session['market']
    outcome_pk = request.session['outcome']
    market = Market.objects.get(pk=market_pk)
    outcome = Outcome.objects.get(pk=outcome_pk)
    operation = 'Invalid'
    if request.method == 'POST':
        sell_form = SellForm(request.POST)
        buy_form = BuyForm(request.POST)
        if sell_form.is_valid():
            amount = sell_form.cleaned_data['amount']

    b = market.b
    outcomes = Outcome.objects.all()
    old_amounts = (o.outstanding for o in outcomes)
    new_amounts = old_amounts
    if 'buy' in request.POST:
        operation = 'Buy'
        outcome.outstanding += amount
    elif 'sell' in request.POST:
        operation = 'Sell'
        outcome.outstanding -= amount
    outcome.save()
    outcomes = Outcome.objects.all()
    new_amounts = [o.outstanding for o in outcomes]
    cost = cost_function(b, new_amounts) - cost_function(b, old_amounts)
    probs = probabilities(b, new_amounts)
    for o, p in zip(outcomes, probs):
        o.probability = p
        o.save()
    context = {
        'operation': operation,
        'amount': amount,
        'cost': cost,
        'outcome': outcome,
        'market': market,
        'datetime': datetime.now(),
    }
    template = loader.get_template('order.html')
    return HttpResponse(template.render(context, request))


def resolve_market(request):
    pass
