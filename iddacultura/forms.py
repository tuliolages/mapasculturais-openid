# -*- coding: utf-8 -*-

from django import forms
from allauth.utils import set_form_field_order
from captcha.fields import ReCaptchaField
from openid_provider.models import OpenID


class OpenIDSignupForm(forms.Form):
    """
    Extende o formulário de registro de usuário para
    mais campos.
    """

    first_name = forms.CharField(label="Nome", max_length=30, help_text='',)
    last_name = forms.CharField(label="Sobrenome", max_length=30, help_text='')
    captcha = ReCaptchaField(attrs={'theme': 'white'})

    def __init__(self, *args, **kwargs):
        ret = super(OpenIDSignupForm, self).__init__(*args, **kwargs)

        first_fields = ['first_name', 'last_name']
        merged_field_order = list(self.fields.keys())

        for field in reversed(first_fields):
            merged_field_order.remove(field)
            merged_field_order.insert(0, field)

        merged_field_order.remove('captcha')
        merged_field_order.append('captcha')
        set_form_field_order(self, merged_field_order)

        return ret

    def signup(self, request, user):
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.save()
        oid = OpenID(user=user, default=True)
        oid.save()
