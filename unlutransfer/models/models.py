# -*- coding: utf-8 -*-
from odoo import models, fields, api, _, tools
from random import randint


class StockPicking(models.Model):
    _inherit = "stock.picking"

    plate_no = fields.Char(string="Plaka No")


class SuppliferInfo(models.Model):
    _inherit = "product.supplierinfo"

    producer = fields.Many2one(
        'res.partner',
        'Producer',
        required=True,
        help="Producer of this product")


class Partner(models.Model):
    _inherit = "res.partner"

    is_paper_supplier = fields.Boolean(string=u'Kağıt Tedarikçisi')


class SaleOrder(models.Model):
    _inherit = "sale.order"

    receipt_no = fields.Char(string="Fatura Numarası")


class ProductTemplate(models.Model):
    _inherit = "product.template"

    product_type = fields.Selection(selection=[('1', u'Satış'), ('2', u'Fason')], string=u"Üretim Tipi")
    product_spesification = fields.Selection(selection=[(1, "Boya"), (2, "Kumaş"), (3, "Baskılı Kağıt"), (4, "Kağıt"),
                                                        (5, "Varak Kağıdı"), (8, "İlaç")], string=u"Ürün Tipi")
    fake_material = fields.Boolean(string=u"Üretim Materyali mi?")
    paper_measurement_type = fields.Selection(selection=[(1, 'kg'), (2, 'mt')], string="Fason Kumaş Ölçü Birimi")
    fiber_content = fields.Text(string=u"Elyaf İçeriği")
    paper_type = fields.Selection(selection=[('1', u'Satın Alım'), ('2', u'Üretim')], string=u"Kağıt Üretim Tipi")
    sale_paper_type = fields.Selection(selection=[('1', u'Satın Alım'), ('2', u'Üretim')], string=u"Kağıt Üretim Tipi")
    width = fields.Char(string="Genişlik (cm)")
    production_type = fields.Selection(selection=[('1', u'Gofre Baskı'), ('2', u'Transfer Baskılı Kumaş'),
                                                  ('3', u'Varak Baskılı Kumuaş')], string=u"Üretim Tipi")
    sale_production_type = fields.Selection(selection=[('1', u'Gofre Baskı'), ('2', u'Transfer Baskılı Kumaş'),
                                                       ('3', u'Varak Baskılı Kumaş')], string=u"Üretim Tipi")
    texture_no = fields.Char(string="Desen No")
    sale_texture_no = fields.Char(string="Desen No")
    variant_no = fields.Char(string="Varyant No")
    sale_variant_no = fields.Char(string="Varyant No")
    paper = fields.Many2one(
        'product.product',
        string=u"Kağıt",
        domain=[('product_spesification', '=', 4), ('width', '!=', '')])
    sale_paper = fields.Many2one(
        'product.product',
        string=u"Kağıt",
        domain=[('product_spesification', '=', 4), ('width', '!=', '')])
    pattern_code = fields.Char(string=u"Kalıp Kodu")
    pattern_code_sub = fields.Many2one('unluransfer.models.pattern', string=u"Kalıp Kodu")
    sale_pattern_code_sub = fields.Many2one('unluransfer.models.pattern', string=u"Kalıp Kodu")
    customer = fields.Many2one('res.partner', string=u"Müşteri")
    sale_customer = fields.Many2one('res.partner', string=u"Müşteri")
    supplier = fields.Many2one(
        'res.partner',
        string=u'Transfer Baskı Kağıdı Tedarikçisi',
        domain=[('is_paper_supplier', '=', True)])
    sale_supplier = fields.Many2one(
        'res.partner',
        string=u'Transfer Baskı Kağıdı Tedarikçisi',
        domain=[('is_paper_supplier', '=', True)])
    foil_paper = fields.Many2one(
        'product.product',
        string=u"Varak Kağıdı",
        domain=[('product_spesification', '=', 5)])
    sale_foil_paper = fields.Many2one(
        'product.product',
        string=u"Varak Kağıdı",
        domain=[('product_spesification', '=', 5)])
    recipe_code = fields.Many2one(
        'product.product',
        string=u"İlaç Kodu",
        domain=[('product_spesification', '=', 8)])
    sale_recipe_code = fields.Many2one(
        'product.product',
        string=u"İlaç Kodu",
        domain=[('product_spesification', '=', 8)])
    standart_material_for_paper = fields.Boolean(
        string=u"Kağıt Üretimi İçin Standart Materyal")
    roll_count = fields.Integer(string="Top Adedi")
    textile = fields.Many2one(
        'product.product',
        string="Kumaş",
        domain=[('product_spesification', '=', 2)])

    textile_description = fields.Char(string="Kumaş Açıklama")


    @api.onchange('textile_description')
    def _check_textile_change(self):
        if self.textile_description:
            self.default_code = self.textile_description

    @api.onchange('paper_type', 'variant_no', 'texture_no', 'customer',
                  'paper', 'foil_paper', 'recipe_code', 'pattern_code_sub')
    def check_change(self):
        if self.production_type == u'2':
            if self.paper_type:
                if self.paper_type == u'1':
                    self.name = (self.texture_no or '') + '-' + (
                        self.variant_no or '') + ("/" + self.customer.name
                                                  if self.customer else '/')
                else:
                    self.name = (self.texture_no or '') + '-' + (
                        self.variant_no or '') + (
                            ("/" + self.paper.width
                             if self.paper.width else '/[PAPER WIDTH]') if
                            self.paper else '') + ("/" + self.customer.name[:6]
                                                   if self.customer else '/')
        elif self.production_type == u'3':
            self.name = (self.pattern_code_sub.name if self.pattern_code_sub
                         else '') + (self.recipe_code.name
                                     if self.recipe_code else '') + "/" + (
                                         self.foil_paper.name
                                         if self.foil_paper else
                                         '') + "/" + (self.customer.name[:6]
                                                      if self.customer else '')
        elif self.production_type == u'1':
            self.name = (self.pattern_code_sub.name if self.pattern_code_sub
                         else '') + "/" + (self.customer.name[:6]
                                           if self.customer else '')

    @api.onchange('sale_paper_type', 'sale_variant_no', 'sale_texture_no',
                  'sale_customer', 'sale_paper', 'sale_foil_paper',
                  'sale_recipe_code', 'sale_pattern_code_sub')
    def check_change_sale(self):
        if self.sale_production_type == u'2':
            if self.sale_paper_type:
                if self.sale_paper_type == u'1':
                    self.name = (self.sale_texture_no or '') + '-' + (
                        self.sale_variant_no
                        or '') + ("/" + self.sale_customer.name
                                  if self.sale_customer else '/')
                else:
                    self.name = (self.sale_texture_no or '') + '-' + (
                        self.sale_variant_no or '') + (
                            ("/" + self.sale_paper.width
                             if self.sale_paper.width else '/[PAPER WIDTH]')
                            if self.sale_paper else
                            '') + ("/" + self.sale_customer.name[:6]
                                   if self.sale_customer else '/')
        elif self.sale_production_type == u'3':
            self.name = (self.sale_pattern_code_sub.name
                         if self.sale_pattern_code_sub else
                         '') + (self.sale_recipe_code.name
                                if self.sale_recipe_code else '') + "/" + (
                                    self.sale_foil_paper.name
                                    if self.sale_foil_paper else
                                    '') + "/" + (self.sale_customer.name[:6]
                                                 if self.sale_customer else '')
        elif self.sale_production_type == u'1':
            self.name = (self.sale_pattern_code_sub.name
                         if self.sale_pattern_code_sub else
                         '') + "/" + (self.sale_customer.name[:6]
                                      if self.sale_customer else '')

    @api.model
    def create(self, vals):
        # set name
        try:
            if vals["production_type"] == u'2':
                if vals["paper_type"]:
                    if vals["paper_type"] == u'1':
                        customername = ""
                        customerid = vals["customer"]
                        customerenv = self.env["res.partner"]
                        foundcustomers = customerenv.search([('id', '=',
                                                              customerid)])
                        if len(foundcustomers) > 0:
                            foundcustomer = foundcustomers[0]
                            customername = foundcustomer.name[:
                                                              6] if foundcustomer.name else ""
                        product_name = (vals["texture_no"] or '') + '-' + (
                            vals["variant_no"] or '') + "/" + customername
                        vals.update({"name": product_name})
                    else:
                        customername = ""
                        customerid = vals["customer"]
                        customerenv = self.env["res.partner"]
                        foundcustomers = customerenv.search([('id', '=',
                                                              customerid)])
                        if len(foundcustomers) > 0:
                            foundcustomer = foundcustomers[0]
                            customername = foundcustomer.name[:
                                                              6] if foundcustomer.name else ""
                        paperproductwith = ""
                        paperid = vals["paper"]
                        paperenv = self.env["product.product"]
                        foundpapers = paperenv.search([('id', '=', paperid)])
                        if len(foundpapers) > 0:
                            foundpaper = foundpapers[0]
                            paperproductwith = foundpaper.width if foundpaper.width else ""
                        product_name = (vals["texture_no"] or '') + '-' + (
                            vals["variant_no"] or
                            '') + "/" + paperproductwith + "/" + customername
                        vals.update({"name": product_name})
                elif vals["sale_paper_type"]:
                    if vals["sale_paper_type"] == u'1':
                        customername = ""
                        customerid = vals["sale_customer"]
                        customerenv = self.env["res.partner"]
                        foundcustomers = customerenv.search(
                            [('id', '=', customerid)], limit=1)
                        if len(foundcustomers) > 0:
                            foundcustomer = foundcustomers[0]
                            customername = foundcustomer.name[:
                                                              6] if foundcustomer.name else ""
                        product_name = (vals["sale_texture_no"] or
                                        '') + '-' + (vals["sale_variant_no"] or
                                                     '') + "/" + customername
                        vals.update({"name": product_name})
                    else:
                        customername = ""
                        customerid = vals["sale_customer"]
                        customerenv = self.env["res.partner"]
                        foundcustomers = customerenv.search(
                            [('id', '=', customerid)], limit=1)
                        if len(foundcustomers) > 0:
                            foundcustomer = foundcustomers[0]
                            customername = foundcustomer.name[:
                                                              6] if foundcustomer.name else ""
                        paperproductwith = ""
                        paperid = vals["sale_paper"]
                        paperenv = self.env["product.product"]
                        foundpapers = paperenv.search(
                            [('id', '=', paperid)], limit=1)
                        if len(foundpapers) > 0:
                            foundpaper = foundpapers[0]
                            paperproductwith = foundpaper.width if foundpaper.width else ""
                        product_name = (vals["sale_texture_no"] or '') + '-' + (
                            vals["sale_variant_no"] or
                            '') + "/" + paperproductwith + "/" + customername
                        vals.update({"name": product_name})
            elif vals["production_type"] == u'3':
                if vals["product_type"] == u'2':
                    customername = ""
                    customerid = vals["customer"]
                    customerenv = self.env["res.partner"]
                    foundcustomers = customerenv.search([('id', '=',
                                                          customerid)])
                    if len(foundcustomers) > 0:
                        foundcustomer = foundcustomers[0]
                        customername = foundcustomer.name[:
                                                          6] if foundcustomer.name else ""
                    recipe_code_name = ""
                    recipeid = vals["recipe_code"]
                    productenv = self.env["product.product"]
                    foundrecipes = productenv.search([('id', '=', recipeid)])
                    if len(foundrecipes) > 0:
                        foundrecipe = foundrecipes[0]
                        recipe_code_name = foundrecipe.name if foundrecipe.name else ""
                    foil_paper_name = ""
                    foilpaperid = vals["foil_paper"]
                    productenv = self.env["product.product"]
                    foundfoilpapers = productenv.search([('id', '=',
                                                          foilpaperid)])
                    if len(foundfoilpapers) > 0:
                        foundfoilpaper = foundfoilpapers[0]
                        foil_paper_name = foundfoilpaper.name if foundfoilpaper.name else ""
                    patterncodename = ""
                    pattern_code_sub = vals["pattern_code_sub"]
                    patternenv = self.env["unluransfer.models.pattern"]
                    foundpatterns = patternenv.search([('id', '=',
                                                        pattern_code_sub)])
                    if len(foundpatterns) > 0:
                        foundpattern = foundpatterns[0]
                        patterncodename = foundpattern.name if foundpattern.name else ""
                    product_name = patterncodename + recipe_code_name + "/" + foil_paper_name + "/" + customername
                    vals.update({"name": product_name})
                else:
                    customername = ""
                    customerid = vals["sale_customer"]
                    customerenv = self.env["res.partner"]
                    foundcustomers = customerenv.search([('id', '=',
                                                          customerid)])
                    if len(foundcustomers) > 0:
                        foundcustomer = foundcustomers[0]
                        customername = foundcustomer.name[:
                                                          6] if foundcustomer.name else ""
                    recipe_code_name = ""
                    recipeid = vals["sale_recipe_code"]
                    productenv = self.env["product.product"]
                    foundrecipes = productenv.search([('id', '=', recipeid)])
                    if len(foundrecipes) > 0:
                        foundrecipe = foundrecipes[0]
                        recipe_code_name = foundrecipe.name if foundrecipe.name else ""
                    foil_paper_name = ""
                    foilpaperid = vals["sale_foil_paper"]
                    productenv = self.env["product.product"]
                    foundfoilpapers = productenv.search([('id', '=',
                                                          foilpaperid)])
                    if len(foundfoilpapers) > 0:
                        foundfoilpaper = foundfoilpapers[0]
                        foil_paper_name = foundfoilpaper.name if foundfoilpaper.name else ""
                    patterncodename = ""
                    pattern_code_sub = vals["sale_pattern_code_sub"]
                    patternenv = self.env["unluransfer.models.pattern"]
                    foundpatterns = patternenv.search([('id', '=',
                                                        pattern_code_sub)])
                    if len(foundpatterns) > 0:
                        foundpattern = foundpatterns[0]
                        patterncodename = foundpattern.name if foundpattern.name else ""
                    product_name = patterncodename + recipe_code_name + "/" + foil_paper_name + "/" + customername
                    vals.update({"name": product_name})
            elif vals["production_type"] == u'1':
                if vals["product_type"] == u'2':
                    patterncodename = ""
                    pattern_code_sub = vals["pattern_code_sub"]
                    patternenv = self.env["unluransfer.models.pattern"]
                    foundpatterns = patternenv.search([('id', '=',
                                                        pattern_code_sub)])
                    if len(foundpatterns) > 0:
                        foundpattern = foundpatterns[0]
                        patterncodename = foundpattern.name if foundpattern.name else ""
                    customername = ""
                    customerid = vals["customer"]
                    customerenv = self.env["res.partner"]
                    foundcustomers = customerenv.search([('id', '=',
                                                          customerid)])
                    if len(foundcustomers) > 0:
                        foundcustomer = foundcustomers[0]
                        customername = foundcustomer.name[:
                                                          6] if foundcustomer.name else ""

                    product_name = patterncodename + "/" + customername
                    vals.update({"name": product_name})
                else:
                    patterncodename = ""
                    pattern_code_sub = vals["sale_pattern_code_sub"]
                    patternenv = self.env["unluransfer.models.pattern"]
                    foundpatterns = patternenv.search([('id', '=',
                                                        pattern_code_sub)])
                    if len(foundpatterns) > 0:
                        foundpattern = foundpatterns[0]
                        patterncodename = foundpattern.name if foundpattern.name else ""
                    customername = ""
                    customerid = vals["sale_customer"]
                    customerenv = self.env["res.partner"]
                    foundcustomers = customerenv.search([('id', '=',
                                                          customerid)])
                    if len(foundcustomers) > 0:
                        foundcustomer = foundcustomers[0]
                        customername = foundcustomer.name[:
                                                          6] if foundcustomer.name else ""

                    product_name = patterncodename + "/" + customername
                    vals.update({"name": product_name})
        except Exception as e:
            pass
        if "product_type" in vals:
            if vals["product_type"]:
                if vals["product_type"] == u'2':
                    vals["route_ids"] = [(6, 0, [1, 5])]
                    # Fason Kumaş Üret
                    productenv = self.env["product.product"]
                    main_uom_id = vals["uom_id"]
                    measurement_type = vals["paper_measurement_type"]
                    uom = 0
                    productuom = self.env["product.uom"]
                    if measurement_type == 1:
                        founduoms = productuom.search([('name', '=', 'kg')])
                        if len(founduoms) > 0:
                            uom = founduoms[0]
                    else:
                        founduoms = productuom.search([('name', '=', 'mt')])
                        if len(founduoms) > 0:
                            uom = founduoms[0]

                    foundpartner = self.env["res.partner"].search(
                        [('id', '=', vals["customer"])])

                    kumasdata = {}
                    kumasdata["name"] = "FK" + str(
                        randint(10000, 99999)) + "/" + foundpartner[0].name[:6]
                    kumasdata["fake_material"] = True
                    kumasdata["product_spesification"] = 2
                    kumasdata["route_ids"] = [(6, 0, [1, 6])]
                    kumasdata["categ_id"] = 15
                    kumasdata["tracking"] = "lot"
                    if uom != 0:
                        kumasdata["uom_id"] = uom.id
                        kumasdata["uom_po_id"] = uom.id
                    if "textile_description" in vals:
                        if vals["textile_description"]:
                            kumasdata["default_code"] = vals["textile_description"]
                    kumasdata["paper_measurement_type"] = measurement_type
                    createdtextile = productenv.create(kumasdata)

                    supplierdata = {}
                    supplierdata["delay"] = 0
                    supplierdata["min_qty"] = 0
                    supplierdata["price"] = 0
                    supplierdata["name"] = vals["customer"]
                    supplierdata["producer"] = vals["customer"]
                    supplierdata[
                        "product_tmpl_id"] = createdtextile.product_tmpl_id.id

                    supplierenv = self.env["product.supplierinfo"]
                    supplierenv.create(supplierdata)
                    # Transfer Baskılı Kumaş
                    if "production_type" in vals:
                        if vals["production_type"]:
                            if vals["production_type"] == u'2':
                                # Paper Creation & Lookup
                                founduoms = productuom.search([('name', '=',
                                                                'mt')])
                                uomid = 0
                                if len(founduoms) > 0:
                                    uomid = founduoms[0].id
                                foundpapers = productenv.search(
                                    [('texture_no', '=', vals["texture_no"]),
                                     ('variant_no', '=', vals["variant_no"]),
                                     ('fake_material', '=', True)])
                                if len(foundpapers) == 0:
                                    paperData = {}
                                    if vals["paper_type"] == u'1':
                                        paperData[
                                            "name"] = vals["texture_no"] + "-" + vals["variant_no"]
                                        paperData["texture_no"] = vals[
                                            "texture_no"]
                                        paperData["variant_no"] = vals[
                                            "variant_no"]
                                        paperData["fake_material"] = True
                                        paperData["product_spesification"] = 3
                                        paperData["route_ids"] = [(6, 0,
                                                                   [1, 6])]
                                        paperData["categ_id"] = 15
                                        paperData["tracking"] = "lot"
                                        if uomid != 0:
                                            paperData["uom_id"] = uomid
                                            paperData["uom_po_id"] = uomid
                                    elif vals["paper_type"] == u'2':

                                        if "paper" in vals:
                                            if vals["paper"]:
                                                foundpaperinfos = productenv.search(
                                                    [('id', '=',
                                                      vals["paper"])])
                                                if len(foundpaperinfos) > 0:
                                                    foundpaperinfo = foundpaperinfos[
                                                        0]

                                                    paperData[
                                                        "name"] = vals["texture_no"] + "-" + vals["variant_no"] + "/" + foundpaperinfo.width
                                                    paperData[
                                                        "texture_no"] = vals[
                                                            "texture_no"]
                                                    paperData[
                                                        "variant_no"] = vals[
                                                            "variant_no"]
                                                    paperData[
                                                        "fake_material"] = True
                                                    paperData[
                                                        "product_spesification"] = 3
                                                    paperData["route_ids"] = [
                                                        (6, 0, [1, 5, 6])
                                                    ]
                                                    paperData["categ_id"] = 15
                                                    paperData[
                                                        "tracking"] = "lot"
                                                    if uomid != 0:
                                                        paperData[
                                                            "uom_id"] = uomid
                                                        paperData[
                                                            "uom_po_id"] = uomid
                                    createdpaper = productenv.create(paperData)
                                    if vals["paper_type"] == u'1':
                                        supplierdata = {}
                                        supplierdata["delay"] = 0
                                        supplierdata["min_qty"] = 0
                                        supplierdata["price"] = 0
                                        supplierdata["name"] = vals["supplier"]
                                        supplierdata["producer"] = vals[
                                            "supplier"]
                                        supplierdata[
                                            "product_tmpl_id"] = createdpaper.product_tmpl_id.id

                                        supplierenv.create(supplierdata)

                                    bomenv = self.env["mrp.bom"]
                                    bomlineenv = self.env["mrp.bom.line"]

                                    if vals["paper_type"] == u'2':
                                        paperBom = bomenv.create({
                                            'product_tmpl_id':
                                            createdpaper.product_tmpl_id.id,
                                            "product_qty":
                                            1,
                                            "type":
                                            "normal",
                                            "product_uom_id":
                                            createdpaper.uom_id.id
                                        })
                                        bomlineenv.create({
                                            "product_id":
                                            foundpaperinfo.id,
                                            "product_qty":
                                            1,
                                            "bom_id":
                                            paperBom.id,
                                            "product_uom_id":
                                            foundpaperinfo.uom_id.id
                                        })

                                        # Search For Default Material
                                        founddyes = productenv.search(
                                            [('standart_material_for_paper',
                                              '=', True),
                                             ('product_spesification', '=',
                                              1)])

                                        for dye in founddyes:
                                            bomlineenv.create({
                                                "product_id":
                                                dye.id,
                                                "product_qty":
                                                2.25,
                                                "bom_id":
                                                paperBom.id
                                            })

                                else:
                                    createdpaper = foundpapers[0]
                            elif vals["production_type"] == u'3':
                                foundpapers = productenv.search(
                                    [('id', '=', int(vals["foil_paper"]))])
                                createdpaper = foundpapers[0]
                if vals["product_type"] == u'1':
                    vals["route_ids"] = [(6, 0, [1, 5])]
                    # Fason Kumaş Üretme
                    productenv = self.env["product.product"]
                    main_uom_id = vals["uom_id"]
                    uom = 0
                    productuom = self.env["product.uom"]

                    foundpartner = self.env["res.partner"].search(
                        [('id', '=', vals["sale_customer"])])
                    # Transfer Baskılı Kumaş
                    if "sale_production_type" in vals:
                        if vals["sale_production_type"]:
                            if vals["sale_production_type"] == u'2':
                                # Paper Creation & Lookup
                                founduoms = productuom.search([('name', '=',
                                                                'mt')])
                                uomid = 0
                                if len(founduoms) > 0:
                                    uomid = founduoms[0].id
                                foundpapers = productenv.search(
                                    [('texture_no', '=',
                                      vals["sale_texture_no"]),
                                     ('variant_no', '=',
                                      vals["sale_texture_no"]),
                                     ('fake_material', '=', True)])
                                sale_papers = productenv.search(
                                    [('sale_texture_no', '=',
                                      vals["sale_texture_no"]),
                                     ('sale_variant_no', '=',
                                      vals["sale_variant_no"]),
                                     ('fake_material', '=', True)])
                                if len(foundpapers) == 0 and len(
                                        sale_papers) == 0:
                                    paperData = {}
                                    if vals["sale_paper_type"] == u'1':
                                        paperData[
                                            "name"] = vals["sale_texture_no"] + "-" + vals["sale_variant_no"]
                                        paperData["sale_texture_no"] = vals[
                                            "sale_texture_no"]
                                        paperData["sale_variant_no"] = vals[
                                            "sale_variant_no"]
                                        paperData["fake_material"] = True
                                        paperData["product_spesification"] = 3
                                        paperData["route_ids"] = [(6, 0,
                                                                   [1, 6])]
                                        paperData["categ_id"] = 15
                                        paperData["tracking"] = "lot"
                                        if uomid != 0:
                                            paperData["uom_id"] = uomid
                                            paperData["uom_po_id"] = uomid
                                    elif vals["sale_paper_type"] == u'2':

                                        if "sale_paper" in vals:
                                            if vals["sale_paper"]:
                                                foundpaperinfos = productenv.search(
                                                    [('id', '=',
                                                      vals["sale_paper"])])
                                                if len(foundpaperinfos) > 0:
                                                    foundpaperinfo = foundpaperinfos[
                                                        0]

                                                    paperData[
                                                        "name"] = vals["sale_texture_no"] + "-" + vals["sale_variant_no"] + "/" + foundpaperinfo.width
                                                    paperData[
                                                        "sale_texture_no"] = vals[
                                                            "sale_texture_no"]
                                                    paperData[
                                                        "sale_variant_no"] = vals[
                                                            "sale_variant_no"]
                                                    paperData[
                                                        "fake_material"] = True
                                                    paperData[
                                                        "product_spesification"] = 3
                                                    paperData["route_ids"] = [
                                                        (6, 0, [1, 5, 6])
                                                    ]
                                                    paperData["categ_id"] = 15
                                                    paperData[
                                                        "tracking"] = "lot"
                                                    if uomid != 0:
                                                        paperData[
                                                            "uom_id"] = uomid
                                                        paperData[
                                                            "uom_po_id"] = uomid
                                    createdpaper = productenv.create(paperData)
                                    if vals["sale_paper_type"] == u'1':
                                        supplierdata = {}
                                        supplierdata["delay"] = 0
                                        supplierdata["min_qty"] = 0
                                        supplierdata["price"] = 0
                                        supplierdata["name"] = vals[
                                            "sale_supplier"]
                                        supplierdata["producer"] = vals[
                                            "supplier"]
                                        supplierdata[
                                            "product_tmpl_id"] = createdpaper.product_tmpl_id.id

                                        supplierenv.create(supplierdata)

                                    bomenv = self.env["mrp.bom"]
                                    bomlineenv = self.env["mrp.bom.line"]

                                    if vals["sale_paper_type"] == u'2':
                                        paperBom = bomenv.create({
                                            'product_tmpl_id':
                                            createdpaper.product_tmpl_id.id,
                                            "product_qty":
                                            1,
                                            "type":
                                            "normal",
                                            "product_uom_id":
                                            createdpaper.uom_id.id
                                        })
                                        bomlineenv.create({
                                            "product_id":
                                            foundpaperinfo.id,
                                            "product_qty":
                                            1,
                                            "bom_id":
                                            paperBom.id,
                                            "product_uom_id":
                                            foundpaperinfo.uom_id.id
                                        })

                                        # Search For Default Material
                                        founddyes = productenv.search(
                                            [('standart_material_for_paper',
                                              '=', True),
                                             ('product_spesification', '=',
                                              1)])

                                        for dye in founddyes:
                                            bomlineenv.create({
                                                "product_id":
                                                dye.id,
                                                "product_qty":
                                                2.25,
                                                "bom_id":
                                                paperBom.id
                                            })

                                else:
                                    createdpaper = foundpapers[0]
                            elif vals["sale_production_type"] == u'3':
                                foundpapers = None
                                foundpapers = productenv.search(
                                    [('id', '=', int(vals["foil_paper"]))])
                                foundpapers_sale = productenv.search(
                                    [('id', '=',
                                      int(vals["sale_foil_paper"]))])
                                if foundpapers > 0:
                                    createdpaper = foundpapers[0]
                                elif foundpapers_sale:
                                    createdpaper = foundpapers[0]
        createdmainProduct = super(ProductTemplate, self).create(vals)

        if "product_type" in vals:
            if vals["product_type"]:
                if vals["product_type"] == u'2':
                    # Create BOM
                    bomenv = self.env["mrp.bom"]
                    createdBOM = bomenv.create({
                        'product_tmpl_id':
                        createdmainProduct.id,
                        "product_qty":
                        1,
                        "type":
                        "normal",
                        "product_uom_id":
                        createdmainProduct.uom_id.id
                    })

                    # Create BOM Lines
                    bomlineenv = self.env["mrp.bom.line"]
                    if vals["production_type"] != u'1':
                        bomlineenv.create({
                            "product_id":
                            createdpaper.id,
                            "product_qty":
                            1,
                            "bom_id":
                            createdBOM.id,
                            "product_uom_id":
                            createdpaper.uom_id.id
                        })
                    bomlineenv.create({
                        "product_id":
                        createdtextile.id,
                        "product_qty":
                        1,
                        "bom_id":
                        createdBOM.id,
                        "product_uom_id":
                        createdtextile.uom_id.id
                    })

                    if "recipe_code" in vals:
                        if vals["recipe_code"]:
                            recipe_code = vals["recipe_code"]
                            recipes = productenv.search([('id', '=',
                                                          recipe_code)])
                            recipe = recipes[0]
                            bomlineenv.create({
                                "product_id": recipe.id,
                                "product_qty": 1,
                                "bom_id": createdBOM.id
                            })
                if vals["product_type"] == u'1':
                    # Create BOM
                    bomenv = self.env["mrp.bom"]
                    createdBOM = bomenv.create({
                        'product_tmpl_id':
                        createdmainProduct.id,
                        "product_qty":
                        1,
                        "type":
                        "normal",
                        "product_uom_id":
                        createdmainProduct.uom_id.id
                    })

                    # Create BOM Lines
                    bomlineenv = self.env["mrp.bom.line"]
                    if vals["sale_production_type"] != u'1':
                        bomlineenv.create({
                            "product_id":
                            createdpaper.id,
                            "product_qty":
                            1,
                            "bom_id":
                            createdBOM.id,
                            "product_uom_id":
                            createdpaper.uom_id.id
                        })

                    # Selected Textile
                    if "textile" in vals:
                        if vals["textile"]:
                            textileid = vals["textile"]
                            textiles = productenv.search(
                                [('id', '=', textileid)], limit=1)

                            if len(textiles) > 0:
                                selected_textile = textiles[0]
                                bomlineenv.create({
                                    "product_id":
                                    selected_textile.id,
                                    "product_qty":
                                    1,
                                    "bom_id":
                                    createdBOM.id,
                                    "product_uom_id":
                                    selected_textile.uom_id.id
                                })

                    if "sale_recipe_code" in vals:
                        if vals["sale_recipe_code"]:
                            recipe_code = vals["sale_recipe_code"]
                            recipes = productenv.search([('id', '=',
                                                          recipe_code)])
                            recipe = recipes[0]
                            bomlineenv.create({
                                "product_id": recipe.id,
                                "product_qty": 1,
                                "bom_id": createdBOM.id
                            })
        return createdmainProduct

    @api.multi
    def write(self, vals):
        # TODO: REFACTOR BOMS :(((
        return super(ProductTemplate, self).write(vals)


