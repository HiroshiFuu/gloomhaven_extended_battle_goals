from django.core.management.base import BaseCommand

from backend.models import Region
from backend.models import Province
from backend.models import Hospital

import json

REGION_PROVINCE_MAPPING = {
    'ACEH': 'MEDAN',
    'SUMATERA UTARA': 'MEDAN',
    'SUMATERA BARAT': 'MEDAN',
    'RIAU': 'MEDAN',
    'KEPULAUAN RIAU': 'MEDAN',

    'JAMBI': 'JAKARTA',
    'SUMATRA SELATAN': 'JAKARTA',
    'SUMATERA SELATAN': 'JAKARTA',
    'BENGKULU': 'JAKARTA',
    'KEPULAUAN BANGKA BELITUNG': 'JAKARTA',
    'LAMPUNG': 'JAKARTA',
    'BANTEN': 'JAKARTA',
    'DKI JAKARTA': 'JAKARTA',
    'JAWA BARAT': 'JAKARTA',
    'JAWA TENGAH': 'JAKARTA',
    'DI YOGYAKARTS': 'JAKARTA',
    'KALIMANTAN BARAT': 'JAKARTA',
    'DAERAH ISTIMEWA YOGYAKARTA': 'JAKARTA',

    'JAWA TIMUR': 'SURABAYA',
    'BALI': 'SURABAYA',
    'KALIMANTAN TENGAH': 'SURABAYA',
    'KALIMANTAN UTARA': 'SURABAYA',
    'KALIMANTAN TIMUR': 'SURABAYA',
    'KALIMANTAN SELATAN': 'SURABAYA',

    'NUSA TENGGARA BARAT': 'MAKASSAR',
    'NUSA TENGGARA TIMUR': 'MAKASSAR',
    'SULAWESI BARAT': 'MAKASSAR',
    'SULAWESI SELATAN': 'MAKASSAR',
    'SULAWESI TENGGARA': 'MAKASSAR',
    'SULAWESI TENGAH': 'MAKASSAR',
    'GORONTALO': 'MAKASSAR',
    'SULAWESI UTARA': 'MAKASSAR',
    'MALUKU': 'MAKASSAR',
    'MALUKU UTARA': 'MAKASSAR',
    'PAPUA': 'MAKASSAR',
    'PAPUA BARAT': 'MAKASSAR',
}

#python .\manage.py load_hospitals "C:\Users\fenhao\Hewlett Packard Enterprise\CME @Innovation Lab - Indonesia Hopsitals\Feng Hao\mockdata\rs.json"
class Command(BaseCommand):
    help = "Load hospital records from rs.json"

    def add_arguments(self, parser):
        parser.add_argument('rs_file', nargs='+', help='rs.json file path')

    def handle(self, *args, **options):
        rec_count = 0
        if len(options['rs_file']) > 0:
            Hospital.truncate()
            Province.truncate()
            Region.truncate()
            with open(options['rs_file'][0]) as f:
                hospitals_data = json.load(f)
                for hospital_data in hospitals_data:
                    rec_count += 1
                    wilayah = hospital_data['wilayah']
                    print(rec_count, wilayah)
                    province_name = wilayah.split(', ')[1]
                    province_name = province_name.upper()
                    region_name = REGION_PROVINCE_MAPPING[province_name]
                    region_name = region_name.upper()
                    region = Region.objects.filter(name=region_name).first()
                    if region is None:
                        region = Region.objects.create(name=region_name)
                    province = Province.objects.filter(name=province_name).first()
                    if province is None:
                        province = Province.objects.create(name=province_name, region=region)
                    Hospital.objects.create(name=hospital_data['nama'], code=hospital_data['kode_rs'], beds=int(hospital_data['tempat_tidur']), telephone=hospital_data['telepon'], address=hospital_data['alamat'], type=hospital_data['tipe'], region=region, province=province, lng=hospital_data['lokasi']['lon'], lat=hospital_data['lokasi']['lat'], in_master_list=True)
                if rec_count > 0:
                    print('Done. Total {} hospital(s) added.'.format(rec_count))