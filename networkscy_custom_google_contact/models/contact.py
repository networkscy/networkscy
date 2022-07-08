from odoo import models, fields, api
from . import connection
from . import constants
from . import people
import logging


class GoogleModResPartner(models.Model):
    _inherit = constants.RES_PARTNER_MODEL

    source = fields.Char(string="Source", readonly=True)
    gc_id = fields.Char(string="Google ID", copy=False, tracking=True)
    gc_etag = fields.Char(string="Google eTag", copy=False, tracking=True)

    _sql_constraints = [
        # ('state_id_fkey', 'CHECK(1=1)', "Bypass res.partner with res.country.state!")
        # Add Constraint for gc_id uniqueness, it require new database
        ('gc_id_unique', 'unique(gc_id)', 'gc_id already exists!')
    ]

    def get_db_token(self):
        credentials = self.env[constants.GOOGLE_MOD_CREDENTIALS_MODEL].get_google_credentials()
        if constants.RESPONSE_ERROR_KEY not in credentials and constants.RESPONSE_ERR_MESSAGE_KEY not in credentials:
            connect = connection.Connection(google_app_cred=credentials, default_env=self.env)
            conn_response = connect.get_msv_access_token()
            if not conn_response["err_status"]:
                return conn_response["response"]
        return None

    def write(self, values):
        _db_updated_record = super(GoogleModResPartner, self).write(values)

        # Real Time Sync
        # This commented code being used either create or update a contact from Odoo to Google Contact
        _logging = logging.getLogger(__name__)
        '''
        try:
            local_update_record = self.env[constants.RES_PARTNER_MODEL].search([
                '&', ('id', '=', self.id), '&', ('active_sync', '=', True), ('is_family', '=', False)
            ])
            if local_update_record and len(local_update_record) > 0:
                db_ref_token = self.get_db_token()
                if db_ref_token:
                    _people = people.People(gl_access_token=db_ref_token, default_env=self.env)
                    sr_resp = _people.create_contact(l2s_contact=local_update_record[0])
                    if sr_resp["err_status"]:
                        _logging.error("Create/Update Contact Error: " + sr_resp["response"])
                else:
                    _logging.error("Oops, Google credentials are not found. Please try again")
        except Exception as ex:
            _logging.exception("Oops, Google Contact updation exception found: " + str(ex))
        '''
        return _db_updated_record

    @api.model
    def unlink(self, values):
        override_unlink = super(GoogleModResPartner, self).unlink()

        _logging = logging.getLogger(__name__)
        for cid in values:
            '''
            This code is used when you want to able auto sync toggle option
            ref_contact = self.env[constants.RES_PARTNER_MODEL].search([
                '&', ('id', '=', cid), ('active_sync', '=', True)
            ])
            '''
            try:
                ref_contact = self.env[constants.RES_PARTNER_MODEL].search([('id', '=', cid)])
                if ref_contact and len(ref_contact) > 0 and ref_contact.gc_id:
                    db_ref_token = self.get_db_token()
                    if db_ref_token:
                        _people = people.People(gl_access_token=db_ref_token, default_env=self.env)
                        sr_resp = _people.delete_serv_contact_by_id(ref_contact[0].gc_id)
                        if sr_resp["err_status"]:
                            _logging.error("Delete Contact Error: " + str(sr_resp["response"]))

                self.env.cr.execute('delete from ' + constants.RES_PARTNER_STASH_MODEL + ' where id=' + str(cid))
            except Exception as ex:
                _logging.exception("Oops, unable to delete database contact: " + str(ex))

        return override_unlink

    @api.model
    def update_params(self, values):
        _logging = logging.getLogger(__name__)

        try:
            if len(values) > 0:
                upd_query = "update " + constants.RES_PARTNER_STASH_MODEL + " set"
                for _field in values:
                    if type(values[_field]) == bool:
                        upd_query += " " + _field + "=" + str(values[_field]) + ","
                    elif type(values[_field]) == list:
                        for _fid in values[_field]:
                            upd_query += " " + _field + "= (6, 0, " + str(_fid) + "),"
                    else:
                        if _field == 'gc_id':
                            chk_flag, chk_uniq_id = self.check_google_cred_value(res_partner_id=self.id, new_gc_id=values[_field])
                            if not chk_flag and not chk_uniq_id:
                                upd_query += " " + _field + "='" + str(values[_field]) + "',"
                        else:
                            upd_query += " " + _field + "='" + str(values[_field]) + "',"
                upd_query = upd_query[:-1] + " where id=" + str(self.id)
                self.env.cr.execute(upd_query)
                return True
            else:
                return False
        except:
            pass

    @api.model
    def update_categories_params(self, values):
        _logging = logging.getLogger(__name__)

        if len(values) > 0:
            del_query = "delete from  " + constants.RES_PARTNER_CATEGORY_REL_MODEL + " where partner_id=" + str(self.id)
            self.env.cr.execute(del_query)
            comb_query = ""
            for category_id in values:
                comb_query += "insert into " + constants.RES_PARTNER_CATEGORY_REL_MODEL + \
                              " (category_id, partner_id)" + " values (" + str(category_id) + ", " + str(self.id) + ");"
            if len(comb_query) > 0:
                self.env.cr.execute(comb_query)
            return True
        else:
            return False

    def force_update(self):
        _logging = logging.getLogger(__name__)

        try:
            local_update_record = self.env[constants.RES_PARTNER_MODEL].search([
                '&', ('id', '=', self.id), '&', ('active_sync', '=', True), ('is_family', '=', False)
            ])
            if local_update_record and len(local_update_record) > 0:
                db_ref_token = self.get_db_token()
                if db_ref_token:
                    _people = people.People(gl_access_token=db_ref_token, default_env=self.env)
                    sr_resp = _people.create_contact(l2s_contact=local_update_record[0])
                    if sr_resp["err_status"]:
                        _logging.error("Force Update  >>>  Create/Update Contact Error: " + sr_resp["response"])
                else:
                    _logging.error("Force Update  >>>  Google Credentials fetch error found")
        except Exception as ex:
            _logging.exception("Force Update  >>>  Exception found: " + str(ex))

    def check_google_cred_value(self, res_partner_id, new_gc_id):
        chk_partner_flag, chk_uniq_gc_id_flag = False, False
        try:
            chk_res_partner_gc_id_exist = self.env[constants.RES_PARTNER_MODEL].search([
                ('gc_id', '=', new_gc_id)
            ])
            if chk_res_partner_gc_id_exist and len(chk_res_partner_gc_id_exist) > 0:
                chk_uniq_gc_id_flag = True
                for _partner in chk_res_partner_gc_id_exist:
                    if _partner.id == res_partner_id:
                        chk_partner_flag = True
                        break
            else:
                chk_res_partner_exist = self.env[constants.RES_PARTNER_MODEL].search([
                    '&', ('id', '=', res_partner_id), ('gc_id', '!=', False)
                ])
                if chk_res_partner_exist and len(chk_res_partner_exist) > 0:
                    chk_partner_flag = True
        except:
            pass
        return chk_partner_flag, chk_uniq_gc_id_flag
