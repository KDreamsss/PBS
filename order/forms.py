from django import forms
from .models import Photographer, Order

class PhotographerRegisterForm(forms.ModelForm):
	class Meta:
		model = Photographer
		fields = '__all__'
		exclude = ('user', 'photographer' )


class ProfileUpdateForm(forms.ModelForm):
	class Meta:
		model = Photographer
		fields = ['devices', 'application', 'price', 'experience']

class NewOrderForm(forms.ModelForm):
	date = forms.DateField(widget=forms.DateInput(
        attrs={
            'type': 'date',
        }
    ))
	start_time = forms.TimeField(widget=forms.TimeInput(
		attrs={
            'type': 'time',
        }
	))
	end_time = forms.TimeField(widget=forms.TimeInput(
		attrs={
            'type': 'time',
        }
	))
	def __init__(self, *args, **kwargs):
		p, c = kwargs.pop('photographer'), kwargs.pop('customer')
		super(NewOrderForm, self).__init__(*args, **kwargs)
		self.fields['to_user1'].initial, self.fields['from_user1'].initial = p, c
		self.fields['to_user1'].disabled, self.fields['from_user1'].disabled = True, True
		self.fields['from_user1'].widget = forms.HiddenInput()

	place = forms.CharField(label = "Location")
	description = forms.CharField(label = "Photoshoot Description")
	# to_user1 = forms.CharField(label = "Selected Photographer")
	class Meta:
		model = Order
		fields = '__all__'
		exclude = ('status',)
