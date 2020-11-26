 # -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request,content_disposition


class ReportController(http.Controller):
    @http.route(['/web/download/course-exam-report'], type='http', auth="user")
    def print_report(self, id,**kw):
        exam = request.env['faculty.course_exam'].sudo().search([('id', '=', id)], limit=1)
        pdf, _ = request.env.ref('faculty.report_course_exam').sudo().render_qweb_pdf([id])
        pdfhttpheaders = [('Content-Type', 'application/pdf'),
                          ('Content-Length', len(pdf)),
                          #('Content-Disposition', 'attachment; filename="report.pdf"'),]
                          ('Content-Disposition', content_disposition('%s - Examen.PDF' % (exam.course_id.name)))]
        return request.make_response(pdf, headers=pdfhttpheaders)





