from django import forms
from django.contrib.auth.models import User

from blog.models import Post, Comment

class UserEditProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name','last_name','email')
        #fields = '__all__'

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('title','text','pub_date','location','category','image')
        widgets = {
            'pub_date': forms.DateInput(attrs={'type': 'datetime-local'}),
            'text': forms.Textarea(attrs={'rows': 5, 'cols': 22})
        } 

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)
        widgets = {
            'text': forms.Textarea(attrs={'rows': 5, 'cols': 22})
        }