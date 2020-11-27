# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class FacultyCourse(models.Model):
    _name = 'faculty.course'
    _description = 'Faculty Course'

    name = fields.Char('Name', required=True)
    description = fields.Text('Description')
    credit = fields.Integer('Credits')
    professor_id = fields.Many2one('faculty.professor', 'Professor', required=True)
    student_line_ids = fields.One2many('faculty.course.line', 'course_id', string='Students')
    user_id = fields.Many2one(related='professor_id.user_id', string='Users', store=True)
    student_count = fields.Integer(compute='_compute_students_count', string="Students Count")
    state = fields.Selection([('draft', 'Draft'), ('close', 'Close')], string="State", default='draft')

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

    def set_close(self):
        for course in self:
            course.write({'state': 'close'})


class CourseLine(models.Model):
    _name = 'faculty.course.line'
    _description = 'Course Line'

    student_id = fields.Many2one('faculty.students', 'Students')
    course_id = fields.Many2one('faculty.course', 'Course')
    professor_id = fields.Many2one('faculty.professor', 'Professor')

    def unlink(self):
        for line in self:
            student = self.env['faculty.students'].search([('id', '=', line.student_id.id)])
            value = student.credit + line.course_id.credit
            student.write({'credit': value})
        return super(CourseLine, self).unlink()


class FacultyStudents(models.Model):
    _name = 'faculty.students'
    _description = 'Faculty Students'

    name = fields.Char('Name', required=True)
    credit = fields.Integer('Credits')
    login = fields.Char('Email', required=True)
    user_id = fields.Many2one('res.users', 'Users', readonly=True)
    course_count = fields.Integer(compute='_compute_course_count', string="Students Count")

    def _compute_course_count(self):
        for record in self:
            record.course_count = self.env['faculty.course.line'].search_count(
                [('student_id', '=', self.id)])

    @api.model
    def create(self, values):
        res = super(FacultyStudents, self).create(values)
        group_user = self.env.ref('faculty.faculty_student')
        user = self.env["res.users"].sudo()
        obj = user.create({'name': values['name'],
                           'login': values['login'],
                        })
        obj.write({'groups_id': [(4, group_user.id)]})
        
        res.user_id = obj.id
        return res

    def write(self, vals):
        res = super(FacultyStudents, self).write(vals)
        if 'name' in vals or 'login' in vals:
            user = self.env["res.users"].sudo().search([('id', '=', self.user_id.id)])
            user.write({'name': self.name,
                        'login': self.login,
                       })
        return res

    def unlink(self):
        for line in self:
            user = self.env["res.users"].sudo().search([('id', '=', line.user_id.id)])
            for record in user:
                record.unlink()
        return super(FacultyStudents, self).unlink()

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
    login = fields.Char('Email', required=True)
    user_id = fields.Many2one('res.users', 'Users', readonly=True)
    course_count = fields.Integer(compute='_compute_course_count', string="Students Count")

    @api.model
    def create(self, values):
        res = super(FacultyProfessor, self).create(values)
        group_user = self.env.ref('faculty.faculty_professor')
        user = self.env["res.users"].sudo()
        obj = user.create({'name': values['name'],
                           'login': values['login'],
                        })
        obj.write({'groups_id': [(4, group_user.id)]})
        res.user_id = obj.id

        return res

    def write(self, vals):
        res = super(FacultyProfessor, self).write(vals)
        if 'name' in vals or 'login' in vals:
            user = self.env["res.users"].sudo().search([('id', '=', self.user_id.id)])
            user.write({'name': self.name,
                        'login': self.login,
                       })
        return res

    def unlink(self):
        for line in self:
            user = self.env["res.users"].sudo().search([('id', '=', line.user_id.id)])
            for record in user:
                record.unlink()
        return super(FacultyProfessor, self).unlink()

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
    note_ids = fields.One2many('faculty.exam_note', 'exam_id', string='Note')
    note_count = fields.Integer(compute='_compute_note_count', string="Count note")

    @api.model
    def create(self, values):
        res = super(CourseExam, self).create(values)
        note = self.env["faculty.exam_note"]
        course = self.env["faculty.course.line"].search([('course_id', '=', values['course_id'])])
        for c in course:
            note.create({'student_id': c.student_id.id,
                        'exam_id': res.id})
        return res

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

    def _compute_note_count(self):
        self.note_count = len(self.note_ids)

    def get_note(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Notes',
            'view_mode': 'tree',
            'res_model': 'faculty.exam_note',
            'domain': [('exam_id', '=', self.id)],
        }


class ExamQuestion(models.Model):
    _name = 'faculty.exam.question'
    _description = 'Exam Question'

    name = fields.Text('Name', required=True)
    exam_id = fields.Many2one('faculty.course_exam', 'Exam')


class ExamNote(models.Model):
    _name = 'faculty.exam_note'
    _description = 'Exam Note'

    student_id = fields.Many2one('faculty.students', 'Student', readonly=True)
    exam_id = fields.Many2one('faculty.course_exam', 'Exam')
    value_note = fields.Float('Note')











