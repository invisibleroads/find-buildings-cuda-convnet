from pyramid.config import Configurator

from . import view


def describe():
    return dict(
        route=view.ROUTE_NAME,
        title=view.PACKAGE_TITLE)


def includeme(config):
    config.scan()
    config.include(view)
    config.add_static_view(
        view.ROUTE_NAME + '/_',
        view.PACKAGE_NAME + ':assets', cache_max_age=3600)


def main(global_config, **settings):
    config = Configurator(settings=settings)
    config.include('crosscompute')
    includeme(config)
    return config.make_wsgi_app()