class Product(models.Model):
    _inherit = "product.product"

    @api.onchange('paper_type', 'variant_no', 'texture_no', 'customer',
                  'paper', 'foil_paper', 'recipe_code', 'pattern_code_sub')
    def check_change(self):
        if self.production_type == u'2':
            if self.paper_type:
                if self.paper_type == u'1':
                    self.name = (self.texture_no or '') + '-' + (
                        self.variant_no or '') + ("/" + self.customer.name
                                                  if self.customer else '/')
                else:
                    self.name = (self.texture_no or '') + '-' + (
                        self.variant_no or '') + (
                            ("/" + self.paper.width
                             if self.paper.width else '/[PAPER WIDTH]') if
                            self.paper else '') + ("/" + self.customer.name[:6]
                                                   if self.customer else '/')
        elif self.production_type == u'3':
            self.name = (self.pattern_code_sub.name if self.pattern_code_sub
                         else '') + (self.recipe_code.name
                                     if self.recipe_code else '') + "/" + (
                                         self.foil_paper.name
                                         if self.foil_paper else
                                         '') + "/" + (self.customer.name[:6]
                                                      if self.customer else '')
        elif self.production_type == u'1':
            self.name = (self.pattern_code_sub.name if self.pattern_code_sub
                         else '') + "/" + (self.customer.name[:6]
                                           if self.customer else '')


