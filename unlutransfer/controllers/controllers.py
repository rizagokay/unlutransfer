# -*- coding: utf-8 -*-
from odoo import http

# class Unlutransfer(http.Controller):
#     @http.route('/unlutransfer/unlutransfer/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/unlutransfer/unlutransfer/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('unlutransfer.listing', {
#             'root': '/unlutransfer/unlutransfer',
#             'objects': http.request.env['unlutransfer.unlutransfer'].search([]),
#         })

#     @http.route('/unlutransfer/unlutransfer/objects/<model("unlutransfer.unlutransfer"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('unlutransfer.object', {
#             'object': obj
#         })