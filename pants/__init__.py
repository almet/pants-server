from pyramid.config import Configurator
from pyramid.events import NewRequest
from tokenlib import TokenManager


def main(global_config, **settings):
    # We need to disable cornice's exception handling views
    settings.setdefault("handle_exceptions", False)

    config = Configurator(settings=settings)
    config.include("pyramid_hawkauth")
    config.include("cornice")
    config.include("pyramid_jinja2")
    config.add_jinja2_search_path("pants:templates")

    config.scan("pants.views")

    token_manager = TokenManager(secret=settings['token-secret'])
    config.registry.token_manager = token_manager

    def add_db_to_request(event):
        event.request.token_manager = token_manager
    config.add_subscriber(add_db_to_request, NewRequest)

    return config.make_wsgi_app()
