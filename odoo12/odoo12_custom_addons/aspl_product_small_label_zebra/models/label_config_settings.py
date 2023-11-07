# -*- coding: utf-8 -*-
#################################################################################
# Author      : Acespritech Solutions Pvt. Ltd. (<www.acespritech.com>)
# Copyright(c): 2012-Present Acespritech Solutions Pvt. Ltd.
# All Rights Reserved.
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#################################################################################

from odoo import fields, models, api, _

class label_config_settings(models.Model):
    _name = "label.config.settings"
    _description = "label.config.settings"

    odoo_instance_location = fields.Selection([('cloud', 'Cloud'),
                                               ('local', 'Local')],
                                              string="Odoo Instance Location", default="cloud")
    cloud_printer_lines = fields.One2many('cloud.printer.line', 'config_id', string="Cloud Printers")

    printer_server_server_id = fields.Many2one('printer.server', string="Printer Server")
    node_application_url = fields.Char(string="Node Application URL")

    @api.one
    def execute(self,):
        return True

    @api.model
    def default_get(self, fields):
        res = super(label_config_settings, self).default_get(fields)
        last_id = self.search([], limit=1)
        if last_id:
            res.update({'odoo_instance_location': last_id.odoo_instance_location,
                        'printer_server_server_id': last_id.printer_server_server_id and last_id.printer_server_server_id.id or False,
                        'cloud_printer_lines': [(6, 0, last_id.cloud_printer_lines.ids)],
                        'node_application_url': last_id.node_application_url})
        return res

    @api.model
    def create(self, vals):
        all_ids = self.search([])
        if all_ids:
            all_ids.unlink()
        return super(label_config_settings, self).create(vals)


class cloud_printer_line(models.Model):
    _name = 'cloud.printer.line'
    _description = 'cloud.printer.line'

    name = fields.Char(string="Printer Name", required=True)
    config_id = fields.Many2one('label.config.settings', string="Configuration Ref")

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
