from django.db import models
from django.contrib import auth

# Public
class Market(models.Model):
    b = models.FloatField(default=0.0)
    number_of_outcomes = models.IntegerField(default=1)
    start_date = models.DateTimeField('start date')
    end_date = models.DateTimeField('end date')

# Public
class Outcome(models.Model):
    market = models.ForeignKey(Market, on_delete=models.CASCADE)
    outcome_date = models.DateTimeField('outcome date')
    outstanding = models.IntegerField(default=0)
    probability = models.FloatField(default=0.0)

# Private
class Position(models.Model):
    outcome = models.ForeignKey(Outcome, on_delete=models.CASCADE)
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE)
    volume = models.IntegerField(default=0)
    active = models.BoolField(default=True)

# Private
class Order(models.Model):
    outcome = models.ForeignKey(Outcome, on_delete=models.CASCADE)
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE)
    position = models.ForeignKey(Position, on_delete=models.CASCADE, null=True)
    volume = models.IntegerField(default=0)
    executed = models.BoolField(default=False)

# Private
class Portfolio(models.Model):
    name = models.CharField(max_length=256)
    user = models.ForeignKey(auth.User, on_delete=models.CASCADE)