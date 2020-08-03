from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.contrib.auth.models import User
from django.conf import settings

from django.db.models import Count
from django.db.models import Case
from django.db.models import When
from django.db.models import Value
from django.db.models import CharField

from rest_framework.authtoken.serializers import AuthTokenSerializer
from rest_framework import status
from rest_framework import schemas
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token
from rest_framework.decorators import authentication_classes
from rest_framework.permissions import AllowAny
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .models import Region
from .models import Hospital
from .models import PatientInfo
from .models import XrayAnalysisFinding
from .models import Site
from .models import AnalysisSetting
from .models import MedicalImage

from .serializers import UserSerializer
from .serializers import HealthStatsSerializer
from .serializers import DetailedHealthStatsSerializer
from .serializers import TimeseriesHealthStatsSerializer
from .serializers import HospitalSerializer
from .serializers import RegionSerializer

from backend.constants import MALE, FEMALE, DISEASES, AGE_GROUPS, AGE_GROUPS_VALUES

import json
from datetime import date, datetime, timedelta
from collections import defaultdict
import copy

VERSION_PARAMETER = openapi.Parameter('version', openapi.IN_PATH, required=True, description='API Version', type=openapi.TYPE_STRING, default='v1')

START_DATE_PARAMETER = openapi.Parameter('startDate', openapi.IN_QUERY, required=True, description='Start Date', type=openapi.TYPE_STRING, default='2020-06-10')

END_DATE_PARAMETER = openapi.Parameter('endDate', openapi.IN_QUERY, required=False, description='End Date', type=openapi.TYPE_STRING, default='2020-06-15')

RESPONSE_400_DATA = {
    'status': 400,
    'error': 'BAD REQUEST',
    'message': None
}

RESPONSE_401_DATA = {
    'status': 401,
    'error': 'UNAUTHORIZED',
    'message': None
}

RESPONSE_500_DATA = {
    'status': 500,
    'error': 'INTERNAL SERVER ERROR',
    'message': None
}

RESPONSE_404_VERSION = {
    'status': 404,
    'error': 'NOT FOUND',
    'message': 'version number not found'
}

RESPONSE_404_ENDPOINT = {
    'status': 404,
    'error': 'NOT FOUND',
    'message': 'this endpoint does not exist'
}

GENDER_VALUES = {
    'male': 0,
    'female': 0
}

AGE_GROUP_VALUES = {
    '0-5': 0,
    '6-17': 0,
    '18-30': 0,
    '31-45': 0,
    '46-59': 0,
    '60+': 0
}

HEALTH_STATS_DATA = {
    'total': 0,
    'gender': copy.deepcopy(GENDER_VALUES),
    'ageGroup': copy.deepcopy(AGE_GROUP_VALUES),
}

TEST_DATA_DATE = '2020-06-10'

REST_FRAMEWORK = getattr(settings, 'REST_FRAMEWORK', None)
ALLOWED_VERSIONS = REST_FRAMEWORK.get('ALLOWED_VERSIONS', '')

from ipware import get_client_ip

