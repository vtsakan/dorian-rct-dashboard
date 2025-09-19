from django.contrib import admin
from .models import (
    Study,
    Participant,
    Visit,
    QuestionnaireTemplate,
    Question,
    Choice,
    VisitAssessment, # Using the new, correct model name
    Answer,
    # We are keeping these for future data entry steps
    ClinicalAssessment,
    BiologicalSample,
    Neuroimaging, 
    WearableDataPoint
)

# --- INLINES FOR BUILDING QUESTIONNAIRES ---
# This section allows you to create your questionnaires, questions, and choices
class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 3

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('text', 'questionnaire')
    list_filter = ('questionnaire',)
    inlines = [ChoiceInline]

class QuestionInline(admin.TabularInline):
    model = Question
    extra = 1
    fields = ('text', 'order')
    show_change_link = True

@admin.register(QuestionnaireTemplate)
class QuestionnaireTemplateAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    inlines = [QuestionInline]


# --- INLINES FOR MANAGING VISITS AND ASSESSMENTS ---
# These are for our new visit-centric workflow

class VisitAssessmentInline(admin.TabularInline):
    """Allows assigning questionnaires directly on the Visit page in the admin."""
    model = VisitAssessment
    extra = 1

# These are for the next step of data entry, but we can prepare them here
class ClinicalAssessmentInline(admin.StackedInline):
    model = ClinicalAssessment

class BiologicalSampleInline(admin.StackedInline):
    model = BiologicalSample

class NeuroimagingInline(admin.StackedInline):
    model = Neuroimaging


# --- ADMIN CONFIGURATIONS FOR CORE MODELS ---

@admin.register(Visit)
class VisitAdmin(admin.ModelAdmin):
    """The main admin page for a visit, showing all related data."""
    list_display = ('participant', 'visit_type', 'visit_date', 'is_complete')
    inlines = [
        VisitAssessmentInline,
        ClinicalAssessmentInline,
        BiologicalSampleInline,
        NeuroimagingInline
    ]

class VisitInline(admin.TabularInline):
    """Shows a summary of visits on the Participant's admin page."""
    model = Visit
    extra = 0 # Don't show empty slots for new visits here
    fields = ('visit_type', 'visit_date', 'is_complete')
    readonly_fields = ('visit_type', 'visit_date', 'is_complete')
    show_change_link = True # Allows clicking to the full visit page

@admin.register(Participant)
class ParticipantAdmin(admin.ModelAdmin):
    """The main admin page for a participant."""
    list_display = ('participant_id', 'status', 'study', 'enrollment_date')
    list_filter = ('status', 'study')
    search_fields = ('participant_id',)
    inlines = [VisitInline]
    # NOTE: Admin actions for eligibility/enrollment are removed,
    # as this is now handled by the main dashboard buttons.

# --- Simple registrations for other models ---
admin.site.register(Study)
admin.site.register(WearableDataPoint)