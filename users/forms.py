from django import forms


class LoginForm(forms.Form):
    email = forms.CharField(label="input your email", max_length=100, widget=forms.TextInput(attrs={"class":"form-control form-control-md", "placeholder":"Enter your email"}))
    password = forms.CharField(max_length=32, widget=forms.PasswordInput(attrs={"class":"form-control form-control-md", "placeholder":"Enter your password"}))


class ResetPasswordForm(forms.Form):
    email = forms.CharField(label="input your email", max_length=100, widget=forms.TextInput(attrs={"class":"form-control form-control-md", "placeholder":"Enter your email"}))


class ChangePasswordForm(forms.Form):
    password = forms.CharField(max_length=32, widget=forms.PasswordInput(attrs={"class":"form-control form-control-md", "placeholder":"Enter your new password"}))
    password_confirmation = forms.CharField(max_length=32, widget=forms.PasswordInput(attrs={"class":"form-control form-control-md", "placeholder":"confirm your new password"}))
