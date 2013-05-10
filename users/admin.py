import datetime

from django import forms

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.contrib.auth.models import User

from users.models import DashboardUser

class UserCreateForm(forms.ModelForm):
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput, required=True)
    password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput, required=True)

    class Meta:
        model = DashboardUser
        fields = ('username', 'email', 'first_name', 'last_name')

    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError('Passwords don\'t match')
        return password2

    def save(self, commit=True):
        user = super(UserCreateForm, self).save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        user.date_joined = datetime.datetime.now()

        if commit:
            user.save()
        
        return user

class UserChangeForm(forms.ModelForm):
    password = ReadOnlyPasswordHashField()

    class Meta:
        model = DashboardUser

    def clean_password(self):
        # Regardless of what the user provides, return the initial value.
        # This is done here, rather than on the field, because the
        # field does not have access to the initial value
        return self.initial['password']


class DashboardUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'date_joined', 'is_active', 'is_staff')
    search_fields = ['email']
   
    filter_horizontal = () 
    
    add_form = UserCreateForm
    form = UserChangeForm
    
admin.site.register(DashboardUser, DashboardUserAdmin)
