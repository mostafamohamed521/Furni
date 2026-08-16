from django import forms


class CartAddProductForm(forms.Form):
    # A plain integer field (not a fixed 1-10 dropdown) so it matches what
    # the product detail page's quantity input actually allows — capping at
    # a sane upper bound just to prevent absurd values; the real stock limit
    # is enforced separately inside Cart.add().
    quantity = forms.IntegerField(
        min_value=1, max_value=999, initial=1,
        widget=forms.NumberInput(attrs={'class': 'form-control'}),
    )
    override = forms.BooleanField(required=False, initial=False, widget=forms.HiddenInput)
