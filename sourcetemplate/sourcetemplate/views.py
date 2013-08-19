from django.http import HttpResponse, Http404
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse

from django import forms
from django.utils.translation import ugettext_lazy as _
from userena.forms import (SignupForm, AuthenticationForm)

# I want to 
def home(request):
	form_signup = SignupForm
	form_signin = AuthenticationForm
	return render_to_response("home.html", { "form": form_signup, "form_signin": form_signin,}, context_instance=RequestContext(request))

