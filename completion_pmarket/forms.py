from django import forms

class BuyForm(forms.Form):
    amount = forms.DecimalField(label='Amount')

class SellForm(forms.Form):
    amount = forms.DecimalField(label='Amount')
