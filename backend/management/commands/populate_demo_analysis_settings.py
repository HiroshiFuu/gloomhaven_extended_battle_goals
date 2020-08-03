from django.core.management.base import BaseCommand

from backend.models import Site
from backend.models import AnalysisSetting

from backend.constants import DISEASES

import random
import json

class Command(BaseCommand):
    help = "Populate X-Ray Analysis Settings"

    def handle(self, *args, **options):
        AnalysisSetting.truncate()

        for site in Site.objects.all():
            setting = {}
            for disease in DISEASES:
                setting[disease] = random.randint(0, 100)
            AnalysisSetting.objects.create(threshold=json.dumps(setting), site=site)