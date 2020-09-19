# -*- coding: utf-8 -*-
{
    'name': "Print Badge",
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','hr'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/template.xml',
        'views/print_badge.xml',
        'report/paper_format.xml'
    ],
   
}
