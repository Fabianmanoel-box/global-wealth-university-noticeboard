from django import forms
from .models import Notice, Category


class NoticeForm(forms.ModelForm):
    class Meta:
        model = Notice
        fields = ['title', 'content', 'category', 'attachment',
                  'is_important', 'status', 'scheduled_at', 'expiry_date']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-uou focus:border-transparent',
                'placeholder': 'Enter notice title'
            }),
            'content': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-uou focus:border-transparent',
                'rows': 8,
                'placeholder': 'Write the full announcement...'
            }),
            'category': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-uou'
            }),
            'attachment': forms.FileInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg'
            }),
            'status': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg'
            }),
            'scheduled_at': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-uou focus:border-transparent bg-white',
                'placeholder': 'Leave empty to publish now',
                'autocomplete': 'off',
            }),
            'expiry_date': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-uou focus:border-transparent bg-white',
                'placeholder': 'Pick expiry date and time...',
                'autocomplete': 'off',
            }),
            'is_important': forms.CheckboxInput(attrs={
                'class': 'h-4 w-4 text-uou rounded'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # scheduled_at is optional
        self.fields['scheduled_at'].required = False
        self.fields['expiry_date'].required = False
        # Make date fields accept our format
        self.fields['scheduled_at'].input_formats = ['%Y-%m-%d %H:%M', '%Y-%m-%dT%H:%M']
        self.fields['expiry_date'].input_formats = ['%Y-%m-%d %H:%M', '%Y-%m-%dT%H:%M']


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'slug', 'description', 'color']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-uou'
            }),
            'slug': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-uou',
                'placeholder': 'auto-generated from name if left blank'
            }),
            'description': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg',
                'rows': 3
            }),
            'color': forms.Select(
                attrs={
                    'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg'
                },
                choices=[
                    ('blue', 'Blue'), ('green', 'Green'), ('red', 'Red'),
                    ('yellow', 'Yellow'), ('purple', 'Purple'), ('indigo', 'Indigo'),
                ]
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['slug'].required = False