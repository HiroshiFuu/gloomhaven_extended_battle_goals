from django.db import models
from django.conf import settings
from django.utils import timezone
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.dispatch import receiver

from jsonfield import JSONField

from .constants import GENDERS

import json


# Create your models here.
class LogMixin(models.Model):
    class Meta:
        abstract = True

    created_at = models.DateTimeField(
        editable=False, auto_now_add=True, verbose_name='Created At')
    modified_at = models.DateTimeField(
        editable=False, blank=True, null=True, verbose_name='Modified At')

    def save(self, *args, **kwargs):
        if not self.id:
            self.created_at = timezone.now()
        self.modified_at = timezone.now()
        return super().save(*args, **kwargs)


class TruncateMixin(models.Model):
    class Meta:
        abstract = True

    @classmethod
    def truncate(cls):
        from django.db import connection
        with connection.cursor() as cursor:
            if 'sqlite3' in settings.DATABASES['default']['ENGINE']:
                cursor.execute('DELETE FROM "{0}";'.format(cls._meta.db_table))
                cursor.execute('DELETE FROM sqlite_sequence WHERE NAME="{0}";'.format(cls._meta.db_table))
            else:
                cursor.execute('DELETE FROM {0};'.format(cls._meta.db_table))
                cursor.execute('ALTER TABLE {0} AUTO_INCREMENT = 1;'.format(cls._meta.db_table))
            print('TABLE "{0}" TRUNCATED, INDEX RESETED'.format(cls._meta.db_table))


class Region(LogMixin, TruncateMixin):
    name = models.CharField('Region Name', max_length=31)
    lng = models.FloatField('Longitude', null=True, blank=True)
    lat = models.FloatField('Latitude', null=True, blank=True)
    zoom = models.FloatField('Zoom Level', null=True, blank=True)
    color = models.CharField('Color', max_length=15, null=True, blank=True)
    rgb = models.CharField('RGB', max_length=15, null=True, blank=True)
    order = models.PositiveSmallIntegerField ('Order', default=0)

    class Meta:
        managed = True
        db_table = 'region'
        verbose_name = 'Region'
        ordering = ['order']

    def __str__(self):
        return '{}: {} {}'.format(self.name, self.color, self.rgb)


