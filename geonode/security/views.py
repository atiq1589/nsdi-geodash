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

try:
    import json
except ImportError:
    from django.utils import simplejson as json
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse
from django.views.decorators.http import require_POST
from django.shortcuts import get_object_or_404
from django.conf import settings
from django.core.mail import send_mail

from notify.signals import notify

from geonode.utils import resolve_object
from geonode.base.models import ResourceBase
from geonode.layers.models import Layer
from geonode.documents.models import Document
from geonode.maps.models import Map

if "notification" in settings.INSTALLED_APPS:
    from notification import models as notification


def _perms_info(obj):
    info = obj.get_all_level_info()

    return info


def _perms_info_json(obj):
    info = _perms_info(obj)
    info['users'] = dict([(u.username, perms)
                          for u, perms in info['users'].items()])
    info['groups'] = dict([(g.name, perms)
                           for g, perms in info['groups'].items()])

    return json.dumps(info)


def resource_permissions(request, resource_id):
    try:
        resource = resolve_object(
            request, ResourceBase, {
                'id': resource_id}, 'base.change_resourcebase_permissions')

    except PermissionDenied:
        # we are handling this in a non-standard way
        return HttpResponse(
            'You are not allowed to change permissions for this resource',
            status=401,
            content_type='text/plain')

    if request.method == 'POST':
        permission_spec = json.loads(request.body)
        resource.set_permissions(permission_spec)

        return HttpResponse(
            json.dumps({'success': True}),
            status=200,
            content_type='text/plain'
        )

    elif request.method == 'GET':
        permission_spec = _perms_info_json(resource)
        return HttpResponse(
            json.dumps({'success': True, 'permissions': permission_spec}),
            status=200,
            content_type='text/plain'
        )
    else:
        return HttpResponse(
            'No methods other than get and post are allowed',
            status=401,
            content_type='text/plain')


@require_POST
def set_bulk_permissions(request):

    permission_spec = json.loads(request.POST.get('permissions', None))
    resource_ids = request.POST.getlist('resources', [])
    if permission_spec is not None:
        not_permitted = []
        for resource_id in resource_ids:
            try:
                resource = resolve_object(
                    request, ResourceBase, {
                        'id': resource_id
                    },
                    'base.change_resourcebase_permissions')
                resource.set_permissions(permission_spec)
            except PermissionDenied:
                not_permitted.append(ResourceBase.objects.get(id=resource_id).title)

        return HttpResponse(
            json.dumps({'success': 'ok', 'not_changed': not_permitted}),
            status=200,
            content_type='text/plain'
        )
    else:
        return HttpResponse(
            json.dumps({'error': 'Wrong permissions specification'}),
            status=400,
            content_type='text/plain')


@require_POST
def request_permissions(request):
    """ Request permission to download a resource.
    """
    uuid = request.POST['uuid']
    resource = get_object_or_404(ResourceBase, uuid=uuid)
    try:
        # notification.send(
        #     [resource.owner],
        #     'request_download_resourcebase',
        #     {'from_user': request.user, 'resource': resource}
        # )
        # notify layer owners that this layer is requested to download
        if resource.resource_type == 'layer':
            verb = 'requested to download your layer'
            resource = Layer.objects.get(id=resource.id)
        elif resource.resource_type == 'document':
            verb = 'requested to download your document'
            resource = Document.objects.get(id=resource.id)
        elif resource.resource_type == 'map':
            verb = 'requested to download your map'
            resource = Map.objects.get(id=resource.id)
        try:
            body = """
            You have received the following notice from {0}



            The user {1} requested you to download this {2}:
            {3}


            {4}


            Please go to resource page and assign the download permissions if you wish.



            To see other notices or change how you receive notifications, please go to {5}
            """.format(settings.SITEURL, request.user, resource.resource_type, resource.title, settings.SITEURL[:-1]+resource.detail_url, settings.SITEURL)

            send_mail(
            "A  {}'s download has been requested".format(resource.resource_type),
            body,

            request.user.email,
            [resource.owner.email],
            fail_silently=False,
            )
        except:
            pass

        notify.send(request.user, recipient=resource.owner, actor=request.user,
            verb='requested to download your resource', target=resource)
        return HttpResponse(
            json.dumps({'success': 'ok', }),
            status=200,
            content_type='text/plain')
    except:
        return HttpResponse(
            json.dumps({'error': 'error delivering notification'}),
            status=400,
            content_type='text/plain')
