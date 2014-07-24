from os.path import basename, dirname
from pyramid.view import view_config
from voluptuous import Schema, MultipleInvalid

from . import run
from crosscompute.libraries import queue
from crosscompute.libraries import validation as v


PACKAGE_TITLE = 'Count buildings in satellite images'
PACKAGE_NAME = basename(dirname(__file__))
ROUTE_NAME = PACKAGE_NAME.replace('_', '-')
DEFAULT_STRFTIME = '%Y-%m-%d %H:%M'


def includeme(config):
    config.add_route(
        ROUTE_NAME, '/%s' % ROUTE_NAME)


@view_config(
    renderer=PACKAGE_NAME + ':show.mako',
    request_method='GET',
    route_name=ROUTE_NAME)
def count_buildings(request):
    return dict(
        title=PACKAGE_TITLE)


@view_config(
    permission='run',
    renderer='json',
    request_method='POST',
    route_name=ROUTE_NAME)
def count_buildings_(request):
    try:
        params = Schema({
            v.Required('classifier_name'): unicode,
            v.Required('image_url'): unicode,
        }, extra=True)(dict(request.params))
    except MultipleInvalid as exception:
        return {'errors': v.render_errors(request, exception.errors)}
    classifier_name = params['classifier_name']
    image_url = params['image_url']
    image_name = basename(image_url)
    target_name = '%s-%s' % (classifier_name, image_name)
    return queue.schedule(
        request, 'gpu', run.schedule, target_name,
        classifier_name, image_url)
