from django import forms
from django.utils.translation import ugettext, ugettext_lazy as _
from django.contrib.auth.models import User

class UserForm(forms.ModelForm):
   
    error_messages = {
        'password_mismatch': _("The two password fields didn't match."),
    }
    password1 = forms.CharField(label=_("Password"),
        widget=forms.PasswordInput)
    password2 = forms.CharField(label=_("Password confirmation"),
        widget=forms.PasswordInput,
        help_text=_("Enter the same password as above, for verification."))

    class Meta:
	    """Meta Class. This class defines the informations
	    that will be used based on existent set
	    from User Model.
	    """

	    model = User
	    fields = ('first_name', 'username')


    def clean_password2(self):
        """ Used to clean the password """
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError(
                self.error_messages['password_mismatch'],
                code='password_mismatch',
            )
        return password2

    def save(self, commit=True):
        """ Used to save the user """
        user = super(UserForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user