##################################################################################################################
# ########################################      Google Apps Basic      ###########################################
##################################################################################################################

GC_AUTH_URL = 'https://accounts.google.com/o/oauth2/v2/auth'
GC_AUTH_EXCODE_URL = 'https://oauth2.googleapis.com/token'
GC_SCOPE_BASE_URL = 'https://www.googleapis.com/auth/'
GC_BASE_URL = 'https://{{service}}.googleapis.com/'
GC_SERVICE_REPLACER = '{{service}}'
GC_REQ_TIMEOUT = 30
GC_SCOPES = ['contacts', 'userinfo.profile', 'userinfo.email']

CONTACT_SOURCE = 'Google Contacts'
RES_PARTNER_MODEL = 'res.partner'
RES_PARTNER_CATEGORY_MODEL = 'res.partner.category'
RES_PARTNER_TITLE_MODEL = 'res.partner.title'
RES_COUNTRY_MODEL = 'res.country'
RES_COUNTRY_STATE_MODEL = 'res.country.state'
RES_PARTNER_CATEGORY_REL_MODEL = 'res_partner_res_partner_category_rel'
RES_PARTNER_STASH_MODEL = 'res_partner'
RES_USERS_MODEL = 'res.users'
IR_CRON_MODEL = 'ir.cron'
IR_MODEL_MODEL = 'ir.model'
IR_CRON_SLASH_MODEL = 'ir_cron'
IR_ATTACHMENT_MODEL = 'ir.attachment'
RES_PARTNER_STREET_MODEL = 'res.partner.street'
RES_PARTNER_STREET_STASH_MODEL = 'res_partner_street'
RES_CITY_ZIP_MODEL = 'res.city.zip'
RES_PARTNER_STREET_DESC = 'Res-Partner Street Model'

RES_PARTNER_FIRST_NAME_MODEL = 'res.partner.first.name'
RES_PARTNER_LAST_NAME_MODEL = 'res.partner.last.name'

SOCIAL_PROFILE_MODEL = 'social.profile'
SOCIAL_PROFILE_TYPE_MODEL = 'social.profile.type'
SOCIAL_PROFILE_MODEL_DESC = 'Social Profile Model Desc'
SOCIAL_PROFILE_TYPE_MODEL_DESC = 'Social Profile Type Model Desc'

RES_PARTNER_RELATION_TYPE_MODEL = 'res.partner.relation.type'
RES_PARTNER_RELATION_ALL_MODEL = 'res.partner.relation.all'
RES_PARTNER_RELATION_TYPE_SELECTION_MODEL = 'res.partner.relation.type.selection'
RES_PARTNER_RELATION_MODEL = 'res.partner.relation.custom'
RES_PARTNER_RELATION_MODEL_DESC = 'Res Partner Relation Model Desc'

GOOGLE_MOD_CREDENTIALS_MODEL = 'google.mod.credentials'
GOOGLE_MOD_CONNECTOR_MODEL = 'google.mod.connector'
GOOGLE_MOD_CRON_MODEL = 'google.mod.cron'
GOOGLE_MOD_RES_CUSTOM_MODEL = 'google.mod.res.custom'
GOOGLE_MOD_IMPORT_STATS_MODEL = 'google.mod.import.stats'
GOOGLE_MOD_EXPORT_STATS_MODEL = 'google.mod.export.stats'
GOOGLE_MOD_CRON_STASH_MODEL = 'google_mod_cron'

GOOGLE_MOD_SPLITTER_URI = '&'
GOOGLE_MOD_CODE_VAL_URI = 'code='
GOOGLE_MOD_CREDENTIALS_RDT_URI = '/google_mod_success'
GOOGLE_MOD_CREDENTIALS_RDT_ODOO_URI = '/web'
GOOGLE_MOD_CREDENTIALS_RDT_URI_ERR = 'Oops, Given redirect url is not supported, Please try again'

RESPONSE_ERROR_KEY = 'error'
RESPONSE_ITEMS_KEY = 'items'
RESPONSE_MESSAGES_KEY = 'message'
RESPONSE_FILES_KEY = 'files'
RESPONSE_RESULTS_KEY = 'results'
RESPONSE_ERR_MESSAGE_KEY = 'err_message'

DEFAULT_INDEX = -1
ACCESS_TOKEN_ATTEMPT = 3
TOKEN_ERROR_CODE = '80049228'
TOKEN_ERR_STATUS_CODE = 401
DEFAULT_ATTACHMENT_PATH = '\\office_attachments\\'
CHECK_TIMER_MINUTES = 1
HALT_EXECUTION_SECONDS = 3
DEFAULT_COUNTRY_ID = 55 # Cyprus

