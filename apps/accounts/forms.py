from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth import authenticate


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={
        'class': 'form-control'
    }))
    phone = forms.CharField(required=True, max_length=11, widget=forms.TextInput(attrs={
        'class': 'form-control'
    }))

    class Meta:
        model = User
        fields = ['username', 'email', 'phone', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'class': 'form-control'})
        self.fields['password1'].widget.attrs.update({'class': 'form-control'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control'})
        self.fields['username'].error_messages = {
            'required': 'نام کاربری الزامی است.',
            'unique': 'این نام کاربری قبلاً ثبت شده است.',
        }
        self.fields['password1'].help_text = ''
        self.fields['password2'].help_text = ''

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if not phone.startswith('09') or len(phone) != 11 or not phone.isdigit():
            raise forms.ValidationError('شماره موبایل معتبر نیست. مثال: 09123456789')
        from apps.accounts.models import Profile
        if Profile.objects.filter(phone=phone).exists():
            raise forms.ValidationError('این شماره موبایل قبلاً ثبت شده است.')
        return phone

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('این ایمیل قبلاً ثبت شده است.')
        return email


class LoginForm(forms.Form):
    identifier = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'یوزرنیم، ایمیل یا شماره موبایل'
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'رمز عبور'
    }))
    remember_me = forms.BooleanField(required=False)

    def clean(self):
        identifier = self.cleaned_data.get('identifier')
        password = self.cleaned_data.get('password')

        if not identifier or not password:
            return self.cleaned_data

        user = None

        # ورود با یوزرنیم
        user = authenticate(username=identifier, password=password)

        # ورود با ایمیل
        if user is None:
            try:
                username = User.objects.get(email=identifier).username
                user = authenticate(username=username, password=password)
            except User.DoesNotExist:
                pass

        # ورود با شماره موبایل
        if user is None:
            try:
                from apps.accounts.models import Profile
                username = Profile.objects.get(phone=identifier).user.username
                user = authenticate(username=username, password=password)
            except Profile.DoesNotExist:
                pass

        if user is None:
            raise forms.ValidationError('اطلاعات وارد شده اشتباه است.')

        self.cleaned_data['user'] = user
        return self.cleaned_data
    
class EditProfileForm(forms.Form):
    first_name = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(required=False, widget=forms.EmailInput(attrs={'class': 'form-control'}))
    phone = forms.CharField(required=False, max_length=11, widget=forms.TextInput(attrs={'class': 'form-control'}))
    new_password = forms.CharField(required=False, widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    confirm_password = forms.CharField(required=False, widget=forms.PasswordInput(attrs={'class': 'form-control'}))

    def clean(self):
        new_password = self.cleaned_data.get('new_password')
        confirm_password = self.cleaned_data.get('confirm_password')
        if new_password and new_password != confirm_password:
            raise forms.ValidationError('رمز عبور و تکرار آن یکسان نیستند.')
        return self.cleaned_data    