# -*- coding: utf-8 -*-
{
    'name' : 'hr employee info',
    'version' : '1.0',
    'sequence': 1,
    'depends' : ['hr','hr_contract','base'],
    'data': [
        'security/ir.model.access.csv',
        'views/hr_employee_info.xml',
        'views/contract.xml',
    ],
    'installable': True,
}