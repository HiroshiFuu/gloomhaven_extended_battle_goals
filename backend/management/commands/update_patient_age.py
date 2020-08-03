from django.core.management.base import BaseCommand

from backend.models import PatientInfo

from datetime import date


class Command(BaseCommand):
    help = "Update Patient Age"

    def handle(self, *args, **options):
    	count = 0
    	update_count = 0
    	total = len(PatientInfo.objects.all())
    	today = date.today()
    	for patientinfo in PatientInfo.objects.all():
    		age = today.year - patientinfo.dob.year - ((today.month, today.day) < (patientinfo.dob.month, patientinfo.dob.day))
    		if patientinfo.age != age:
	    		patientinfo.age = age
	    		patientinfo.save()
	    		print(patientinfo)
	    		update_count += 1
    		count += 1
    		print('{} / {} patients processed. {} patients updated.'.format(count, total, update_count))
    	print('Patient Age Updated')
