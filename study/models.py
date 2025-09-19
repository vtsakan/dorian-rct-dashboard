# study/models.py

from django.db import models
from django.utils.translation import gettext_lazy as _

# --- Core Foundational Models ---

class Study(models.Model):
    """Represents a single clinical trial, e.g., 'DORIAN GRAY Project'."""
    name = models.CharField(max_length=200, unique=True, help_text=_("The official name of the study."))
    description = models.TextField(blank=True, null=True)
    start_date = models.DateField()
    end_date = models.DateField(blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Studies"


class Participant(models.Model):
    """Represents a single participant's journey through the study."""
    class Status(models.TextChoices):
        SCREENING = 'SCREENING', _('Screening')
        ELIGIBLE = 'ELIGIBLE', _('Eligible')
        ENROLLED = 'ENROLLED', _('Enrolled')
        WITHDRAWN = 'WITHDRAWN', _('Withdrawn')
        COMPLETED = 'COMPLETED', _('Completed')

    participant_id = models.CharField(max_length=100, unique=True, blank=True, help_text=_("Unique, anonymized identifier for the participant."))
    study = models.ForeignKey(Study, on_delete=models.PROTECT, related_name='participants')
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.SCREENING)
    enrollment_date = models.DateField(blank=True, null=True) # Populated when status becomes ENROLLED
    assigned_group_name = models.CharField(max_length=100, blank=True, null=True, help_text=_("Name of the assigned group, e.g., 'Intervention' or 'Control'"))

    # Basic demographics needed for eligibility/stratification
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=10, choices=[('MALE', 'Male'), ('FEMALE', 'Female'), ('OTHER', 'Other')])

    def save(self, *args, **kwargs):
        if not self.participant_id:
            last_participant = Participant.objects.filter(study=self.study).order_by('id').last()
            last_id = 0
            if last_participant:
                try:
                    last_id = int(last_participant.participant_id.split('-')[-1])
                except (ValueError, IndexError):
                    last_id = 0 # Fallback
            self.participant_id = f"DG-{self.study.id}-{last_id + 1:04d}"
        super().save(*args, **kwargs)

    def __str__(self):
        return self.participant_id

class Visit(models.Model):
    """Represents a scheduled data collection timepoint for a participant."""
    # --- MODIFY THIS PART ---
    class VisitType(models.TextChoices):
        BASELINE = 'BASELINE', _('Baseline Visit')
        VISIT1 = 'VISIT1', _('Visit 1 (6-Month)')
        VISIT2 = 'VISIT2', _('Visit 2 (12-Month)')
        EXIT = 'EXIT', _('Exit Visit')
    # --- END OF MODIFICATION ---

    participant = models.ForeignKey(Participant, on_delete=models.CASCADE, related_name='visits')
    visit_type = models.CharField(max_length=20, choices=VisitType.choices)
    visit_date = models.DateField()
    is_complete = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.participant.participant_id} - {self.get_visit_type_display()}"
    
    class Meta:
        unique_together = ('participant', 'visit_type')

# --- Data Collection Models (Based on the provided document) ---

class ClinicalAssessment(models.Model):
    """Stores data from clinical and functional assessments."""
    visit = models.OneToOneField(Visit, on_delete=models.CASCADE, related_name='clinical_assessment')
    
    # Fields from "Clinical & Functional Assessments" section 
    moca_score = models.IntegerField(blank=True, null=True, verbose_name="Montreal Cognitive Assessment (MoCA) score") # [cite: 9]
    ntb_results_summary = models.TextField(blank=True, null=True, verbose_name="Neuropsychological Test Battery (NTB) Results") # [cite: 10]
    nyha_class = models.CharField(max_length=10, blank=True, null=True, verbose_name="NYHA classification") # [cite: 11]
    six_minute_walk_test_meters = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True, verbose_name="6-minute walk test (meters)") # [cite: 12]
    tug_test_seconds = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True, verbose_name="Timed up-and-go (TUG) test (seconds)") # [cite: 13]

    def __str__(self):
        return f"Clinical Assessment for {self.visit}"


