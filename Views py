"""Flask Server for IntSights App."""
__author__ = "IBM"

# IMPORTS
import json
import os
import copy
import requests
from datetime import datetime, timedelta
from base64 import b64encode
from flask import request, render_template, Blueprint, jsonify
from qpylib.encdec import Encryption
import dashboard_utility as du
import logger_manager as lm
import common_utility as cu
import intsights_utility as iu
import conf_manager as cm
import response_handler
import constants as con
import uuid
import regex

# object of the get_set_start_time class.
set_get_start_end_time = du.GetSetTime()

APP_ROOT = cu.STORE_PATH
APP_CONFIG = cu.APP_CONFIG
common_header = cu.HEADERS
INP_CONFIG = cu.INP_CONFIG
ALERT_CONFIG = cu.ALERT_CONFIG
STORED_DATA = {}
INPUT_CONFIG_GENERAL_ERROR = "Error while rendering input page. Error = {0}"
alerts_assignee_constant = "Assignees"
alerts_tags_constant = "Alert Tags"
related_ioc_key = "Related IOCs"
asset_details_key = "Asset Details"
flagged_alert_key = "Flagged Alert"
filter_expression = "AND \"{0}\" = '{1}'"
filter_expression_without_match = "AND \"{0}\" != '{1}'"

# Initializing objects
viewsbp = Blueprint("viewsbp", __name__, url_prefix="/")
logger = cu.app_logger

live_qpylib = lm.Singleton.get_qpylib_instance()
logger.info("App started.")




@viewsbp.route("/get_input_config", methods=["POST"])
def get_input_config():
    """Endpoint called when to get input configurations."""
    is_error = False
    try:
        stored_data = {}
        if not os.path.isfile(INP_CONFIG):
            cm.ConfManager(INP_CONFIG)
        if not os.path.isfile(ALERT_CONFIG):
            cm.ConfManager(ALERT_CONFIG)

        stored_input_data = cu.get_data_from_file(INP_CONFIG)
        stored_alert_data = cu.get_data_from_file(ALERT_CONFIG)

        stored_data["ioc"] = stored_input_data
        stored_data["alert"] = stored_alert_data

        return jsonify(stored_data)
    except KeyError as e:
        logger.error(
            "Key not found while rendering input page. Key = {0}".format(
                str(e)
            )
        )
        is_error = True
    except Exception as e:
        logger.error(
            INPUT_CONFIG_GENERAL_ERROR.format(str(e))
        )
        is_error = True
    if is_error:
        return jsonify({"error": con.FLASK_GENERAL_ERROR})
    return jsonify(stored_data)