# Create your views here.
def get_health_stats_data_from_hospitals(hospitals, image_date=TEST_DATA_DATE):
    # print(image_date)
    health_stats = copy.deepcopy(HEALTH_STATS_DATA)
    # print(health_stats)
    # diseases = defaultdict(int)
    diseases = {}
    disease_details = copy.deepcopy(HEALTH_STATS_DATA)
    for disease in DISEASES:
        diseases[disease.lower()] = copy.deepcopy(disease_details)
    # print(diseases)
    if type(hospitals) == Hospital:
        hospitals = [hospitals]
    for hospital in hospitals:
        filteredXrayAnalysisFindings = XrayAnalysisFinding.objects.filter(medical_image__site__hospital=hospital, medical_image__image_date=image_date)
        ageGroupedFilteredXrayAnalysisFindings = filteredXrayAnalysisFindings.values('name', 'value', 'medical_image__patient_info__gender', 'medical_image__patient_info__age').annotate(
                medical_image__patient_info__age_group=Case(
                    When(medical_image__patient_info__age__lte=5, then=Value('0-5')),
                    When(medical_image__patient_info__age__gt=5, medical_image__patient_info__age__lte=17, then=Value('6-17')),
                    When(medical_image__patient_info__age__gt=17, medical_image__patient_info__age__lte=30, then=Value('18-30')),
                    When(medical_image__patient_info__age__gt=30, medical_image__patient_info__age__lte=45, then=Value('31-45')),
                    When(medical_image__patient_info__age__gt=45, medical_image__patient_info__age__lte=59, then=Value('46-59')),
                    When(medical_image__patient_info__age__gt=59, then=Value('60+')),
                    output_field=CharField(),
                )
            )
        # print(ageGroupedFilteredXrayAnalysisFindings)
        analysis_setting = AnalysisSetting.objects.get(site__hospital=hospital)
        threshold = json.loads(analysis_setting.threshold)
        for finding in ageGroupedFilteredXrayAnalysisFindings:
            # print(finding['name'], finding['medical_image__patient_info__gender'], finding['medical_image__patient_info__age_group'])
            diagnosed = True
            name = finding['name']
            if name in threshold:
                if finding['value'] < threshold[name]:
                    diagnosed = False
            if diagnosed:
                health_stats['total'] += 1
                health_stats['gender'][finding['medical_image__patient_info__gender']] += 1
                health_stats['ageGroup'][finding['medical_image__patient_info__age_group']] += 1
                name = name.lower()
                diseases[name]['total'] += 1
                diseases[name]['gender'][finding['medical_image__patient_info__gender']] += 1
                diseases[name]['ageGroup'][finding['medical_image__patient_info__age_group']] += 1
    health_stats['diseases'] = diseases
    return health_stats

