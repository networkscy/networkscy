from . import constants
import requests
import logging


class Profile:
    def __init__(self, gl_access_token):
        self.__logging = logging.getLogger(__name__)
        self.__req_version = constants.GC_CONTACT_PROFILE_VERSION
        self.__req_timeout = constants.GC_REQ_TIMEOUT
        self.__base_endpoint = constants.GC_BASE_URL

        self.__default_service = constants.GC_CONTACT_PROFILE_SERVICE
        self.__profile_me = constants.GC_CONTACT_PROFILE_LINK
        self.__gl_access_token = gl_access_token
        self.__req_headers = {"Authorization": "Bearer " + self.__gl_access_token}

        self.__js_resp = {
            "err_status": True,
            "response": "",
            "addons": None
        }

    def reset_response(self):
        self.__js_resp["err_status"] = True
        self.__js_resp["response"] = ""
        self.__js_resp["addons"] = None

    def get_profile(self):
        self.reset_response()
        try:
            req_url = self.__base_endpoint.replace('{{service}}', self.__default_service) + \
                      self.__req_version + self.__profile_me
            req_params = {
                constants.GC_CONTACT_PROFILE_REQ_FLD_NAME: constants.GC_CONTACT_PROFILE_REQ_FLDS_SEP.join(
                    constants.GC_CONTACT_SEARCH_FLDS)
            }
            sr_resp = requests.get(req_url, params=req_params, headers=self.__req_headers).json()
            if constants.RESPONSE_ERROR_KEY not in sr_resp:
                self.__js_resp["response"] = sr_resp
                self.__js_resp["err_status"] = False
            else:
                self.__js_resp["response"] = sr_resp[constants.RESPONSE_ERROR_KEY]
        except Exception as ex:
            self.__logging.exception("Google Contact Profile Exception: " + str(ex))
            self.__js_resp["response"] = constants.GC_PROFILE_EXCEPT
        return self.__js_resp
