from django.urls import path
from . import views

urlpatterns = [
    # Core pages
    path('', views.dashboard, name='dashboard'),
    path('participant/add/', views.add_participant, name='add_participant'),
    path('participant/<int:participant_id>/', views.participant_detail, name='participant_detail'),
    path('participant/<int:participant_id>/create-visit/', views.create_visit, name='create_visit'),

    # Visit and Assessment URLs
    path('participant/<int:participant_id>/visit/<int:visit_id>/', views.visit_dashboard, name='visit_dashboard'),
    
    # The more specific 'questionnaires' URL now comes BEFORE the generic '<slug>' URL.
    path('participant/<int:participant_id>/visit/<int:visit_id>/questionnaires/', views.visit_questionnaires, name='visit_questionnaires'),
    path('participant/<int:participant_id>/visit/<int:visit_id>/assign-questionnaire/', views.assign_questionnaire, name='assign_questionnaire'),
    path('participant/<int:participant_id>/visit/<int:visit_id>/assessment/<int:assessment_id>/', views.take_questionnaire, name='take_questionnaire'),
    
    # The generic data entry URL is now last, to act as a catch-all.
    path('participant/<int:participant_id>/visit/<int:visit_id>/<slug:category_slug>/', views.visit_data_entry, name='visit_data_entry'),
    path('participant/<int:participant_id>/wearables/', views.wearable_dashboard, name='wearable_dashboard'),

]