from django.conf.urls import patterns, include, url
from django.conf import settings
from accounts.forms import EditProfileForm2
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required

from django.views.generic import TemplateView
from userena import views as userena_views

from django.conf.urls.i18n import i18n_patterns

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
	(r'^i18n/', include('django.conf.urls.i18n')),
)

urlpatterns += i18n_patterns('',
    # Examples:
    # url(r'^$', 'nr.views.home', name='home'),
    # url(r'^nr/', include('nr.foo.urls')),
    # For django-userena
    (r'^accounts/', include('userena.urls')), 
    url(r'^$', 'sourcetemplate.views.home', name='home'),
    # The contact form - its just a page with an email address
    url(r'^contact/$', login_required(TemplateView.as_view(template_name="contact.html")), name="contact"),
    url(r'^faq/$', TemplateView.as_view(template_name="faq.html"), name="faq"),
    url(r'^termsandconditions/$', TemplateView.as_view(template_name="termsandconditions.html"), name="termsandconditions"),

    # Uncomment the admin/doc line below to enable admin documentation:
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
)

# urlpatterns += patterns('', (r'^static/(.*)$', 'django.views.static.serve', { 'document_root': settings.STATIC_ROOT }), ) 
urlpatterns += i18n_patterns('', (r'^static/(.*)$', 'django.views.static.serve', { 'document_root': settings.STATIC_ROOT }), ) 
urlpatterns += i18n_patterns('', (r'^media/(.*)$', 'django.views.static.serve',  { 'document_root': settings.MEDIA_ROOT }), ) 
