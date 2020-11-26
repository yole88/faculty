# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class FacultyInscription(models.TransientModel):
    _name = "faculty.inscription_wizard"
    _description = 'Faculty Inscription'

    course_id = fields.Many2one('faculty.course', string="Course", required=True)
    student_id = fields.Many2one('faculty.students', string="Student", required=True)

    def create_course(self):
        obj = self.env['faculty.students'].search([('id', '=', self.student_id.id)])
        line = self.env['faculty.course.line']
        student = self.env['faculty.course.line'].search([('student_id', '=', self.student_id.id),
                                                          ('course_id', '=', self.course_id.id)])
        if not student:
            line.create({'course_id': self.course_id.id,
                         'student_id': self.student_id.id,
                         'professor_id': self.course_id.professor_id.id})
            if obj:
                value = obj.credit - self.course_id.credit
                obj.write({'credit': value})
        else:
            raise UserError(
                _(
                    'No Health Professional associated to this user!'
                ))



