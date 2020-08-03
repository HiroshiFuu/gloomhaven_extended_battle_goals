# -*- coding:utf-8 -*-
from django import http
from django.urls import reverse

import logging
logger = logging.getLogger(__name__)


def index(request):
	if request.user.is_authenticated:
		# url = reverse('users:detail', kwargs={'username': request.user.username})
		return http.HttpResponseRedirect('draw_battle_goal/')
	else:
		return http.HttpResponseRedirect(reverse('account_login'))
