# -*- coding: utf-8 -*-
{
    'name': "Ünlü Transfer",

    'summary': """Ünlü Transfer Uygulama Paketi""",

    'description': """
        Ünlü Transfer için yapılan modifikasyonları içeren paket.
    """,

    'author': "Mechsoft",
    'website': "http://www.mechsoft.com.tr",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'MRP',
    'version': '1.2',

    # any module necessary for this one to work correctly
    'depends': ['base', 'stock', 'sale', 'document', 'product', 'mrp'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    'installable': True,
}
