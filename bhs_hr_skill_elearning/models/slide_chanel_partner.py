# -*- coding: utf-8 -*-
from odoo import models, fields, api,_
from odoo.tools import html2plaintext

class ResumeLine(models.Model):
    _inherit = 'hr.resume.line'

    # Trạng thái
    completed = fields.Boolean(string="Completed", default=True)

class SlideChannelPartnerInherit(models.Model):

    _inherit = 'slide.channel.partner'

    def _recompute_completion(self):
        # NOTE: KHI KẾ THỪA HÀM NÀY CẦN COPY LẠI GHI ĐÈ CẢ HÀM NÀY
        # CODE BASE WEBSITE SLIDE:website_slides/slide_channel.py
        """ This method computes the completion and member_status of attendees that are neither
            'invited' nor 'completed'. Indeed, once completed, membership should remain so.
            We do not do any update on the 'invited' records.
            One should first set member_status to 'joined' before recomputing those values
            when enrolling an invited or archived attendee.
            It takes into account the previous completion value to add or remove karma for
            completing the course to the attendee (see _post_completion_update_hook)
        """
        read_group_res = self.env['slide.slide.partner'].sudo()._read_group(
            ['&', '&', ('channel_id', 'in', self.mapped('channel_id').ids),
             ('partner_id', 'in', self.mapped('partner_id').ids),
             ('completed', '=', True),
             ('slide_id.is_published', '=', True),
             ('slide_id.active', '=', True)],
            ['channel_id', 'partner_id'],
            aggregates=['__count'])
        mapped_data = {
            (channel.id, partner.id): count
            for channel, partner, count in read_group_res
        }

        completed_records = self.env['slide.channel.partner']
        uncompleted_records = self.env['slide.channel.partner']
        for record in self:
            if record.member_status in ('completed', 'invited'):
                continue

            # GHI NHẬN RESUME LINE
            employee_id = self.env['hr.employee'].sudo().search(
                [('user_id.partner_id', '=', record.partner_id.id)])
            for emp in employee_id:
                # Nếu chưa ghi nhận thì tạo
                check_resume_data = self.env['hr.resume.line'].search(
                    [('employee_id', '=', emp.id), ('channel_id', '=', record.channel_id.id)])
                if not check_resume_data:
                    line_type = self.env.ref('hr_skills_slides.resume_type_training', raise_if_not_found=False)
                    self.env['hr.resume.line'].create({
                        'employee_id': emp and emp.id,
                        'name': _('Studying course: %s') % record.channel_id.name,
                        'date_start': fields.Date.today(),
                        'description': html2plaintext(record.channel_id.description),
                        'line_type_id': line_type and line_type.id,
                        'display_type': 'course',
                        'channel_id': record.channel_id.id,
                        'completed': False
                    })

            was_finished = record.completion == 100
            record.completed_slides_count = mapped_data.get((record.channel_id.id, record.partner_id.id), 0)
            record.completion = round(100.0 * record.completed_slides_count / (record.channel_id.total_slides or 1))

            if not record.channel_id.active:
                continue
            elif not was_finished and record.completed_slides_count >= record.channel_id.total_slides:
                completed_records += record
            elif was_finished and record.completed_slides_count < record.channel_id.total_slides:
                uncompleted_records += record

            if record.completion == 100:
                record.member_status = 'completed'
            elif record.completion == 0:
                record.member_status = 'joined'
            else:
                record.member_status = 'ongoing'

        if completed_records:
            # CODE GHI NHẬN HOÀN THÀNH KHÓA HỌC:
            for completed_data in completed_records:
                employee_completed_id = self.env['hr.employee'].sudo().search(
                    [('user_id.partner_id', '=', completed_data.partner_id.id)])
                resume_data = self.env['hr.resume.line'].search([('employee_id', 'in', employee_completed_id.ids),
                                                                 ('channel_id', '=', completed_data.channel_id.id),
                                                                 ('completed', '!=', True)])
                resume_data.write({'name': _('Completed course: %s') % completed_data.channel_id.name,
                                   'date_end': fields.Date.today(), 'completed': True})

            completed_records._post_completion_update_hook(completed=True)
            completed_records._send_completed_mail()

        if uncompleted_records:
            uncompleted_records._post_completion_update_hook(completed=False)

    # def _recompute_completion(self):
    #     # NOTE: KHI KẾ THỪA HÀM NÀY CẦN COPY LẠI GHI ĐÈ CẢ HÀM NÀY
    #     # CODE BASE WEBSITE SLIDE:website_slides/slide_channel.py
    #     read_group_res = self.env['slide.slide.partner'].sudo().read_group(
    #         ['&', '&', ('channel_id', 'in', self.mapped('channel_id').ids),
    #          ('partner_id', 'in', self.mapped('partner_id').ids),
    #          ('completed', '=', True),
    #          ('slide_id.is_published', '=', True),
    #          ('slide_id.active', '=', True)],
    #         ['channel_id', 'partner_id'],
    #         groupby=['channel_id', 'partner_id'], lazy=False)
    #     mapped_data = dict()
    #     for item in read_group_res:
    #         mapped_data.setdefault(item['channel_id'][0], dict())
    #         mapped_data[item['channel_id'][0]][item['partner_id'][0]] = item['__count']
    #
    #     completed_records = self.env['slide.channel.partner']
    #     for record in self:
    #         # GHI NHẬN RESUME LINE
    #         employee_id = self.env['hr.employee'].sudo().search(
    #             [('user_id.partner_id', '=', record.partner_id.id)])
    #         for emp in employee_id:
    #             # Nếu chưa ghi nhận thì tạo
    #             check_resume_data = self.env['hr.resume.line'].search([('employee_id', '=', emp.id), ('channel_id', '=', record.channel_id.id)])
    #             if not check_resume_data:
    #                 line_type = self.env.ref('hr_skills_slides.resume_type_training', raise_if_not_found=False)
    #                 self.env['hr.resume.line'].create({
    #                     'employee_id': emp and emp.id,
    #                     'name': _('Studying course: %s') % record.channel_id.name,
    #                     'date_start': fields.Date.today(),
    #                     'description': html2plaintext(record.channel_id.description),
    #                     'line_type_id': line_type and line_type.id,
    #                     'display_type': 'course',
    #                     'channel_id': record.channel_id.id,
    #                     'completed': False
    #                 })
    #         record.completed_slides_count = mapped_data.get(record.channel_id.id, dict()).get(record.partner_id.id, 0)
    #         record.completion = 100.0 if record.completed else round(
    #             100.0 * record.completed_slides_count / (record.channel_id.total_slides or 1))
    #
    #         if not record.completed and record.channel_id.active and record.completed_slides_count >= record.channel_id.total_slides:
    #             completed_records += record
    #
    #     if completed_records:
    #         # CODE GHI NHẬN HOÀN THÀNH KHÓA HỌC:
    #         for completed_data in completed_records:
    #             employee_completed_id = self.env['hr.employee'].sudo().search(
    #                 [('user_id.partner_id', '=', completed_data.partner_id.id)])
    #             resume_data = self.env['hr.resume.line'].search([('employee_id', 'in', employee_completed_id.ids), ('channel_id', '=', completed_data.channel_id.id), ('completed', '!=', True)])
    #             resume_data.write({'name': _('Completed course: %s') % completed_data.channel_id.name, 'date_end': fields.Date.today(), 'completed': True})
    #
    #         completed_records._set_as_completed()
    #         completed_records._send_completed_mail()

