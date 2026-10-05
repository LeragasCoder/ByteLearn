from django import forms


class PurchaseForm(forms.Form):
    buyer_name = forms.CharField(
        label="نام و نام خانوادگی",
        max_length=120,
        widget=forms.TextInput(
            attrs={
                "class": "input",
                "autocomplete": "name",
                "placeholder": "نام و نام خانوادگی",
            }
        ),
        error_messages={
            "required": "نام را وارد کنید.",
            "max_length": "نام طولانی است.",
        },
    )
    buyer_email = forms.EmailField(
        label="ایمیل",
        widget=forms.EmailInput(
            attrs={
                "class": "input",
                "autocomplete": "email",
                "placeholder": "you@example.com",
                "inputmode": "email",
                "dir": "ltr",
            }
        ),
        error_messages={
            "required": "ایمیل را وارد کنید.",
            "invalid": "ایمیل واردشده معتبر نیست.",
        },
    )

    def clean_buyer_name(self):
        name = " ".join(self.cleaned_data["buyer_name"].split())
        if len(name) < 2:
            raise forms.ValidationError("نام باید حداقل دو حرف باشد.")
        return name

    def clean_buyer_email(self):
        return self.cleaned_data["buyer_email"].strip().lower()
