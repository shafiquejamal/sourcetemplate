from django.http import HttpResponse, Http404
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse

from django import forms
from django.utils.translation import ugettext_lazy as _
from userena.forms import (SignupForm, AuthenticationForm)

from django.contrib.auth import authenticate, login, logout, REDIRECT_FIELD_NAME
from userena.forms import (SignupForm, SignupFormOnlyEmail, AuthenticationForm,
                           ChangeEmailForm, EditProfileForm)
from userena.decorators import secure_required
from userena.utils import signin_redirect, get_profile_model, get_user_model
from django.views.generic import TemplateView
from userena import settings as userena_settings
from userena import signals as userena_signals
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages

class ExtraContextTemplateView(TemplateView):
    """ Add extra context to a simple template view """
    extra_context = None

    def get_context_data(self, *args, **kwargs):
        context = super(ExtraContextTemplateView, self).get_context_data(*args, **kwargs)
        if self.extra_context:
            context.update(self.extra_context)
        return context

    # this view is used in POST requests, e.g. signup when the form is not valid
    post = TemplateView.get
# I want to 
def home(request):
	return render_to_response("home.html", { "form_signup": SignupForm, "form_signin": AuthenticationForm,}, context_instance=RequestContext(request))

@secure_required
def signin(request, auth_form=AuthenticationForm,
           template_name='home.html',
           redirect_field_name=REDIRECT_FIELD_NAME,
           redirect_signin_function=signin_redirect, extra_context=None):
    """
    Signin using email or username with password.

    Signs a user in by combining email/username with password. If the
    combination is correct and the user :func:`is_active` the
    :func:`redirect_signin_function` is called with the arguments
    ``REDIRECT_FIELD_NAME`` and an instance of the :class:`User` who is is
    trying the login. The returned value of the function will be the URL that
    is redirected to.

    A user can also select to be remembered for ``USERENA_REMEMBER_DAYS``.

    :param auth_form:
        Form to use for signing the user in. Defaults to the
        :class:`AuthenticationForm` supplied by userena.

    :param template_name:
        String defining the name of the template to use. Defaults to
        ``userena/signin_form.html``.

    :param redirect_field_name:
        Form field name which contains the value for a redirect to the
        succeeding page. Defaults to ``next`` and is set in
        ``REDIRECT_FIELD_NAME`` setting.

    :param redirect_signin_function:
        Function which handles the redirect. This functions gets the value of
        ``REDIRECT_FIELD_NAME`` and the :class:`User` who has logged in. It
        must return a string which specifies the URI to redirect to.

    :param extra_context:
        A dictionary containing extra variables that should be passed to the
        rendered template. The ``form`` key is always the ``auth_form``.

    **Context**

    ``form``
        Form used for authentication supplied by ``auth_form``.

    """
    form = auth_form()

    if request.method == 'POST':
        form = auth_form(request.POST, request.FILES)
        if form.is_valid():
            identification, password, remember_me = (form.cleaned_data['identification'],
                                                     form.cleaned_data['password'],
                                                     form.cleaned_data['remember_me'])
            user = authenticate(identification=identification,
                                password=password)
            if user.is_active:
                login(request, user)
                if remember_me:
                    request.session.set_expiry(userena_settings.USERENA_REMEMBER_ME_DAYS[1] * 86400)
                else: request.session.set_expiry(0)

                if userena_settings.USERENA_USE_MESSAGES:
                    messages.success(request, _('You have been signed in.'),
                                     fail_silently=True)

                # Whereto now?
                redirect_to = redirect_signin_function(
                    request.REQUEST.get(redirect_field_name), user)
                return HttpResponseRedirect(redirect_to)
            else:
                return redirect(reverse('userena_disabled',
                                        kwargs={'username': user.username}))

    if not extra_context: extra_context = dict()
    extra_context.update({
        'form_signin': form,
        'form_signup': SignupForm,
        'next': request.REQUEST.get(redirect_field_name),
    })
    return ExtraContextTemplateView.as_view(template_name=template_name,
                                            extra_context=extra_context)(request)

@secure_required
def signup(request, signup_form=SignupForm,
           template_name='home.html', success_url=None,
           extra_context=None):
    """
    Signup of an account.

    Signup requiring a username, email and password. After signup a user gets
    an email with an activation link used to activate their account. After
    successful signup redirects to ``success_url``.

    :param signup_form:
        Form that will be used to sign a user. Defaults to userena's
        :class:`SignupForm`.

    :param template_name:
        String containing the template name that will be used to display the
        signup form. Defaults to ``userena/signup_form.html``.

    :param success_url:
        String containing the URI which should be redirected to after a
        successful signup. If not supplied will redirect to
        ``userena_signup_complete`` view.

    :param extra_context:
        Dictionary containing variables which are added to the template
        context. Defaults to a dictionary with a ``form`` key containing the
        ``signup_form``.

    **Context**

    ``form``
        Form supplied by ``signup_form``.

    """
    # If no usernames are wanted and the default form is used, fallback to the
    # default form that doesn't display to enter the username.
    if userena_settings.USERENA_WITHOUT_USERNAMES and (signup_form == SignupForm):
        signup_form = SignupFormOnlyEmail

    auth_form=AuthenticationForm
    form_signin = auth_form()

    form = signup_form()

    if request.method == 'POST':
        form = signup_form(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()

            # Send the signup complete signal
            userena_signals.signup_complete.send(sender=None,
                                                 user=user)


            if success_url: redirect_to = success_url
            else: redirect_to = reverse('userena_signup_complete',
                                        kwargs={'username': user.username})

            # A new signed user should logout the old one.
            if request.user.is_authenticated():
                logout(request)

            if (userena_settings.USERENA_SIGNIN_AFTER_SIGNUP and
                not userena_settings.USERENA_ACTIVATION_REQUIRED):
                user = authenticate(identification=user.email, check_password=False)
                login(request, user)

            return redirect(redirect_to)

    if not extra_context: extra_context = dict()
    extra_context['form_signin'] = form_signin
    extra_context['form_signup'] = form
    return ExtraContextTemplateView.as_view(template_name=template_name,
                                            extra_context=extra_context)(request)

