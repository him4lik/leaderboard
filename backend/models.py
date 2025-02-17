from django.db import models
from lib.base_classes import BaseModel
from django.forms.models import model_to_dict
from leaderboard.config import GenderChoices
from datetime import datetime, timedelta, date
from django.utils import timezone

class Contestant(BaseModel):
	username = models.CharField(max_length=30)
	score = models.IntegerField(default=0)
	date_joined = models.DateTimeField(auto_now_add=True, null=True)
	gender = models.CharField(max_length=10, choices=[(i.name, i.value) for i in GenderChoices], null=True, blank=True)

	@classmethod
	def add_contestant(cls, username, gender):
		if not username:
			return {"success": False, "msg":"Username not provided"}
		contestant, created = cls.objects.get_or_create(username=username)
		if not created:
			return {"success": False, "msg":"Username already taken"}
		contestant.gender = gender
		contestant.save()
		return {"success":True}

	def update_contestant(self, data):
		pass

	def jsonify(self):
		data = model_to_dict(self, exclude=[])
		data['date_joined'] = self.date_joined.strftime('%Y-%m-%d')
		data['gender'] = self.gender or ""
		return data

class Game(BaseModel):
	name = models.CharField(max_length=30)
	active = models.BooleanField(default=False)
	description = models.TextField(null=True, blank=True)
	popularity_score = models.FloatField(default=0)
	upvotes = models.IntegerField(default=0)

	@property
	def max_concurrent_players(self):
		concurrent_players = HistoricalGameSession.objects.filter(game=self).order_by('concurrent_players')
		max_concurrent_players = concurrent_players.last().concurrent_players if concurrent_players else 0
		return max_concurrent_players

	@classmethod
	def add_game(cls, name, active):
		game, created = cls.objects.get_or_create(name=name)
		if not created:
			return {"success": False, "error":"Game with provided name already exists"}
		game.active = active
		game.save()
		return {"success":True}

	def update_game(self, data):
		pass

	def jsonify(self):
		data = model_to_dict(self, exclude=[])
		data['action'] = False if self.active else True
		session = self.gamesession_set.filter(active=True).last()
		data['num_participents'] = session.contestants.count() if session else None
		data['possible_contestants'] = [{"username":contestant.username, "id":contestant.id} for contestant in Contestant.objects.exclude(id__in=[i.id for i in session.contestants.all()])] if session else []
		data['sessions_played'] = GameSession.objects.filter(game=self).count()
		return data

	def __str__(self):
		return self.name

	def end_all_sessions(self):
		sessions = self.gamesession_set.all()
		for session in sessions:
			session.active = False
			session.save()
		cont_detail = SessionContestantDetail.objects.filter(session__in=sessions, active=True)
		for i in cont_detail:
			i.active=False
			i.save()

	def save(self, *args, **kwargs):
		game = Game.objects.filter(pk=self.pk)
		if game and self.active==True and game.first().active == False:
			GameSession.create_session(self.name)
		elif game and self.active==False and game.first().active == True:
			self.end_all_sessions()
		elif not game and self.active == True:
			GameSession.create_session(self.name)
		super(Game, self).save(*args, **kwargs)

	def active_sessions(self, start_date, end_date):
		final1 = HistoricalGameSession.objects.filter(
			game = self,
			active=True,
			history_date__date__lte=end_date,
			history_date__date__gte=start_date).order_by('id', 'history_date').distinct('id')

		final2 = HistoricalGameSession.objects.filter(
			game = self,
			history_date__date__lt=start_date,
			history_date__date__gte=start_date-timedelta(days=1)).order_by('id', 'history_date').distinct('id')
		
		return final1 or final2


	def active_session_user_details_count(self, start_date, end_date):
		active_sessions = self.active_sessions(start_date, end_date)
		final1 = HistoricalSessionContestantDetail.objects.filter(
			session_id__in=[i.id for i in active_sessions],
			history_date__date__lt=start_date,
			history_date__date__gte=start_date-timedelta(days=1)).order_by('id', 'history_date').distinct('id')
	
		final2 = HistoricalSessionContestantDetail.objects.filter(
			session_id__in=[i.id for i in active_sessions],
			active=True,
			history_date__date__lte=end_date,
			history_date__date__gte=start_date).order_by('id', 'history_date').distinct('id')
		users = set([i.contestant for i in final1 | final2])
		return len(users)

	@property
	def max_daily_sessions(self):
		his_date = HistoricalGameSession.objects.filter(game=self).order_by('history_date').first()
		if his_date:
			start_date = his_date.history_date.date()
		else:
			start_date = date.today()
		max_sessions = 0
		for i in range((date.today() - start_date).days + 1):
			current_date = start_date + timedelta(days=i)
			max_sessions = max(max_sessions, len(self.active_sessions(current_date, current_date)))
		return max_sessions

	@property
	def max_daily_players(self):
		his_detail = HistoricalSessionContestantDetail.objects.filter(session__game=self).order_by('history_date').first()
		if his_detail:
			start_date = his_detail.history_date.date()
		else:
			start_date = date.today()
		max_players = 0
		for i in range((date.today() - start_date).days + 1):
			current_date = start_date + timedelta(days=i)
			max_players = max(max_players, self.active_session_user_details_count(current_date, current_date))
			return max_players


