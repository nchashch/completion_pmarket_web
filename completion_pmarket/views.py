import math
import django
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.template import loader
from .models import Market, Outcome, Position, Portfolio, Order
from .forms import BuyForm, SellForm, LoginForm, CreateMarketForm
import datetime


def index(request):
    markets_list = Market.objects.order_by('-start_date')[:5]
    template = loader.get_template('index.html')
    context = {
        'markets_list': markets_list,
    }
    return HttpResponse(template.render(context, request))

def portfolio(request):
    template = loader.get_template('portfolio.html')
    user_pk = request.user.pk
    portfolio = Portfolio.objects.get(user=user_pk)
    positions = Position.objects.all().filter(portfolio=portfolio)
    positions = [p for p in positions if p.volume != 0]
    for p in positions:
        p.outcome.percent = p.outcome.probability * 100
        p.expected_value = p.outcome.probability * p.volume
    context = {
        'portfolio': portfolio,
        'positions': positions,
    }
    return HttpResponse(template.render(context, request))

def market(request):
    outcomes_list = []
    market = None
    if request.GET:
        market = request.GET['pk']
        outcomes_list = Outcome.objects.order_by('outcome_date').filter(market=market)
        for o in outcomes_list:
            o.percent = o.probability * 100
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
            outcome.percent = outcome.probability * 100
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
    position_pk = request.GET['pk']
    position = Position.objects.get(pk=position_pk)
    position.outcome.percent = position.outcome.probability * 100
    position.expected_value = position.outcome.probability * position.volume
    context = {
        'position': position,
    }
    template = loader.get_template('position.html')
    return HttpResponse(template.render(context, request))

def cost_function(b, amounts):
    return b * math.log(sum((math.e ** (a / b) for a in amounts)))

def probabilities(b, amounts):
    s = sum((math.e ** (a/b) for a in amounts))
    return [(math.e ** (a/b)) / s for a in amounts]

# TODO: Update positions
# TODO: Add orders
def order(request):
    amount = 0
    market_pk = request.session['market']
    outcome_pk = request.session['outcome']
    market = Market.objects.get(pk=market_pk)
    outcome = Outcome.objects.get(pk=outcome_pk)
    portfolio = Portfolio.objects.get(user=request.user.pk)
    operation = 'Invalid'
    if request.method == 'POST':
        sell_form = SellForm(request.POST)
        buy_form = BuyForm(request.POST)
        if sell_form.is_valid():
            amount = sell_form.cleaned_data['amount']

    outcomes = Outcome.objects.all().filter(market=market.pk)
    new_outcomes = Outcome.objects.all().filter(market=market.pk)

    b = market.b
    if 'buy' in request.POST:
        operation = 'Buy'
        outcome.outstanding += amount
        for i, o in enumerate(new_outcomes):
            if o.pk == outcome.pk:
                new_outcomes[i].outstanding += float(amount)
    elif 'sell' in request.POST:
        operation = 'Sell'
        outcome.outstanding -= amount
        for i, o in enumerate(new_outcomes):
            if o.pk == outcome.pk:
                new_outcomes[i].outstanding += float(amount)

    old_amounts = (o.outstanding for o in outcomes)
    new_amounts = [o.outstanding for o in new_outcomes]
    cost = cost_function(b, new_amounts) - cost_function(b, old_amounts)

    position = Position.objects.all().filter(outcome=outcome, portfolio=portfolio)
    if position:
        position = position[0]
    else:
        position = Position()
        position.outcome = outcome
        position.market = outcome.market
        position.portfolio = portfolio

    if operation == 'Buy' and portfolio.cash < cost or amount < 0:
        return redirect('/outcome?pk={}'.format(outcome.pk))
    elif operation == 'Sell' and position.volume < amount or amount < 0:
        return redirect('/outcome?pk={}'.format(outcome.pk))
    outcome.save()
    outcome.old_percent = outcome.probability * 100
    portfolio.cash -= cost
    portfolio.save()

    order = Order()
    order.outcome = outcome
    order.portfolio = portfolio
    order.position = position
    order.timestamp = datetime.datetime.now()
    if operation == 'Buy':
        order.volume = amount
        position.volume += amount
    elif operation == 'Sell':
        order.volume = -amount
        position.volume -= amount
    position.save()
    order.save()
    probs = probabilities(b, new_amounts)
    outcomes = Outcome.objects.all().filter(market=market)
    for o, p in zip(outcomes, probs):
        o.probability = p
        o.save()
        if o.pk == outcome.pk:
            outcome.new_percent = o.probability * 100
    context = {
        'operation': operation,
        'amount': amount,
        'cost': cost,
        'outcome': outcome,
        'market': market,
        'datetime': order.timestamp,
    }
    template = loader.get_template('order.html')
    return HttpResponse(template.render(context, request))

def create_market(request):
    if request.method == 'POST':
        form = CreateMarketForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            b = form.cleaned_data['b']
            start_date = form.cleaned_data['start_date']
            end_date = form.cleaned_data['end_date']
            number_of_outcomes = (end_date - start_date).days
            market = Market(
                name = name,
                b = b,
                number_of_outcomes = number_of_outcomes,
                start_date = start_date,
                end_date = end_date
            )
            market.save()
            base = start_date
            date_list = [base + datetime.timedelta(days=x) for x in range(0, number_of_outcomes+1)]
            P = 1/number_of_outcomes
            for date in date_list:
                outcome = Outcome(
                    market = market,
                    outcome_date = date,
                    outstanding = 0,
                    probability = P)
                outcome.save()
            return redirect('/')
    else:
        form = CreateMarketForm()
    context = {
        'form': form,
    }
    template = loader.get_template('create_market.html')
    return HttpResponse(template.render(context, request))

def resolve_outcome(request):
    if request.user.is_superuser:
        if request.method == 'POST':
            outcome_pk = int(request.POST['pk'])
            outcome = Outcome.objects.get(pk=outcome_pk)
            market = outcome.market
            if market.resolved:
                return redirect('/')
            market.resolved = True
            market.save()
            outcome.winning = True
            outcome.save()
            outcome_positions = Position.objects.all().filter(outcome=outcome)
            positions = Position.objects.all().filter(market=market)
            for p in positions:
                p.closed = True
                p.save()
            outcomes = Outcome.objects.all().filter(market=market)
            amounts = [o.outstanding for o in outcomes]
            total_cash = cost_function(market.b, amounts)
            total_winning = (op.volume for op in outcome_positions)
            total_winning = sum(total_winning)

            for op in outcome_positions:
                share = op.volume/total_winning
                portfolio = op.portfolio
                portfolio.cash += share * total_cash
                portfolio.save()
            return redirect('/outcome?pk={}'.format(outcome_pk))
    else:
        return redirect('/')

def login_user(request):
    form = LoginForm(request.POST)
    if form.is_valid():
        username = form.cleaned_data['username']
        password = form.cleaned_data['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                return redirect('/')
            else:
                return redirect('login')
    template = loader.get_template('login.html')
    context = {
        'form': form,
    }
    return HttpResponse(template.render(context, request))

def signup(request):
    template = loader.get_template('signup.html')
    if request.method == 'POST':
        f = UserCreationForm(request.POST)
        if f.is_valid():
            user = f.save()
            portfolio = Portfolio()
            portfolio.user = user
            portfolio.name = user.username + '_portfolio'
            portfolio.cash = 0
            portfolio.save()
            login(request, user)
            return redirect('/')
    else:
        f = UserCreationForm()
    context = {
        "form": f,
    }
    return HttpResponse(template.render(context, request))

def logout_user(request):
    logout(request)
    return redirect('/')
