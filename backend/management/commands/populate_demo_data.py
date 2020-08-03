from django.core.management.base import BaseCommand

from backend.models import Site
from backend.models import Hospital
from backend.models import MedicalImage
from backend.models import XrayAnalysisFinding
from backend.models import PatientInfo
from backend.models import AnalysisSetting

from backend.constants import MALE, FEMALE, DISEASES

from essential_generators import DocumentGenerator
from random_timestamp import random_timestamp
import random
import string
from datetime import date
import json


class Command(BaseCommand):
    help = "Populate demo data"

    def add_arguments(self, parser):
        parser.add_argument('data_date', nargs='+', help='data date(Y-m-d)')

    def handle(self, *args, **options):
        data_date = None
        date_str = options['data_date'][0]
        if date_str == 'reset':
            XrayAnalysisFinding.truncate()
            MedicalImage.truncate()
            PatientInfo.truncate()
            AnalysisSetting.truncate()
            Site.truncate()
            print('demo data truncated')
        elif date_str == 'today':
            data_date = date.today()
        else:
            from datetime import datetime
            format_str = '%Y-%m-%d' # The format
            data_date = datetime.strptime(date_str, format_str)
        if data_date is None:
            return

        image_rec_count = 0
        finding_rec_count = 0
        index = 0
        Hospitals = Hospital.objects.all()
        site_count = len(Hospitals)
        doc_gen = DocumentGenerator()
        today = date.today()

        for hospital in Hospitals:
            site = Site.objects.filter(hospital=hospital).first()
            if site is None:
                code = str(random.randint(10000, 30000))
                site = Site.objects.filter(code=code).first()
                while site is not None:
                    code = str(random.randint(10000, 30000))
                    site = Site.objects.filter(code=code).first()
                site = Site.objects.create(code=code, hospital=hospital)

            for i in range(random.randint(9, 30)):
                dob = random_timestamp(part='DATE')
                age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
                patient_info = PatientInfo.objects.create(date_acquired=data_date, name=doc_gen.name(), identity_no=self.gen_ic(), gender=random.choice([MALE, FEMALE]), dob=dob, age=age, modality='CT', site=site)

                medical_image = MedicalImage.objects.create(image_date=data_date, image_path='/demo_path', image_name='demo', site=site, patient_info=patient_info)
                image_rec_count += 1

                for disease in DISEASES:
                    xray_analysis_finding = XrayAnalysisFinding.objects.create(name=disease, value=random.randint(0, 100), medical_image=medical_image)
                    finding_rec_count += 1
            index += 1
            if index >= 0 or (image_rec_count > 0 and finding_rec_count > 0):
                print('{} / {} site(s) finished. {} image(s) added. {} finding(s) added.'.format(index, site_count, image_rec_count, finding_rec_count))
            
        if image_rec_count > 0 and finding_rec_count > 0:
            print('Done. Total {} image(s) added. Total {} finding(s) added.'.format(image_rec_count, finding_rec_count))

    def gen_ic(self):
        return random.choice(['S', 'G']) + ''.join([str(random.randint(0, 9)) for i in range(7)]) + random.choice(string.ascii_uppercase)