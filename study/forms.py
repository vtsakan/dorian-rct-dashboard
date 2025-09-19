from django import forms
# This import section brings the model names into this file
from .models import (
    Participant,
    Study,
    ClinicalAssessment,
    BiologicalSample,
    Neuroimaging,
    Question,
    Choice
)
from django.utils import timezone

class ParticipantCreationForm(forms.ModelForm):
    study = forms.ModelChoiceField(queryset=Study.objects.all())

    class Meta:
        model = Participant
        fields = ['study', 'date_of_birth', 'gender']
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'

    def save(self, commit=True):
        participant = super().save(commit=False)
        # The status is now set in the view, not the form.
        if commit:
            participant.save()
        return participant


class QuestionnaireForm(forms.Form):
    def __init__(self, *args, **kwargs):
        questions = kwargs.pop('questions')
        super().__init__(*args, **kwargs)
        for question in questions:
            choices = [(c.id, c.text) for c in question.choices.all()]
            self.fields[f'question_{question.id}'] = forms.ChoiceField(
                label=question.text,
                choices=choices,
                widget=forms.RadioSelect,
                required=True
            )

# --- FORMS FOR THE DATA ENTRY TILES ---

class ClinicalAssessmentForm(forms.ModelForm):
    class Meta:
        model = ClinicalAssessment
        exclude = ['visit']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'


class BiologicalSampleForm(forms.ModelForm):
    class Meta:
        model = BiologicalSample
        exclude = ['visit']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'


class NeuroimagingForm(forms.ModelForm):
    class Meta:
        model = Neuroimaging
        exclude = ['visit']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'