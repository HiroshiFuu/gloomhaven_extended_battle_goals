from django.db import models
from django.utils import timezone
from django.conf import settings


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


class ActorGoal(LogMixin):
    actor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    goal_img_path = models.CharField('Goal Image Path', max_length=127)
    batch = models.PositiveIntegerField('Batch')

    class Meta:
        managed = True
        db_table = 'actor_goal'
        verbose_name = 'Actor Goal'
        ordering = ['-created_at']

    def __str__(self):
        return '{}: {} {}'.format(self.actor, self.batch, self.goal_img_path)


class GoalState(LogMixin):
    distributed = models.BooleanField('Distributed', default=False)
    for_batch = models.PositiveIntegerField('For Batch')

    class Meta:
        managed = True
        db_table = 'goal_state'
        verbose_name = 'Goal State'

    def __str__(self):
        return '{}: {}'.format(self.for_batch, self.distributed)

