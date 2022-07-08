from odoo import api, models, fields
from . import connection
from . import constants
from . import people
import logging


class GoogleModCronOperation(models.Model):
    _name = constants.GOOGLE_MOD_CRON_MODEL
    _description = "Google Connector Cron Settings"

    is_auto_import = fields.Boolean(default=lambda self: self.get_auto_import_status())
    import_interval_num = fields.Integer(default=lambda self: self.get_import_interval_num())
    import_call_num = fields.Selection([('1', 'One Time'), ('-1', 'Unlimited Time')],
                                       default=lambda self: self.get_import_call_num())
    import_interval_type = fields.Selection([('minutes', 'Minutes'), ('hours', 'Hours'), ('days', 'Days')],
                                            default=lambda self: self.get_import_interval_type())

    is_auto_export = fields.Boolean(default=lambda self: self.get_auto_export_status())
    export_interval_num = fields.Integer(default=lambda self: self.get_export_interval_num())
    export_call_num = fields.Selection([('1', 'One Time'), ('-1', 'Unlimited Time')],
                                       default=lambda self: self.get_export_call_num())
    export_interval_type = fields.Selection([('minutes', 'Minutes'), ('hours', 'Hours'), ('days', 'Days')],
                                            default=lambda self: self.get_export_interval_type())

    def write(self, values):
        return super(GoogleModCronOperation, self).write(values)

    def export_mod_contacts(self):
        _log = logging.getLogger(__name__)

        pop_message = ""
        _log.exception(">>>>>>>>>>>>>>> Google Contacts Export CronJob is being started")
        credentials = self.env[constants.GOOGLE_MOD_CREDENTIALS_MODEL].get_google_credentials()
        if constants.RESPONSE_ERROR_KEY not in credentials and constants.RESPONSE_ERR_MESSAGE_KEY not in credentials:
            connect = connection.Connection(google_app_cred=credentials, default_env=self.env)
            conn_response = connect.get_msv_access_token()
            if not conn_response["err_status"]:
                _people = people.People(gl_access_token=conn_response["response"], default_env=self.env)
                _log.exception(">>>>>>>>>>>>>>> Start calling export helping method of People Object")
                _gc_response = _people.export_contacts()
                if not _gc_response["err_status"]:
                    _log.exception(">>>>>>>>>>>>>>> Adding logs information after successful execution")
                    self.env[constants.GOOGLE_MOD_EXPORT_STATS_MODEL].create({
                        'new_contact': _gc_response["success"],
                        'update_contact': _gc_response["updated"],
                        'contact_ids': [[ 6, 0, _gc_response["contact_ids"] ]]
                    })
                    pop_message += "Contacts exported successfully: " + str(_gc_response["success"])
                else:
                    pop_message += str(_gc_response["response"])
            else:
                pop_message += str(conn_response["response"])
        else:
            pop_message += credentials[constants.RESPONSE_ERR_MESSAGE_KEY]
        _log.exception(">>>>>>>>>>>>>>> Closing Google Contacts Export CronJob with this: " + pop_message)
        return pop_message

    def import_mod_contacts(self):
        _log = logging.getLogger(__name__)

        pop_message = ""
        _log.exception(">>>>>>>>>>>>>>> Google Contacts Import CronJob is being started")
        credentials = self.env[constants.GOOGLE_MOD_CREDENTIALS_MODEL].get_google_credentials()
        if constants.RESPONSE_ERROR_KEY not in credentials and constants.RESPONSE_ERR_MESSAGE_KEY not in credentials:
            connect = connection.Connection(google_app_cred=credentials, default_env=self.env)
            conn_response = connect.get_msv_access_token()
            if not conn_response["err_status"]:
                _people = people.People(gl_access_token=conn_response["response"], default_env=self.env)
                _log.exception(">>>>>>>>>>>>>>> Start calling import helping method of People Object")
                _gc_response = _people.import_contacts()
                if not _gc_response["err_status"]:
                    _log.exception(">>>>>>>>>>>>>>> Adding logs information after successful execution")
                    self.env[constants.GOOGLE_MOD_IMPORT_STATS_MODEL].create({
                        'new_contact': _gc_response["success"],
                        'update_contact': _gc_response["updated"],
                        'contact_ids': [[ 6, 0, _gc_response["contact_ids"] ]]
                    })
                    pop_message += "Contacts imported successfully: " + str(_gc_response["success"])
                else:
                    pop_message += str(_gc_response["response"])
            else:
                pop_message += str(conn_response["response"])
        else:
            pop_message += credentials[constants.RESPONSE_ERR_MESSAGE_KEY]
        _log.exception(">>>>>>>>>>>>>>> Closing Google Contacts Import CronJob with this: " + pop_message)
        return pop_message

    def update_import_cron(self, data):
        _logging = logging.getLogger(__name__)

        delete_query = "delete from " + constants.IR_CRON_SLASH_MODEL + " where cron_name='" + \
                       constants.GC_IMPORT_DEF_NAME + "';"
        self.env.cr.execute(delete_query)

        chk_exist_cron = self.env[constants.IR_CRON_MODEL].search([('name', '=', constants.GC_IMPORT_DEF_NAME)])
        if chk_exist_cron  and len(chk_exist_cron) > 0:
            chk_exist_cron[0].write({
                'numbercall': data["import_call_num"],
                'active': data["is_auto_import"],
                'interval_number': data["import_interval_num"],
                'interval_type': data["import_interval_type"],
            })
        else:
            self.env[constants.IR_CRON_MODEL].create({
                'name': constants.GC_IMPORT_DEF_NAME,
                'model_id': self.env[constants.IR_MODEL_MODEL].search([
                    ("model", "=", constants.GOOGLE_MOD_CRON_MODEL)])[0].id,
                'code': 'model.import_mod_contacts()',
                'numbercall': '-1',  # data["import_call_num"],
                'active': False,  # data["is_auto_import"],
                'interval_number': 1,  # data["import_interval_num"],
                'interval_type': 'minutes',  # data["import_interval_type"],
                'priority': 2,
                'doall': 1 # This flag value is being for restart cron job if it's failed
            })

    def update_export_cron(self, data):
        _logging = logging.getLogger(__name__)

        delete_query = "delete from " + constants.IR_CRON_SLASH_MODEL + " where cron_name='" + \
                       constants.GC_EXPORT_DEF_NAME + "';"
        self.env.cr.execute(delete_query)

        chk_exist_cron = self.env[constants.IR_CRON_MODEL].search([('name', '=', constants.GC_EXPORT_DEF_NAME)])
        if chk_exist_cron  and len(chk_exist_cron) > 0:
            chk_exist_cron[0].write({
                'numbercall': data["export_call_num"],
                'active': data["is_auto_export"],
                'interval_number': data["export_interval_num"],
                'interval_type': data["export_interval_type"]
            })
        else:
            self.env[constants.IR_CRON_MODEL].create({
                'name': constants.GC_EXPORT_DEF_NAME,
                'model_id': self.env[constants.IR_MODEL_MODEL].search([
                    ("model", "=", constants.GOOGLE_MOD_CRON_MODEL)])[0].id,
                'code': 'model.export_mod_contacts()',
                'numbercall': '-1', # data["export_call_num"],
                'active': False, # data["is_auto_export"],
                'interval_number': 1, # data["export_interval_num"],
                'interval_type': 'minutes', # data["export_interval_type"],
                'priority': 1
            })

    def save_config_mod(self):
        _logging = logging.getLogger(__name__)

        rep_message = ''
        data_db_struct = {
            'is_auto_import': self.is_auto_import, 'import_interval_num': self.import_interval_num,
            'import_call_num': self.import_call_num, 'import_interval_type': self.import_interval_type,
            'is_auto_export': self.is_auto_export, 'export_interval_num': self.export_interval_num,
            'export_call_num': self.export_call_num, 'export_interval_type': self.export_interval_type
        }
        try:
            db_rows = self.env[self._name].search([])
            if db_rows and len(db_rows) > 0:
                _logging.info("Update Cron Job record")
                if db_rows[0]:
                    db_rows[0].write(data_db_struct)
                rep_message += constants.GC_CRON_CONFIG_UPDATE
            else:
                _logging.info("Create Cron Job record")
                super().create(data_db_struct)
                rep_message += constants.GC_CRON_CONFIG_SAVE
            self.update_import_cron(data=data_db_struct)
            self.update_export_cron(data=data_db_struct)
        except Exception as ex:
            _logging.exception("Google Drive Cron Config Exception: " + str(ex))
            rep_message += constants.GC_CRON_CONFIG_EXCEPT
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': constants.FAILURE_POP_UP_TITLE,
                'message': rep_message,
                'sticky': False,
            }
        }

    @api.model
    def get_auto_import_status(self):
        db_rows = self.env[self._name].search([('is_auto_import', "=", True)])
        return db_rows[constants.DEFAULT_INDEX].is_auto_import if len(db_rows) > 0 else False

    @api.model
    def get_auto_export_status(self):
        db_rows = self.env[self._name].search([('is_auto_export', "=", True)])
        return db_rows[constants.DEFAULT_INDEX].is_auto_export if len(db_rows) > 0 else False

    @api.model
    def get_import_interval_num(self):
        db_rows = self.env[self._name].search([])
        return int(db_rows[constants.DEFAULT_INDEX].import_interval_num) \
            if len(db_rows) > 0 and db_rows[constants.DEFAULT_INDEX].import_interval_num else 1

    @api.model
    def get_export_interval_num(self):
        db_rows = self.env[self._name].search([])
        return int(db_rows[constants.DEFAULT_INDEX].export_interval_num) \
            if len(db_rows) > 0 and db_rows[constants.DEFAULT_INDEX].export_interval_num else 1

    @api.model
    def get_import_call_num(self):
        db_rows = self.env[self._name].search([])
        return db_rows[constants.DEFAULT_INDEX].import_call_num \
            if len(db_rows) > 0 and db_rows[constants.DEFAULT_INDEX].import_call_num else '1'

    @api.model
    def get_export_call_num(self):
        db_rows = self.env[self._name].search([])
        return db_rows[constants.DEFAULT_INDEX].export_call_num \
            if len(db_rows) > 0 and db_rows[constants.DEFAULT_INDEX].export_call_num else '1'

    @api.model
    def get_import_interval_type(self):
        db_rows = self.env[self._name].search([])
        return db_rows[constants.DEFAULT_INDEX].import_interval_type \
            if len(db_rows) > 0 and db_rows[constants.DEFAULT_INDEX].import_interval_type else 'minutes'

    @api.model
    def get_export_interval_type(self):
        db_rows = self.env[self._name].search([])
        return db_rows[constants.DEFAULT_INDEX].export_interval_type \
            if len(db_rows) > 0 and db_rows[constants.DEFAULT_INDEX].export_interval_type else 'minutes'
