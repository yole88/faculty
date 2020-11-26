# -*- coding: utf-8 -*-
{
    'name': 'Faculty',
    'version': '12.5',
    'description': ''' Faculty
    ''',
    'category': 'Faculty',
    'author': 'IT Admin',
    'website': '',
    'depends': [
        'base'
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/faculty_view.xml',
        'wizards/faculty_inscription.xml',
        'reports/report_definition.xml',
        'reports/report_course_exam.xml',
    ],
    'application': True,
}