class BiologicalSample(models.Model):
    """Stores results from biological samples."""
    visit = models.OneToOneField(Visit, on_delete=models.CASCADE, related_name='biological_sample')

    # Fields from "Biological Sample Results" section [cite: 14]
    initial_blood_screening_summary = models.TextField(blank=True, null=True, help_text="B12, folate, thyroid, liver, kidney function") # [cite: 15]
    gfap = models.DecimalField(max_digits=10, decimal_places=4, blank=True, null=True, verbose_name="GFAP") # [cite: 16]
    nfl = models.DecimalField(max_digits=10, decimal_places=4, blank=True, null=True, verbose_name="NfL") # [cite: 16]
    abeta40_42_ratio = models.DecimalField(max_digits=10, decimal_places=4, blank=True, null=True, verbose_name="Abeta40/42 Ratio") # [cite: 16]
    ptau217 = models.DecimalField(max_digits=10, decimal_places=4, blank=True, null=True, verbose_name="ptau217") # [cite: 16]
    
    def __str__(self):
        return f"Biological Sample for {self.visit}"


class Neuroimaging(models.Model):
    """Stores confirmation of neuroimaging procedures."""
    visit = models.OneToOneField(Visit, on_delete=models.CASCADE, related_name='neuroimaging')

    # Fields from "Neuroimaging Data" section [cite: 17]
    mri_completed = models.BooleanField(default=False, verbose_name="Research MRI Completed") # [cite: 18, 33]
    mri_report = models.FileField(upload_to='mri_reports/', blank=True, null=True)
    mri_key_findings = models.TextField(blank=True, null=True) # [cite: 18]

    def __str__(self):
        return f"Neuroimaging for {self.visit}"


class Questionnaire(models.Model):
    """Stores results from patient-reported questionnaires."""
    visit = models.ForeignKey(Visit, on_delete=models.CASCADE, related_name='questionnaires')
    
    class QuestionnaireType(models.TextChoices):
        MLHF = 'MLHF', _('Minnesota Living with Heart Failure') # [cite: 20]
        EQ5D5L = 'EQ-5D-5L', _('Quality of Life (EQ-5D-5L)') # [cite: 21]
        HADS = 'HADS', _('Hospital Anxiety and Depression Scale') # [cite: 22]
        FAQ = 'FAQ', _('Functional Assessment Questionnaire') # [cite: 23]
        MIDI = 'MIDI', _('Measurement Instrument for Determinants of Innovations') # [cite: 24]

    name = models.CharField(max_length=10, choices=QuestionnaireType.choices)
    # Using a JSON field is highly flexible for storing various questionnaire scores
    results = models.JSONField(blank=True, null=True)

    def __str__(self):
        return f"{self.get_name_display()} for {self.visit}"


class WearableDataPoint(models.Model):
    """Represents a single point of passively collected data."""
    participant = models.ForeignKey(Participant, on_delete=models.CASCADE, related_name='wearable_data')
    timestamp = models.DateTimeField(db_index=True)
    
    # Example fields from "Wearable & Mobile Device Data" section [cite: 39]
    heart_rate = models.IntegerField(blank=True, null=True) # [cite: 40]
    hrv = models.IntegerField(blank=True, null=True, verbose_name="Heart Rate Variability") # [cite: 40]
    blood_pressure_systolic = models.IntegerField(blank=True, null=True) # [cite: 40]
    blood_pressure_diastolic = models.IntegerField(blank=True, null=True) # [cite: 40]
    spo2 = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True, verbose_name="SpO2") # [cite: 40]
    respiratory_rate = models.IntegerField(blank=True, null=True) # [cite: 40]
    steps_count = models.IntegerField(blank=True, null=True) # [cite: 40]

    def __str__(self):
        return f"Data for {self.participant.participant_id} at {self.timestamp}"

    class Meta:
        ordering = ['-timestamp']


# study/models.py (add these new models at the end)

# --- Questionnaire Template Models ---