class PaperType(models.Model):
    _name = "unlutransfer.models.paper"
    _description = u"Kağıt Tipi"

    name = fields.Char(string=u"Kağıt Adı")
    width = fields.Char(string=u"Kağıt Eni")


class Pattern(models.Model):
    _name = "unluransfer.models.pattern"

    name = fields.Char(string="Kalıp Adı", required=True)

    production_type = fields.Selection(
        selection=[('1', u'Gofre'), ('3', u'Varak')],
        string=u"Üretim Tipi",
        required=True)

    production_date = fields.Date(string="Kalıp Üretim Tarihi")
    supplier = fields.Many2one(
        'res.partner',
        string="Kalıp Üreticisi",
        domain=[('is_company', '=', True)])
    width = fields.Float(string="Kalıp Eni")
    depth = fields.Float(string="Kalıp Derinliği")
    perimiter = fields.Float(string="Kalıp Çevresi")
    weight = fields.Float(string="Kalıp Ağırlığı")
    attachment_ids = fields.Many2many('ir.attachment',
                                      'patterns_attachments_rel', 'pattern_id',
                                      'attachment_id', u'Fotoğraflar')
    revision_date = fields.Date(string="Revizyon Tarihi")
    revision_comment = fields.Text(string="Revizyon Açıklaması")


