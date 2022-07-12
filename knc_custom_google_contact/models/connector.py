from odoo import models, fields, api
from . import connection
from . import constants
from datetime import *
from . import people
import logging


class GoogleModSync(models.Model):
    _name = constants.GOOGLE_MOD_CONNECTOR_MODEL
    _description = "Google Connector Settings"

    import_contact = fields.Boolean(default=False)
    export_contact = fields.Boolean(default=False)

    custom_from_datetime = fields.Datetime('From Date', default=lambda self: (fields.datetime.now() - timedelta(hours=1)))
    custom_to_datetime = fields.Datetime('To Date', default=lambda self: (fields.datetime.now() + timedelta(hours=1)))

    def synchronize(self):
        _logging = logging.getLogger(__name__)

        pop_up_message, date_error_chk = "", False
        imp_contact, exp_contact = 0, 0
        imp_upd_contact, exp_upd_contact = 0, 0
        imp_contact_ids, exp_contact_ids = [], []

        try:
            if self.custom_from_datetime > self.custom_to_datetime:
                date_error_chk = True

            if not date_error_chk:
                credentials = self.env[constants.GOOGLE_MOD_CREDENTIALS_MODEL].get_google_credentials()
                if constants.RESPONSE_ERROR_KEY not in credentials and \
                        constants.RESPONSE_ERR_MESSAGE_KEY not in credentials:
                    connect = connection.Connection(google_app_cred=credentials, default_env=self.env)
                    conn_response = connect.get_msv_access_token()
                    if not conn_response["err_status"]:
                        if self.import_contact or self.export_contact:
                            _people = people.People(
                                gl_access_token=conn_response["response"], default_env=self.env,
                                initial_date=self.custom_from_datetime, end_date=self.custom_to_datetime)

                            if self.import_contact:
                                contact_response = _people.import_contacts()
                                if not contact_response["err_status"]:
                                    imp_contact += contact_response["success"]
                                    imp_upd_contact += contact_response["updated"]
                                    imp_contact_ids = contact_response["contact_ids"]

                            if self.export_contact:
                                contact_response = _people.export_contacts()
                                if not contact_response["err_status"]:
                                    exp_contact += contact_response["success"]
                                    exp_upd_contact += contact_response["updated"]
                                    exp_contact_ids = contact_response["contact_ids"]

                        if self.import_contact or self.export_contact:
                            if imp_contact or imp_upd_contact:
                                self.env[constants.GOOGLE_MOD_IMPORT_STATS_MODEL].create({
                                    'connector': self.id,
                                    'new_contact': imp_contact,
                                    'update_contact': imp_upd_contact,
                                    'contact_ids': [[ 6, 0, imp_contact_ids ]]
                                })

                            if exp_contact or exp_upd_contact:
                                self.env[constants.GOOGLE_MOD_EXPORT_STATS_MODEL].create({
                                    'connector': self.id,
                                    'new_contact': exp_contact,
                                    'update_contact': exp_upd_contact,
                                    'contact_ids': [[ 6, 0, exp_contact_ids ]]
                                })

                            if pop_up_message == "":
                                pop_up_message += constants.SYNC_PROCESS_MSG
                        else:
                            pop_up_message = constants.NO_OPT_SECTION_ERR
                    else:
                        pop_up_message += conn_response["response"]
                else:
                    pop_up_message += credentials[constants.RESPONSE_ERR_MESSAGE_KEY]
                    _logging.info("Error while Sync: " + credentials[constants.RESPONSE_ERROR_KEY])
            else:
                pop_up_message += constants.INVALID_DATE_RANGES
        except Exception as ex:
            _logging.exception("Sync Exception: " + str(ex))
            pop_up_message += constants.SYNC_REQ_ERROR
        return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': "System Notification",
                    'message': pop_up_message,
                    'sticky': False,
                }
            }
