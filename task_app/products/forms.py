from django import forms
from django.contrib.auth.forms import AuthenticationForm, UsernameField

from .models import Product


class LoginForm(AuthenticationForm):
    username = UsernameField(widget=forms.TextInput(attrs={
        'autofocus': True,
        'placeholder': 'Логін',
    }),
        label='')
    password = forms.CharField(
        label='',
        strip=False,
        widget=forms.PasswordInput(attrs={
            'autocomplete': 'current-password',
            'placeholder': 'Пароль',
        }),
    )


class ProductCreateForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'price']
        widgets = {
            'name': forms.TextInput(
                attrs={
                    'placeholder': '2 і більше символи',
                }
            ),
            'price': forms.NumberInput(
                attrs={
                    'placeholder': 'Має бути більше ніж 0',
                }
            )
        }

    def clean_name(self):
        data = self.cleaned_data.get('name')
        if len(data) < 2:
            raise forms.ValidationError('Назва має містини 2 і більше символів ')
        return data

    def clean_price(self):
        data = self.cleaned_data.get('price')
        if data <= 0:
            raise forms.ValidationError('Ціна має бути більше ніж 0')
        return data