#################################################################################################################
# ####################################        Cron Setting Configuration        #################################
#################################################################################################################

GC_IMPORT_DEF_NAME = 'Google Contacts Import'
GC_EXPORT_DEF_NAME = 'Google Contacts Export'
GC_CRON_CONFIG_SAVE = 'Cron configuration saved successfully'
GC_CRON_CONFIG_UPDATE = 'Cron configuration updated successfully'
GC_CRON_CONFIG_EXCEPT = 'Oops, cron configuration is not saved. Please try again'

##################################################################################################################
# ##########################################     Contacts Section      ###########################################
##################################################################################################################

GC_CONTACT_PROFILE_VERSION = 'v1'

GC_CONTACT_GROUP_KEY = 'contactGroups'
GC_CONTACT_GROUP_CL_LINK = '/contactGroups'
GC_CONTACT_GROUP_GET_LINK = '/{{group_id}}'

GC_CONTACT_PROFILE_LINK = '/people/me'
GC_CONTACT_GET_LINK = '/people/{{people_id}}'
GC_CONTACT_CREATE_LINK = '/people:createContact'
GC_CONTACT_SEARCH_LINK = '/people:searchContacts'
GC_CONTACT_UPDATE_LINK = '/people/{{people_id}}:updateContact'
GC_CONTACT_DELETE_LINK = '/people/{{people_id}}:deleteContact'
GC_CONTACT_UPDATE_PHOTO_LINK = '/people/{{people_id}}:updateContactPhoto'
GC_CONTACT_DELETE_PHOTO_LINK = '/people/{{people_id}}:deleteContactPhoto'
GC_CONTACT_LIST_LINK = '/connections'
GC_CONTACT_SOURCE = 'GOOGLE_CONTACT'

GC_CONTACT_SEARCH_FLDS = [
    'names', 'emailAddresses', 'metadata', 'addresses', 'organizations', 'locations', 'phoneNumbers',
    'urls', 'memberships', 'relations', 'birthdays', 'userDefined', 'nicknames', 'occupations',
    'biographies', 'imClients', 'photos'
]
GC_CONTACT_UPDATE_FLDS = [
    'names', 'emailAddresses', 'addresses', 'organizations', 'phoneNumbers', 'urls', 'memberships',
    'relations', 'birthdays', 'userDefined', 'nicknames', 'occupations', 'biographies', 'imClients',
    'photos'
]
GC_CONTACT_UPDATE_ADDON_FLDS = [
    'names', 'emailAddresses', 'addresses', 'organizations', 'phoneNumbers', 'urls', 'memberships',
    'relations', 'birthdays', 'userDefined', 'nicknames', 'occupations', 'biographies', 'imClients'
]

GC_CONTACT_PROFILE_SERVICE = 'people'
GC_CONTACT_PROFILE_REQ_FLD_NAME = 'personFields'
GC_CONTACT_PROFILE_REQ_FLDS_SEP = ','

GC_PROFILE_EMAIL_FD = 'emailAddresses'
GC_PROFILE_EMAIL_FD_INTERNAL = 'value'
GC_PROFILE_NAME_FD = 'names'
GC_PROFILE_NAME_FD_INTERNAL = 'displayName'

GC_PROFILE_EXCEPT = "Oops, unable to get profile information, Please try again."

GC_CONTACTS_MEMBERSHIPS_GET_ERR = 'Oops, unable to get either local or server contact memberships. Please try again.'
GC_CONTACTS_MEMBERSHIPS_GET_EXCEPT = 'Oops, get contact memberships either local or server failed. Please try again.'
GC_CONTACTS_MEMBERSHIPS_CHK_ERR = 'Oops, unable to check either local or server contact memberships. Please try again.'
GC_CONTACTS_MEMBERSHIPS_CHK_EXCEPT = 'Oops, check contact memberships either local or server failed. Please try again.'
GC_CONTACTS_MEMBERSHIPS_CRT_ERR = 'Oops, unable to create either local or server contact memberships. Please try again.'
GC_CONTACTS_MEMBERSHIPS_CRT_EXCEPT = 'Oops, create contact memberships either local or server failed. Please try again.'
GC_CONTACTS_MEMBERSHIPS_UPD_ERR = 'Oops, unable to update either local or server contact memberships. Please try again.'
GC_CONTACTS_MEMBERSHIPS_UPD_EXCEPT = 'Oops, update contact memberships either local or server failed. Please try again.'

