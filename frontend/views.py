from django.shortcuts import render
from django.shortcuts import redirect
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required

from .models import ActorGoal
from .models import GoalState

from .constants import BATTLE_GOALS

# Create your views here.
@login_required(login_url='/accounts/login/')
def draw_battle_goal(request):
    actor = request.user
    goal = ActorGoal.objects.filter(actor=actor).order_by('batch').last()
    if goal is None:
        return HttpResponse('No actor added yet!!!')
    if request.method == 'POST':
        selected = int(request.POST['selected'])
        # print('selected', selected)
        if selected == 1:
            goal.selected_goal_img_path = goal.drawn_goal_1_img_path
        if selected == 2:
            goal.selected_goal_img_path = goal.drawn_goal_2_img_path
        goal.save()
    img_path = goal.selected_goal_img_path
    img_path_1 = goal.drawn_goal_1_img_path
    img_path_2 = goal.drawn_goal_2_img_path
    state = GoalState.objects.filter(for_batch=goal.batch).first()
    if state is None:
        distributed = False
    else:
        distributed = state.distributed
    return render(request, 'draw_battle_goal.html', {'img_path': img_path, 'img_path_1': img_path_1, 'img_path_2': img_path_2, 'distributed': distributed})


@login_required(login_url='/accounts/login/')
def selected_battle_goal(request):
    if request.method == 'POST':
        actor = request.user
        goal = ActorGoal.objects.filter(actor=actor).order_by('batch').last()
        selected = int(request.POST['selected'])
        # print('selected', selected)
        if selected == 1:
            goal.selected_goal_img_path = goal.drawn_goal_1_img_path
        if selected == 2:
            goal.selected_goal_img_path = goal.drawn_goal_2_img_path
        goal.save()
    # return HttpResponseRedirect(reverse('frontend:draw_battle_goal'))
    return redirect('frontend:draw_battle_goal', permanent=True)