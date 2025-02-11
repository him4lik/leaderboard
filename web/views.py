from lib.base_classes import BaseView
from backend.models import Contestant, Game,GameSession, SessionContestantDetail, HistoricalContestant
from .forms import ContestantForm, GameForm, ContestantUpdateForm, GameUpdateForm, GameSessionForm
from django.urls import reverse
from django.shortcuts import render, HttpResponse, redirect, reverse
from django.http import HttpResponseRedirect
from django.db.models import Sum, OuterRef, Subquery, Sum

class AdminDashboardView(BaseView):
	template_name = 'admin_dashboard.html'
	contestant_form = ContestantForm
	game_form = GameForm
	session_form = GameSessionForm

	def get_context_data(self, request):
		as_on = request.GET.get("as_on", None)
		context = {}
		forms = [self.contestant_form(), self.game_form(), self.session_form()]
		if as_on:
			contestants = HistoricalContestant.objects.filter(history_date__date__lte=as_on).order_by('id', 'history_date').distinct('id')
			contestants = sorted([c.__dict__ for c in contestants], key=lambda x: x["score"]) 
		else:
			contestants = Contestant.objects.all().order_by('-score', 'date_joined')
			contestants = [contestant.jsonify() for contestant in contestants]
		games = Game.objects.all().order_by('name')
		rank = 1
		if contestants:
			prev_score = contestants[0]['score']
			contestants[0]['rank'] = 1
			for contestant in contestants[1:]:
				print(contestant['score'], prev_score)
				if contestant['score'] < prev_score:
					print(contestant['score'], prev_score, rank)
					rank += 1
					prev_score = contestant['score'] 
				contestant['rank'] = rank
					
		context['data'] = {
			"contestants":contestants,
			"games":[game.jsonify() for game in games],
			}
		# print(context)
		context['user'] = request.user
		context['forms'] = forms
		context['errors'] = request.GET.get('errors', '')
		context['as_on'] = as_on

		return context

	def post_context_data(self, request):
		# token = request.token
		context = {}
		# forms = [self.form()]
		username = request.POST.get('username', None)
		gender = request.POST.get('gender', None)
		print(gender)
		resp = Contestant.add_contestant(username, gender)
		# if resp['success'] == False:
			
		contestants = Contestant.objects.all().order_by('score', 'date_joined')
		games = Game.objects.all().order_by('name')
		context['data'] = [contestant.jsonify() for contestant in contestants]
		context['user'] = request.user
		context['forms'] = forms
		return context

class ContestantCRUDView(BaseView):
	template_name = 'contestant_update.html'
	update_form = ContestantUpdateForm 

	def post_context_data(self, request):
		context = {}
		return context

	def validate_request(self, request, action):
		username = request.POST.get('username', None)
		gender = request.POST.get('gender', None)
		success = True
		msg = "Validated"
		if gender and gender not in ['Male', 'Female']:
			success = False
			msg = "Gender can only be Male or Female"
		if not username:
			success = False
			msg = "Username can't be empty"
		return {"success":success, "data":{"username":username, "gender":gender}, "msg":msg}

	def post(self, request, action):
		resp = self.validate_request(request, action) 
		if resp.get('success', False) == True:
			if action == 'add':
				result = Contestant.add_contestant(resp['data']['username'], resp['data']['gender'])
				if result.get('success', False) == True:
					return redirect(reverse('admin-dashboard')) 
				return redirect(reverse('admin-dashboard', kwargs={"errors":result.get('msg', "Something went wrong")}))
			elif action == 'delete':
				try:
					contestant = Contestant.objects.get(username=resp['data']['username'])
					contestant.delete()
					return redirect(reverse('admin-dashboard'))
				except Contestant.DoesNotExist:
					return redirect(reverse('admin-dashboard', kwargs={"errors":"Contestant does not exists"}))
			elif action == 'update':
				try:
					contestant = Contestant.objects.get(username=resp['data']['username'])
					form = self.update_form(request.POST)
					if form.is_valid():
						contestant.gender = request.POST.get('gender', contestant.gender)
						contestant.save()
						return redirect(reverse('admin-dashboard'))
					context = {
						"forms": [self.update_form(instance=contestant)]
					}
					return render(request, self.template_name, context) 
				except Contestant.DoesNotExist:
					return redirect(reverse('admin-dashboard', kwargs={"errors":"Contestant does not exists"}))
		return redirect(reverse('admin-dashboard')+f"?errors={resp.get('msg', 'Something went wrong')}")