class Province(LogMixin, TruncateMixin):
    name = models.CharField('Province Name', max_length=63)
    region = models.ForeignKey(Region, related_name='provinces', on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        managed = True
        db_table = 'province'
        verbose_name = 'Province'

    def __str__(self):
        return '{}, {}'.format(self.name, self.region)


class Hospital(LogMixin, TruncateMixin):
    name = models.CharField('Hospital Name', max_length=127, null=True)
    code = models.CharField('Hospital Code', max_length=15)
    beds = models.PositiveSmallIntegerField('Hospital Beds', null=True)
    telephone = models.CharField('Hospital Telephone', max_length=31, null=True, blank=True)
    address = models.CharField('Hospital Address', max_length=255, null=True)
    type = models.CharField('Hospital Type', max_length=127, null=True)
    province = models.ForeignKey(Province, on_delete=models.CASCADE, null=True, blank=True)
    lng = models.FloatField('Longitude', null=True)
    lat = models.FloatField('Latitude', null=True)
    logo = models.ImageField('Logo', upload_to='logos', null=True, blank=True)
    region = models.ForeignKey(Region, on_delete=models.CASCADE, null=True, blank=True)
    in_master_list = models.BooleanField('In Master List', default=False)

    class Meta:
        managed = True
        db_table = 'hospital'
        verbose_name = 'Hospital'

    def __str__(self):
        return '{}: {} @ {},{}'.format(self.name, self.region, self.lng, self.lat)

    # def save(self, *args, **kwargs):
        # print('save', self.logo)
        # if self.logo:
        #     print(self.logo.path)
        # save_hospitals_master_list()
        # super().save(*args, **kwargs)


class Site(LogMixin, TruncateMixin):
    code = models.CharField('Site Code', max_length=31)
    hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        managed = True
        db_table = 'site'
        verbose_name = 'ROBO Site'

    def __str__(self):
        return '{}: {}'.format(self.code, self.hospital.name)


class AnalysisSetting(LogMixin, TruncateMixin):
    threshold = JSONField()
    site = models.ForeignKey(Site, on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        managed = True
        db_table = 'analysis_setting'
        verbose_name = 'Analysis Setting'

    def __str__(self):
        return '{}: {}'.format(self.site.code, self.threshold)


class PatientInfo(LogMixin, TruncateMixin):
    date_acquired = models.DateField(null=True, verbose_name='Date Acquired')
    name = models.CharField(max_length=255, null=True, verbose_name='Name')
    identity_no =  models.CharField(max_length=31, verbose_name='Gender')
    gender = models.CharField(max_length=15, choices=GENDERS, verbose_name='Gender')
    dob = models.DateField(null=True, verbose_name='Date of Birth')
    age = models.PositiveSmallIntegerField(null=True, blank=True, verbose_name='Age')
    modality = models.CharField(max_length=255, null=True, verbose_name='Modality')
    site = models.ForeignKey(Site, on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        managed = True
        db_table = 'patient_info'
        verbose_name = 'Patient Info'

    def __str__(self):
        return '{}({}): {} {}'.format(self.name, self.identity_no, self.gender, self.dob)


class MedicalImage(LogMixin, TruncateMixin):
    image_date = models.DateField(null=True, verbose_name='Image Date')
    image_path = models.CharField(max_length=255, null=True, verbose_name='Image File Path')
    image_name = models.CharField(max_length=255, null=True, verbose_name='Image Name')
    site = models.ForeignKey(Site, on_delete=models.CASCADE, null=True, blank=True)
    patient_info = models.ForeignKey(PatientInfo, on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        managed = True
        db_table = 'medical_image'
        verbose_name = 'Medical Image'

    def __str__(self):
        return '{}-{}: {} {}'.format(self.site.code, self.image_name, self.image_date, self.image_path)


class XrayAnalysisFinding(LogMixin, TruncateMixin):
    name = models.CharField(max_length=127, null=True, verbose_name='Disease Name')
    value = models.FloatField(null=True, verbose_name='Disease Confidence')
    medical_image = models.ForeignKey(MedicalImage, on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        managed = True
        db_table = 'xray_analysis_finding'
        verbose_name = 'X-Ray Analysis Finding'

    def __str__(self):
        return '{}: {} {}'.format(self.medical_image.image_name, self.name, self.value)


def save_hospitals_master_list():
    file_path = 'hospitals_master_list.json'
    if default_storage.exists(file_path):
        default_storage.delete(file_path)
    json_data = []
    for hospital in Hospital.objects.all():
        hospital_data = {}
        hospital_data['name'] = hospital.name
        hospital_data['code'] = hospital.code
        hospital_data['beds'] = hospital.beds
        hospital_data['telephone'] = hospital.telephone
        hospital_data['address'] = hospital.address
        hospital_data['type'] = hospital.type
        hospital_data['region'] = hospital.region.name
        hospital_data['province'] = hospital.province.name
        hospital_data['lng'] = hospital.lng
        hospital_data['lat'] = hospital.lat
        hospital_data['logo'] = hospital.logo.name
        json_data.append(hospital_data)
    json_value = json.dumps(json_data, indent=4)
    path = default_storage.save(file_path, ContentFile(json_value))
    # print('save_hospitals_master_list', path)


@receiver(models.signals.pre_save, sender=Hospital)
def auto_delete_file_on_change(sender, instance, **kwargs):
    """
    Deletes old file from filesystem when corresponding 
    `MediaFile` object is updated with new file.
    """
    if not instance.pk:
        return False

    try:
        old_logo = sender.objects.get(pk=instance.pk).logo
    except sender.DoesNotExist:
        return False

    new_logo = instance.logo
    if not old_logo == new_logo:
        if old_logo:
            # print('auto_delete_file_on_change old', old_logo.path)
            # if new_logo:
            #     print('auto_delete_file_on_change new', new_logo.path)
            if default_storage.exists(old_logo.path):
                default_storage.delete(old_logo.path)


@receiver(models.signals.post_save, sender=Hospital)
def auto_generate_on_save(sender, instance, created, **kwargs):
    """
    Generate master list when `MediaFile` object is saved.
    """
    save_hospitals_master_list()


@receiver(models.signals.post_delete, sender=Hospital)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    """
    Deletes file from filesystem when corresponding 
    `MediaFile` object is deleted.
    """
    if instance.logo:
        if default_storage.exists(instance.logo.path):
            default_storage.delete(instance.logo.path)
    save_hospitals_master_list()


@receiver(models.signals.post_save, sender=Province)
def auto_update_on_save(sender, instance, created, **kwargs):
    """
    Update region on Hospital
    """
    for hospital in Hospital.objects.filter(province=instance):
        hospital.region = instance.region
        hospital.save()