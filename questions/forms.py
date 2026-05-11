from django import forms

from .models import Answer, Question, Tag


class QuestionForm(forms.ModelForm):
    tags = forms.CharField(
        required=False,
        label="Tags",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'python, django, web',
        }),
        help_text="Enter tags separated by commas",
    )

    class Meta:
        model = Question
        fields = ('title', 'text')
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter a brief question title',
            }),
            'text': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 8,
                'placeholder': 'Describe your problem in detail...',
            }),
        }

    def clean_tags(self):
        tags_str = self.cleaned_data.get('tags', '')
        return [t.strip() for t in tags_str.split(',') if t.strip()]

    def save(self, commit=True, author=None):
        question = super().save(commit=False)
        if author is not None:
            question.author = author
        if commit:
            question.save()
            tag_names = self.cleaned_data.get('tags', [])
            tags = []
            for name in tag_names:
                tag, _ = Tag.objects.get_or_create(name=name)
                tags.append(tag)
            question.tags.set(tags)
        return question


class AnswerForm(forms.ModelForm):
    class Meta:
        model = Answer
        fields = ('text',)
        widgets = {
            'text': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 6,
                'placeholder': 'Enter your answer...',
            }),
        }