class GameCRUDView(BaseView):
	update_form = GameUpdateForm
	template_name = 'game_update.html'

	def post_context_data(self, request):
		context = {}
		return context

	def validate_request(self, request, action):
		print(request.POST)
		name = request.POST.get('name', None)
		active = True if request.POST.get('active', None) == 'on' else None
		success = True
		msg = "Validated"
		if not name:
			success = False
			msg = "Name can't be empty"
		return {"success":success, "data":{"name":name, "active":active}, "msg":msg}

	def post(self, request, action):
		resp = self.validate_request(request, action) 
		if resp.get('success', False) == True:
			if action == 'add':
				active = True if resp['data']['active'] == True else False
				result = Game.add_game(resp['data']['name'], active)
				if result.get('success', False) == True:
					return redirect(reverse('admin-dashboard')) 
				return redirect(reverse('admin-dashboard')+ f"?errors={result.get('msg', 'Something went wrong')}")
			elif action == 'delete':
				try:
					game = Game.objects.get(name=resp['data']['name'])
					game.delete()
					return redirect(reverse('admin-dashboard'))
				except Game.DoesNotExist:
					return redirect(reverse('admin-dashboard', kwargs={"errors":"Game does not exists"}))
			elif action == 'update':
				print(request.POST)
				name = request.POST.get('name', None)
				try:
					game = Game.objects.get(name=resp['data']['name'])
					if len(request.POST)>2:
						form = self.update_form(request.POST)
						if form.is_valid():
							active = True if request.POST.get('active', None) in [True, 'on', "True"] else False
							game.active = active
							game.description = request.POST.get('description', None)
							game.save()
							return redirect(reverse('admin-dashboard'))
					context = {
						"forms": [self.update_form(instance=game)]
					}
					return render(request, self.template_name, context) 
				except Game.DoesNotExist:
					return redirect(reverse('admin-dashboard', kwargs={"errors":"Contestant does not exists"}))
		return redirect(reverse('admin-dashboard')+ f"?errors={resp.get('msg', 'Something went wrong')}")


class GameSessionView(BaseView):
	template_name = 'game_sessions.html'
	session_form = GameSessionForm

	def get_context_data(self, request):
		print(request.GET)
		context = {}
		name = request.GET.get('name',None)
		as_on = request.GET.get('as_on',None)
		# forms = [self.session_form({"game":name})]
		if not name:
			context['errors'] = "Name of the game was not provided"
			return context
		sessions = GameSession.objects.filter(game__name=name).order_by('-id')

		leaders = []
		if as_on:
			leaders = Contestant.objects.filter(
				sessioncontestantdetail__session__game__name=name, 
				sessioncontestantdetail__entry_time__date__lte=as_on).annotate(
			    tot_score=Subquery(
			        SessionContestantDetail.objects.filter(
			        	session__game__name=name,
			            contestant=OuterRef('pk'),
			            entry_time__date__lte=as_on
			        ).values('contestant').annotate(total_score=Sum('score')).values('total_score')[:1]
			    )
			).distinct()
			leaders = leaders.order_by('-tot_score')
		else:
			leaders = Contestant.objects.filter(sessioncontestantdetail__session__game__name=name).annotate(tot_score = Sum('sessioncontestantdetail__score')).order_by('-tot_score')

		context['data'] = {
			"sessions":[session.jsonify() for session in sessions],
			}
		context['user'] = request.user
		context['game_name'] = name
		context['errors'] = request.GET.get('errors', '')
		context['leaders'] = leaders
		context['as_on'] = as_on

		return context

	def post_context_data(self, request):
		context = {}
		return context

	def validate_request(self, request):
		print(request.POST)
		game = request.POST.get('game', None)
		success = True
		msg = "Validated"
		if not game:
			success = False
			msg = "Name can't be empty"
		return {"success":success, "data":{"game":game}, "msg":msg}

	def post(self, request):
		resp = self.validate_request(request) 
		action = request.POST.get('action', None)
		game_name = resp['data']['game']
		if resp.get('success', False) == True:
			if action == 'add':
				resp = GameSession.create_session(game_name)
			elif action == 'delete':
				pass
			elif action == 'update':
				game = Game.objects.get(name=game_name)
				if not game.active:
					return redirect(reverse('admin-dashboard')+ f"?errors={resp.get('msg', 'Something went wrong')}")
				session = game.gamesession_set.filter(active=True).last()
				contestants = Contestant.objects.filter(id__in=request.POST.getlist('contestant_ids', []))
				session.add_contestants(contestants)
		if resp.get('success',False) == True:
			return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
		return redirect(reverse('game-session')+ f"?errors={resp.get('msg', 'Something went wrong')}")


class GameSessionStatusView(BaseView):
	template_name = 'session_status.html'
	# contestant_form = ContestantForm
	# game_form = GameForm
	# session_form = GameSessionForm

	def get_context_data(self, request):
		context = {}
		# forms = [self.contestant_form(), self.game_form(), self.session_form()]
		session = GameSession.objects.get(id=request.GET.get('id', None))
		active = False
		if session.active:
			active = True
		cont_details = SessionContestantDetail.objects.filter(session=session, active=active).order_by('score')
		
		context['data'] = {
			"cont_details":[cont_detail.jsonify() for cont_detail in cont_details],
			}
		context['user'] = request.user
		# context['forms'] = forms
		# context['errors'] = request.GET.get('errors', '')

		return context

	def post_context_data(self, request):
		print(request.POST)
		cont_detail = SessionContestantDetail.objects.get(id=request.POST['id'])
		action = request.POST.get('action', '')
		session = cont_detail.session
		if action == 'Add':
			session.contestants.add(cont_detail.contestant)
			cont_detail.active = True
		else:
			session.contestants.remove(cont_detail.contestant)
			cont_detail.active = False

		cont_detail.save()
		
		
		context = {}
		cont_details = SessionContestantDetail.objects.filter(session=session, active=True).order_by('score')
		
		context['data'] = {
			"cont_details":[cont_detail.jsonify() for cont_detail in cont_details],
			}
		context['user'] = request.user
		
		return context