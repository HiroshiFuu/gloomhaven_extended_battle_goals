from django.core.management.base import BaseCommand

from backend.models import Site
from backend.models import Hospital
from backend.models import MedicalImage
from backend.models import XrayAnalysisFinding
from backend.models import PatientInfo

from backend.constants import MALE, FEMALE

import mysql.connector
from mysql.connector import Error
import random
import string
from essential_generators import DocumentGenerator
from random_timestamp import random_timestamp

class Command(BaseCommand):
    help = "Load sites data"

    def add_arguments(self, parser):
        parser.add_argument('user', nargs='+', help='db user')
        parser.add_argument('password', nargs='+', help='db password')
    #     parser.add_argument('site_config', nargs='+', help='site.config file path')

    def handle(self, *args, **options):
        if len(options['user']) >= 0 and len(options['password']) >= 0:
            image_rec_count = 0
            finding_rec_count = 0
            Site.objects.all().delete()
            MedicalImage.truncate()
            XrayAnalysisFinding.truncate()
            PatientInfo.truncate()
            site_count = 10
            doc_gen = DocumentGenerator()
            
            for i in range(0, site_count):
                try:
                    Hospitals = Hospital.objects.all()
                    hospital = random.choice(Hospitals)
                    site = Site.objects.create(code=str(random.randint(10000, 30000)), hospital=hospital)
                    port = 3600 + i

                    connection = mysql.connector.connect(host='10.60.3.4',
                                                         port=port,
                                                         database='medical_analysis',
                                                         user=options['user'][0],
                                                         password=options['password'][0])
                    cursor = connection.cursor(dictionary=True)

                    sql_select_Query = 'SELECT * FROM upload_item'
                    cursor.execute(sql_select_Query)
                    upload_items = cursor.fetchall()
                    for item in upload_items:
                        medical_image = MedicalImage.objects.create(image_date=item['image_date'], image_path=item['image_path'], image_name=item['name'], image_size=item['size'], image_type=item['type'], site=site)
                        image_rec_count += 1

                        PatientInfo.objects.create(date_acquired=item['image_date'], name=doc_gen.name(), identity_no=self.gen_ic(), gender=random.choice([MALE, FEMALE]), dob=random_timestamp(part='DATE'), modality='CT', medical_image=medical_image)

                        sql_select_Query = 'SELECT f.name, f.value FROM upload_item as i INNER JOIN xray_analysis as a ON i.id = a.upload_item_id INNER JOIN xray_analysis_finding AS f ON a.id = f.analysis_id WHERE i.id = %s'

                        cursor.execute(sql_select_Query, (item['id'],))
                        xray_analysis_findings = cursor.fetchall()
                        for finding in xray_analysis_findings:
                            xray_analysis_finding = XrayAnalysisFinding.objects.create(name=finding['name'], value=finding['value'], medical_image=medical_image)
                            finding_rec_count += 1
                except Error as e:
                    print('Error reading data from Mariadb {}'.format(port), e)
                    break
                finally:
                    if connection:
                        if connection.is_connected():
                            connection.close()
                            cursor.close()
                            print('Mariadb connection is closed')
                if image_rec_count > 0 and finding_rec_count > 0:
                    print('{} / {} finished. {} image(s) added. {} finding(s) added.'.format(i+1, site_count, image_rec_count, finding_rec_count))
                
            if image_rec_count > 0 and finding_rec_count > 0:
                print('Done. Total {} image(s) added. Total {} finding(s) added.'.format(image_rec_count, finding_rec_count))

    def gen_ic(self):
        return random.choice(['S', 'G']) + ''.join([str(random.randint(0, 9)) for i in range(8)]) + random.choice(string.ascii_uppercase)