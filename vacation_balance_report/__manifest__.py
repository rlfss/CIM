# -*- coding: utf-8 -*-
{
    'name': "Vacation Balance Report",

    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','hr','hr_contract','report_xlsx','hr_holidays'],

    # always loaded
    'data': [
        #'security/ir.model.access.csv',
        #'views/views.xml',
        'wizards/vacation_balance.xml',
        'reports/report.xml'
        
    ],
    
}
