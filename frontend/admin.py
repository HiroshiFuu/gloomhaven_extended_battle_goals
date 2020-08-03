from django.contrib import admin
from django.urls import path
from django.http import HttpResponseRedirect
from django.contrib.auth.models import User
from django.utils.html import format_html

from .models import ActorGoal
from .models import GoalState

from .constants import BATTLE_GOALS

import copy
import random


# Register your model's admin here.
@admin.register(ActorGoal)
class ActorGoalAdmin(admin.ModelAdmin):
    change_list_template = 'change_list.html'
    list_display = [
        'actor',
        'goal_img_preview',
        'batch',
    ]
    # list_display_links = ('name', )
    search_fields = ['actor', 'batch']

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path('draw_new_battle_goals/', self.draw_new_battle_goals, name='draw_new_battle_goals'),
        ]
        return my_urls + urls

    def draw_new_battle_goals(self, request):
        # self.message_user(request, 'Drawing new battle goals..')
        actors = User.objects.all()
        # print(actors)
        GOALS = copy.deepcopy(BATTLE_GOALS)
        drawn_goals = random.sample(GOALS, len(actors))
        # print(drawn_goals)
        last_actor_goal = ActorGoal.objects.last()
        if last_actor_goal is None:
            last_batch = 1
        else:
            last_batch = last_actor_goal.batch + 1
        for index, actor in enumerate(actors):
            ActorGoal.objects.create(actor=actor, goal_img_path=drawn_goals[index], batch=last_batch)
            state = GoalState.objects.all().first()
            state.last_batch = last_batch
            state.distributed = False
            state.save()
        return HttpResponseRedirect('../')

    def goal_img_preview(self, obj):
        goal_id = 'goal_' + str(obj.id)
        goal_name = obj.goal_img_path.split('/')[-1].split('.')[0]
        # print(obj.goal_img_path, goal_name)
        return format_html(
            '''
            <img id="{}" style="display:none; position:absolute; top:50px; left:-50px); height:calc(297px); width:calc(210px); border:3px solid; z-index:1000;" src="{}" />
            <div style="font-size:12pt; position:relative; cursor:pointer;" 
            onmouseover="document.getElementById('{}').style.display='block'; position: 'relative'; document.getElementById('{}').style.left=this.getBoundingClientRect().left+'px'; document.getElementById('{}').style.cursor='pointer';"
            onmouseout="document.getElementById('{}').style.display='none';">{}</div>
            '''.format(goal_id, obj.goal_img_path, goal_id, goal_id, goal_id, goal_id, goal_name))


@admin.register(GoalState)
class GoalStateAdmin(admin.ModelAdmin):
    list_display = [
        'for_batch',
        'distributed',
        'modified_at',
    ]