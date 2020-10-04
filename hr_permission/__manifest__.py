{
    "name" : "Permission Requests",
    "version" : "1.0",
    "category" : "hr",
    "depends" : ["base","hr","hr_holidays"],
    "data" : [
        'data/mail_template.xml',
        'security/ir.model.access.csv',
        'view/permission_requests.xml',
        'view/leave_return.xml',
        'data/sequence.xml',
    ],
    "installable": True
}