class GameSession(BaseModel):
	game = models.ForeignKey(Game, on_delete=models.CASCADE)
	contestants = models.ManyToManyField(Contestant, through='SessionContestantDetail')
	active = models.BooleanField(default=True)
	duration_in_sec = models.IntegerField(blank=True, default=0)
	concurrent_players = models.IntegerField(default=0)
	date_created = models.DateTimeField(auto_now_add=True)

	def jsonify(self):
		data = model_to_dict(self, exclude=[])
		data['game'] = self.game.name
		data['contestants'] = self.contestants.all()
		data['duration_in_sec'] = f"{self.duration_in_sec//60} min {self.duration_in_sec%60} sec"
		data['date_created'] = self.date_created.strftime('%Y-%m-%d %H:%M:%S')
		return data

	@classmethod
	def create_session(cls,  name):
		try:
			game = Game.objects.get(name=name)
		except Game.DoesNotExist:
			return {"success":False,"msg":"Invalid game name"}
		live_sessions = cls.objects.filter(game=game, active=True)
		if live_sessions:
			return {"success":False,"msg":"One game session is already active"}
		cls.objects.create(game=game)
		return {"success":True,"msg":"Game session created"}

	def add_contestants(self, contestants):
		for contestant in contestants:
			try:
				session_detail = SessionContestantDetail.objects.get(
					contestant=contestant,
					session=self,
					)
				session_detail.active = True
			except:
				session_detail = SessionContestantDetail(
					contestant=contestant,
					session=self)
			session_detail.save()
			self.contestants.add(contestant)

	def save(self, *args, **kwargs):
		session = GameSession.objects.filter(pk=self.pk).last()
		if session and self.active == False and session.active == True:
			self.duration_in_sec = (timezone.now() - self.date_created).seconds
		super(GameSession, self).save(*args, **kwargs)


class SessionContestantDetail(BaseModel):
	contestant = models.ForeignKey(Contestant, on_delete=models.CASCADE)
	session = models.ForeignKey(GameSession, on_delete=models.CASCADE)
	entry_time = models.DateTimeField(auto_now_add=True)
	score = models.IntegerField(default=0)
	active = models.BooleanField(default=True)
	

	def save(self, *args, **kwargs):
		session_detail = SessionContestantDetail.objects.filter(pk=self.pk).last()
		if session_detail and session_detail.active == True and self.active == False:
			his_detail = session_detail.history.filter(active=False).order_by('history_date').last()
			if his_detail:
				self.contestant.score = self.contestant.score - his_detail.score + self.score
			else:
				self.contestant.score += self.score
			self.contestant.save()
		if not session_detail or (session_detail.active != self.active):
			offset = 1 if self.active else 0
			game = self.session.game
			self.session.concurrent_players = SessionContestantDetail.objects.filter(active=True, session__game=game).count() + offset
			self.session.save()
		super(SessionContestantDetail, self).save(*args, **kwargs)

	def jsonify(self):
		data = model_to_dict(self, exclude=[])
		data['contestant'] = self.contestant
		data['session'] = self.session
		data['entry_time'] = self.entry_time.strftime("%Y-%m-%d %H:%M:%S")
		return data
