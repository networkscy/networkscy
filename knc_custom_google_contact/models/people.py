from . import connection
from . import constants
from datetime import *
import requests
import logging
import base64
import pytz
import time
import json
import re


class People:
    def __init__(self, gl_access_token, default_env, initial_date=None, end_date=None):
        self.__logging = logging.getLogger(__name__)

        self.__gl_access_token = gl_access_token
        self.__default_env = default_env
        self.__initial_date = initial_date
        self.__end_date = end_date

        self.__req_version = constants.GC_CONTACT_PROFILE_VERSION
        self.__req_timeout = constants.GC_REQ_TIMEOUT
        self.__default_service = constants.GC_CONTACT_PROFILE_SERVICE
        self.__base_endpoint = constants.GC_BASE_URL.replace(constants.GC_SERVICE_REPLACER, self.__default_service)

        self.__create_contact_api = constants.GC_CONTACT_CREATE_LINK
        self.__search_contact_api = constants.GC_CONTACT_SEARCH_LINK
        self.__update_contact_api = constants.GC_CONTACT_UPDATE_LINK
        self.__update_contact_photo_api = constants.GC_CONTACT_UPDATE_PHOTO_LINK
        self.__delete_contact_photo_api = constants.GC_CONTACT_DELETE_PHOTO_LINK
        self.__get_contact_api = constants.GC_CONTACT_PROFILE_LINK
        self.__get_contact_by_id_api = constants.GC_CONTACT_GET_LINK
        self.__get_contact_list_api = constants.GC_CONTACT_LIST_LINK
        self.__delete_contact_api = constants.GC_CONTACT_DELETE_LINK

        self.__contact_group_lc_api = constants.GC_CONTACT_GROUP_CL_LINK
        self.__get_contact_group_api = constants.GC_CONTACT_GROUP_GET_LINK

        self.__clean_tags_re = re.compile('<.*?>')
        self.__buffer_categories = {"call": False, "data": []}
        self.__google_api_credentials = {}
        self.__req_headers = {
            'Authorization': 'Bearer ' + self.__gl_access_token,
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        self.__js_resp = {
            "err_status": True,
            "response": None,
            "total": 0,
            "success": 0,
            "failed": 0,
            "updated": 0,
            "contact_ids": []
        }

    def reset_response(self):
        self.__js_resp["err_status"] = True
        self.__js_resp["response"] = None
        self.__js_resp["total"] = 0
        self.__js_resp["success"] = 0
        self.__js_resp["failed"] = 0
        self.__js_resp["updated"] = 0
        self.__js_resp["contact_ids"] = []

    ##############################################################################################################
    # ########################       Google API Credential LifeCycle Adjustment       ############################
    ##############################################################################################################

    def check_execution_timer(self, starter_dt):
        try:
            self.__logging.info(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> CT: Checking Execution Timer for Google Credentials")
            execution_dt = datetime.now()
            diff_dt = int((execution_dt - starter_dt).total_seconds() // 60)
            if diff_dt >= constants.CHECK_TIMER_MINUTES:
                self.check_auth_token()
                starter_dt = execution_dt
        except Exception as ex:
            self.__logging.exception("Check Execution Timer Exception: " + str(ex))
        return starter_dt

    def check_auth_token(self):
        self.__logging.info(
            ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> GCLC: Start Process for checking and verifying Google Credentials")
        if len(self.__google_api_credentials) == 0:
            self.__google_api_credentials = self.__default_env[constants.GOOGLE_MOD_CREDENTIALS_MODEL].get_google_credentials()

        if constants.RESPONSE_ERROR_KEY not in self.__google_api_credentials and \
                constants.RESPONSE_ERR_MESSAGE_KEY not in self.__google_api_credentials:
            self.__logging.info(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> GCLC: Start checking and verifying the google credentials")
            _connection_object = connection.Connection(google_app_cred=self.__google_api_credentials, default_env=self.__default_env)
            ak_resp = _connection_object.get_quick_msv_access_token()
            if not ak_resp["err_status"]:
                self.__logging.info(">>>>>>>>>>>>>>>>>>>>>>>>>>>>> GCLC: Getting verifying google credentials")
                new_wrk_token = ak_resp["response"]
                if new_wrk_token:
                    self.__logging.info(">>>>>>>>>>>>>>>>>>>>>>>>>>>>> GCLC: Replacing the with verified google credentials in headers")
                    self.__req_headers['Authorization'] = 'Bearer ' + new_wrk_token
                else:
                    self.__logging.info(">>>>>>>>>>>>>>>>>>>>>>>>>>>>> GCLC: Unable to find the verified google credentials")
            else:
                self.__logging.info(">>>>>>>>>>>>>>>>>>>>>>>>>>>>> GCLC: Unable to getting verifying google credentials")
        else:
            self.__logging.info(">>>>>>>>>>>>>>>>>>>>>>>>>>>>> GCLC: Unable to getting google default credentials")

    ##############################################################################################################
    # #############################      People Memberships Labels Operations     ################################
    ##############################################################################################################

    def get_serv_category_by_id(self, label_resource):
        gt_resp = {"err_status": True, "response": None}
        try:
            req_url = self.__base_endpoint + self.__req_version + '/' + label_resource
            sr_resp = requests.get(req_url, headers=self.__req_headers, timeout=self.__req_timeout).json()
            if constants.RESPONSE_ERROR_KEY not in sr_resp and len(sr_resp) > 0:
                gt_resp["err_status"] = False
            gt_resp["response"] = sr_resp
        except Exception as ex:
            self.__logging.exception("Get Server Label Exception: " + str(ex))
            gt_resp["response"] = constants.GC_CONTACTS_MEMBERSHIPS_GET_EXCEPT
        return gt_resp

    def chk_serv_category(self, s2l_category=None, l2s_category=None, custom_fields=None):
        chk_resp = {"err_status": True, "response": None}
        try:
            if s2l_category:
                pass
            elif l2s_category or custom_fields:
                if not self.__buffer_categories["call"]:
                    self.__buffer_categories["call"] = True
                    gt_resp = self.get_membership_resource_list()
                    if not gt_resp["err_status"]:
                        self.__buffer_categories["data"] = gt_resp["response"]
                if l2s_category:
                    for sr_category in self.__buffer_categories["data"]:
                        if sr_category["formattedName"] == l2s_category.name:
                            chk_resp["response"] = sr_category
                            chk_resp["err_status"] = False
                            break
                elif custom_fields:
                    for sr_category in self.__buffer_categories["data"]:
                        if sr_category["formattedName"] == custom_fields["name"]:
                            chk_resp["response"] = sr_category
                            chk_resp["err_status"] = False
                            break
            else:
                chk_resp["response"] = constants.GC_CONTACTS_MEMBERSHIPS_CHK_ERR
        except Exception as ex:
            self.__logging.exception("Check Server Contact Label Exception: " + str(ex))
            chk_resp["response"] = constants.GC_CONTACTS_MEMBERSHIPS_CHK_EXCEPT
        return chk_resp

    # def create_membership_resource(self, s2l_category=None, l2s_category=None, custom_fields=None):
        # crt_resp = {"err_status": True, "response": None}
        # try:
            # if s2l_category:
                # gt_serv_resp = self.get_serv_category_by_id(
                    # label_resource=s2l_category["contactGroupMembership"]["contactGroupResourceName"])
                # if not gt_serv_resp["err_status"]:
                    # s2l_category = gt_serv_resp["response"]
                    # chk_exist_category = self.__default_env[constants.RES_PARTNER_CATEGORY_MODEL].search([
                        # ('name', '=', s2l_category['formattedName'])
                    # ])
                    # if chk_exist_category and len(chk_exist_category) > 0:
                        # chk_exist_category[0].write({
                            # 'gc_name': s2l_category['name'],
                            # 'gc_res_id': s2l_category["resourceName"].split('/')[1]
                        # })
                        # crt_resp["response"] = chk_exist_category[0]
                    # else:
                        # crt_resp["response"] = self.__default_env[constants.RES_PARTNER_CATEGORY_MODEL].create({
                            # 'name': s2l_category['formattedName'],
                            # 'gc_name': s2l_category['name'],
                            # 'gc_res_id': s2l_category["resourceName"].split('/')[1]
                        # })
                    # crt_resp["err_status"] = False
            # elif l2s_category or custom_fields:
                # if l2s_category:
                    # srv_params = {
                        # "contactGroup": {
                            # "name": l2s_category.name
                        # }
                    # }
                # else:
                    # srv_params = {
                        # "contactGroup": {
                            # "name": custom_fields['name']
                        # }
                    # }
                # req_url = self.__base_endpoint + self.__req_version + self.__contact_group_lc_api
                # sr_resp = requests.post(req_url, data=json.dumps(srv_params), headers=self.__req_headers,
                                        # timeout=self.__req_timeout).json()
                # if constants.RESPONSE_ERROR_KEY not in sr_resp:
                    # crt_resp["response"] = sr_resp
                    # crt_resp["err_status"] = False
                # else:
                    # crt_resp["response"] = constants.GC_CONTACTS_MEMBERSHIPS_CRT_ERR
            # else:
                # crt_resp["response"] = constants.GC_CONTACTS_MEMBERSHIPS_CRT_ERR
        # except Exception as ex:
            # self.__logging.exception("Create either Contact Category or Membership  Exception: " + str(ex))
            # crt_resp["response"] = constants.GC_CONTACTS_MEMBERSHIPS_CRT_EXCEPT
        # return crt_resp

    def get_membership_resource_list(self):
        gt_mbr_resp = {"err_status": True, "response": None}
        try:
            tmp_membership_resource_list, next_page_token = [], None
            while True:
                req_url = self.__base_endpoint + self.__req_version + self.__contact_group_lc_api
                if next_page_token:
                    req_url += '?pageToken=' + next_page_token
                sr_resp = requests.get(req_url, headers=self.__req_headers, timeout=self.__req_timeout).json()
                if constants.RESPONSE_ERROR_KEY not in sr_resp:
                    tmp_membership_resource_list += sr_resp[constants.GC_CONTACT_GROUP_KEY]
                    if 'nextPageToken' in sr_resp:
                        next_page_token = sr_resp['nextPageToken']
                    else:
                        break
                else:
                    break

            if len(tmp_membership_resource_list) > 0:
                gt_mbr_resp["response"] = tmp_membership_resource_list
                gt_mbr_resp["err_status"] = False
            else:
                gt_mbr_resp["response"] = constants.GC_CONTACTS_MEMBERSHIPS_GET_ERR
        except Exception as ex:
            self.__logging.exception("Get Contact Membership Resource Lists: " + str(ex))
            gt_mbr_resp["response"] = constants.GC_CONTACTS_MEMBERSHIPS_GET_EXCEPT
        return gt_mbr_resp

    ##############################################################################################################
    # ########################################      People Operations     ########################################
    ##############################################################################################################

    def delete_serv_contact_by_id(self, people_id):
        del_resp = {"err_status": True, "response": None}
        try:
            req_url = self.__base_endpoint + self.__req_version + self.__delete_contact_api.replace(
                '{{people_id}}', people_id)
            sr_resp = requests.delete(req_url, headers=self.__req_headers, timeout=self.__req_timeout).json()
            if constants.RESPONSE_ERROR_KEY not in sr_resp:
                del_resp["err_status"] = False
            del_resp["response"] = sr_resp
        except Exception as ex:
            self.__logging.exception("Delete Contact Exception: " + str(ex))
            del_resp["response"] = constants.GC_CONTACTS_GET_EXCEPT
        return del_resp

    def delete_profile_image_by_contact(self, addon_id):
        del_resp = {"err_status": True, "response": None}
        try:
            req_url = self.__base_endpoint + self.__req_version + \
                      self.__delete_contact_photo_api.replace("{{people_id}}", addon_id)
            sr_resp = requests.delete(req_url, headers=self.__req_headers, timeout=self.__req_timeout).json()
            if constants.RESPONSE_ERROR_KEY not in sr_resp:
                del_resp["err_status"] = False
            del_resp["response"] = str(sr_resp)
        except Exception as ex:
            self.__logging.exception("Delete Contact Image Exception: " + str(ex))
            del_resp["response"] = constants.GC_CONTACTS_UPD_EXCEPT
        return del_resp

    def update_profile_image_by_contact(self, l2s_contact, addon_id=None):
        upd_resp = {"err_status": True, "response": None}
        try:
            req_url = self.__base_endpoint + self.__req_version + \
                      self.__update_contact_photo_api.replace("{{people_id}}", addon_id)
            payload = {"photoBytes": l2s_contact.image_1920.decode()}
            sr_resp = requests.patch(req_url, data=json.dumps(payload), headers=self.__req_headers,
                                     timeout=self.__req_timeout).json()
            if constants.RESPONSE_ERROR_KEY not in sr_resp:
                upd_resp["err_status"] = False
            upd_resp["response"] = str(sr_resp)
        except Exception as ex:
            self.__logging.exception("Update Contact Image Exception: " + str(ex))
            upd_resp["response"] = constants.GC_CONTACTS_UPD_EXCEPT
        return upd_resp

    def get_contact_detail_by_id(self, people_id):
        gt_resp = {"err_status": True, "response": None}
        try:
            if people_id and type(people_id) != bool:
                req_url = self.__base_endpoint + self.__req_version + self.__get_contact_by_id_api.replace(
                    '{{people_id}}', people_id) + '?personFields=names'
                sr_resp = requests.get(req_url, headers=self.__req_headers, timeout=self.__req_timeout).json()
                if constants.RESPONSE_ERROR_KEY not in sr_resp:
                    gt_resp["err_status"] = False
                gt_resp["response"] = sr_resp
            else:
                gt_resp["response"] = constants.GC_CONTACTS_GET_ERR
        except Exception as ex:
            self.__logging.exception("Get Contact Detail Exception: " + str(ex))
            gt_resp["response"] = constants.GC_CONTACTS_GET_EXCEPT
        return gt_resp

    def get_default_membership(self):
        gt_resp = {"err_status": True, "response": None}
        try:
            custom_wid = None
            custom_fields = {'name': '# Odoo (v15) (Shared)'}

            chk_def_label = self.chk_serv_category(custom_fields=custom_fields)
            if not chk_def_label["err_status"]:
                custom_wid = chk_def_label["response"]["resourceName"].split('/')[1]
            else:
                crt_custom_fields_resp = self.create_membership_resource(custom_fields=custom_fields)
                if not crt_custom_fields_resp["err_status"]:
                    custom_wid = crt_custom_fields_resp["response"]["resourceName"].split('/')[1]

            if custom_wid:
                gt_resp["response"] = {
                    "contactGroupMembership": {
                        "contactGroupResourceName": constants.GC_CONTACT_GROUP_KEY + '/' + custom_wid
                    }
                }
                gt_resp["err_status"] = False
        except Exception as ex:
            self.__logging.exception("Get Default Membership Exception: " + str(ex))
        return gt_resp

    # def create_membership_lists(self, s2l_contact=None, l2s_contact=None):
        # crt_ms_resp = {"err_status": True, "response": None}
        # try:
            # if s2l_contact:
                # tmp_local_categories = []
                # if len(s2l_contact["memberships"]) > 0:
                    # for sr_membership in s2l_contact["memberships"]:
                        # chk_lc_resp = self.create_membership_resource(s2l_category=sr_membership)
                        # if not chk_lc_resp["err_status"]:
                            # tmp_local_categories.append(chk_lc_resp["response"].id)
                # crt_ms_resp["response"] = tmp_local_categories
                # crt_ms_resp["err_status"] = False
            # elif l2s_contact:
                # tmp_membership_listing = []
                # prev_wid = [], None
                # for _category in l2s_contact.category_id:
                    # res_wid = None

                    # chk_resp = self.chk_serv_category(l2s_category=_category)
                    # if not chk_resp["err_status"]:
                        # res_wid = chk_resp["response"]["resourceName"].split('/')[1]
                        # _category.write({
                            # 'gc_res_id': res_wid,
                            # 'gc_name': chk_resp["response"]['name']
                        # })
                    # else:
                        # crt_srv_resp = self.create_membership_resource(l2s_category=_category)
                        # if not crt_srv_resp["err_status"]:
                            # crt_lc_resp = self.create_membership_resource(s2l_category=crt_srv_resp["response"])
                            # if not crt_lc_resp["err_status"]:
                                # res_wid = crt_lc_resp["response"].gc_res_id

                    # if res_wid and res_wid != prev_wid:
                        # tmp_membership_listing.append({
                            # "contactGroupMembership": {
                                # "contactGroupResourceName": constants.GC_CONTACT_GROUP_KEY + '/' + res_wid
                            # }
                        # })
                        # prev_wid = res_wid

                # if len(tmp_membership_listing) > 0:
                    # crt_ms_resp["response"] = tmp_membership_listing
                    # crt_ms_resp["err_status"] = False
                # else:
                    # crt_ms_resp["err_status"] = constants.GC_CONTACTS_MEMBERSHIPS_CRT_ERR
            # else:
                # crt_ms_resp["response"] = constants.GC_CONTACTS_MEMBERSHIPS_CRT_ERR
        # except Exception as ex:
            # self.__logging.exception("Create Contact Membership Listing Exception: " + str(ex))
            # crt_ms_resp["response"] = constants.GC_CONTACTS_MEMBERSHIPS_CRT_EXCEPT
        # return crt_ms_resp

    def get_custom_relations(self, sr_custom_fields, _type):
        gt_cum_resp = {"err_status": True, "response": None}
        try:
            tmp_custom_ids = []
            for each in sr_custom_fields:
                if 'person' in each:
                    def_value = each['person']
                else:
                    def_value = each['value']

                chk_exist_rec = self.__default_env[constants.GOOGLE_MOD_RES_CUSTOM_MODEL].search([
                    '&', ('name', '=', def_value), ('type', '=', _type)
                ])
                if len(chk_exist_rec) > 0:
                    tmp_custom_ids.append(chk_exist_rec[0].id)
                else:
                    nw_record = self.__default_env[constants.GOOGLE_MOD_RES_CUSTOM_MODEL].create({
                        'type': _type,
                        'name': def_value,
                        'label': str(each['type']).capitalize()
                    })
                    tmp_custom_ids.append(nw_record.id)
            if len(tmp_custom_ids) > 0:
                gt_cum_resp["response"] = tmp_custom_ids
                gt_cum_resp["err_status"] = False
        except Exception as ex:
            self.__logging.exception("Get Local Custom Fields Exception: " + str(ex))
        return gt_cum_resp

    def create_update_serv_contact(self, db_contact, is_update=False, addon_info=None):
        crt_srv_resp = {"err_status": True, "response": None}
        try:
            # Add Real Update datetime when create or updating contact on Google server
            real_update_time = pytz.utc.localize(datetime.utcnow()).astimezone(pytz.timezone(constants.DEFAULT_TIMEZONE))
            updated_tz = db_contact.write_date
            if type(updated_tz) == str:
                updated_tz = datetime.strptime(db_contact.write_date, constants.DEFAULT_DATETIME_FORMAT)
            updated_tz = updated_tz.astimezone(pytz.timezone(constants.DEFAULT_TIMEZONE))

            gl_json_params = {
                "addresses": [
                    {
                        'type': "Work",
                        "streetAddress": db_contact.street if db_contact.street else "",
                        'extendedAddress': db_contact.street2 if db_contact.street2 else "",
                        'poBox': db_contact.state_id.name if db_contact.state_id else "",
                        "city": db_contact.city if db_contact.city else "",
                        "postalCode": db_contact.zip if db_contact.zip else "",
                        'country': db_contact.country_id.name if db_contact.country_id else ""
                    },
                    {
                        'type': "Home",
                        "streetAddress": db_contact.street_home if db_contact.street_home else "",
                        'extendedAddress': db_contact.street2_home if db_contact.street2_home else "",
                        'poBox': db_contact.state_id_home.name if db_contact.state_id_home else "",
                        "city": db_contact.city_home if db_contact.city_home else "",
                        "postalCode": db_contact.zip_home if db_contact.zip_home else "",
                        'country': db_contact.country_id_home.name if db_contact.country_id_home else ""
                    }
                ],
                "emailAddresses": [
                    {"value": db_contact.email if db_contact.email else "", "type": "Work"},
                    {"value": db_contact.email_personal if db_contact.email_personal else "", "type": "Home"},
                    {"value": db_contact.email_other if db_contact.email_other else "", "type": "Other"},
                    {"value": db_contact.email_alternate if db_contact.email_alternate else "", "type": "Alternate"},
                ],
                "nicknames": [{
                    "type": "DEFAULT",
                    "value": db_contact.printed_name if db_contact.printed_name else ""
                }],
                "phoneNumbers": [
                    {"value": db_contact.mobile if db_contact.mobile else "", "type": "Mobile"},
                    {"value": db_contact.phone if db_contact.phone else "", "type": "Work"},
                    {"value": db_contact.phone_business if db_contact.phone_business else "", "type": "Pager"},
                    {"value": db_contact.phone_other if db_contact.phone_other else "", "type": "Other"},
                    {"value": db_contact.phone_company if db_contact.phone_company else "", "type": "Main"},
                ],
                "urls": [
                    {"value": db_contact.website if db_contact.website else "", "type": "homePage"},
                    {"value": db_contact.map_work if db_contact.map_work else "", "type": "Work Map"},
                    {"value": db_contact.map_home if db_contact.map_home else "", "type": "Home Map"}
                ],
                "memberships": [{
                    'contactGroupMembership': {
                        'contactGroupResourceName': 'contactGroups/myContacts'
                    }
                }],
                "userDefined": [
                    {"key": "Odoo Last Updated", "value": str(updated_tz.strftime(constants.DEFAULT_RES_DATETIME_FORMAT))},
                    {"key": "Google Last Updated", "value": str(real_update_time.strftime(constants.DEFAULT_RES_DATETIME_FORMAT))},
                    {"key": constants.GC_CONTACTS_USER_DEFINED_ID, "value": str(db_contact.id)}
                ],
                "biographies": [{
                    "value": re.sub(self.__clean_tags_re, '', db_contact.comment) if db_contact.comment else "Default",
                    "contentType": "TEXT_PLAIN"
                }]
            }

            '''
            Custom defined Relationships fields
            "relations": [
                {"person": db_contact.relation_spouse.name if db_contact.relation_spouse else '', "type": "Spouse"},
                {"person": db_contact.relation_mother.name if db_contact.relation_mother else '', "type": "Mother"},
                {"person": db_contact.relation_father.name if db_contact.relation_father else '', "type": "Father"},
                {"person": db_contact.relation_child.name if db_contact.relation_child else '', "type": "Child"},
                {"person": db_contact.relation_friend.name if db_contact.relation_friend else '', "type": "Friend"},
                {"person": db_contact.relation_referred.name if db_contact.relation_referred else '', "type": "ReferredBy"},
            ],
            '''

            #########################################################################################################
            # ##################################### Check Individual or Company #####################################
            #########################################################################################################

            if db_contact.is_company:
                gl_json_params["names"] = [{
                    "givenName": "",
                    "familyName": db_contact.name,
                    "displayName": db_contact.name,
                    #"honorificPrefix": "Company"
                }]
                gl_json_params["organizations"] = [{
                    "name": db_contact.commercial_company_name if db_contact.commercial_company_name else "",
                    #"title": "Company",
                }]
                gl_json_params["imClients"] = [
                    {"protocol": "ID / Reg. #", "username": str(db_contact.vat) if db_contact.vat else ""}
                ]

                if db_contact.reg_date:
                    cs_reg_date = db_contact.reg_date
                    if type(cs_reg_date) == str:
                        cs_reg_date = datetime.strptime(cs_reg_date, constants.DEFAULT_CS_DATE_FORMAT)
                    gl_json_params["events"] = [
                        {
                            "date": {
                                "year": cs_reg_date.year,
                                "month": cs_reg_date.month,
                                "day": cs_reg_date.day
                            },
                            "type": "Reg. Date",
                            "formattedType": "Reg. Date"
                        }
                    ]
            else:
                if db_contact.type == 'contact':
                    gl_json_params["names"] = [{
                        "displayName": db_contact.name,
                        "givenName": db_contact.firstname if db_contact.firstname else "",
                        "familyName": db_contact.lastname if db_contact.lastname else "",
                        # "middleName": db_contact.middle_name.name if db_contact.middle_name else "",
                        #"honorificPrefix": db_contact.title.name if db_contact.title.name else ""
                    }]
                    gl_json_params["organizations"] = [{
                        "name": db_contact.commercial_company_name if db_contact.commercial_company_name else "",
                        "title": db_contact.function if db_contact.function else ""
                    }]
                else:
                    gl_json_params["names"] = [{
                        "givenName": "@",
                        "familyName": db_contact.name,
                        "displayName": db_contact.name,
                    }]
                    gl_json_params["organizations"] = [{
                        "name": db_contact.commercial_company_name if db_contact.commercial_company_name else "",
                        "title": db_contact.function if db_contact.function else ""
                    }]

                gl_json_params["imClients"] = [
                    {"protocol": "ID #", "username": str(db_contact.id_no) if db_contact.id_no else ""}
                ]

            #########################################################################################################
            # ################################   End Check Individual or Company  ###################################
            #########################################################################################################

            gt_def_membership_resp = self.get_default_membership()
            if not gt_def_membership_resp["err_status"]:
                gl_json_params["memberships"].append(gt_def_membership_resp["response"])

            if db_contact.birthday:
                _birth_day = db_contact.birthday
                if type(_birth_day) == str:
                    _birth_day = datetime.strptime(_birth_day, constants.DEFAULT_DATETIME_FORMAT.split(' ')[0])
                gl_json_params["birthdays"] = [{
                    "date": {
                        "day": _birth_day.day,
                        "month": _birth_day.month,
                        "year": _birth_day.year
                    }
                }]

            # if db_contact.category_id and len(db_contact.category_id) > 0:
                # listing_resp = self.create_membership_lists(l2s_contact=db_contact)
                # if not listing_resp["err_status"]:
                    # gl_json_params["memberships"] += listing_resp["response"]

            # For Social Profile Custom Manageable fields
            try:
                if db_contact.social_profile_ids and len(db_contact.social_profile_ids) > 0:
                    for sp_each in db_contact.social_profile_ids:
                        gl_json_params["urls"].append({
                            "value": sp_each.name,
                            "type": sp_each.sp_type.label if sp_each.sp_type.label else "Other"
                        })
            except:
                pass

            # For RelationShips Custom Manageable fields
            # try:
                # gl_json_params["relations"] = []
                # if db_contact.inverse_relation_ids and len(db_contact.inverse_relation_ids) > 0:
                    # for rel_each in db_contact.inverse_relation_ids:
                        # if rel_each.this_partner_id:
                            # gl_json_params["relations"].append({
                                # "person": rel_each.this_partner_id.name,
                                # "type": rel_each.type_selection_id.name if rel_each.type_selection_id.name else "N/A"
                            # })
            # except Exception as ex:
                # self.__logging.exception("Google Export Relation Exception: " + str(ex))

            if not is_update:
                self.__logging.info("* >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> Creating Contact to Google for ID : " + str(db_contact.id)) # Panos 06/03/2022 - Checked
                req_url = self.__base_endpoint + self.__req_version + self.__create_contact_api
                sr_resp = requests.post(req_url, data=json.dumps(gl_json_params), headers=self.__req_headers,
                                        timeout=self.__req_timeout).json()
            else:
                gc_id = db_contact.gc_id
                gl_json_params["etag"] = db_contact.gc_etag
                if not db_contact.gc_id and not db_contact.gc_etag:
                    gc_id = addon_info["gc_id"]
                    gl_json_params["etag"] = addon_info["gc_etag"]

                if gc_id and 'etag' in gl_json_params:
                    try:
                        del gl_json_params["names"][0]["displayName"]
                    except:
                        pass

                    self.__logging.info("* >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>  Updating Contact to Google with ID : " + str(db_contact.id)) # Panos 06/03/2022 - Checked
                    req_url = self.__base_endpoint + self.__req_version + self.__update_contact_api.replace(
                        "{{people_id}}", gc_id) + "?updatePersonFields=" + ','.join(constants.GC_CONTACT_UPDATE_ADDON_FLDS)
                    sr_resp = requests.patch(req_url, data=json.dumps(gl_json_params), headers=self.__req_headers,
                                             timeout=self.__req_timeout).json()
                    if constants.RESPONSE_ERROR_KEY in sr_resp:
                        gr_resp = self.get_contact_detail_by_id(people_id=gc_id)
                        if not gr_resp["err_status"]:
                            gl_json_params["etag"] = gr_resp["response"]["etag"]
                            sr_resp = requests.patch(req_url, data=json.dumps(gl_json_params), headers=self.__req_headers,
                                                     timeout=self.__req_timeout).json()
                else:
                    sr_resp = {
                        constants.RESPONSE_ERROR_KEY: {
                            constants.RESPONSE_MESSAGES_KEY: constants.GC_CONTACTS_CRT_ERR
                        }
                    }

            if constants.RESPONSE_ERROR_KEY not in sr_resp:
                resource_id = sr_resp["resourceName"].split('/')[1]
                # Update Google ID if newly created contact
                if not is_update:
                    db_contact.update_params({'gc_id': resource_id, 'gc_etag': sr_resp["etag"]})

                if db_contact.image_1920:
                    self.__logging.info("* >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>  Contact Image Found for ID : " + str(db_contact.id)) # Panos 06/03/2022 - Checked
                    upd_resp = self.update_profile_image_by_contact(l2s_contact=db_contact, addon_id=resource_id)
                    self.__logging.info("* >>>>>>>>>>>>>>>>>>>> Contact Image is Saved for ID : " + str(db_contact.id))  # Panos 06/03/2022 - Checked
                    if upd_resp["err_status"]:
                        self.__logging.info("Update Contact Image: " + upd_resp["response"])
                    else:
                        get_detl_resp = self.get_contact_detail_by_id(people_id=resource_id)
                        if not get_detl_resp["err_status"]:
                            db_contact.update_params({'gc_etag': get_detl_resp["response"]["etag"]})
                else:
                    #self.__logging.info("* >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>  Contact Image Not Found for ID : " + str(db_contact.id)) # Panos 06/03/2022 - Checked
                    upd_resp = self.delete_profile_image_by_contact(addon_id=resource_id)
                    if upd_resp["err_status"]:
                        #self.__logging.info("Update Contact Image: " + upd_resp["response"])
                        self.__logging.info("* >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>  Contact Image Not Found for ID : " + str(db_contact.id))  # Panos 06/03/2022 - Checked
                    else:
                        get_detl_resp = self.get_contact_detail_by_id(people_id=resource_id)
                        if not get_detl_resp["err_status"]:
                            db_contact.update_params({'gc_etag': get_detl_resp["response"]["etag"]})

                crt_srv_resp["response"] = sr_resp
                crt_srv_resp["err_status"] = False
            else:
                crt_srv_resp["response"] = sr_resp[constants.RESPONSE_ERROR_KEY][constants.RESPONSE_MESSAGES_KEY]
        except Exception as ex:
            self.__logging.exception("Create Server Contact Exception: " + str(ex))
            crt_srv_resp["response"] = constants.GC_CONTACTS_CRT_EXCEPT
        return crt_srv_resp

    def create_update_local_contact(self, sr_contact, previous_local_contact=None):
        crt_lc_resp = {"err_status": True, "response": None}
        try:
            firstname, lastname = None, None

            db_data_params = {
                'gc_etag': sr_contact["etag"],
                # 'title': sr_contact["names"][0]["honorificPrefix"] if 'honorificPrefix' in sr_contact["names"][0] else 'Mr/Mrs',
                'name': sr_contact["names"][0]["displayName"],
                # 'firstname': sr_contact["names"][0]["givenName"],
                # 'middle_name': sr_contact["names"][0]["middleName"],
                # 'lastname': sr_contact["names"][0]["familyName"],
                'source': constants.GC_CONTACT_SOURCE,
            }

            # Check Google Resource ID
            try:
                resource_id = sr_contact["resourceName"].split('/')[1]
                if previous_local_contact:
                    if not previous_local_contact.gc_id:
                        db_data_params['gc_id'] = resource_id
                else:
                    db_data_params['gc_id'] = resource_id
            except:
                pass

            # Check for Title field for Many2one relationship
            # if 'honorificPrefix' in sr_contact["names"][0] and sr_contact["names"][0]["honorificPrefix"]:
                # title_id = self.__default_env[constants.RES_PARTNER_TITLE_MODEL].search([
                    # ('name', '=', str(sr_contact["names"][0]["honorificPrefix"]).capitalize())
                # ])
                # if title_id and len(title_id) > 0:
                    # title_id = title_id[0].id
                # else:
                    # title_id = self.__default_env[constants.RES_PARTNER_TITLE_MODEL].create({
                        # 'name': str(sr_contact["names"][0]["honorificPrefix"]).capitalize()
                    # }).id

            # Check the First Name field for Many2one relationship
            # if 'givenName' in sr_contact["names"][0] and sr_contact["names"][0]["givenName"]:
                # firstname = self.__default_env[constants.RES_PARTNER_FIRST_NAME_MODEL].search([
                    # ('name', '=', sr_contact["names"][0]["givenName"])
                # ])
                # if firstname and len(first_name_id) > 0:
                    # firstname = firstname[0].id
                # else:
                    # firstname = self.__default_env[constants.RES_PARTNER_FIRST_NAME_MODEL].create({
                        # 'name': sr_contact["names"][0]["givenName"]
                    # }).id

            # Check the Last Name field for Many2one relationship
            # if 'familyName' in sr_contact["names"][0] and sr_contact["names"][0]["familyName"]:
                # last_name_id = self.__default_env[constants.RES_PARTNER_LAST_NAME_MODEL].search([
                    # ('name', '=', sr_contact["names"][0]["familyName"])
                # ])
                # if last_name_id and len(last_name_id) > 0:
                    # last_name_id = last_name_id[0].id
                # else:
                    # last_name_id = self.__default_env[constants.RES_PARTNER_LAST_NAME_MODEL].create({
                        # 'name': sr_contact["names"][0]["familyName"]
                    # }).id

            # Check the Middle Name field for Many2one relationship
            # if 'middleName' in sr_contact["names"][0] and sr_contact["names"][0]["middleName"]:
                # middle_name_id = self.__default_env[constants.RES_PARTNER_LAST_NAME_MODEL].search([
                    # ('name', '=', sr_contact["names"][0]["middleName"])
                # ])
                # if middle_name_id and len(middle_name_id) > 0:
                    # middle_name_id = middle_name_id[0].id
                # else:
                    # middle_name_id = self.__default_env[constants.RES_PARTNER_LAST_NAME_MODEL].create({
                        # 'name': sr_contact["names"][0]["middleName"]
                    # }).id

            if firstname:
                db_data_params["firstname"] = firstname
            # if middle_name_id:
                # db_data_params["middle_name"] = middle_name_id
            if lastname:
                db_data_params["lastname"] = lastname
            # if title_id:
                # db_data_params["title"] = title_id

            if "birthdays" in sr_contact and len(sr_contact['birthdays']) > 0:
                birth_date = sr_contact["birthdays"][0]["date"]
                birth_date = str(birth_date["day"]) + '/' + str(birth_date["month"]) + "/" + str(birth_date["year"])
                db_data_params["birthday"] = str(datetime.strptime(
                    birth_date, constants.DEFAULT_DATETIME_FORMAT.split(' ')[0]))

            if "emailAddresses" in sr_contact and len(sr_contact["emailAddresses"]) > 0:
                db_data_params["email"] = sr_contact["emailAddresses"][0]["value"]
                db_data_params["email_personal"] = sr_contact["emailAddresses"][1]["value"] if len(sr_contact["emailAddresses"]) > 1 else ""
                db_data_params["email_other"] = sr_contact["emailAddresses"][2]["value"] if len(sr_contact["emailAddresses"]) > 2 else ""
                db_data_params["email_alternate"] = sr_contact["emailAddresses"][3]["value"] if len(sr_contact["emailAddresses"]) > 3 else ""
            else:
                db_data_params["email"] = ""

            if 'organizations' in sr_contact and len(sr_contact["organizations"]) > 0:
                if "title" in sr_contact["organizations"][0]:
                    db_data_params["function"] = sr_contact["organizations"][0]["title"]
                try:
                    chk_company = self.__default_env[constants.RES_PARTNER_MODEL].search([
                        '&', ('name', '=', sr_contact["organizations"][0]["name"]), ('is_company', '=', True)
                    ])
                    if chk_company and len(chk_company) > 0:
                        db_data_params["parent_id"] = chk_company[0].id
                    else:
                        db_data_params["parent_id"] = self.__default_env[constants.RES_PARTNER_MODEL].create({
                            'name': sr_contact["organizations"][0]["name"],
                            'is_company': True,
                            'company_type': 'company'
                        }).id
                except:
                    self.__logging.exception("Unable to check company information")

            if 'phoneNumbers' in sr_contact and len(sr_contact["phoneNumbers"]) > 0:
                db_data_params["phone"] = sr_contact["phoneNumbers"][0]["value"]
                db_data_params["mobile"] = sr_contact["phoneNumbers"][1]["value"] if len(sr_contact["phoneNumbers"]) > 1 else ""

                filter_res = list(filter(lambda x: x['type'] == "pager", sr_contact['phoneNumbers']))
                db_data_params["phone_business"] = filter_res[0]["value"] if len(filter_res) > 1 else ""

                filter_res = list(filter(lambda x: x['type'] == "other", sr_contact['phoneNumbers']))
                db_data_params["phone_other"] = filter_res[0]["value"] if len(filter_res) > 1 else ""

                filter_res = list(filter(lambda x: x['type'] == "main", sr_contact['phoneNumbers']))
                db_data_params["phone_company"] = filter_res[0]["value"] if len(filter_res) > 1 else ""
            else:
                db_data_params["phone"] = ""
                db_data_params["mobile"] = ""

            if 'addresses' in sr_contact and len(sr_contact["addresses"]) > 0:
                db_data_params["street"] = sr_contact["addresses"][0]["streetAddress"] if 'streetAddress' in sr_contact["addresses"][0] else ""
                db_data_params["street2"] = sr_contact["addresses"][0]["extendedAddress"] if 'extendedAddress' in sr_contact["addresses"][0] else ""
                db_data_params["city"] = sr_contact["addresses"][0]["city"] if 'city' in sr_contact["addresses"][0] else ""
                db_data_params["zip"] = sr_contact["addresses"][0]["postalCode"] if 'postalCode' in sr_contact["addresses"][0] else ""

                try:
                    if 'country' in sr_contact["addresses"][0] and sr_contact["addresses"][0]["country"] and len(sr_contact["addresses"][0]["country"]) > 0:
                        chk_country_exist = self.__default_env[constants.RES_COUNTRY_MODEL].search([
                            ('name', '=', sr_contact["addresses"][0]['country'])
                        ])
                        if chk_country_exist and len(chk_country_exist) > 0:
                            db_data_params["country_id"] = chk_country_exist[0].id
                        else:
                            db_data_params["country_id"] = self.__default_env[constants.RES_COUNTRY_MODEL].create({
                                'name': sr_contact["addresses"][0]['country']
                            }).id
                except Exception as ex:
                    self.__logging.exception("Unable to handle Work Address Country field: " + str(ex))

                try:
                    if 'poBox' in sr_contact["addresses"][0] and sr_contact["addresses"][0]["poBox"] and len(sr_contact["addresses"][0]["poBox"]) > 0:
                        chk_state_exist = self.__default_env[constants.RES_COUNTRY_STATE_MODEL].search([
                            ('name', '=', sr_contact["addresses"][0]['poBox'])
                        ])
                        if chk_state_exist and len(chk_state_exist) > 0:
                            db_data_params["state_id"] = chk_state_exist[0].id
                        else:
                            db_data_params["state_id"] = self.__default_env[constants.RES_COUNTRY_STATE_MODEL].create({
                                'name': sr_contact["addresses"][0]['poBox'],
                                'country_id': db_data_params["country_id"] if "country_id" in db_data_params else constants.DEFAULT_COUNTRY_ID,
                                'code': ''.join([w[0] for w in sr_contact["addresses"][0]['poBox'].split(' ')])
                            }).id
                except Exception as ex:
                    self.__logging.exception("Unable to handle Work Address State field: " + str(ex))

                if len(sr_contact["addresses"]) > 1:
                    db_data_params["street_home"] = sr_contact["addresses"][1]["streetAddress"] if 'streetAddress' in sr_contact["addresses"][1] else ""
                    db_data_params["street2_home"] = sr_contact["addresses"][1]["extendedAddress"] if 'extendedAddress' in sr_contact["addresses"][1] else ""
                    db_data_params["city_home"] = sr_contact["addresses"][1]["city"] if 'city' in sr_contact["addresses"][1] else ""
                    db_data_params["zip_home"] = sr_contact["addresses"][1]["postalCode"] if 'postalCode' in sr_contact["addresses"][1] else ""

                    try:
                        if 'country' in sr_contact["addresses"][1] and sr_contact["addresses"][1]["country"] and len(sr_contact["addresses"][1]["country"]) > 0:
                            chk_country_exist = self.__default_env[constants.RES_COUNTRY_MODEL].search([
                                ('name', '=', sr_contact["addresses"][1]['country'])
                            ])
                            if chk_country_exist and len(chk_country_exist) > 0:
                                db_data_params["country_id_home"] = chk_country_exist[0].id
                            else:
                                db_data_params["country_id_home"] = self.__default_env[constants.RES_COUNTRY_MODEL].create({
                                    'name': sr_contact["addresses"][1]['country']
                                }).id
                    except Exception as ex:
                        self.__logging.exception("Unable to handle Home Address Country field: " + str(ex))

                    try:
                        if 'poBox' in sr_contact["addresses"][1] and sr_contact["addresses"][1]["poBox"] and len(sr_contact["addresses"][1]["poBox"]) > 0:
                            chk_state_exist = self.__default_env[constants.RES_COUNTRY_STATE_MODEL].search([
                                ('name', '=', sr_contact["addresses"][1]['poBox'])
                            ])
                            if chk_state_exist and len(chk_state_exist) > 0:
                                db_data_params["state_id_home"] = chk_state_exist[0].id
                            else:
                                db_data_params["state_id_home"] = self.__default_env[constants.RES_COUNTRY_STATE_MODEL].create({
                                    'name': sr_contact["addresses"][1]['poBox'],
                                    'country_id': db_data_params["country_id_home"] if "country_id_home" in db_data_params else constants.DEFAULT_COUNTRY_ID,
                                    'code': ''.join([w[0] for w in sr_contact["addresses"][1]['poBox'].split(' ')])
                                }).id
                    except Exception as ex:
                        self.__logging.exception("Unable to handle Home Address State field: " + str(ex))

                else:
                    db_data_params["street_home"] = ""
                    db_data_params["street2_home"] = ""
                    db_data_params["city_home"] = ""
                    db_data_params["zip_home"] = ""
            else:
                db_data_params["street"] = ""
                db_data_params["street2"] = ""
                db_data_params["city"] = ""
                db_data_params["zip"] = ""

            if 'urls' in sr_contact and len(sr_contact["urls"]) > 0:
                db_data_params["website"] = sr_contact['urls'][0]["value"]

                filter_res = list(filter(lambda x: x['type'] == "Work Map", sr_contact['urls']))
                db_data_params["map_work"] = filter_res[0]["value"] if len(filter_res) > 0 else ''

                filter_res = list(filter(lambda x: x['type'] == "Home Map", sr_contact['urls']))
                db_data_params["map_home"] = filter_res[0]["value"] if len(filter_res) > 0 else ''

            else:
                db_data_params["website"] = ""

            # if 'memberships' in sr_contact and len(sr_contact['memberships']) > 0:
                # if previous_local_contact:
                    # ct_mbrs_resp = self.create_membership_lists(s2l_contact=sr_contact)
                    # if not ct_mbrs_resp["err_status"]:
                        # previous_local_contact.update_categories_params(ct_mbrs_resp["response"])

            if 'biographies' in sr_contact and len(sr_contact['biographies']) > 0:
                db_data_params['comment'] = sr_contact['biographies'][0]['value']

            try:
                # Check for company or individual
                if 'givenName' in sr_contact["names"][0] and sr_contact["names"][0]["givenName"] and '#' in sr_contact["names"][0]["givenName"]:
                    field = 'vat'
                else:
                    field = 'id_no'
                if field:
                    if 'imClients' in sr_contact and len(sr_contact['imClients']) > 0:
                        db_data_params[field] = sr_contact['imClients'][0]['username']
                    if field == 'vat' and 'events' in sr_contact and len(sr_contact['events']) > 0:
                        sr_date_object = sr_contact['events'][0]['date']
                        sr_date_str = str(sr_date_object["year"]) + '-' + str(sr_date_object["month"]) + '-' + str(sr_date_object["day"])
                        sr_date = datetime.strptime(sr_date_str, constants.DEFAULT_CS_DATE_FORMAT)
                        db_data_params["reg_date"] = str(sr_date)
            except:
                pass

            if previous_local_contact:
                previous_local_contact.update_params(db_data_params)
                crt_lc_resp["response"] = previous_local_contact
            else:
                db_data_params["gc_id"] = sr_contact["resourceName"].split('/')[1]
                contact_obj = self.__default_env[constants.RES_PARTNER_MODEL].create(db_data_params)

                # if 'memberships' in sr_contact and len(sr_contact['memberships']) > 0:
                    # ct_mbrs_resp = self.create_membership_lists(s2l_contact=sr_contact)
                    # if not ct_mbrs_resp["err_status"]:
                        # contact_obj.update_categories_params(ct_mbrs_resp["response"])

                crt_lc_resp["response"] = contact_obj

            current_local_contact = crt_lc_resp["response"]

            ##########################################################################################
            # ###########################   Custom Code for Profile Image   ##########################
            ##########################################################################################
            try:
                if 'photos' in sr_contact and len(sr_contact["photos"]) > 0:
                    byte_data = base64.b64encode(requests.get(sr_contact["photos"][0]['url'], headers=self.__req_headers).content)

                    for img_dim in constants.GC_CONTACTS_IMAGE_DIMENSION:
                        chk_image_rec = self.__default_env[constants.IR_ATTACHMENT_MODEL].search([
                            '&', '&', ('res_field', '=', img_dim), ('res_model', '=', 'res.partner'),
                            ('res_id', '=', current_local_contact.id),
                        ])
                        if chk_image_rec and len(chk_image_rec) > 0:
                            chk_image_rec[0].write({'type': 'binary', 'datas': byte_data})
                        else:
                            self.__default_env[constants.IR_ATTACHMENT_MODEL].create({
                                'name': img_dim,
                                'res_model': 'res.partner',
                                'res_field': img_dim,
                                'res_id': current_local_contact.id,
                                'type': 'binary',
                                'datas': byte_data
                            })
                    # db_data_params["image_1920"] = base64.b64encode(requests.get(sr_contact["photos"][0]['url']).content).decode(encoding="utf-8")
            except Exception as ex:
                self.__logging.exception("Exception Profile Image Import: " +str(ex))

            ##########################################################################################
            # ###########################   Custom Code for Social Profile   #########################
            ##########################################################################################

            try:
                social_profile_addons = []
                if 'urls' in sr_contact and len(sr_contact['urls']) > 1:
                    for social_profile in sr_contact['urls'][1:]:
                        if social_profile['type'] not in ['Work Map', 'Home Map']:
                            chk_type = self.__default_env[constants.SOCIAL_PROFILE_TYPE_MODEL].search([
                                ('name', '=', social_profile['type'])
                            ])
                            if chk_type and len(chk_type) > 0:
                                type_id = chk_type[0].id
                            else:
                                type_id = self.__default_env[constants.SOCIAL_PROFILE_TYPE_MODEL].create({
                                    'name': social_profile['type']
                                }).id
    
                            if type_id:
                                chk_record_exist = self.__default_env[constants.SOCIAL_PROFILE_MODEL].search([
                                    '&', '&', ('name', '=', social_profile["value"]), ('sp_type', '=', type_id),
                                    ('sp_partner_id', '=', current_local_contact.id)
                                ])
                                if chk_record_exist and len(chk_record_exist) > 0:
                                    continue
                                else:
                                    record_id = self.__default_env[constants.SOCIAL_PROFILE_MODEL].create({
                                        'name': social_profile["value"],
                                        'sp_type': type_id,
                                        'sp_partner_id': current_local_contact.id
                                    }).id
                                    social_profile_addons.append(record_id)
    
                    if len(social_profile_addons) > 0:
                        pass
                        #current_local_contact.update_params({'social_profile_ids': social_profile_addons})
            except Exception as ex:
                self.__logging.exception("Exception Social Profile Import: " +str(ex))

            #######################################################################################################
            # ################################   Custom Code for Relation Ships   #################################
            #######################################################################################################
                
            try:
                relationship_ids_addons = []
                if 'relations' in sr_contact and len(sr_contact['relations']) > 0:
                    for relationship in sr_contact['relations']:
                        # Check Relation Type
                        chk_type = self.__default_env[constants.RES_PARTNER_RELATION_TYPE_MODEL].search([
                            '|', ('name', '=', relationship['type']), ('name_inverse', '=', relationship['type'])
                        ])
                        if chk_type and len(chk_type) > 0:
                            type_id = chk_type[0].id
                        else:
                            type_id = self.__default_env[constants.RES_PARTNER_RELATION_TYPE_MODEL].create({
                                'name': relationship['type'],
                                'google_label': relationship['type'],
                                'name_inverse': 'Custom',
                                'related_google_label': "Custom",
                            }).id

                        # Check RelationShip Person
                        chk_rel_partner = self.__default_env[constants.RES_PARTNER_MODEL].search([
                            ('name', '=', relationship['person'])
                        ])
                        if chk_rel_partner and len(chk_rel_partner) > 0:
                            sel_partner_id = chk_rel_partner[0].id
                        else:
                            sel_partner_id = self.__default_env[constants.RES_PARTNER_MODEL].create({
                                'name': relationship['person']
                            }).id

                        if type_id and sel_partner_id:
                            chk_record_exist = self.__default_env[constants.RES_PARTNER_RELATION_ALL_MODEL].search([
                                '&', '&', ('this_partner_id', '=', current_local_contact.id),
                                ('other_partner_id', '=', sel_partner_id), ('type_id', '=', type_id)
                            ])
                            if chk_record_exist and len(chk_record_exist) > 0:
                                continue
                            else:
                                selection_id = self.__default_env[constants.RES_PARTNER_RELATION_TYPE_SELECTION_MODEL].search([
                                    '&', ('type_id', '=', type_id), ('name', '=', relationship['type'])
                                ])
                                if selection_id and len(selection_id) > 0:
                                    selection_id = selection_id[0].id
                                else:
                                    selection_id = self.__default_env[
                                        constants.RES_PARTNER_RELATION_TYPE_SELECTION_MODEL].create({
                                        'type_id': type_id,
                                        'name': relationship['type']
                                    })
                                record_id = self.__default_env[constants.RES_PARTNER_RELATION_ALL_MODEL].create({
                                    'this_partner_id': sel_partner_id,
                                    'other_partner_id': current_local_contact.id,
                                    'type_id': type_id,
                                    'type_selection_id': selection_id
                                }).id
                                relationship_ids_addons.append(record_id)

                    if len(relationship_ids_addons) > 0:
                        pass
                        # current_local_contact.update_params({'relation_ids': relationship_ids_addons})
            except Exception as ex:
                self.__logging.exception("Exception Relationships Import: " +str(ex))

            crt_lc_resp["err_status"] = False
        except Exception as ex:
            self.__logging.exception("Create Local Contact Exception: " + str(ex))
            crt_lc_resp["response"] = constants.GC_CONTACTS_CRT_EXCEPT
        return crt_lc_resp

    ############################################################################################################
    # #########################################      Imports & Exports   #######################################
    ############################################################################################################

    def get_serv_contact_stat(self, l2s_contact):
        is_update, addons = False, None
        try:
            if l2s_contact.gc_id or l2s_contact.gc_etag:
                gt_detail_resp = self.get_contact_detail_by_id(people_id=l2s_contact.gc_id)
                if not gt_detail_resp["err_status"]:
                    exist_serv_contact = gt_detail_resp["response"]
                    # resource_id = exist_serv_contact["resourceName"].split('/')[1]
                    # addons = {'gc_id': l2s_contact.gc_id, 'gc_etag': exist_serv_contact["etag"]}
                    ## If above statement is not work as expect, you can comment above statement and uncomment the below statement
                    addons = {'gc_id': l2s_contact.gc_id, 'gc_etag': l2s_contact.gc_etag, 'db_exist': True}
                    is_update = True

            if not is_update:
                chk_contact_resp = self.check_contact(l2s_contact=l2s_contact)
                if not chk_contact_resp["err_status"]:
                    exist_serv_contact = chk_contact_resp["response"][0]["person"]
                    resource_id = exist_serv_contact["resourceName"].split('/')[1]
                    addons = {'gc_id': resource_id, 'gc_etag': exist_serv_contact["etag"]}
                    is_update = True

            if is_update:
                inner_addon = {'gc_etag': addons["gc_etag"]}
                if not l2s_contact.gc_id:
                    inner_addon["gc_id"] = addons["gc_id"]
                    addons["db_exist"] = True
                l2s_contact.update_params(inner_addon)
        except Exception as ex:
            self.__logging.exception("Get Server Contact Status Exception: " + str(ex))
        return is_update, addons

    def check_contact(self, s2l_contact=None, l2s_contact=None):
        chk_resp = {"err_status": True, "response": None}
        try:
            if s2l_contact:
                is_found = False

                ####################################################################################
                # ##################   Check DB contact by Google Resource ID    ###################
                ####################################################################################
                sr_gid = s2l_contact["resourceName"].split('/')[1]
                chk_contact_by_gc_id = self.__default_env[constants.RES_PARTNER_MODEL].search([('gc_id', '=', sr_gid)])
                if chk_contact_by_gc_id and len(chk_contact_by_gc_id) > 0:
                    chk_resp["response"] = chk_contact_by_gc_id[0]
                    chk_resp["err_status"] = False
                    is_found = True

                ####################################################################################
                # ###################   Check DB contact by Odoo Contact ID    #####################
                ####################################################################################
                if not is_found and "userDefined" in s2l_contact and len(s2l_contact["userDefined"]) > 0:
                    odoo_cnt_id = None
                    for usr_def in s2l_contact["userDefined"]:
                        if usr_def["key"] == constants.GC_CONTACTS_USER_DEFINED_ID and usr_def["value"]:
                            odoo_cnt_id = usr_def["value"]
                            break

                    if odoo_cnt_id:
                        chk_contact_by_id = self.__default_env[constants.RES_PARTNER_MODEL].search([('id', '=', odoo_cnt_id)])
                        if chk_contact_by_id and len(chk_contact_by_id) > 0:
                            chk_resp["response"] = chk_contact_by_id[0]
                            chk_resp["err_status"] = False
                            is_found = True

                ####################################################################################
                # ################   Check DB contact by Name and Email Fields    ##################
                ####################################################################################
                if not is_found:
                    query = []
                    if 'emailAddresses' in s2l_contact and len(s2l_contact["emailAddresses"]) > 0:
                        query.append('&')
                        query.append(('email', '=', s2l_contact["emailAddresses"][0]["value"]))
                    query.append(('name', '=', s2l_contact["names"][0]["displayName"]))
                    chk_contact_exist = self.__default_env[constants.RES_PARTNER_MODEL].search(query)
                    if chk_contact_exist and len(chk_contact_exist) > 0:
                        chk_resp["response"] = chk_contact_exist[0]
                        chk_resp["err_status"] = False

            elif l2s_contact:
                req_url = self.__base_endpoint + self.__req_version + self.__search_contact_api + \
                          "?query=" + l2s_contact.name
                          # constants.GC_CONTACT_PROFILE_REQ_FLDS_SEP.join(constants.GC_CONTACT_SEARCH_FLDS) + \
                          # "&query='" + l2s_contact.name
                if l2s_contact.email:
                    req_url += ',' + l2s_contact.email
                if l2s_contact.phone:
                    req_url += ',' + l2s_contact.phone
                if l2s_contact.mobile:
                    req_url += ',' + l2s_contact.mobile
                req_url += "&readMask=names,emailAddresses,phoneNumbers,organizations"
                #req_url = req_url.replace(' ', '%20')

                sr_resp = requests.get(req_url, headers=self.__req_headers, timeout=self.__req_timeout).json()
                if constants.RESPONSE_ERROR_KEY not in sr_resp and len(sr_resp) > 0:
                    chk_resp["response"] = sr_resp[constants.RESPONSE_RESULTS_KEY]
                    chk_resp["err_status"] = False
                else:
                    chk_resp["response"] = sr_resp
            else:
                chk_resp["response"] = constants.GC_CONTACTS_CHK_ERR
        except Exception as ex:
            self.__logging.exception("Check Contact Exception: " + str(ex))
            chk_resp["response"] = constants.GC_CONTACTS_CHK_EXCEPT
        return chk_resp

    def update_contact(self, local_contact=None, local_serv_contact=None, l2s_contact=None):
        upd_resp = {"err_status": True, "response": None}
        try:
            if local_contact and local_serv_contact:
                lc_upd_resp = self.create_update_local_contact(
                    sr_contact=local_serv_contact, previous_local_contact=local_contact)
                if not lc_upd_resp["err_status"]:
                    upd_resp["err_status"] = False
                upd_resp["response"] = lc_upd_resp["response"]
            elif l2s_contact:
                is_update, addons = self.get_serv_contact_stat(l2s_contact=l2s_contact)
                serv_resp = self.create_update_serv_contact(
                    db_contact=l2s_contact, is_update=is_update, addon_info=addons)
                if not serv_resp["err_status"]:
                    upd_resp["err_status"] = False
                upd_resp["response"] = serv_resp["response"]
            else:
                upd_resp["response"] = constants.GC_CONTACTS_UPD_ERR
        except Exception as ex:
            self.__logging.exception("Check Contact Exception: " + str(ex))
            upd_resp["response"] = constants.GC_CONTACTS_UPD_EXCEPT
        return upd_resp

    def create_contact(self, s2l_contact=None, l2s_contact=None):
        crt_resp = {"err_status": True, "response": None, "addon": None}
        try:
            if s2l_contact:
                lc_resp = self.create_update_local_contact(sr_contact=s2l_contact)
                if not lc_resp["err_status"]:
                    crt_resp["err_status"] = False
                crt_resp["response"] = lc_resp["response"]

            elif l2s_contact:
                self.__logging.info("* >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>  Checking Contact Status from Google for ID : " + str(l2s_contact.id)) # Panos 06/03/2022 - Checked
                is_update, addons = self.get_serv_contact_stat(l2s_contact=l2s_contact)
                serv_resp = self.create_update_serv_contact(
                    db_contact=l2s_contact, is_update=is_update, addon_info=addons)
                if not serv_resp["err_status"]:
                    crt_resp["err_status"] = False
                    crt_resp["addon"] = is_update
                crt_resp["response"] = serv_resp["response"]
            else:
                crt_resp["response"] = constants.GC_CONTACTS_CRT_ERR
        except Exception as ex:
            self.__logging.exception("Create Contact Exception: " + str(ex))
            crt_resp["response"] = constants.GC_CONTACTS_CRT_EXCEPT
        return crt_resp

    ##############################################################################################################
    # #################################    Baseline Cron & Manual Methods    #####################################
    ##############################################################################################################

    def read_serv_contacts(self):
        try:
            req_url = self.__base_endpoint + self.__req_version + self.__get_contact_api + \
                      self.__get_contact_list_api + '?personFields=' + \
                      constants.GC_CONTACT_PROFILE_REQ_FLDS_SEP.join(constants.GC_CONTACT_SEARCH_FLDS)
            sr_resp = requests.get(req_url, headers=self.__req_headers, timeout=self.__req_timeout).json()
            if constants.RESPONSE_ERROR_KEY not in sr_resp:
                tmp_contact_lists = []
                if self.__initial_date and self.__end_date:
                    for sr_contact in sr_resp["connections"]:
                        meta_info_sources = sr_contact["metadata"]["sources"]
                        update_date = None
                        for mt_info in meta_info_sources:
                            if mt_info['type'] == 'CONTACT':
                                update_date = mt_info["updateTime"]
                                break

                        if update_date:
                            try:
                                update_date = datetime.strptime(
                                    update_date.replace('T', ' ').split('.')[0], constants.DEFAULT_DATETIME_FORMAT)
                            except:
                                update_date = datetime.strptime(update_date.replace('T', ' ').split('.')[0], constants.DEFAULT_CS_DATETIME_FORMAT)

                            if self.__initial_date <= update_date <= self.__end_date:
                                tmp_contact_lists.append(sr_contact)

                elif "connections" in sr_resp:
                    tmp_contact_lists = sr_resp["connections"]
                else:
                    self.__js_resp["response"] = constants.GC_CONTACTS_IMP_NOT_FND

                if len(tmp_contact_lists) > 0:
                    self.__js_resp["response"] = tmp_contact_lists
                    self.__js_resp["total"] = len(tmp_contact_lists)
                    self.__js_resp["err_status"] = False
                else:
                    self.__js_resp["response"] = constants.GC_CONTACTS_IMP_NOT_FND
            else:
                self.__js_resp["response"] = sr_resp[constants.RESPONSE_ERROR_KEY][constants.RESPONSE_MESSAGES_KEY]
        except Exception as ex:
            self.__logging.exception("Server Import Contacts Exception: " + str(ex))
            self.__js_resp["response"] = constants.GC_CONTACTS_IMP_SERV_EXCEPT

    def import_contacts(self):
        self.reset_response()
        try:
            self.__logging.info("* >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>  Start Google Contacts Import Process") # Panos 06/03/2022
            self.read_serv_contacts()
            if not self.__js_resp["err_status"]:
                for _contact in self.__js_resp["response"]:
                    try:
                        self.__logging.info(
                            ">>>>>>>>>>>>>>>>    Check contact from database      >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
                        chk_contact_resp = self.check_contact(s2l_contact=_contact)
                        if chk_contact_resp["err_status"]:
                            self.__logging.info(
                                ">>>>>>>>>>>>>>>>    Create contact to Odoo database      >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
                            crt_resp = self.create_contact(s2l_contact=_contact)
                            if not crt_resp["err_status"]:
                                self.__js_resp["success"] += 1
                                self.__js_resp["contact_ids"].append(crt_resp["response"].id)
                            else:
                                self.__js_resp["failed"] += 1
                        else:
                            self.__logging.info(
                                ">>>>>>>>>>>>>>>>    Update contact to Odoo database      >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
                            upd_resp = self.update_contact(
                                local_contact=chk_contact_resp["response"], local_serv_contact=_contact)
                            if upd_resp["err_status"]:
                                self.__logging.error("Update Odoo Contact Error: " + upd_resp["response"])
                            else:
                                self.__js_resp["updated"] += 1
                                self.__js_resp["contact_ids"].append(chk_contact_resp["response"].id)
                    except Exception as ex:
                        self.__logging.info(">> Import SGL Contact Exception: " + str(ex))
                        self.__js_resp["failed"] += 1
        except Exception as ex:
            self.__logging.exception("Import Contacts Exception: " + str(ex))
            self.__js_resp["response"] = constants.GC_CONTACTS_IMP_EXCEPT
        return self.__js_resp

    def write_serv_contacts(self, db_contacts_data):
        self.reset_response()
        try:
            self.__logging.info("* >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>  Start Google Contacts Export Process") # Panos 06/03/2022 - Checked
            starter_dt = datetime.now()
            for _contact in db_contacts_data:
                # Check Execution timer to verification of Auth Token values
                # starter_dt = self.check_execution_timer(starter_dt=starter_dt)

                # Direct call for Check Oauth Google Credentials
                # If Execution timer is not working as expected, then comment line 1318 and uncomment the line 1323
                # But if use the direct calling the check oauth method, it will create overhead execution of api calling
                self.check_auth_token()

                self.__logging.info("* >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>  Checking Contact Existence to Google for ID : " + str(_contact.id)) # Panos 06/03/2022 - Checked
                chk_serv_status = self.check_contact(l2s_contact=_contact)
                if chk_serv_status["err_status"]:
                    crt_resp = self.create_contact(l2s_contact=_contact)
                    if not crt_resp["err_status"]:
                        if crt_resp["addon"]:
                            self.__js_resp["updated"] += 1
                        else:
                            self.__js_resp["success"] += 1
                    else:
                        self.__logging.info("Internal Error Export Contact: " + crt_resp["response"])
                        self.__js_resp["failed"] += 1
                else:
                    self.__logging.info("* >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>  Direct Update Contact to Google with ID : " + str(_contact.id)) # Panos 06/03/2022 - Shown for some contacts ??
                    upd_resp = self.update_contact(l2s_contact=_contact)
                    if upd_resp["err_status"]:
                        self.__logging.error("Update Google Contact Error: " + upd_resp["response"])
                    else:
                        self.__js_resp["updated"] += 1

                self.__js_resp["contact_ids"].append(_contact.id)
                # Add delay to avoid exceed api calls exception
                time.sleep(constants.HALT_EXECUTION_SECONDS)
        except Exception as ex:
            self.__logging.exception("Export Server Contact Exception: " + str(ex))
            self.__js_resp["response"] = constants.GC_CONTACTS_EXP_SERV_EXCEPT

    def export_contacts(self):
        self.reset_response()
        try:
            query_params = []
            if self.__initial_date and self.__end_date:
                query_params.append('&')
                query_params.append('&')
                query_params.append(('write_date', '>=', str(self.__initial_date)))
                query_params.append(('write_date', '<=', str(self.__end_date)))

            query_params.append('&')
            query_params.append(('is_family', '=', False))
            query_params.append(('active_sync', '=', True))

            _db_contacts = self.__default_env[constants.RES_PARTNER_MODEL].search(query_params, order='write_date desc')
            if _db_contacts and len(_db_contacts) > 0:
                self.write_serv_contacts(db_contacts_data=_db_contacts)
                self.__js_resp["err_status"] = len(_db_contacts)
                self.__js_resp["err_status"] = False
            else:
                self.__js_resp["response"] = constants.GC_CONTACTS_EXP_NOT_FND
        except Exception as ex:
            self.__logging.exception("Export Contacts Exception: " + str(ex))
            self.__js_resp["response"] = constants.GC_CONTACTS_EXP_EXCEPT
        return self.__js_resp