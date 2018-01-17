from django.forms import Form, ModelForm, CharField
from django.contrib.auth.hashers import check_password

from user.models import User


class RegisterForm(ModelForm):
    class Meta:
        model = User
        fields = ['nickname', 'password', 'head', 'age', 'sex']



class LoginForm(Form):
    nickname = CharField(max_length=64)
    password = CharField(max_length=64)

    def chk_password(self):
        nickname = self.cleaned_data['nickname']
        password = self.cleaned_data['password']

        try:
            user = User.objects.get(nickname=nickname)
            return user, check_password(password, user.password)
        except:
            return None, False