GC_CONTACTS_GET_ERR = 'Oops, unable to get either local or server contact. Please try again.'
GC_CONTACTS_GET_EXCEPT = 'Oops, get contact either local or server failed. Please try again.'
GC_CONTACTS_CHK_ERR = 'Oops, unable to check either local or server contact. Please try again.'
GC_CONTACTS_CHK_EXCEPT = 'Oops, check contact either local or server failed. Please try again.'
GC_CONTACTS_CRT_ERR = 'Oops, unable to create either local or server contact. Please try again.'
GC_CONTACTS_CRT_EXCEPT = 'Oops, create contact either local or server failed. Please try again.'
GC_CONTACTS_UPD_ERR = 'Oops, unable to update either local or server contact. Please try again.'
GC_CONTACTS_UPD_EXCEPT = 'Oops, create update either local or server failed. Please try again.'

GC_CONTACTS_IMP_NOT_FND = 'Oops, no contacts found from server. Please try again.'
GC_CONTACTS_IMP_EXCEPT = 'Oops, Import Contacts failed, Please try again.'
GC_CONTACTS_IMP_SERV_EXCEPT = 'Oops, Import Contacts from Server failed, Please try again.'
GC_CONTACTS_EXP_EXCEPT = 'Oops, Export Contacts failed, Please try again.'
GC_CONTACTS_EXP_SERV_EXCEPT = 'Oops, Export Contacts to Server failed, Please try again.'
GC_CONTACTS_EXP_NOT_FND = "Oops, Contacts are not found either according to date ranges"

GC_CONTACTS_IMAGE_DIMENSION = ['image_128', 'image_256', 'image_512','image_1024', 'image_1920']
GC_CONTACTS_USER_DEFINED_ID = "Odoo Database ID"

###################################################################################################################
# #########################################      Connection Section      ##########################################
###################################################################################################################

GC_CONN_URL_FAILED = "Oops, unable to generate authorization link."
GC_CONN_URL_EXCEPT = "Oops, unable to generate authorize link, Please try again."
GC_CONN_CRED_NOT_FND = "Oops, unable to find credentials. Please try again."
GC_CONN_CRED_ACS_FAILED = "Oops, unable to generate access credentials, Please try again."
GC_CONN_CRED_ACS_EXCEPT = "Oops, unable to request for access credentials, Please try again."
GC_CONN_RAT_FAILED = "Oops, unable to refresh authorization information."
GC_CONN_RAT_EXCEPT = "Oops, unable to request for refresh authorize info, Please try again."

# System Messages
FAILURE_POP_UP_TITLE = 'System Alert'
AUTH_URL_CREATION_FAILED = 'Oops, system unable to create authorize link'
AUTH_URL_CREATION_EXCEPT = 'Oops, system found exception while creating authorize link'

SYNC_REQ_ERROR = 'Oops, unable to process given request, Please try again'
ACCESS_TOKEN_ERR_REFRESH = 'Oops, unable to refresh authorization information, Please try again'
ACCESS_TOKEN_EXCEPT = 'Oops, unable to get credentials information, Please try again'
ACCESS_TOKEN_CRED_NTFND = 'Oops, credentials information not found, Please save credentials before usage'
ACCESS_TOKEN_NOTFOUND = 'Oops, authorization information not found, Please authorize account before usage'
ACCESS_TOKEN_INVALID = 'Oops, authorization information is invalid, Please authorize account again'
GRANT_CODE_ERR = 'Unable to get authorization code information, Please try again.'

NO_OPT_SECTION_ERR = 'Oops, no operation is not being selected, Please some operation to proceed.'
SYNC_PROCESS_MSG = "Synchronization process completed"

# DateTime Format
DEFAULT_DATETIME = '01/01/2020 07:00:00'
DEFAULT_DATETIME_FORMAT = '%d/%m/%Y %H:%M:%S'
DEFAULT_TZ_DATETIME_FORMAT = '%d/%m/%YT%H:%M:%S'
DEFAULT_RES_DATETIME_FORMAT = '%d/%m/%Y - %H:%M:%S'
DEFAULT_TIMEZONE = "Asia/Nicosia"
DEFAULT_CS_DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'
DEFAULT_CS_DATE_FORMAT = '%Y-%m-%d'
INVALID_DATE_RANGES = "Invalid date ranges found, Please correct date ranges."