class QuestionnaireTemplate(models.Model):
    """A template for a questionnaire, e.g., 'HADS', 'MoCA'."""
    name = models.CharField(max_length=100, unique=True, help_text=_("Name of the questionnaire (e.g., HADS)"))
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class Question(models.Model):
    """A single question within a QuestionnaireTemplate."""
    questionnaire = models.ForeignKey(QuestionnaireTemplate, on_delete=models.CASCADE, related_name='questions')
    text = models.CharField(max_length=500)
    order = models.PositiveIntegerField(help_text=_("The order in which the question appears."))

    def __str__(self):
        return self.text

    class Meta:
        ordering = ['order']


class Choice(models.Model):
    """A multiple-choice option for a Question."""
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='choices')
    text = models.CharField(max_length=200)
    value = models.IntegerField(help_text=_("The score/value for this choice."))

    def __str__(self):
        return f"{self.question.text[:30]}... - {self.text} ({self.value})"


# --- Participant-Specific Data Models ---

class VisitAssessment(models.Model):
    """Links a Questionnaire to a specific Visit where it needs to be completed."""
    visit = models.ForeignKey(Visit, on_delete=models.CASCADE, related_name='assessments')
    questionnaire_template = models.ForeignKey(QuestionnaireTemplate, on_delete=models.PROTECT)
    completed_at = models.DateTimeField(null=True, blank=True)
    total_score = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return f"{self.visit} - {self.questionnaire_template.name}"

    class Meta:
        unique_together = ('visit', 'questionnaire_template')


class Answer(models.Model):
    """Stores a participant's selected choice for a specific question."""
    visit_assessment = models.ForeignKey(VisitAssessment, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey(Question, on_delete=models.PROTECT)
    selected_choice = models.ForeignKey(Choice, on_delete=models.PROTECT)

    def __str__(self):
        return f"Answer for {self.visit_assessment}"
    

# --- Data Collection Models (Based on the provided document) ---

class ClinicalAssessment(models.Model):
    """Stores data from clinical and functional assessments."""
    visit = models.OneToOneField(Visit, on_delete=models.CASCADE, related_name='clinical_assessment')
    updated_at = models.DateTimeField(auto_now=True)

    # Fields from "Clinical & Functional Assessments" section
    moca_score = models.IntegerField(blank=True, null=True, verbose_name="Montreal Cognitive Assessment (MoCA) score")
    ntb_results_summary = models.TextField(blank=True, null=True, verbose_name="Neuropsychological Test Battery (NTB) Results")
    nyha_class = models.CharField(max_length=10, blank=True, null=True, verbose_name="NYHA classification")
    six_minute_walk_test_meters = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True, verbose_name="6-minute walk test (meters)")
    tug_test_seconds = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True, verbose_name="Timed up-and-go (TUG) test (seconds)")

    def __str__(self):
        return f"Clinical Assessment for {self.visit}"


class BiologicalSample(models.Model):
    """Stores results from biological samples."""
    visit = models.OneToOneField(Visit, on_delete=models.CASCADE, related_name='biological_sample')
    updated_at = models.DateTimeField(auto_now=True)

    # Fields from "Biological Sample Results" section
    initial_blood_screening_summary = models.TextField(blank=True, null=True, help_text="B12, folate, thyroid, liver, kidney function")
    gfap = models.DecimalField(max_digits=10, decimal_places=4, blank=True, null=True, verbose_name="GFAP")
    nfl = models.DecimalField(max_digits=10, decimal_places=4, blank=True, null=True, verbose_name="NfL")
    abeta40_42_ratio = models.DecimalField(max_digits=10, decimal_places=4, blank=True, null=True, verbose_name="Abeta40/42 Ratio")
    ptau217 = models.DecimalField(max_digits=10, decimal_places=4, blank=True, null=True, verbose_name="ptau217")
    
    def __str__(self):
        return f"Biological Sample for {self.visit}"


class Neuroimaging(models.Model):
    """Stores confirmation of neuroimaging procedures."""
    visit = models.OneToOneField(Visit, on_delete=models.CASCADE, related_name='neuroimaging')
    updated_at = models.DateTimeField(auto_now=True)

    # Fields from "Neuroimaging Data" section
    mri_completed = models.BooleanField(default=False, verbose_name="Research MRI Completed")
    mri_report = models.FileField(upload_to='mri_reports/', blank=True, null=True)
    mri_key_findings = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Neuroimaging for {self.visit}"