class StockPackOperation(models.Model):
    _inherit = "stock.pack.operation"

    calculate = fields.Boolean(string="Hesapla")

    width = fields.Float(string="En")
    weight = fields.Float(string="Gramaj")
    gross_weight = fields.Float(string="Net Ağırlık")

    @api.onchange('width', 'weight', 'gross_weight')
    def calculate_qty_done(self):
        if self.width != 0 and self.weight != 0 and self.gross_weight != 0:
            a = 1000 * self.gross_weight
            qty_done = (a / (self.width * self.weight)) * 100
            self.qty_done = qty_done


class PackOperationLot(models.Model):
    _inherit = "stock.pack.operation.lot"

    roll_count = fields.Integer(string="Top")

    @api.model
    def create(self, vals):
        createdlot = super(PackOperationLot, self).create(vals)
        if "roll_count" in vals:
            if vals["roll_count"]:
                roll_count = vals["roll_count"]

                if createdlot.operation_id:
                    operation = createdlot.operation_id
                    if operation.product_id:
                        product = operation.product_id
                        productroll_count = product.roll_count
                        newcount = productroll_count + roll_count
                        productvals = {"roll_count": newcount}
                        product.write(productvals)

        return createdlot

    @api.multi
    def write(self, vals):
        if "roll_count" in vals:
            if vals["roll_count"]:
                roll_count = vals["roll_count"]
                for record in self:
                    if record.operation_id:
                        operation = record.operation_id
                        if operation.product_id:
                            product = operation.product_id
                            counttoadd = roll_count - record.roll_count
                            productroll_count = product.roll_count
                            newcount = productroll_count + counttoadd
                            productvals = {"roll_count": newcount}
                            product.write(productvals)

        return super(PackOperationLot, self).write(vals)

    @api.multi
    def unlink(self):
        # Decrease roll_count before unlink
        for record in self:
            if record.roll_count:
                if record.operation_id:
                    operation = record.operation_id
                    if operation.product_id:
                        product = operation.product_id
                        roll_count = record.roll_count
                        productroll_count = product.roll_count
                        newcount = productroll_count - roll_count
                        productvals = {"roll_count": newcount}
                        product.write(productvals)
        return super(PackOperationLot, self).unlink()


