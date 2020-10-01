# -*- coding: utf-8 -*-
{
    'name': "General Request",
    'author': "M.shorbagy",
    'version': '0.1',
    'depends': ['base','hr','website', 'portal','website_forum'],
    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/general_request.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
