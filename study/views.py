from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.utils import timezone
from django.db import transaction
from django.utils import timezone
from django.db.models import Avg, Sum
import json

# Corrected imports for our new models
from .models import (
    Participant,
    Visit,
    VisitAssessment,
    QuestionnaireTemplate,
    Question,
    Choice,
    Answer,
    ClinicalAssessment,
    BiologicalSample,
    Neuroimaging,
    WearableDataPoint
)
from .forms import (
    ParticipantCreationForm,
    QuestionnaireForm,
    ClinicalAssessmentForm,
    BiologicalSampleForm,
    NeuroimagingForm
)

# --- Participant and Dashboard Views ---

@login_required
def dashboard(request):
    recent_participants = Participant.objects.order_by('-id')[:10]
    return render(request, 'study/dashboard.html', {'participants': recent_participants})

@login_required
def add_participant(request):
    if request.method == 'POST':
        form = ParticipantCreationForm(request.POST)
        if form.is_valid():
            participant = form.save(commit=False)
            participant.status = Participant.Status.SCREENING
            participant.save()
            Visit.objects.create(
                participant=participant,
                visit_type=Visit.VisitType.BASELINE,
                visit_date=timezone.now().date()
            )
            messages.success(request, f"Participant {participant.participant_id} created and Baseline visit scheduled.")
            return redirect('participant_detail', participant_id=participant.id)
    else:
        form = ParticipantCreationForm()
    return render(request, 'study/add_participant.html', {'form': form})

@login_required
def participant_detail(request, participant_id):
    participant = get_object_or_404(Participant, pk=participant_id)
    visits = Visit.objects.filter(participant=participant).order_by('visit_date')
    existing_visit_types = [v.visit_type for v in visits]
    all_possible_visits = Visit.VisitType.choices
    creatable_visits = [
        (code, label) for code, label in all_possible_visits
        if code not in existing_visit_types
    ]
    context = {
        'participant': participant,
        'visits': visits,
        'creatable_visits': creatable_visits,
    }
    return render(request, 'study/participant_detail.html', context)

@login_required
@require_POST
def create_visit(request, participant_id):
    participant = get_object_or_404(Participant, pk=participant_id)
    visit_type_to_create = request.POST.get('visit_type')
    if not visit_type_to_create:
        messages.error(request, "No visit type was selected.")
        return redirect('participant_detail', participant_id=participant.id)
    if Visit.objects.filter(participant=participant, visit_type=visit_type_to_create).exists():
        messages.warning(request, f"A {visit_type_to_create} visit already exists for this participant.")
    else:
        Visit.objects.create(
            participant=participant,
            visit_type=visit_type_to_create,
            visit_date=timezone.now().date()
        )
        messages.success(request, f"Successfully created the visit.")
    return redirect('participant_detail', participant_id=participant.id)


# --- Visit and Assessment Views ---

@login_required
def visit_dashboard(request, participant_id, visit_id):
    """Displays a dashboard with tiles for each data entry category for a visit."""
    participant = get_object_or_404(Participant, pk=participant_id)
    visit = get_object_or_404(Visit, pk=visit_id, participant=participant)
    
    # --- NEW LOGIC: Fetch the status for each category ---
    # We use try/except blocks in case the record hasn't been created yet.
    try:
        clinical_assessment = visit.clinical_assessment
    except ClinicalAssessment.DoesNotExist:
        clinical_assessment = None
        
    try:
        biological_sample = visit.biological_sample
    except BiologicalSample.DoesNotExist:
        biological_sample = None
        
    try:
        neuroimaging = visit.neuroimaging
    except Neuroimaging.DoesNotExist:
        neuroimaging = None

    # For questionnaires, we check if any have been completed for this visit.
    questionnaires_status = visit.assessments.filter(completed_at__isnull=False).order_by('-completed_at').first()

    context = {
        'participant': participant,
        'visit': visit,
        'clinical_assessment': clinical_assessment,
        'biological_sample': biological_sample,
        'neuroimaging': neuroimaging,
        'questionnaires_status': questionnaires_status,
    }
    return render(request, 'study/visit_dashboard.html', context)

@login_required
def visit_data_entry(request, participant_id, visit_id, category_slug):
    participant = get_object_or_404(Participant, pk=participant_id)
    visit = get_object_or_404(Visit, pk=visit_id, participant=participant)
    category_map = {
        'clinical-functional': (ClinicalAssessment, ClinicalAssessmentForm),
        'biological-samples': (BiologicalSample, BiologicalSampleForm),
        'neuroimaging': (Neuroimaging, NeuroimagingForm),
    }
    if category_slug not in category_map:
        messages.error(request, "Invalid data category specified.")
        return redirect('visit_dashboard', participant_id=participant_id, visit_id=visit_id)
    Model, Form = category_map[category_slug]
    instance = Model.objects.get_or_create(visit=visit)[0]
    if request.method == 'POST':
        form = Form(request.POST, request.FILES, instance=instance)
        if form.is_valid():
            form.save()
            messages.success(request, f"{category_slug.replace('-', ' ').title()} data saved successfully.")
            return redirect('visit_dashboard', participant_id=participant_id, visit_id=visit_id)
    else:
        form = Form(instance=instance)
    context = {
        'participant': participant,
        'visit': visit,
        'form': form,
        'category_name': category_slug.replace('-', ' ').title(),
    }
    return render(request, 'study/visit_data_entry.html', context)

