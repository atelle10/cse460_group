from django import forms

class ClubApplicationForm(forms.Form):
    club_name = forms.CharField(
        max_length=120,
        widget=forms.TextInput(attrs={'placeholder': 'Enter your club name'})
    )
    description = forms.CharField(
        widget=forms.Textarea(attrs={'placeholder': 'Provide a description for your club', 'rows': 4})
    )
    location = forms.CharField(
        max_length=120,
        widget=forms.TextInput(attrs={'placeholder': 'i.e., Main address or campus'})
    )
    categories = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={'placeholder': 'i.e., technology, sports, music (comma-separated)'})
    )