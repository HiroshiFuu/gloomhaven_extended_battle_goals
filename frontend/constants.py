from os import listdir

GOALS_IMG_PATH = '/static/goals_img'
BATTLE_GOALS = []

def scan_all_goals():
  global BATTLE_GOALS
  BATTLE_GOALS = []
  for goal in listdir('./frontend' + GOALS_IMG_PATH):
    BATTLE_GOALS.append(GOALS_IMG_PATH + '/' + goal)
  # print(BATTLE_GOALS)
scan_all_goals()