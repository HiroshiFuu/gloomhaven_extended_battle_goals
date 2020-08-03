from django.core.management.base import BaseCommand

from backend.models import Site
from backend.models import AnalysisSetting

import mysql.connector
from mysql.connector import Error

import json

class Command(BaseCommand):
    help = "Load X-Ray analysis setting"

    def add_arguments(self, parser):
        parser.add_argument('user', nargs='+', help='db user')
        parser.add_argument('password', nargs='+', help='db password')

    def handle(self, *args, **options):
        if len(options['user']) >= 0 and len(options['password']) >= 0:
            AnalysisSetting.objects.all().delete()
            Sites = Site.objects.all()
            site_count = len(Sites)
            try:
                connection = mysql.connector.connect(host='10.60.3.4',
                                                     port=3306,
                                                     database='medical_analysis',
                                                     user=options['user'][0],
                                                     password=options['password'][0])
                cursor = connection.cursor(dictionary=True)

                sql_select_Query = 'SELECT * FROM xray_analysis_settings'
                cursor.execute(sql_select_Query)
                setting = cursor.fetchone()
                for site in Sites:
                    AnalysisSetting.objects.create(threshold=json.loads(setting['threshold_json']), site=site)
                print('threshold setting loaded.')
            except Error as e:
                print('Error reading data from Mariadb {}'.format(port), e)
            finally:
                if connection:
                    if connection.is_connected():
                        connection.close()
                        cursor.close()
                        print('Mariadb connection is closed')