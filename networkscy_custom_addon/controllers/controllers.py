# -*- coding: utf-8 -*-
# from odoo import http


# class KncCustom(http.Controller):
#     @http.route('/knc_custom/knc_custom', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/knc_custom/knc_custom/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('knc_custom.listing', {
#             'root': '/knc_custom/knc_custom',
#             'objects': http.request.env['knc_custom.knc_custom'].search([]),
#         })

#     @http.route('/knc_custom/knc_custom/objects/<model("knc_custom.knc_custom"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('knc_custom.object', {
#             'object': obj
#         })
