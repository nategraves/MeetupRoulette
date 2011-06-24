from django.shortcuts import render_to_response
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
			
			try:
				raw_data = urllib2.urlopen(url).read().decode('latin1').encode('utf8')
				meetups = json.loads(raw_data)
			except:
				meetups = {'shit is broken'}
			
			return render_to_response('roulette/meetup.html', {
				'meetup': random.choice(meetups['results'])
			}, context_instance = RequestContext(request))
	else:
		return HttpResponseRedirect('/')