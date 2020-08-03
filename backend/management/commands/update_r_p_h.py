from django.core.management.base import BaseCommand

from backend.models import Region
from backend.models import Province
from backend.models import Hospital

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


class Command(BaseCommand):
    help = "Re-map Region Province Mapping"

    def handle(self, *args, **options):
        for province in Province.objects.all():
            region_name = REGION_PROVINCE_MAPPING[province.name]
            region = Region.objects.filter(name=region_name).first()
            if region_name != region.name:
                print(province.name, '|', region_name, '|', region.name)
            province.region = region
            province.save()
        print('Province Done.')
        for hospital in Hospital.objects.all():
            if hospital.region.name != hospital.province.region.name:
                print(hospital.name, '|', hospital.region.name, '|', hospital.province.region.name)
            hospital.region = hospital.province.region
            hospital.save()
        print('Hospital Done.')