from backend.models import SessionContestantDetail, Game, HistoricalGameSession
import random
from datetime import date, timedelta
from leaderboard.celery import app
from celery import shared_task
import time

@app.task
def refresh_scores():
	while True:
		time.sleep(10)
		session_detail = SessionContestantDetail.objects.filter(active=True)
		for det in session_detail:
			det.score = random.randint(0,100)
		SessionContestantDetail.objects.bulk_update(session_detail, ['score'])

@app.task
def refresh_popularity_score():
	while True:
		time.sleep(60)
		games = Game.objects.all()
		max_upvotes = max([game.upvotes  for game in games]) if games else 0  
		for game in games:
			yesterday = date.today()-timedelta(days=1)

			w1 = game.active_session_user_details_count(yesterday, yesterday)
			max_daily_players = game.max_daily_players  

			w2 = SessionContestantDetail.objects.filter(session__game=game, active=True).count()
			max_concurrent_players = game.max_concurrent_players  

			w3 = game.upvotes

			w4 = len(game.active_sessions(yesterday, yesterday))
			lengthiest_session = game.gamesession_set.order_by('duration_in_sec').last()
			max_session_length = lengthiest_session.duration_in_sec if lengthiest_session else 0  

			w5 = w4
			max_daily_sessions = game.max_daily_sessions  
			
			score = (0.3 * (w1/(max_daily_players or 1)) + 
				0.2 * (w2/(max_concurrent_players or 1)) + 
				0.25 * (w3/(max_upvotes or 1)) + 
				0.15 * (w4/(max_session_length or 1) )+ 
				0.1 * (w5/(max_daily_sessions or 1)))
			game.popularity_score = score
			game.save()