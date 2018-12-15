from django.contrib.auth import authenticate
from django.contrib.auth.forms import UserCreationForm
from django import forms

class BuyForm(forms.Form):
    amount = forms.DecimalField(label='Amount')

class SellForm(forms.Form):
    amount = forms.DecimalField(label='Amount')

class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)

    def clean(self, *args, **kwargs):
        username = self.cleaned_data.get("username")
        password = self.cleaned_data.get("password")
        if username and password:
            user = authenticate(username=username, password=password)
            if not user:
                raise forms.ValidationError("User does not exist.")
            if not user.is_active:
                raise forms.ValidationError("User is no longer active.")
        return super(LoginForm, self).clean(*args, **kwargs)
