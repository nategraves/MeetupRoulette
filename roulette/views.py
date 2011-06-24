from django.shortcuts import render_to_response, HttpResponseRedirect
from django.template import RequestContext
from roulette.forms import RandomMeetupForm
from django.conf import settings
import json, urllib2, random

def index(request):
	form = RandomMeetupForm()
	return render_to_response('roulette/index.html', {
		'form': form
	}, context_instance = RequestContext(request))
	
def meetup(request):
	if request.method == 'POST':
		form = RandomMeetupForm(request.POST)
		if form.is_valid():
			lat = form.cleaned_data['lat']
			lon = form.cleaned_data['lon']
			url = "https://api.meetup.com/2/open_events?key=%s&sign=true&lon=%s&lat=%s" % (settings.MEETUP_API_KEY, lon, lat)
			new_form = RandomMeetupForm()
			
			try:
				raw_data = urllib2.urlopen(url).read().decode('latin1').encode('utf8')
				meetups = json.loads(raw_data)
			except:
				meetups = {'shit is broken'}
			
			is_okay_to_rsvp = False

			while is_okay_to_rsvp == False:
				meetup = random.choice(meetups['results'])
				if "fee" not in meetup and meetup['group']['join_mode'] == 'open':
					if "rsvp_limit" in meetup and meetup['yes_rsvp_count'] >= meetup['rsvp_limit']:
						is_okay_to_rsvp = False
					else:
 						is_okay_to_rsvp = True
			
			
			return render_to_response('roulette/meetup.html', {
				'meetup': meetup,
				'form': new_form
			}, context_instance = RequestContext(request))
	else:
		return HttpResponseRedirect('/')