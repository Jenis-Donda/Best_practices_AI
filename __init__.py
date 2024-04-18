"""Module : __init__.py."""
# Licensed Materials - Property of IBM
# 5725I71-CC011829
# (C) Copyright IBM Corp. 2015, 2020. All Rights Reserved.
# US Government Users Restricted Rights - Use, duplication or
# disclosure restricted by GSA ADP Schedule Contract with IBM Corp.

__author__ = "IBM"

from flask import Flask
from qpylib import qpylib, log_qpylib, __version__
import secrets
from qpylib.encdec import Encryption, EncryptionError
from packaging import version
from flask_wtf.csrf import CSRFProtect
from . import path  # noqa F401


def suppress_syslog():
    """Suppress QPyLib logging to syslog."""
    return None


# Flask application factory.
def create_app():
    """Create Flask app.

    Returns
    -------
    Object
        Return flask application object.

    """
    # Create a Flask instance.
    qflask = Flask(__name__)

    # Retrieve QRadar app id.
    qradar_app_id = qpylib.get_app_id()

    # Initialize logging.
    if version.parse(__version__) >= version.parse("2.0.5"):
        qpylib.create_log(False)
    else:
        log_qpylib._get_address_for_syslog = suppress_syslog
        qpylib.create_log()

    # Create unique session cookie name for this app.
    qflask.config["SESSION_COOKIE_NAME"] = "session_{0}".format(qradar_app_id)
    # Set a secret key used by cryptographic components in the QRadar framework
    # for signing things like cookies
    secret_key = None
    try:
        # Read in secret key
        secret_key_store = Encryption({"name": "secret_key", "user": "flask_secret"})
        secret_key = secret_key_store.decrypt()
        qpylib.log("App started using a saved secret key.")
    except EncryptionError:
        # If secret key file doesn't exist/fail to decrypt it,
        # generate a new random password for it and encrypt it
        qpylib.log("Secret key not found, creating one...")
        secret_key_store = Encryption({"name": "secret_key", "user": "flask_secret"})
        secret_key = os.urandom(16)
        secret_key_store.encrypt(secret_key)

    qflask.secret_key = secret_key

    # Hide server details in endpoint responses.
    # pylint: disable=unused-variable
    @qflask.after_request
    def obscure_server_header(resp):
        resp.headers["Server"] = "QRadar App {0}".format(qradar_app_id)
        return resp


    # Register q_url_for function for use with Jinja2 templates.
    qflask.add_template_global(qpylib.q_url_for, "q_url_for")

    # To enable app health checking, the QRadar App Framework
    # requires every Flask app to define a /debug endpoint.
    # The endpoint function should contain a trivial implementation
    # that returns a simple confirmation response message.
    @qflask.route("/debug")
    def debug():
        return "Pong!"

    # Import additional endpoints.
    # For more information see:
    #   https://flask.palletsprojects.com/en/1.1.x/tutorial/views
    from . import views

    qflask.register_blueprint(views.viewsbp)

    return qflask