class StockHistory(models.Model):
    _inherit = "stock.history"

    roll_count = fields.Integer(string="Top")

    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self._cr, 'stock_history')
        self._cr.execute("""
            CREATE VIEW stock_history AS (
              SELECT MIN(id) as id,
                move_id,
                location_id,
                company_id,
                product_id,
                product_categ_id,
                product_template_id,
                SUM(quantity) as quantity,
                date,
                COALESCE(SUM(price_unit_on_quant * quantity) / NULLIF(SUM(quantity), 0), 0) as price_unit_on_quant,
                source,
                string_agg(DISTINCT serial_number, ', ' ORDER BY serial_number) AS serial_number,
                roll_count
                FROM
                ((SELECT
                    stock_move.id AS id,
                    stock_move.id AS move_id,
                    dest_location.id AS location_id,
                    dest_location.company_id AS company_id,
                    stock_move.product_id AS product_id,
                    product_template.id AS product_template_id,
                    product_template.categ_id AS product_categ_id,
                    quant.qty AS quantity,
                    stock_move.date AS date,
                    quant.cost as price_unit_on_quant,
                    stock_move.origin AS source,
                    stock_production_lot.name AS serial_number,
                    product_template.roll_count AS roll_count
                FROM
                    stock_quant as quant
                JOIN
                    stock_quant_move_rel ON stock_quant_move_rel.quant_id = quant.id
                JOIN
                    stock_move ON stock_move.id = stock_quant_move_rel.move_id
                LEFT JOIN
                    stock_production_lot ON stock_production_lot.id = quant.lot_id
                JOIN
                    stock_location dest_location ON stock_move.location_dest_id = dest_location.id
                JOIN
                    stock_location source_location ON stock_move.location_id = source_location.id
                JOIN
                    product_product ON product_product.id = stock_move.product_id
                JOIN
                    product_template ON product_template.id = product_product.product_tmpl_id
                WHERE quant.qty>0 AND stock_move.state = 'done' AND dest_location.usage in ('internal', 'transit')
                AND (
                    not (source_location.company_id is null and dest_location.company_id is null) or
                    source_location.company_id != dest_location.company_id or
                    source_location.usage not in ('internal', 'transit'))
                ) UNION ALL
                (SELECT
                    (-1) * stock_move.id AS id,
                    stock_move.id AS move_id,
                    source_location.id AS location_id,
                    source_location.company_id AS company_id,
                    stock_move.product_id AS product_id,
                    product_template.id AS product_template_id,
                    product_template.categ_id AS product_categ_id,
                    - quant.qty AS quantity,
                    stock_move.date AS date,
                    quant.cost as price_unit_on_quant,
                    stock_move.origin AS source,
                    stock_production_lot.name AS serial_number,
                    product_template.roll_count AS roll_count
                FROM
                    stock_quant as quant
                JOIN
                    stock_quant_move_rel ON stock_quant_move_rel.quant_id = quant.id
                JOIN
                    stock_move ON stock_move.id = stock_quant_move_rel.move_id
                LEFT JOIN
                    stock_production_lot ON stock_production_lot.id = quant.lot_id
                JOIN
                    stock_location source_location ON stock_move.location_id = source_location.id
                JOIN
                    stock_location dest_location ON stock_move.location_dest_id = dest_location.id
                JOIN
                    product_product ON product_product.id = stock_move.product_id
                JOIN
                    product_template ON product_template.id = product_product.product_tmpl_id
                WHERE quant.qty>0 AND stock_move.state = 'done' AND source_location.usage in ('internal', 'transit')
                AND (
                    not (dest_location.company_id is null and source_location.company_id is null) or
                    dest_location.company_id != source_location.company_id or
                    dest_location.usage not in ('internal', 'transit'))
                ))
                AS foo
                GROUP BY move_id, location_id, company_id, product_id, product_categ_id, date, source, product_template_id, roll_count
            )""")
