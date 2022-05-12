from django import forms
from .models import Comments, Post, Reports

class NewPostForm(forms.ModelForm):
	class Meta:
		model = Post
		fields = ['description', 'pic', 'tags']

class NewCommentForm(forms.ModelForm):

	class Meta:
		model = Comments
		fields = ['comment']

class NewReportForm(forms.ModelForm):

	class Meta:
		model = Reports
		fields = '__all__'