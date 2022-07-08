from ..models.connection import Connection
from urllib.parse import unquote
from ..models.constants import *
from odoo.http import request
from odoo import http
import werkzeug
import logging


class TeamsIntegration(http.Controller):
    @http.route(GOOGLE_MOD_CREDENTIALS_RDT_URI, auth='public')
    def index(self, **kw):
        _log = logging.getLogger(__name__)

        def_model = request.env[GOOGLE_MOD_CREDENTIALS_MODEL]
        last_conseq_record = def_model.search([])[DEFAULT_INDEX]
        try:
            if GOOGLE_MOD_CODE_VAL_URI in str(http.request.httprequest.full_path):
                grant_code = str(http.request.httprequest.full_path).split(GOOGLE_MOD_CODE_VAL_URI)[1]
                if GOOGLE_MOD_SPLITTER_URI in grant_code:
                    grant_code = grant_code.split(GOOGLE_MOD_SPLITTER_URI)[0]
                grant_code = unquote(grant_code)

                google_cloud_params = {
                    'redirect_url': last_conseq_record.redirect_url,
                    'client_id': last_conseq_record.client_id,
                    'client_secret': last_conseq_record.client_secret
                }
                conn = Connection(google_app_cred=google_cloud_params)
                _response = conn.generate_access_token(grant_code=grant_code)
                if not _response["err_status"]:
                    last_conseq_record.grant_code = grant_code
                    last_conseq_record.access_token = conn.get_access_token()
                    last_conseq_record.refresh_token = conn.get_refresh_token()
                    def_model.update(last_conseq_record)
                    # Create cronjob in schedule actions
                    request.env[GOOGLE_MOD_CRON_MODEL].save_config_mod()

                    return werkzeug.utils.redirect(GOOGLE_MOD_CREDENTIALS_RDT_ODOO_URI)
                else:
                    return "Connection failed: " + str(_response["response"])
            else:
                return GRANT_CODE_ERR
        except Exception as ex:
            return "Internal Exception found: "+str(ex)
