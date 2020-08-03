from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required

from .models import ActorGoal
from .models import GoalState

from .constants import BATTLE_GOALS

# Create your views here.
@login_required(login_url='/accounts/login/')
def draw_battle_goal(request):
	actor = request.user
	goal = ActorGoal.objects.filter(actor=actor).last()
	img_path = goal.goal_img_path
	state = GoalState.objects.filter(for_batch=goal.batch).first()
	if state is None:
		distributed = False
	else:
		distributed = state.distributed
	return render(request, 'draw_battle_goal.html', {'img_path': img_path, 'distributed': distributed})