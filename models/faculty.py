# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
import base64



class FacultyCourse(models.Model):
    _name = 'faculty.course'
    _description = 'Faculty Course'

    name = fields.Char('Name', required=True)
    description = fields.Text('Description')
    credit = fields.Integer('Credits')
    professor_id = fields.Many2one('faculty.professor', 'Professor', required=True)
    student_line_ids = fields.One2many('faculty.course.line', 'course_id', string='Students')
    user_id = fields.Many2one('res.users', 'Users')
    student_count = fields.Integer(compute='_compute_students_count', string="Students Count")

    @api.onchange('professor_id')
    def _onchange_user(self):
        if self.professor_id.user_id:
            self.user_id = self.professor_id.user_id

    def _compute_students_count(self):
        student_data = self.env['faculty.course.line'].read_group([('course_id', 'in', self.ids)], ['course_id'],
                                                                  ['course_id'])
        result = dict((data['course_id'][0], data['course_id_count']) for data in student_data)
        for student in self:
            student.student_count = result.get(student.id, 0)


class CourseLine(models.Model):
    _name = 'faculty.course.line'
    _description = 'Course Line'

    student_id = fields.Many2one('faculty.students', 'Students')
    course_id = fields.Many2one('faculty.course', 'Course')
    professor_id = fields.Many2one('faculty.professor', 'Professor')


class FacultyStudents(models.Model):
    _name = 'faculty.students'
    _description = 'Faculty Students'

    name = fields.Char('Name', required=True)
    credit = fields.Integer('Credits')
    course_count = fields.Integer(compute='_compute_course_count', string="Students Count")

    def _compute_course_count(self):
        for record in self:
            record.course_count = self.env['faculty.course.line'].search_count(
                [('student_id', '=', self.id)])

    def get_courses(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Courses',
            'view_mode': 'tree',
            'view_id': self.env.ref('faculty.view_faculty_course_line_action').id,
            'res_model': 'faculty.course.line',
            'domain': [('student_id', '=', self.id)],
            'context': "{'create': False}"
        }


class FacultyProfessor(models.Model):
    _name = 'faculty.professor'
    _description = 'Faculty Professor'

    name = fields.Char('Name', required=True)
    user_id = fields.Many2one('res.users', 'Users', required=True)

    course_count = fields.Integer(compute='_compute_course_count', string="Students Count")

    def _compute_course_count(self):
        for record in self:
            record.course_count = self.env['faculty.course'].search_count(
                [('professor_id', '=', self.id)])

    def get_courses(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Courses',
            'view_mode': 'tree',
            'res_model': 'faculty.course',
            'domain': [('professor_id', '=', self.id)],
            'context': "{'create': False}"
        }


class CourseExam(models.Model):
    _name = 'faculty.course_exam'
    _description = 'Course exam'
    _rec_name = 'course_id'

    course_id = fields.Many2one('faculty.course', string="Course", required=True)
    date = fields.Datetime(string="Date")
    question_ids = fields.One2many('faculty.exam.question', 'exam_id', string='Question')
    doc_count = fields.Integer(compute='_compute_attached_docs_count', string="Number of documents attached")

    def button_download_exam(self):
        if not self.id:
            return
        return {
                'type': 'ir.actions.act_url',
                'url': '/web/download/course-exam-report?id=%s' % (self.id),
                'target': 'self',
                }

    def print_report(self):
        return self.env.ref('faculty.report_course_exam').report_action(self.id)

    def _compute_attached_docs_count(self):
        Attachment = self.env['ir.attachment']
        for exam in self:
            exam.doc_count = Attachment.search_count([
                '&',
                ('res_model', '=', 'faculty.course_exam'), ('res_id', '=', exam.id)
            ])

    def attachment_documents(self):
        attachment_action = self.env.ref('base.action_attachment')
        action = attachment_action.read()[0]
        action['domain'] = str([
            '&',
            ('res_model', '=', 'faculty.course_exam'),
            ('res_id', 'in', self.ids)
        ])
        action['context'] = "{'default_res_model': '%s','default_res_id': %d}" % (self._name, self.id)
        return action


class ExamQuestion(models.Model):
    _name = 'faculty.exam.question'
    _description = 'Exam Question'

    name = fields.Text('Name', required=True)
    exam_id = fields.Many2one('faculty.course_exam', 'Exam')








