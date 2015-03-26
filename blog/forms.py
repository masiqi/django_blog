from django import forms
from blog.models import Category, Blog, UserSettings, Comment

class WriteBlogForm(forms.ModelForm):
    title = forms.CharField(max_length=255, widget=forms.TextInput(attrs={'class':'aw_title'}))
    tags = forms.CharField(required=False, max_length=255, widget=forms.TextInput(attrs={'class':'aw_tags'}))
    summary = forms.CharField(widget=forms.Textarea(), required=False)
    
    class Meta:
        model = Blog
        exclude = ('user')
    
    def __init__(self, user=None, *args, **kwargs):
        self.user = user
        super(WriteBlogForm, self).__init__(*args, **kwargs)
        categories = Category.objects.filter(user=self.user).order_by('pk')
        choice = list()
        for c in categories:
            choice.append((c.id, c.name))
        self.fields['category'] = forms.ChoiceField(choices=choice)
    
    def clean_category(self):
        data = self.cleaned_data['category']
        return Category.objects.get(pk=data)
        
    def save(self, commit=True):
        if not self.cleaned_data.get("summary"):
            self.cleaned_data["summary"] = self.cleaned_data.get("content")[0:200]
        #print self.cleaned_data
        return super(WriteBlogForm, self).save(commit)
    
class ProfileForm(forms.ModelForm):
    class Meta:
        model = UserSettings
        exclude = ('user')
        
    def __init__(self, user=None, *args, **kwargs):
        self.user = user
        super(ProfileForm, self).__init__(*args, **kwargs)    

class WriteCommentForm(forms.ModelForm):
    blog = forms.CharField(widget=forms.HiddenInput())
    
    class Meta:
        model = Comment
        exclude = ('user')

    def clean_blog(self):
        data = self.cleaned_data['blog']
        return Blog.objects.get(pk=data)
        
#    def __init__(self, user=None, *args, **kwargs):
#        self.user = user
#        super(ProfileForm, self).__init__(*args, **kwargs)