@login_required
def visit_questionnaires(request, participant_id, visit_id):
    participant = get_object_or_404(Participant, pk=participant_id)
    visit = get_object_or_404(Visit, pk=visit_id, participant=participant)
    assessments = VisitAssessment.objects.filter(visit=visit)
    assigned_template_ids = assessments.values_list('questionnaire_template_id', flat=True)
    assignable_questionnaires = QuestionnaireTemplate.objects.exclude(id__in=assigned_template_ids)
    context = {
        'participant': participant,
        'visit': visit,
        'assessments': assessments,
        'assignable_questionnaires': assignable_questionnaires,
    }
    return render(request, 'study/visit_detail.html', context)

@login_required
@require_POST
def assign_questionnaire(request, participant_id, visit_id):
    visit = get_object_or_404(Visit, pk=visit_id, participant_id=participant_id)
    template_id = request.POST.get('questionnaire_template')
    if not template_id:
        messages.error(request, "No questionnaire was selected.")
    else:
        questionnaire_template = get_object_or_404(QuestionnaireTemplate, pk=template_id)
        VisitAssessment.objects.get_or_create(
            visit=visit,
            questionnaire_template=questionnaire_template
        )
        messages.success(request, f"Assigned '{questionnaire_template.name}' to this visit.")
    return redirect('visit_questionnaires', participant_id=visit.participant.id, visit_id=visit.id)

@login_required
def take_questionnaire(request, participant_id, visit_id, assessment_id):
    """Displays and processes the form for a specific questionnaire assessment."""
    assessment = get_object_or_404(VisitAssessment, pk=assessment_id, visit_id=visit_id)
    questions = assessment.questionnaire_template.questions.all()

    if request.method == 'POST':
        # This part for saving the form remains the same
        form = QuestionnaireForm(request.POST, questions=questions)
        if form.is_valid():
            total_score = 0
            with transaction.atomic():
                assessment.answers.all().delete() # Clear old answers before saving new ones
                for question in questions:
                    choice_id = form.cleaned_data[f'question_{question.id}']
                    selected_choice = get_object_or_404(Choice, pk=choice_id)
                    Answer.objects.create(
                        visit_assessment=assessment,
                        question=question,
                        selected_choice=selected_choice
                    )
                    total_score += selected_choice.value
                
                assessment.total_score = total_score
                assessment.completed_at = timezone.now() # Update the completion time
                assessment.save()
            
            messages.success(request, f"Assessment answers have been updated successfully.")
            return redirect('visit_questionnaires', participant_id=participant_id, visit_id=visit_id)
    else:
        # If the form has been completed before, create a dictionary of initial values.
        initial_data = {}
        if assessment.completed_at:
            for answer in assessment.answers.all():
                initial_data[f'question_{answer.question.id}'] = answer.selected_choice.id
        
        # Pass the initial_data to the form
        form = QuestionnaireForm(questions=questions, initial=initial_data)
        # --- END OF NEW LOGIC ---
            
    context = {
        'participant': assessment.visit.participant,
        'visit': assessment.visit,
        'assessment': assessment,
        'form': form
    }
    return render(request, 'study/take_questionnaire.html', context)

@login_required
def wearable_dashboard(request, participant_id):
    participant = get_object_or_404(Participant, pk=participant_id)

    # --- Prepare data for the last 24 hours ---
    one_day_ago = timezone.now() - timezone.timedelta(days=1)
    wearable_data_last_24h = WearableDataPoint.objects.filter(
        participant=participant,
        timestamp__gte=one_day_ago
    ).order_by('timestamp')

    # --- Calculate Summaries for the Tiles ---
    latest_bp = WearableDataPoint.objects.filter(participant=participant).exclude(blood_pressure_systolic__isnull=True).order_by('-timestamp').first()
    latest_spo2 = wearable_data_last_24h.exclude(spo2__isnull=True).last()
    avg_hr_last_24h = wearable_data_last_24h.aggregate(avg_hr=Avg('heart_rate'))
    today_start = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
    steps_today = WearableDataPoint.objects.filter(participant=participant, timestamp__gte=today_start).aggregate(total_steps=Sum('steps_count'))

    # --- Prepare data for the charts ---
    hr_labels = [data.timestamp.strftime('%H:%M') for data in wearable_data_last_24h if data.heart_rate]
    hr_data = [data.heart_rate for data in wearable_data_last_24h if data.heart_rate]
    
    spo2_labels = [data.timestamp.strftime('%H:%M') for data in wearable_data_last_24h if data.spo2]
    # --- THIS IS THE CORRECTED LINE ---
    # We convert the Decimal 'data.spo2' into a float
    spo2_data = [float(data.spo2) for data in wearable_data_last_24h if data.spo2]

    context = {
        'participant': participant,
        'latest_bp': latest_bp,
        'latest_spo2': latest_spo2,
        'avg_hr_last_24h': avg_hr_last_24h.get('avg_hr'),
        'steps_today': steps_today.get('total_steps'),
        'hr_labels': json.dumps(hr_labels),
        'hr_data': json.dumps(hr_data),
        'spo2_labels': json.dumps(spo2_labels),
        'spo2_data': json.dumps(spo2_data),
    }
    return render(request, 'study/wearable_dashboard.html', context)