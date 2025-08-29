from django import forms
from django.core.validators import FileExtensionValidator


class CandidatureUploadForm(forms.Form):
    email = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'votre.email@example.com'
        })
    )
    
    cv_file = forms.FileField(
        label="CV (PDF)",
        validators=[FileExtensionValidator(allowed_extensions=['pdf'])],
        help_text="Format PDF uniquement, max 10 MB - Votre nom et prénom seront extraits automatiquement du CV",
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': '.pdf'
        })
    )
    
    def clean_cv_file(self):
        file = self.cleaned_data.get('cv_file')
        if file:
            # Check file size (10 MB max)
            if file.size > 10 * 1024 * 1024:
                raise forms.ValidationError("Le fichier ne doit pas dépasser 10 MB")
        return file