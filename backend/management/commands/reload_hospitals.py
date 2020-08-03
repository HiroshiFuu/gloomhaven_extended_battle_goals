from django.core.management.base import BaseCommand

from backend.models import Region
from backend.models import Province
from backend.models import Hospital

import json

class Command(BaseCommand):
    help = "Re-Load hospital records"

    def add_arguments(self, parser):
        parser.add_argument('rs_file', nargs='+', help='rs.json file path')

    def handle(self, *args, **options):
        with open(options['rs_file'][0]) as f:
            hospitals_data = json.load(f)
            for hospital_data in hospitals_data:
                wilayah = hospital_data['wilayah']
                province_name = wilayah.split(', ')[1]
                print(province_name)
                province = Province.objects.get(name=province_name)
                print(province)
                hospital = Hospital.objects.get(code=hospital_data['kode_rs'])
                hospital.province = province
                hospital.save()