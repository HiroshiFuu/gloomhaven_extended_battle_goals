from django.utils.translation import gettext as _


# Create your constants here.
MALE = 'male'
FEMALE = 'female'
NOT_SURE = 'not_sure'

GENDERS = [
  (MALE, _('Male')),
  (FEMALE, _('Female')),
  (NOT_SURE, _('Not Sure')),
]


DISEASES = [
  "CARDIOMEGALY",
  "EDEMA",
  "NODULE",
  "PNEUMONIA",
  "MASS",
  "INFILTRATION",
  "EFFUSION",
  "CONSOLIDATION",
  "ATELECTASIS",
  "EMPHYSEMA",
  "FIBROSIS",
  "PLEURAL_THICKENING",
  "PNEUMOTHORAX",
  "HERNIA",
  "TUBERCULOSIS",
]


AGE_GROUPS = [
  '0-5',
  '6-17',
  '18-30',
  '31-45',
  '46-59',
  '60+',
]

AGE_GROUPS_VALUES = []

def cal_age_groups_values():
  global AGE_GROUPS_VALUES
  AGE_GROUPS_VALUES = []
  for age_group in AGE_GROUPS:
    values = age_group.split('-')
    if len(values) == 2:
      group_values = []
      for value in values:
        group_values.append(int(value))
      AGE_GROUPS_VALUES.append(group_values)
    else:
      AGE_GROUPS_VALUES.append([int(values[0].replace('+', '')), 999])
cal_age_groups_values()