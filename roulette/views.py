from django.shortcuts import render_to_response, HttpResponseRedirect
from django.template import RequestContext
from roulette.forms import RandomMeetupForm
from django.conf import settings
import json, urllib2, random

def get_url_proper(url):
	return urllib2.openurl(url).read().decode('latin1').encode('utf8')

def index(request):
	form = RandomMeetupForm()
	return render_to_response('roulette/index.html', {
		'form': form
	}, context_instance = RequestContext(request))

def meetup(request):
	# It's easier to keep tweaking the filter rules if it's ugly like this
	def is_possible_meetup(meetup):
		if "fee" in meetup and meetup['fee']['required'] == 1:
			return False
		elif meetup['group']['join_mode'] != 'open':
			return False
		elif "rsvp_limit" in meetup and meetup['yes_rsvp_count'] >= meetup['rsvp_limit']:
			return False
		elif "venue" not in meetup:
			return False
		else:
			return True
			
	def group_requires_info(group_id):
		url = "https://api.meetup.com/2/groups?key=%s&sign=true&fields=join_info&group_id=%s" % (settings.MEETUP_API_KEY, group_id)
		data = json.loads(get_url_proper(url))
		res = data['results'][0]
		if res['join_info']['questions_req'] == "0" and res['join_info']['intro_req'] == "0":
			return False
		else:
			return res['join_info']
	
	if request.method == 'POST':
		form = RandomMeetupForm(request.POST)
		if form.is_valid():
			lat = form.cleaned_data['lat']
			lon = form.cleaned_data['lon']
			url = "https://api.meetup.com/2/open_events?key=%s&sign=true&lon=%s&lat=%s" % (settings.MEETUP_API_KEY, lon, lat)
			new_form = RandomMeetupForm()
			
			try:
				raw_data = get_url_proper(url)
				meetups = json.loads(raw_data)
			except:
				meetups = {'shit is broken'}
			
			is_okay_to_rsvp = False

			while is_okay_to_rsvp == False:
				meetup = random.choice(meetups['results'])
				is_okay_to_rsvp = is_possible_meetup(meetup)
			
			#group_join_requirements = group_requires_info(meetup['group']['id'])
			# Matt Damon is best test in world
			group_join_requirements = group_requires_info(1781190)
			if group_join_requirements:
				if "questions" in group_join_requirements:
					question_fields = group_join_requirements['questions']
				else:
					question_fields = ()
					
				if group_join_requirements['intro_req'] == "1":
					intro_fields = True
				else:
					intro_fields = False
			else:
				question_fields = ()
				intro_fields = False
			
			return render_to_response('roulette/meetup.html', {
				'meetup': meetup,
				'form': new_form,
				'intro_fields': intro_fields,
				'question_fields': question_fields
			}, context_instance = RequestContext(request))
	else:
		return HttpResponseRedirect('/')
		
def rsvp(request):
	if request.method == "POST":
		# First, the user must join the group
		join_url = "http://api.meetup.com/2/profile/?key=%s&group_id=%s&group_urlname=%s" % (settings.MEETUP_API_KEY, request.POST['group_id'], request.POST['group_urlname'])
		for item in request.POST:
			if item.find('answer') > -1 or item.find('intro') > -1:
				join_url += "&%s=%s" % (item, request.POST[item])
				
		join_resp = get_url_proper(url)
		
		# Then we rsvp them to the event
		url = "https://api.meetup.com/rsvp?event_id=%s&rsvp=yes" % request.POST['event_id']
		response = get_url_proper(url)
		
		return render_to_response('roulette/rsvp.html', {
			'response': request.POST
		}, context_instance = RequestContext(request))
	else:
		return HttpResponseRedirect('/')