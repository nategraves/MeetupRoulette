from django import forms

class RandomMeetupForm(forms.Form):
	lat = forms.CharField(widget = forms.HiddenInput)
	lon = forms.CharField(widget = forms.HiddenInput)