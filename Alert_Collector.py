"""Data collection file which collect Alerts of different types using multi-threading."""
import os
import time
import uuid
from datetime import datetime
import common_utility as cu
import threading_utility as tu
import threading
import intsights_utility as iu
import logger_manager as lm
import constants
import conf_manager as cm


# containing list of all threads
thread_registry = tu.ThreadSafeDict()
thread_lock = threading.Lock()


class AlertsCollector(object):
    """The purpose of AlertsCollector is to fetch the alerts from Intsights, and ingest them into QRadar."""

    def __init__(self, alert_type, input_configurations, sync_id, int_util_client, leef_logger=None, logger=None):
        """Initialize class variables."""
        self.alert_type = alert_type
        self.input_configurations = input_configurations
        self.sync_id = sync_id
        self.int_util_client = int_util_client
        self.logger = logger
        self.leef_logger = leef_logger

    def configure_params(self, last_update_to):
        """Configure params for IntSights Alert data fetch API call according to input configurations.

        Parameters
        ----------
        last_update_to : str
            LastUpdateTo date.
        """
        global thread_lock
        checkpoint = cu.get_checkpoint_time(self.alert_type, self.logger)
        start_time = cu.report_date_to_start_time(self.input_configurations["reportDate"])
        is_report_date_changed = self.input_configurations["isReportDateChanged"]
        if is_report_date_changed:
            checkpoint = {}
            self.logger.info(
                "Report date is changed. Attempting to delete checkpoint file and collecting data from Report date."
            )
            cu.delete_checkpoint_file(self.alert_type, self.logger)

            with thread_lock:
                existing_configurations = cu.get_intsights_input_configuration(cu.ALERT_CONFIG, self.logger)
                if existing_configurations:
                    self.input_configurations["isReportDateChanged"] = False
                    existing_configurations[self.alert_type].update(self.input_configurations)

                    conf_m = cm.ConfManager(cu.ALERT_CONFIG)
                    conf_m.add_config({"alertInputConfig": existing_configurations})

        if checkpoint.get("checkpoint"):
            start_time = checkpoint["checkpoint"]
        payload = {
            "alertType[]": self.alert_type,
            "syncId": self.sync_id,
            "lastUpdatedFrom": start_time,
            "lastUpdatedTo": last_update_to,
            "limit": constants.MAX_ALERTS_TO_FETCH,
        }

        if checkpoint.get("offset"):
            payload.update({"offset": checkpoint["offset"]})

        severity_list = self.input_configurations["severity"]

        if "All" in severity_list:
            severity_list = ["High", "Medium", "Low"]
        payload.update({"severity[]": severity_list})

        if str(self.input_configurations["alertStatus"]).lower().strip() == "closed":
            payload.update({"isClosed": "true"})
            self.input_configurations["alertStatus"] = "Closed"
        else:
            payload.update({"isClosed": "false"})
            self.input_configurations["alertStatus"] = "Open"
        with thread_lock:
            conf_m = cm.ConfManager(cu.ALERT_CONFIG)
            existing_configurations = cu.get_intsights_input_configuration(cu.ALERT_CONFIG, self.logger)
            if existing_configurations:
                existing_configurations[self.alert_type].update(self.input_configurations)

            conf_m.add_config({"alertInputConfig": existing_configurations})
        self.api_params = payload
