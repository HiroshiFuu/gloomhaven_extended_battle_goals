from django.contrib import admin

from import_export.admin import ImportExportModelAdmin
from adminsortable2.admin import SortableAdminMixin

from django.conf.locale.en import formats as en_formats
en_formats.DATETIME_FORMAT = "Y-m-d H:i:s"

from .models import Region
from .models import Province
from .models import Hospital
from .models import Site
from .models import AnalysisSetting
from .models import MedicalImage
from .models import XrayAnalysisFinding
from .models import PatientInfo
# from .models import Configuration

# Register your model's admin here.
class ProvinceInline(admin.StackedInline):
    model = Province
    extra = 0


class SiteInline(admin.StackedInline):
    model = Site
    extra = 0


class PatientInfoInline(admin.TabularInline):
    model = PatientInfo
    extra = 0
    per_page = 5


class MedicalImageInline(admin.TabularInline):
    model = MedicalImage
    extra = 0
    per_page = 20


class XrayAnalysisFindingInline(admin.TabularInline):
    model = XrayAnalysisFinding
    extra = 0


@admin.register(Region)
class RegionAdmin(SortableAdminMixin, ImportExportModelAdmin):
    list_display = [
        'order',
        'name',
        'lng',
        'lat',
        'zoom',
        'color',
        'rgb',
    ]
    list_display_links = ('name', )
    search_fields = ['name', 'color']
    # ordering = ['order']
    inlines = [
        ProvinceInline
    ]


@admin.register(Province)
class ProvinceAdmin(ImportExportModelAdmin):
    list_display = [
        'name',
        'region'
    ]
    search_fields = ['name', 'region__name']
    ordering = ['name']


@admin.register(Hospital)
class HospitalAdmin(ImportExportModelAdmin):
    list_display = [
        'name',
        'code',
        'beds',
        'telephone',
        'address',
        'type',
        'region',
        'province',
        'lng',
        'lat',
        'logo',
        'in_master_list',
    ]
    search_fields = ['name', 'code', 'region__name', 'province__name']
    ordering = ['name']
    inlines = [
        SiteInline,
    ]

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return []
        else:
            if request.user.is_superuser:
                return []
            return ['in_master_list']

    def get_inline_instances(self, request, obj=None):
        if obj is None:
            return []
        return [inline(self.model, self.admin_site) for inline in self.inlines]


@admin.register(Site)
class SiteAdmin(ImportExportModelAdmin):
    list_display = [
        'code',
        'hospital',
    ]
    search_fields = ['code', 'hospital__name', 'hospital__region']
    ordering = ['code']
    inlines = [
        PatientInfoInline,
        MedicalImageInline,
    ]


@admin.register(PatientInfo)
class PatientInfoAdmin(ImportExportModelAdmin):
    list_display = [
        'date_acquired',
        'name',
        'identity_no',
        'gender',
        'dob',
        'age',
        'modality',
    ]
    search_fields = ['medical_image__image_name', 'name', 'identity_no', 'modality']
    ordering = ['date_acquired', 'name']
    date_hierarchy = 'date_acquired'
    inlines = [
        MedicalImageInline,
    ]


@admin.register(MedicalImage)
class MedicalImageAdmin(ImportExportModelAdmin):
    list_display = [
        'image_date',
        'image_path',
        'image_name',
        'site',
    ]
    search_fields = ['image_date', 'image_name']
    ordering = ['image_date']
    date_hierarchy = 'image_date'
    inlines = [
        XrayAnalysisFindingInline,
    ]


@admin.register(AnalysisSetting)
class AnalysisSettingAdmin(ImportExportModelAdmin):
    list_display = [
        'site',
        'threshold'
    ]
    search_fields = ['site__code', 'threshold']
    ordering = ['site__code']


@admin.register(XrayAnalysisFinding)
class XrayAnalysisFindingAdmin(ImportExportModelAdmin):
    list_display = [
        'medical_image',
        'name',
        'value',
    ]
    search_fields = ['medical_image__image_name', 'medical_image__site__hospital__code', 'name', 'value']
    ordering = ['medical_image', '-value']


# @admin.register(Configuration)
# class ConfigurationAdmin(admin.ModelAdmin):
#     list_display = [
#         'user',
#         'regions',
#         'constants',
#     ]
#     search_fields = ['user', 'regions']
