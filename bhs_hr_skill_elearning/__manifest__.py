# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'HR Skill eLearning',
    'author': 'Bac Ha Software',
    'website': 'https://bachasoftware.com',
    'maintainer': 'Bac Ha Software',
    'version': '1.0',
    'category': 'Website',
    'sequence': 101,
    'summary': 'HR Skill eLearning',
    'description': """
        A product of Bac Ha Software allows to record online courses that 
        each employee has/is taking in employee information.
    """,
    'images': [],
    'depends': ['website_slides', 'hr_skills_slides'],
    'assets': {
        'web.assets_qweb': [
            'bhs_hr_skill_elearning/static/src/xml/resume_templates.xml',
        ],
    },
    'data': [
        'views/hr_view.xml',
    ],
    'demo': [],
    "external_dependencies": {},
    'images': ['static/description/banner.gif'],
    'installable': True,
    'application': True,
    'auto_install': False,
    'qweb': [],
    'license': 'LGPL-3'
}
