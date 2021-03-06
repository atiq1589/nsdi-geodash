# -*- coding: utf-8 -*-
#########################################################################
#
# Copyright (C) 2016 OSGeo
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
#########################################################################

from django.conf.urls import include, patterns, url
from django.conf import settings
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf.urls.static import static
from geonode.sitemap import LayerSitemap, MapSitemap
from django.views.generic import TemplateView
from django.contrib import admin

import geonode.proxy.urls
from geonode.api.urls import api
from geonode.cms.views import IndexClass

import autocomplete_light

# Setup Django Admin
autocomplete_light.autodiscover()

admin.autodiscover()

js_info_dict = {
    'domain': 'djangojs',
    'packages': ('geonode',)
}

sitemaps = {
    "layer": LayerSitemap,
    "map": MapSitemap
}

urlpatterns = patterns('',

                       # Social authentication
                       url('', include('social.apps.django_app.urls', namespace='social')),

                       # Static pages
                       url(r'^categories_key_words/?$', TemplateView.as_view(template_name='categories_key_words.html'),name='categories_key_words'),
                       # url(r'^/?$', TemplateView.as_view(template_name='index.html'), name='home'),
                       url(r'^/?$', IndexClass.as_view(), name='home'),
                       url(r'^help/$', TemplateView.as_view(template_name='help.html'), name='help'),
                       url(r'^developer/$', TemplateView.as_view(template_name='developer.html'), name='developer'),
                       url(r'^about/$', TemplateView.as_view(template_name='about.html'), name='about'),
                       # Overpass-turbo Files
                       url(r'^overpass_turbo/$', TemplateView.as_view(template_name='overpass_turbo.html'), name='overpass_turbo'),
                       url(r'^formtest/$', TemplateView.as_view(template_name='formtest.html'), name='formtest'),
                       url(r'^add_news/$', TemplateView.as_view(template_name='news/add_news.html'), name='add_news'),
                       url(r'^notifications/$', TemplateView.as_view(template_name='notification/notifications_detail_page.html'), name='notifications_all'),

                       # Layer views
                       (r'^layers/', include('geonode.layers.urls')),

                       # News views
                       (r'^news/', include('geonode.news.urls')),

                       # workspace views
                       (r'^workspace/', include('geonode.workspace.urls')),

                       # nsdi views
                       url(r'^nsdi/', include('geonode.nsdi.urls')),

                       # Map views
                       (r'^maps/', include('geonode.maps.urls')),

                       # cms
                       (r'^cms/', include('geonode.cms.urls')),

                       # Catalogue views
                       (r'^catalogue/', include('geonode.catalogue.urls')),

                       # dashboard views
                       (r'^dashboard/', include('geonode.dashboard.urls')),

                       # data.json
                       url(r'^data.json$', 'geonode.catalogue.views.data_json', name='data_json'),

                       # ident
                       url(r'^ident.json$', 'geonode.views.ident_json', name='ident_json'),

                       # Search views
                       url(r'^search/$', TemplateView.as_view(template_name='search/search.html'), name='search'),
                       url(r'^searchuser/$', TemplateView.as_view(template_name='search/searchuser.html'), name='searchuser'),
                       url(r'^searchorg/$', TemplateView.as_view(template_name='search/searchorg.html'), name='searchorg'),

                       # user notification url
                       url(r'^notifications/', include('notify.urls', 'notifications')),

                       # Social views
                       (r"^account/", include("account.urls")),
                       (r'^user/', include('geonode.people.urls')),
                       (r'^avatar/', include('avatar.urls')),
                       (r'^comments/', include('geonode.dialogos.urls')),
                       (r'^ratings/', include('agon_ratings.urls')),
                       (r'^activity/', include('actstream.urls')),
                       (r'^announcements/', include('announcements.urls')),
                       (r'^messages/', include('user_messages.urls')),
                       (r'^social/', include('geonode.social.urls')),
                       (r'^security/', include('geonode.security.urls')),

                       # Accounts
                       url(r'^account/ajax_login$', 'geonode.views.ajax_login', name='account_ajax_login'),
                       url(r'^account/ajax_lookup$', 'geonode.views.ajax_lookup', name='account_ajax_lookup'),

                       # Meta
                       url(r'^topiccategory/create$', 'geonode.views.topiccategory_create', name='topiccategory-create'),
                       url(r'^topiccategory/list$', 'geonode.views.topiccategory_list', name='topiccategory-list'),
                       url(r'^topiccategory/delete$', 'geonode.views.topiccategory_delete', name='topiccategory-delete'),
                       url(r'^lang\.js$', TemplateView.as_view(template_name='lang.js', content_type='text/javascript'),
                           name='lang'),

                       #keywords
                       url(r'^keyword/create$', 'geonode.views.keyword_create', name='keyword-create'),
                       url(r'^keyword/list$', 'geonode.views.keyword_list', name='keyword-list'),
                       url(r'^keyword/delete$', 'geonode.views.keyword_delete', name='keyword-delete'),

                       url(r'^jsi18n/$', 'django.views.i18n.javascript_catalog', js_info_dict, name='jscat'),
                       url(r'^sitemap\.xml$', 'django.contrib.sitemaps.views.sitemap', {'sitemaps': sitemaps},
                           name='sitemap'),

                       (r'^i18n/', include('django.conf.urls.i18n')),
                       (r'^autocomplete/', include('autocomplete_light.urls')),
                       (r'^admin/', include(admin.site.urls)),
                       (r'^organization/', include('geonode.groups.urls')),
                       (r'^documents/', include('geonode.documents.urls')),
                       (r'^services/', include('geonode.services.urls')),
                       url(r'', include(api.urls)),
                       )

if "geonode.contrib.dynamic" in settings.INSTALLED_APPS:
    urlpatterns += patterns('',
                            (r'^dynamic/', include('geonode.contrib.dynamic.urls')),
                            )

if "geonode.contrib.metadataxsl" in settings.INSTALLED_APPS:
    urlpatterns += patterns('',
                            (r'^showmetadata/', include('geonode.contrib.metadataxsl.urls')),
                            )

if 'geonode.geoserver' in settings.INSTALLED_APPS:
    # GeoServer Helper Views
    urlpatterns += patterns('',
                            # Upload views
                            (r'^upload/', include('geonode.upload.urls')),
                            (r'^gs/', include('geonode.geoserver.urls')),
                            )

if 'notification' in settings.INSTALLED_APPS:
    urlpatterns += patterns('',
                            (r'^notifications/', include('notification.urls')),
                            )

# Set up proxy
urlpatterns += geonode.proxy.urls.urlpatterns

# Serve static files
urlpatterns += staticfiles_urlpatterns()
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
handler403 = 'geonode.views.err403'

# Featured Maps Pattens
urlpatterns += patterns('',
                        (r'^featured/(?P<site>[A-Za-z0-9_\-]+)/$', 'geonode.maps.views.featured_map'),
                        (r'^featured/(?P<site>[A-Za-z0-9_\-]+)/info$', 'geonode.maps.views.featured_map_info'),
                        )

