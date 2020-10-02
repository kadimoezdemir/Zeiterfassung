from flask import Flask
from flask_assets import Environment
from flask_mongoengine import MongoEngine, MongoEngineSessionInterface
from flask_login import LoginManager
from flask_debugtoolbar import DebugToolbarExtension
from flask_bootstrap import Bootstrap
from webassets.loaders import PythonLoader as PythonAssetsLoader

from app import assets
from app.models.models import Mitarbeiter

assets_env = Environment()

def create_app(config=None):
    """
    Factory pattern; create new app with specified config
    :param config: configuration object
    :return: app object
    """

    # new app object
    app = Flask('flask-example')

    # configure app
    app.config.from_object(config)

    # set up database
    db = MongoEngine()
    db.init_app(app);

    #use mongo engine for session store
    app.session_interface = MongoEngineSessionInterface(db)

    # set up assets
    assets_env.init_app(app)

    # set up toolbar
    debug_toolbar = DebugToolbarExtension()
    debug_toolbar.init_app(app)

    # initialize login manager
    login_manager = LoginManager()
    login_manager.login_view = "main.login"
    login_manager.login_message_category = "warning"
    login_manager.init_app(app)

    # initialize bootstrap
    bootstrap = Bootstrap(app)

    @login_manager.user_loader
    def load_user(user_id):
        return Mitarbeiter.objects(username=user_id).first()

    # import and register the different asset bundles
    assets_loader = PythonAssetsLoader(assets)
    for name, bundle in assets_loader.load_bundles().items():
        assets_env.register(name, bundle)

    # load blueprints
    load_blueprints(app)

    return app


def load_blueprints(app):
    """
    Load all blueprints
    :param app: app in which blueprints are registered
    :return:
    """
    from .standardfunktionen.zeitstempel.views import meine_zeitstempel
    from .standardfunktionen.statistiken.views import meine_statistiken
    from .standardfunktionen.statistiken.meine_statistiken_ap5.views import meine_statistiken_ap5
    from .standardfunktionen.statistiken.meine_statistiken_ap6.views import meine_statistiken_ap6

    from .personalmanagement.views import personalmanagement
    from .personalmanagement.mitarbeiter.views import mitarbeiter
    from .personalmanagement.fehltage.views import fehltage
    from .personalmanagement.statistiken.views import statistiken
    from .personalmanagement.statistiken.statistiken_ap5.views import statistiken_ap5
    from .personalmanagement.statistiken.statistiken_ap6.views import statistiken_ap6
    from .personalmanagement.zeitstempel.views import zeitstempel

    # @andreas bitte entfernen sobald die anmeldung auf mitarbeiter umgestellt ist
    from .main.views import main



    # register blueprints
    app.register_blueprint(main)

    app.register_blueprint(meine_zeitstempel, url_prefix='/meine_zeitstempel')
    app.register_blueprint(meine_statistiken, url_prefix='/meine_statistiken')
    app.register_blueprint(meine_statistiken_ap5, url_prefix='/meine_statistiken')
    app.register_blueprint(meine_statistiken_ap6, url_prefix='/meine_statistiken')

    app.register_blueprint(personalmanagement, url_prefix='/personalmanagement')
    app.register_blueprint(mitarbeiter, url_prefix='/mitarbeiter')
    app.register_blueprint(fehltage, url_prefix='/fehltage')
    app.register_blueprint(statistiken, url_prefix='/statistiken')
    app.register_blueprint(statistiken_ap5, url_prefix='/statistiken')
    app.register_blueprint(statistiken_ap6, url_prefix='/fehltage')
    app.register_blueprint(zeitstempel, url_prefix='/zeitstempel')

