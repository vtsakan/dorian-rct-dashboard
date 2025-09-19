import random
from datetime import timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from study.models import Participant, WearableDataPoint

class Command(BaseCommand):
    help = 'Generates a batch of random wearable data for a specific participant.'

    def add_arguments(self, parser):
        # This defines a required command-line argument: the participant's ID
        parser.add_argument('participant_id', type=int, help='The ID of the participant to add data for.')

    def handle(self, *args, **options):
        participant_id = options['participant_id']
        
        try:
            participant = Participant.objects.get(pk=participant_id)
        except Participant.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'Participant with ID "{participant_id}" does not exist.'))
            return

        self.stdout.write(f"Generating 100 sample data points for participant {participant.participant_id}...")

        # We'll generate data for the last 24 hours
        now = timezone.now()
        data_points_to_create = []

        for i in range(100):
            # Create a data point at a random time in the last 24 hours
            random_timestamp = now - timedelta(minutes=random.randint(1, 24 * 60))
            
            data_point = WearableDataPoint(
                participant=participant,
                timestamp=random_timestamp,
                heart_rate=random.randint(60, 100),
                hrv=random.randint(20, 70),
                blood_pressure_systolic=random.randint(110, 130),
                blood_pressure_diastolic=random.randint(70, 85),
                spo2=round(random.uniform(95.0, 99.5), 2),
                respiratory_rate=random.randint(12, 20),
                steps_count=random.randint(50, 200) # Simulating periodic step updates
            )
            data_points_to_create.append(data_point)

        # Use bulk_create for efficiency - it's much faster than saving one by one
        WearableDataPoint.objects.bulk_create(data_points_to_create)

        self.stdout.write(self.style.SUCCESS(f'Successfully added 100 data points for participant {participant.participant_id}.'))