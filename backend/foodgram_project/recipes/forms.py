from django import forms

from .models import RecipeIngredient


class RecipeIngredientForm(forms.ModelForm):
    class Meta:
        model = RecipeIngredient
        fields = '__all__'

    def clean_amount(self):
        amount = self.cleaned_data.get('amount')
        if amount <= 0:
            raise forms.ValidationError(
                "Кол-во ингр-тов должно быть больше ноля."
            )
        return amount
