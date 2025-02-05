from django import forms
from .models import Product, Review

class SearchForm(forms.Form):
    query = forms.CharField(
        label='検索キーワード',
        max_length=100, 
        required=False,
        widget=forms.TextInput(attrs={'placeholder': '検索したいキーワードを入力'})
    )

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'description', 'price', 'category', 'image']

#レビューするために必要
class ReviewForm(forms.ModelForm):
    RATING_CHOICES = [(i, "★" * i) for i in range(1, 6)]  # 1〜5の星
    
    rating = forms.ChoiceField(
        choices=RATING_CHOICES, 
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'})
    )

    class Meta:
        model = Review
        fields = ['rating', 'comment']
        widgets = {
            'comment': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }