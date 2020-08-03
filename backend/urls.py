from django.conf.urls import url
from django.urls import path
from django.urls import re_path

from .views import CustomObtainAuthTokenView
from .views import DestoryObtainAuthTokenView
from .views import GetUserView
from .views import GetAllHealthStatsView
from .views import GetListOfAllRegionsHealthStatsView
from .views import GetRegionHealthStatsByIdView
from .views import GetListOfAllHospitalsHealthStatsView
from .views import GetHospitalHealthStatsByIdView
from .views import GetTimeseriesOfAllHealthStatsView
from .views import GetTimeseriesOfRegionHealthStatsByIdView
from .views import GetTimeseriesOfHospitalHealthStatsByIdView
from .views import GetListOfAllHospitalsDataView
from .views import GetHospitalDataByIdView
from .views import GetListOfRegionsView

from .views import custom404

app_name = 'backend'

urlpatterns = [
    re_path(r'auth/login$', CustomObtainAuthTokenView.as_view(), name='token-auth_login'),
    re_path(r'auth/logout$', DestoryObtainAuthTokenView.as_view(), name='token-auth_logout'),
    re_path(r'auth/user$', GetUserView.as_view(), name='token-auth_user'),

    re_path(r'healthStats$', GetAllHealthStatsView.as_view(), name='health_stats-get'),
    re_path(r'healthStats/regions$', GetListOfAllRegionsHealthStatsView.as_view(), name='health_stats_region-list'),
    re_path(r'healthStats/regions/(?P<id>[A-Z]{1,31})$', GetRegionHealthStatsByIdView.as_view(), name='health_stats_region-get'),
    re_path(r'healthStats/hospitals$', GetListOfAllHospitalsHealthStatsView.as_view(), name='health_stats_hospital-list'),
    re_path(r'healthStats/hospitals/(?P<id>[0-9]{1,31})$', GetHospitalHealthStatsByIdView.as_view(), name='health_stats_hospital-get'),
    re_path(r'healthStats/timeseries$', GetTimeseriesOfAllHealthStatsView.as_view(), name='health_stats_timeseries-get'),
    re_path(r'healthStats/regions/(?P<id>[A-Z]{1,31})/timeseries$', GetTimeseriesOfRegionHealthStatsByIdView.as_view(), name='health_stats_timeseries_region-get'),
    re_path(r'healthStats/hospitals/(?P<id>[0-9]{1,31})/timeseries$', GetTimeseriesOfHospitalHealthStatsByIdView.as_view(), name='health_stats_timeseries_hospital-get'),
    re_path(r'hospitals$', GetListOfAllHospitalsDataView.as_view(), name='hospital_data-list'),
    # re_path(r'hospitalData/hospitals/(?P<id>[0-9]{1,15})$', GetHospitalDataByIdView.as_view(), name='hospital_data-get'),
    re_path(r'regions$', GetListOfRegionsView.as_view(), name='hospital_data_regions-list'),

    re_path(r'.*$', custom404, name='error-404-view'),

    # re_path(r'configuration-token$', QueryConfigurationTokenView.as_view(), name='configuration_token-query'),
]