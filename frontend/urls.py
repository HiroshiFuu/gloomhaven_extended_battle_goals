from django.urls import path, re_path

from frontend import views

app_name = 'frontend'

urlpatterns = [
    # Matches any html file 
    # re_path(r'^.*\.html', views.pages, name='pages'),

    path('draw_battle_goal/', views.draw_battle_goal, name='draw_battle_goal'),
    path('selected_battle_goal/', views.selected_battle_goal, name='selected_battle_goal'),
]