class GetClientDetailsView(APIView):

    @swagger_auto_schema(security=[], responses={200: openapi.Response('Actor Details')}, tags=['Actor'])
    def get(self, request, version=None):
        if request.version in ALLOWED_VERSIONS:
            try:
                ip, is_routable = get_client_ip(request, request_header_order=['X_FORWARDED_FOR', 'REMOTE_ADDR'])
                print(ip)
                print(is_routable)
                if ip is None:
                    print('Unable to get the client\'s IP address')
                else:
                    if is_routable:
                        print('The client\'s IP address is publicly routable on the Internet')
                    else:
                        print('The client\'s IP address is private')

                print('HTTP_X_FORWARDED_FOR', request.META.get('HTTP_X_FORWARDED_FOR'))
                print('X_FORWARDED_FOR', request.META.get('X_FORWARDED_FOR'))
                print('REMOTE_ADDR', request.META.get('REMOTE_ADDR'))
                print('HTTP_X_REAL_IP', request.META.get('HTTP_X_REAL_IP'))
                print('HTTP_CLIENT_IP', request.META.get('HTTP_CLIENT_IP'))
                print('HTTP_VIA', request.META.get('HTTP_VIA'))

                return Response({})
            except Exception as e:
                import traceback
                traceback.print_exc()
                res_data = copy.deepcopy(RESPONSE_500_DATA)
                res_data['message'] = traceback.format_exc()
                return Response(data=res_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response(data=RESPONSE_404_VERSION, status=status.HTTP_404_NOT_FOUND)


class CustomObtainAuthTokenView(APIView):

    @swagger_auto_schema(request_body=AuthTokenSerializer, security=[], responses={200: openapi.Response('User log in with username and password', UserSerializer)}, tags=['Authentication'])
    def post(self, request):
        if request.version == 'v1':
            try:
                serializer = AuthTokenSerializer(data=request.data)
                if not serializer.is_valid():
                    res_data = copy.deepcopy(RESPONSE_401_DATA)
                    res_data['message'] = 'Unable to log in with provided credentials.'
                    return Response(data=res_data, status=status.HTTP_401_UNAUTHORIZED)
                user = serializer.validated_data['user']
                token, created = Token.objects.get_or_create(user=user)
                group = user.groups.all().first()
                if group:
                    role = group.name
                else:
                    role = None
                return Response({'username': user.username, 'role': role, 'token': token.key})
            except Exception as e:
                import traceback
                traceback.print_exc()
                res_data = copy.deepcopy(RESPONSE_500_DATA)
                res_data['message'] = traceback.format_exc()
                return Response(data=res_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response(data=RESPONSE_404_VERSION, status=status.HTTP_404_NOT_FOUND)


class DestoryObtainAuthTokenView(APIView):

    @authentication_classes([TokenAuthentication])
    @swagger_auto_schema(responses={200: openapi.Response('Destroys token in database', UserSerializer)}, tags=['Authentication'])
    def get(self, request):
        if request.version == 'v1':
            try:
                # serializer = AuthTokenSerializer(data=request.data)
                # if not serializer.is_valid():
                #     res_data = copy.deepcopy(RESPONSE_401_DATA)
                #     res_data['message'] = 'Unable to log out with provided credentials.'
                #     return Response(data=res_data, status=status.HTTP_401_UNAUTHORIZED)
                # user = serializer.validated_data['user']
                # token = Token.objects.get(user=user)
                auth_key = request.auth
                print(auth_key)
                token = Token.objects.filter(key=auth_key).first()
                if not token:
                    res_data = copy.deepcopy(RESPONSE_401_DATA)
                    res_data['message'] = 'The token does not exist.'
                    return Response(data=res_data, status=status.HTTP_401_UNAUTHORIZED)
                user = token.user
                token.delete()
                token.save()
                group = user.groups.all().first()
                if group:
                    role = group.name
                else:
                    role = None
                return Response({'username': user.username, 'role': role, 'token': None})
            except Exception as e:
                import traceback
                traceback.print_exc()
                res_data = copy.deepcopy(RESPONSE_500_DATA)
                res_data['message'] = traceback.format_exc()
                return Response(data=res_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response(data=RESPONSE_404_VERSION, status=status.HTTP_404_NOT_FOUND)


class GetUserView(APIView):

    @authentication_classes([TokenAuthentication])
    @swagger_auto_schema(responses={200: openapi.Response('Checks if token is valid and returns user', UserSerializer)}, tags=['Authentication'])
    def get(self, request):
        if request.version == 'v1':
            try:
                auth_key = request.auth
                token = Token.objects.filter(key=auth_key).first()
                if not token:
                    res_data = copy.deepcopy(RESPONSE_401_DATA)
                    res_data['message'] = 'Unable to get user info with provided token.'
                    return Response(data=res_data, status=status.HTTP_401_UNAUTHORIZED)
                user = token.user
                token = Token.objects.get(user=user)
                group = user.groups.all().first()
                if group:
                    role = group.name
                else:
                    role = None
                return Response({'username': user.username, 'role': role, 'token': token.key})
            except Exception as e:
                import traceback
                traceback.print_exc()
                res_data = copy.deepcopy(RESPONSE_500_DATA)
                res_data['message'] = traceback.format_exc()
                return Response(data=res_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response(data=RESPONSE_404_VERSION, status=status.HTTP_404_NOT_FOUND)


class GetAllHealthStatsView(APIView):

    @authentication_classes([TokenAuthentication])
    @swagger_auto_schema(responses={200: openapi.Response('Retrieves aggregated count of all cases in Indonesia', HealthStatsSerializer)}, tags=['Health Stats'])
    def get(self, request):
        if request.version == 'v1':
            try:
                auth_key = request.auth
                token = Token.objects.filter(key=auth_key).first()
                if not token:
                    res_data = copy.deepcopy(RESPONSE_401_DATA)
                    res_data['message'] = 'Unauthorized with provided token.'
                    return Response(data=res_data, status=status.HTTP_401_UNAUTHORIZED)

                hospitals = Hospital.objects.filter(in_master_list=True)
                return Response(data=get_health_stats_data_from_hospitals(hospitals), status=status.HTTP_200_OK)
            except Exception as e:
                import traceback
                traceback.print_exc()
                res_data = copy.deepcopy(RESPONSE_500_DATA)
                res_data['message'] = traceback.format_exc()
                return Response(data=res_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response(data=RESPONSE_404_VERSION, status=status.HTTP_404_NOT_FOUND)


class GetListOfAllRegionsHealthStatsView(APIView):

    @authentication_classes([TokenAuthentication])
    @swagger_auto_schema(responses={200: openapi.Response('Retrieves aggregated count of each region', DetailedHealthStatsSerializer(many=True))}, tags=['Health Stats'])
    def get(self, request):
        if request.version == 'v1':
            try:
                auth_key = request.auth
                token = Token.objects.filter(key=auth_key).first()
                if not token:
                    res_data = copy.deepcopy(RESPONSE_401_DATA)
                    res_data['message'] = 'Unauthorized with provided token.'
                    return Response(data=res_data, status=status.HTTP_401_UNAUTHORIZED)

                regions_health_stats = []
                for region in Region.objects.all():
                    region_health_stats = {'id': region.name.upper()}
                    hospitals = Hospital.objects.filter(in_master_list=True, region=region)
                    region_health_stats['values'] = get_health_stats_data_from_hospitals(hospitals)
                    regions_health_stats.append(region_health_stats)
                return Response(data=regions_health_stats, status=status.HTTP_200_OK)
            except Exception as e:
                import traceback
                traceback.print_exc()
                res_data = copy.deepcopy(RESPONSE_500_DATA)
                res_data['message'] = traceback.format_exc()
                return Response(data=res_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response(data=RESPONSE_404_VERSION, status=status.HTTP_404_NOT_FOUND)


class GetRegionHealthStatsByIdView(APIView):

    @authentication_classes([TokenAuthentication])
    @swagger_auto_schema(responses={200: openapi.Response('Retrieves aggregated count of one region', DetailedHealthStatsSerializer())}, tags=['Health Stats'])
    def get(self, request, id=None):
        if request.version == 'v1':
            try:
                auth_key = request.auth
                token = Token.objects.filter(key=auth_key).first()
                if not token:
                    res_data = copy.deepcopy(RESPONSE_401_DATA)
                    res_data['message'] = 'Unauthorized with provided token.'
                    return Response(data=res_data, status=status.HTTP_401_UNAUTHORIZED)

                region = Region.objects.get(name=id.upper())
                if region is not None:
                    hospitals = Hospital.objects.filter(in_master_list=True, region=region)
                    return Response(data=get_health_stats_data_from_hospitals(hospitals), status=status.HTTP_200_OK)
                else:
                    res_data = copy.deepcopy(RESPONSE_400_DATA)
                    res_data['message'] = 'Region not found.'
                    return Response(data=res_data, status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                import traceback
                traceback.print_exc()
                res_data = copy.deepcopy(RESPONSE_500_DATA)
                res_data['message'] = traceback.format_exc()
                return Response(data=res_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response(data=RESPONSE_404_VERSION, status=status.HTTP_404_NOT_FOUND)


class GetListOfAllHospitalsHealthStatsView(APIView):

    @authentication_classes([TokenAuthentication])
    @swagger_auto_schema(responses={200: openapi.Response('Retrieves aggregated count of each hospital', DetailedHealthStatsSerializer(many=True))}, tags=['Health Stats'])
    def get(self, request):
        if request.version == 'v1':
            try:
                auth_key = request.auth
                token = Token.objects.filter(key=auth_key).first()
                if not token:
                    res_data = copy.deepcopy(RESPONSE_401_DATA)
                    res_data['message'] = 'Unauthorized with provided token.'
                    return Response(data=res_data, status=status.HTTP_401_UNAUTHORIZED)

                hospitals_health_stats = []
                hospitals = Hospital.objects.filter(in_master_list=True)
                for hospital in hospitals:
                    hospital_health_stats = {'id': hospital.code}
                    hospital_health_stats['values'] = get_health_stats_data_from_hospitals(hospital)
                    hospitals_health_stats.append(hospital_health_stats)
                return Response(data=hospitals_health_stats, status=status.HTTP_200_OK)
            except Exception as e:
                import traceback
                traceback.print_exc()
                res_data = copy.deepcopy(RESPONSE_500_DATA)
                res_data['message'] = traceback.format_exc()
                return Response(data=res_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response(data=RESPONSE_404_VERSION, status=status.HTTP_404_NOT_FOUND)


class GetHospitalHealthStatsByIdView(APIView):

    @authentication_classes([TokenAuthentication])
    @swagger_auto_schema(responses={200: openapi.Response('Retrieves aggregated count of one hospital', DetailedHealthStatsSerializer())}, tags=['Health Stats'])
    def get(self, request, id=None):
        if request.version == 'v1':
            try:
                auth_key = request.auth
                token = Token.objects.filter(key=auth_key).first()
                if not token:
                    res_data = copy.deepcopy(RESPONSE_401_DATA)
                    res_data['message'] = 'Unauthorized with provided token.'
                    return Response(data=res_data, status=status.HTTP_401_UNAUTHORIZED)

                hospital = Hospital.objects.filter(in_master_list=True, code=id).first()
                if hospital:
                    return Response(data=get_health_stats_data_from_hospitals(hospital), status=status.HTTP_200_OK)
                else:
                    res_data = copy.deepcopy(RESPONSE_400_DATA)
                    res_data['message'] = 'Hospital not found.'
                    return Response(data=res_data, status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                import traceback
                traceback.print_exc()
                res_data = copy.deepcopy(RESPONSE_500_DATA)
                res_data['message'] = traceback.format_exc()
                return Response(data=res_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response(data=RESPONSE_404_VERSION, status=status.HTTP_404_NOT_FOUND)


class GetTimeseriesOfAllHealthStatsView(APIView):

    @authentication_classes([TokenAuthentication])
    @swagger_auto_schema(manual_parameters=[START_DATE_PARAMETER, END_DATE_PARAMETER], responses={200: openapi.Response('Retrieves daily historical records of all cases in Indonesia', TimeseriesHealthStatsSerializer(many=True))}, tags=['Health Stats'])
    def get(self, request):
        if request.version == 'v1':
            try:
                auth_key = request.auth
                token = Token.objects.filter(key=auth_key).first()
                if not token:
                    res_data = copy.deepcopy(RESPONSE_401_DATA)
                    res_data['message'] = 'Unauthorized with provided token.'
                    return Response(data=res_data, status=status.HTTP_401_UNAUTHORIZED)

                startDate = self.request.query_params.get('startDate', None)
                endDate = self.request.query_params.get('endDate', None)
                try:
                    startDate = datetime.strptime(startDate, '%Y-%m-%d').date()
                    if endDate is None:
                        endDate = date.today()
                    else:
                        endDate = datetime.strptime(endDate, '%Y-%m-%d').date()
                except Exception as e:
                    import traceback
                    traceback.print_exc()
                    res_data = copy.deepcopy(RESPONSE_400_DATA)
                    res_data['message'] = traceback.format_exc().splitlines()[-1]
                    return Response(data=res_data, status=status.HTTP_400_BAD_REQUEST)
                # print(startDate, endDate)

                delta = endDate - startDate
                if delta.days < 0:
                    res_data = copy.deepcopy(RESPONSE_400_DATA)
                    res_data['message'] = 'startDate must be earlier than endDate'
                    return Response(data=res_data, status=status.HTTP_400_BAD_REQUEST)

                timeseries_health_stats = []
                for i in range(delta.days + 1):
                    image_date = startDate + timedelta(days=i)
                    # print('retrieve day', image_date)
                    hospitals = Hospital.objects.filter(in_master_list=True)
                    ts_health_stats = get_health_stats_data_from_hospitals(hospitals, image_date)
                    ts_health_stats['date'] = image_date.strftime('%Y-%m-%d')
                    timeseries_health_stats.append(ts_health_stats)
                return Response(data=timeseries_health_stats, status=status.HTTP_200_OK)
            except Exception as e:
                import traceback
                traceback.print_exc()
                res_data = copy.deepcopy(RESPONSE_500_DATA)
                res_data['message'] = traceback.format_exc()
                return Response(data=res_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response(data=RESPONSE_404_VERSION, status=status.HTTP_404_NOT_FOUND)


class GetTimeseriesOfRegionHealthStatsByIdView(APIView):

    @authentication_classes([TokenAuthentication])
    @swagger_auto_schema(manual_parameters=[START_DATE_PARAMETER, END_DATE_PARAMETER], responses={200: openapi.Response('Retrieves daily historical records of one region', TimeseriesHealthStatsSerializer(many=True))}, tags=['Health Stats'])
    def get(self, request, id=None):
        if request.version == 'v1':
            try:
                auth_key = request.auth
                token = Token.objects.filter(key=auth_key).first()
                if not token:
                    res_data = copy.deepcopy(RESPONSE_401_DATA)
                    res_data['message'] = 'Unauthorized with provided token.'
                    return Response(data=res_data, status=status.HTTP_401_UNAUTHORIZED)

                region = Region.objects.get(name=id)
                if not region:
                    res_data = copy.deepcopy(RESPONSE_400_DATA)
                    res_data['message'] = 'Hospital not found.'
                    return Response(data=res_data, status=status.HTTP_400_BAD_REQUEST)

                startDate = self.request.query_params.get('startDate', None)
                endDate = self.request.query_params.get('endDate', None)
                try:
                    startDate = datetime.strptime(startDate, '%Y-%m-%d').date()
                    if endDate is None:
                        endDate = date.today()
                    else:
                        endDate = datetime.strptime(endDate, '%Y-%m-%d').date()
                except Exception as e:
                    import traceback
                    traceback.print_exc()
                    res_data = copy.deepcopy(RESPONSE_400_DATA)
                    res_data['message'] = traceback.format_exc().splitlines()[-1]
                    return Response(data=res_data, status=status.HTTP_400_BAD_REQUEST)
                # print(startDate, endDate)

                delta = endDate - startDate
                if delta.days < 0:
                    res_data = copy.deepcopy(RESPONSE_400_DATA)
                    res_data['message'] = 'startDate must be earlier than endDate'
                    return Response(data=res_data, status=status.HTTP_400_BAD_REQUEST)

                timeseries_health_stats = []
                for i in range(delta.days + 1):
                    image_date = startDate + timedelta(days=i)
                    # print('retrieve day', image_date)
                    image_date_str = image_date.strftime('%Y-%m-%d')
                    hospitals = Hospital.objects.filter(in_master_list=True, region=region)
                    ts_health_stats = get_health_stats_data_from_hospitals(hospitals, image_date_str)
                    ts_health_stats['date'] = image_date_str
                    timeseries_health_stats.append(ts_health_stats)
                return Response(data=timeseries_health_stats, status=status.HTTP_200_OK)
            except Exception as e:
                import traceback
                traceback.print_exc()
                res_data = copy.deepcopy(RESPONSE_500_DATA)
                res_data['message'] = traceback.format_exc()
                return Response(data=res_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response(data=RESPONSE_404_VERSION, status=status.HTTP_404_NOT_FOUND)


class GetTimeseriesOfHospitalHealthStatsByIdView(APIView):

    @authentication_classes([TokenAuthentication])
    @swagger_auto_schema(manual_parameters=[START_DATE_PARAMETER, END_DATE_PARAMETER], responses={200: openapi.Response('Retrieves daily historical records of one hospital', TimeseriesHealthStatsSerializer(many=True))}, tags=['Health Stats'])
    def get(self, request, id=None):
        if request.version == 'v1':
            try:
                auth_key = request.auth
                token = Token.objects.filter(key=auth_key).first()
                if not token:
                    res_data = copy.deepcopy(RESPONSE_401_DATA)
                    res_data['message'] = 'Unauthorized with provided token.'
                    return Response(data=res_data, status=status.HTTP_401_UNAUTHORIZED)

                hospital = Hospital.objects.filter(in_master_list=True, code=id).first()
                if not hospital:
                    res_data = copy.deepcopy(RESPONSE_400_DATA)
                    res_data['message'] = 'Hospital not found.'
                    return Response(data=res_data, status=status.HTTP_400_BAD_REQUEST)

                startDate = self.request.query_params.get('startDate', None)
                endDate = self.request.query_params.get('endDate', None)
                try:
                    startDate = datetime.strptime(startDate, '%Y-%m-%d').date()
                    if endDate is None:
                        endDate = date.today()
                    else:
                        endDate = datetime.strptime(endDate, '%Y-%m-%d').date()
                except Exception as e:
                    import traceback
                    traceback.print_exc()
                    res_data = copy.deepcopy(RESPONSE_400_DATA)
                    res_data['message'] = traceback.format_exc().splitlines()[-1]
                    return Response(data=res_data, status=status.HTTP_400_BAD_REQUEST)
                # print(startDate, endDate)

                delta = endDate - startDate
                if delta.days < 0:
                    res_data = copy.deepcopy(RESPONSE_400_DATA)
                    res_data['message'] = 'startDate must be earlier than endDate'
                    return Response(data=res_data, status=status.HTTP_400_BAD_REQUEST)

                timeseries_health_stats = []
                for i in range(delta.days + 1):
                    image_date = startDate + timedelta(days=i)
                    # print('retrieve day', image_date)
                    image_date_str = image_date.strftime('%Y-%m-%d')
                    ts_health_stats = get_health_stats_data_from_hospitals(hospital, image_date_str)
                    ts_health_stats['date'] = image_date_str
                    timeseries_health_stats.append(ts_health_stats)
                return Response(data=timeseries_health_stats, status=status.HTTP_200_OK)
            except Exception as e:
                import traceback
                traceback.print_exc()
                res_data = copy.deepcopy(RESPONSE_500_DATA)
                res_data['message'] = traceback.format_exc()
                return Response(data=res_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response(data=RESPONSE_404_VERSION, status=status.HTTP_404_NOT_FOUND)


def custom404(request, exception=None):
    return JsonResponse(RESPONSE_404_ENDPOINT)


class GetListOfAllHospitalsDataView(APIView):

    @authentication_classes([TokenAuthentication])
    @swagger_auto_schema(responses={200: openapi.Response('Retrieves all hospitals info', HospitalSerializer(many=True))}, tags=['Hospitals'])
    def get(self, request):
        if request.version == 'v1':
            try:
                auth_key = request.auth
                token = Token.objects.filter(key=auth_key).first()
                if not token:
                    res_data = copy.deepcopy(RESPONSE_401_DATA)
                    res_data['message'] = 'Unauthorized with provided token.'
                    return Response(data=res_data, status=status.HTTP_401_UNAUTHORIZED)

                hospitals = Hospital.objects.all()
                serializer = HospitalSerializer(hospitals, many=True)
                return Response(data=serializer.data, status=status.HTTP_200_OK)
            except Exception as e:
                import traceback
                traceback.print_exc()
                res_data = copy.deepcopy(RESPONSE_500_DATA)
                res_data['message'] = traceback.format_exc()
                return Response(data=res_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response(data=RESPONSE_404_VERSION, status=status.HTTP_404_NOT_FOUND)


class GetHospitalDataByIdView(APIView):

    @authentication_classes([TokenAuthentication])
    @swagger_auto_schema(responses={200: openapi.Response('Retrieves all hospitals info', HospitalSerializer())}, tags=['Hospitals'])
    def get(self, request, id=None):
        if request.version == 'v1':
            try:
                auth_key = request.auth
                token = Token.objects.filter(key=auth_key).first()
                if not token:
                    res_data = copy.deepcopy(RESPONSE_401_DATA)
                    res_data['message'] = 'Unauthorized with provided token.'
                    return Response(data=res_data, status=status.HTTP_401_UNAUTHORIZED)

                hospital = Hospital.objects.filter(in_master_list=True, code=id).first()
                if not hospital:
                    res_data = copy.deepcopy(RESPONSE_400_DATA)
                    res_data['message'] = 'Hospital not found.'
                    return Response(data=res_data, status=status.HTTP_400_BAD_REQUEST)

                serializer = HospitalSerializer(hospital)
                return Response(data=serializer.data, status=status.HTTP_200_OK)
            except Exception as e:
                import traceback
                traceback.print_exc()
                res_data = copy.deepcopy(RESPONSE_500_DATA)
                res_data['message'] = traceback.format_exc()
                return Response(data=res_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response(data=RESPONSE_404_VERSION, status=status.HTTP_404_NOT_FOUND)


class GetListOfRegionsView(APIView):

    @authentication_classes([TokenAuthentication])
    @swagger_auto_schema(responses={200: openapi.Response('Retrieves all regions info', RegionSerializer(many=True))}, tags=['Regions'])
    def get(self, request):
        if request.version == 'v1':
            try:
                auth_key = request.auth
                token = Token.objects.filter(key=auth_key).first()
                if not token:
                    res_data = copy.deepcopy(RESPONSE_401_DATA)
                    res_data['message'] = 'Unauthorized with provided token.'
                    return Response(data=res_data, status=status.HTTP_401_UNAUTHORIZED)

                regions = Region.objects.all()

                serializer = RegionSerializer(regions, many=True)
                return Response(data=serializer.data, status=status.HTTP_200_OK)
            except Exception as e:
                import traceback
                traceback.print_exc()
                res_data = copy.deepcopy(RESPONSE_500_DATA)
                res_data['message'] = traceback.format_exc()
                return Response(data=res_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response(data=RESPONSE_404_VERSION, status=status.HTTP_404_NOT_FOUND)
