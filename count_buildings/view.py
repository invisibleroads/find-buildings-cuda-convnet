from os.path import basename, dirname
from pyramid.view import view_config
from voluptuous import Boolean, Optional, Schema, MultipleInvalid

from . import run
from crosscompute.libraries import queue
from crosscompute.libraries import validation as v
from crosscompute.models import User, Result, db


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
    user_id = request.authenticated_userid
    try:
        params = Schema({
            v.Required('source_geoimage'): SourceResult(user_id),
            v.Required('classifier_name'): unicode,
            Optional('is_preview'): Boolean(),
        }, extra=True)(dict(request.params))
    except MultipleInvalid as exception:
        return {'errors': v.render_errors(request, exception.errors)}

    source_geoimage = params['source_geoimage']
    classifier_name = params['classifier_name']
    is_preview = params.get('is_preview', False)

    geoimage_summary = source_geoimage.summary
    area_in_square_meters = geoimage_summary['area_in_square_meters']
    try:
        price = run.price(area_in_square_meters)
    except KeyError:
        request.response.status_code = 400
        return {'errors': dict(
            source_geoimage='only geotiffs supported at this time')}
    if geoimage_summary['band_count'] != 4:
        request.response.status_code = 400
        return {'errors': dict(
            source_geoimage='only four band images supported at this time')}

    user = db.query(User).get(request.authenticated_userid)
    balance = user.account.balance
    if 'check' in params:
        return dict(price=price, balance=balance)
    if not is_preview and price > balance:
        request.response.status_code = 400
        return {'errors': dict(price=price, balance=balance)}

    if not is_preview and area_in_square_meters > 5000000:
        queue_type = 'gpu_large'
    else:
        queue_type = 'gpu_small'
    target_name = '%s-%s' % (classifier_name, source_geoimage.name)
    return queue.schedule(
        request, queue_type, run, target_name, price,
        source_geoimage.id, classifier_name, is_preview=is_preview)


def SourceResult(user_id):
    return lambda id: Result.get(user_id, id)
