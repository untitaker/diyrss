import flask
from . import utils, errors
import uuid


def mk_app(config):
    app = flask.Flask('diyrss')
    app.config.update({
        'ASSETS_AUTO_BUILD': False,
        'ASSETS_DEBUG': False
    })
    app.config.update(config)
    utils.cache.init_app(app)

    @app.route('/')
    def index():
        return flask.render_template('index.htm')

    @app.route('/feed', methods=['GET'])
    def get_feed():
        kwargs = dict((k, flask.request.args[k]) for k in
                      ('url', 'main_selector', 'title_selector', 'content_selector'))

        if not all(kwargs.values()):
                return error('You didn\'t fill out all fields'), 400

        flask.g.feed_info = kwargs
        return utils.get_feed(**kwargs)

    @app.errorhandler(errors.SelectorError)
    def css_selector_error(e):
        return error('Invalid CSS Selector'), 400

    @app.errorhandler(errors.URLParseError)
    def url_error(e):
        return error('Invalid URL'), 400

    @app.errorhandler(500)
    def generic_error(e):
        return error('Unknown error'), 500

    @app.errorhandler(errors.RemoteError)
    def bad_gateway(e):
        return error('The remote server couldn\'t be reached'), 502

    @app.errorhandler(errors.BrokenItemError)
    def brokenitem(e):
        return error(e.msg, e.item), 502

    @app.errorhandler(errors.LxmlError)
    def lxmlerror(e):
        return error('Error while parsing the HTML/XML'), 502

    def error(msg, code=None):
        return flask.render_template('error.htm', msg=msg, code=code)

    return app
