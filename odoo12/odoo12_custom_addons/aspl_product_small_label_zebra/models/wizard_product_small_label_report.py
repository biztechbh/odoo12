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
import base64
from odoo.exceptions import Warning
import os, glob
import io
import logging
_logger = logging.getLogger(__name__)
from wand.image import Image as Img

try:
    from simple_zpl2 import ZPLDocument, EAN13_Barcode, Code128_Barcode, EAN8_Barcode, UPC_A_Barcode, QR_Barcode, Standard2of5_Barcode
    barcode_dict = {
        'EAN13': EAN13_Barcode,
        'Code128':Code128_Barcode,
        'EAN8':EAN8_Barcode,
        'UPC_A_Barcode':UPC_A_Barcode,
        'QR': QR_Barcode,
        'Stabdard2to5': Standard2of5_Barcode
    }
except ImportError:
    _logger.error('Cannot `import simple_zpl2`.')

try:
    from zebra import zebra
except ImportError:
    _logger.error('Cannot `import zebra`.')

try:
    from PIL import Image
except ImportError:
    _logger.error('Cannot `import PIL`.')

try:
    from wand.image import Image as Img
except ImportError:
    _logger.error('Cannot `import wand`.')


class product_small_label_design(models.Model):
    _name = 'product.small.label.design'
    _description = 'product.small.label.design'

    @api.multi
    def _get_currency(self):
        return self.env['res.users'].browse([self._uid]).company_id.currency_id

    @api.model
    def default_get(self, fields_list):
        res = super(product_small_label_design, self).default_get(fields_list)
        if self._context.get('wiz_id') and self._context.get('from_wizard'):
            for wiz in self.env['wizard.product.small.label.report'].browse(self._context.get('wiz_id')):
                prod_list = []
                zebra_prod_list = []
                for field_line in wiz.product_field_lines:
                    prod_list.append((0, 0, {'font_size': field_line.font_size,
                                            'font_color': field_line.font_color,
                                            'sequence': field_line.sequence,
                                            'field_id': field_line.field_id.id,
                                            'field_width': field_line.field_width,
                                            'margin_value': field_line.margin_value,
                                            'with_currency': field_line.with_currency}))
                for field_line in wiz.product_field_cloud_lines:
                    zebra_prod_list.append((0, 0, {'field_id':field_line.field_id.id,
                                                    'x_position':field_line.x_position,
                                                    'y_position':field_line.y_position,
                                                    'font_size':field_line.font_size,
                                                    'font_type': field_line.font_type,
                                                    'font_orientation': field_line.font_orientation,
                                                    'alignment':field_line.alignment,
                                                    'with_currency': field_line.with_currency}))

                res.update({
                    'template_label_design': wiz.report_design,
                    'label_width': wiz.label_width,
                    'label_height': wiz.label_height,
                    'dpi': wiz.dpi,
                    'margin_top': wiz.margin_top,
                    'margin_left': wiz.margin_left,
                    'margin_bottom': wiz.margin_bottom,
                    'margin_right': wiz.margin_right,
                    'humanReadable': wiz.humanReadable,
                    'barcode_height': wiz.barcode_height,
                    'barcode_width': wiz.barcode_width,
                    'display_height': wiz.display_height,
                    'display_width': wiz.display_width,
                    'with_barcode': wiz.with_barcode,
                    'label_logo': wiz.label_logo,
                    'product_field_lines': prod_list,
                    'barcode_type': wiz.barcode_type,
                    'currency_id': wiz.currency_id and wiz.currency_id.id,
                    'currency_position': wiz.currency_position,
                    'design_using' : wiz.design_using,
                    'print_text' : wiz.print_text,
                    'text_above' : wiz.text_above,
                    'product_field_cloud_lines' : zebra_prod_list,
                    'zebra_barcode_type' : wiz.zebra_barcode_type,
                    'label_config_option': wiz.label_config_option,
                    'logo_position': wiz.logo_position,
                    'logo_height': wiz.logo_height,
                    'logo_width': wiz.logo_width,
                })
        return res

    name = fields.Char(string="Design Name")
    template_label_design = fields.Text(string="Template Design")
    # label
    label_width = fields.Integer(string='Label Width (mm)', default=38, required=True)
    label_height = fields.Integer(string='Label Height (mm)', default=25, required=True)
    dpi = fields.Integer(string='DPI', default=160, help="The number of individual dots\
                                that can be placed in a line within the span of 1 inch (2.54 cm)")
    margin_top = fields.Integer(string='Margin Top (mm)', default=0)
    margin_left = fields.Integer(string='Margin Left (mm)', default=0)
    margin_bottom = fields.Integer(string='Margin Bottom (mm)', default=0)
    margin_right = fields.Integer(string='Margin Right (mm)', default=0)
    # barcode
    humanReadable = fields.Boolean(string="HumanReadable", help="User wants to print barcode number\
                                    with barcode label.")
    barcode_height = fields.Integer(string="Height", default=300, required=True, help="This height will\
                                    required for the clearity of the barcode.")
    barcode_width = fields.Integer(string="Width", default=1500, required=True, help="This width will \
                                    required for the clearity of the barcode.")
    display_height = fields.Integer(string="Display Height (px)", required=True, default=30,
                                    help="This height will required for display barcode in label.")
    display_width = fields.Integer(string="Display Width (px)", required=True, default=120,
                                   help="This width will required for display barcode in label.")
    with_barcode = fields.Boolean(string='Barcode', help="Click this check box if user want to print\
                                    barcode for Product Label.", default=True)

    # zebra barcode option
    print_text = fields.Selection([('Y', 'Y'), ('N', 'N')], string="Print Text", default="Y")
    text_above = fields.Selection([('Y', 'Y'), ('N', 'N')], string="Text Above", default="N")
    zebra_barcode_type = fields.Selection([('EAN13', 'EAN13'),
                                           ('Code128', 'Code128'),
                                           ('EAN8', 'EAN8'),
                                           ('UPC_A_Barcode', 'UPC_A_Barcode'),
                                           ('QR', 'QR'),
                                           ('Stabdard2to5', 'Stabdard2to5')], string="Barcode Type")

    active = fields.Boolean(string="Active", default=True)
    pricelist_id = fields.Many2one('product.pricelist', string="Pricelist")
    label_logo = fields.Binary(string="Label Logo")
    design_using = fields.Selection([('fields_selection', 'Fields Selection'),
                                     ('xml_design', 'XML Design')],
                                    default='xml_design')
    product_field_lines = fields.One2many('aces.design.field.line', 'design_id', string="Product Fields")
    product_field_cloud_lines = fields.One2many('aces.cloud.design.field.line', 'design_id', string="Product Field(s)")
    barcode_type = fields.Selection([('Codabar', 'Codabar'), ('Code11', 'Code11'),
                                     ('Code128', 'Code128'), ('EAN13', 'EAN13'),
                                     ('Extended39', 'Extended39'), ('EAN8', 'EAN8'),
                                     ('Extended93', 'Extended93'), ('USPS_4State', 'USPS_4State'),
                                     ('I2of5', 'I2of5'), ('UPCA', 'UPCA'),
                                     ('QR', 'QR')], string="Barcode Type")
    currency_id = fields.Many2one('res.currency', string="Currency", default=_get_currency)
    currency_position = fields.Selection([('before', 'Before'),
                                          ('after', 'After')], string="Currency Position", default="before")
    label_config_option = fields.Selection([('cloud', 'Cloud'),
                                            ('local', 'Local')], string="Label Config Ref.", default="cloud")
    logo_position = fields.Selection([('top', 'Top'), ('bottom', 'Bottom')], string="Logo Position")
    logo_height = fields.Integer(string="Logo Height(px)")
    logo_width = fields.Integer(string="Logo width(px)")

    @api.multi
    def close_wizard(self):
        self.write({'active': False})
        return True

    @api.multi
    def go_to_label_wizard(self):
        if not self.name:
            raise Warning(_('Label Design Name is required.'))
        return True


class aces_design_field_line(models.Model):
    _name = 'aces.design.field.line'
    _description = 'aces.design.field.line'

    font_size = fields.Integer(string="Font Size", default=10)
    font_color = fields.Selection([('black', 'Black'), ('blue', 'Blue'),
                                   ('cyan', 'Cyan'), ('gray', 'Gray'),
                                   ('green', 'Green'), ('lime', 'Lime'),
                                   ('maroon', 'Maroon'), ('pink', 'Pink'),
                                   ('purple', 'Purple'), ('red', 'Red'),
                                   ('yellow', 'Yellow')], string="Font Color", default='black')
    sequence = fields.Integer(string="Sequence")
    field_id = fields.Many2one('ir.model.fields', string="Fields Name")
    design_id = fields.Many2one('product.small.label.design', string="Barcode Label ID")
    field_width = fields.Float(string="Field Width(%)", default=100.00)
    margin_value = fields.Char(string="Field Margin(%)(T,R,B,L)", default='0,0,0,0')
    with_currency = fields.Boolean(string="With Currency")


class aces_cloud_design_field_line(models.Model):
    _name = 'aces.cloud.design.field.line'
    _description = 'aces.cloud.design.field.line'

    field_id = fields.Many2one('ir.model.fields', string="Fields Name", required=True)
    design_id = fields.Many2one('product.small.label.design', string="Barcode Label ID")
    x_position = fields.Integer(string="X Position", default=10)
    y_position = fields.Integer(string="Y Position", default=10)
    font_size = fields.Integer(string="Font Size", default=10, required=True)
    font_type = fields.Selection([('A', 'A'), ('B', 'B'), ('C', 'C'), ('D', 'D'), ('E', 'E'), ('F', 'F'), ('G', 'G'), ('H', 'H'), ('I', 'I'),
                            ('J', 'J'), ('K', 'K'), ('L', 'L'), ('M', 'M'), ('N', 'N'), ('O', 'O'), ('P', 'P'), ('Q', 'Q'), ('R', 'R'), ('S', 'S'),
                            ('T', 'T'), ('U', 'U'), ('V', 'V'), ('W', 'W'), ('X', 'X'), ('Y', 'Y'), ('Z', 'Z'), ('0', '0'), ('1', '1'), ('2', '2'),
                            ('3', '3'), ('4', '4'), ('5', '5'), ('6', '6'), ('7', '7'), ('8', '8'), ('9', '9')],
                            string="Font Type", default='B', required=True)
    font_orientation = fields.Selection([('N', 'Normal'), ('R', 'Rotated 90 clockwise'),
                                    ('I', 'Inverted'), ('B', 'Bottom Up (270 rotate)')],
                                    string="Orientation", required=True, default="N")
    alignment = fields.Selection([('C', 'Center'), ('R', 'Right'), ('L', 'Left'), ('J', 'Justify')],
                                 string="Alignment", required=True, default="C")
    with_currency = fields.Boolean(string="With Currency")

class report_image_preview(models.TransientModel):
    _name = 'report.image.preview'
    _description = 'report.image.preview'

    report_image = fields.Binary(string="Report Image")


class wizard_product_small_label_report(models.TransientModel):
    _name = "wizard.product.small.label.report"
    _description = "wizard.product.small.label.report"

    @api.model
    def default_get(self, fields_list):
        res = super(wizard_product_small_label_report, self).default_get(fields_list)
        label_config_id = self.env['label.config.settings'].search([], limit=1)
        if label_config_id:
            res['label_config_option'] = label_config_id.odoo_instance_location
            design_id = self.env['product.small.label.design'].search([('label_config_option', '=', label_config_id.odoo_instance_location)], limit=1)
            if design_id:
                res['design_id'] = design_id.id
        return res

    @api.model
    def _get_report_design(self):
        view_id = self.env['ir.ui.view'].search([('name', '=', 'prod_small_label_zebra')])
        if view_id.arch:
            return view_id.arch

    @api.model
    def _get_report_id(self):
        view_id = self.env['ir.ui.view'].search([('name', '=', 'prod_small_label_zebra')])
        if not view_id:
            raise Warning('Someone has deleted the reference view of report.\
                Please Update the module!')
        return view_id.id

    @api.model
    def _get_report_paperformat_id(self):
        xml_id = self.env['ir.actions.report'].search([('report_name', '=',
                                                        'aspl_product_small_label_zebra.prod_small_label_zebra')])
        if not xml_id or not xml_id.paperformat_id:
            raise Warning('Someone has deleted the reference paperformat of report.Please Update the module!')
        return xml_id.paperformat_id.id

    @api.multi
    def _get_currency(self):
        return self.env['res.users'].browse([self._uid]).company_id.currency_id

    design_id = fields.Many2one('product.small.label.design', string="Template")
    product_ids = fields.One2many('product.small.label.qty', 'prod_small_wiz_id', string='Product List')
    label_width = fields.Integer(string='Label Width (mm)', default=38, required=True)
    label_height = fields.Integer(string='Label Height (mm)', default=25, required=True)
    dpi = fields.Integer(string='DPI', default=160, help="The number of individual dots \
                        that can be placed in a line within the span of 1 inch (2.54 cm)")
    margin_top = fields.Integer(string='Margin Top (mm)', default=0)
    margin_left = fields.Integer(string='Margin Left (mm)', default=0)
    margin_bottom = fields.Integer(string='Margin Bottom (mm)', default=0)
    margin_right = fields.Integer(string='Margin Right (mm)', default=0)

    # barcode input
    with_barcode = fields.Boolean(string='Barcode', help="Click this check box if user want to\
                        print barcode for Product Label.", default=True)
    humanReadable = fields.Boolean(string="HumanReadable", help="User wants to print barcode number \
                                    with barcode label.")
    barcode_height = fields.Integer(string="Height", default=300, required=True,
                                    help="This height will required for the clearity of the barcode.")
    barcode_width = fields.Integer(string="Width", default=1500, required=True,
                                   help="This width will required for the clearity of the barcode.")
    display_height = fields.Integer(string="Display Height (px)", required=True, default=30,
                                    help="This height will required for display barcode in label.")
    display_width = fields.Integer(string="Display Width (px)", required=True, default=120,
                                   help="This width will required for display barcode in label.")

    # zebra barcode option
    print_text = fields.Selection([('Y', 'Y'), ('N', 'N')], string="Print Text", default="Y")
    text_above = fields.Selection([('Y', 'Y'), ('N', 'N')], string="Text Above", default="N")
    orientation = fields.Selection([('N', 'Normal'), ('R', 'Rotate 90 degree'),
                                    ('I', 'Inverted'), ('B', 'Rotate 270 degree')], string="Orientation", default="N")
    zebra_barcode_type = fields.Selection([('EAN13', 'EAN13'),
                                           ('Code128', 'Code128'),
                                           ('EAN8', 'EAN8'),
                                           ('UPC_A_Barcode', 'UPC_A_Barcode'),
                                           ('QR', 'QR'),
                                           ('Stabdard2to5', 'Stabdard2to5')], string="Barcode Type", default="EAN13")
    # report design
    report_design = fields.Text(string="Report Design", default=_get_report_design)
    view_id = fields.Many2one('ir.ui.view', string='Report View', default=_get_report_id)
    paper_format_id = fields.Many2one('report.paperformat', string="Paper Format", default=_get_report_paperformat_id)
    pricelist_id = fields.Many2one('product.pricelist', string="Pricelist")
    make_update_existing = fields.Boolean(string="Update Existing Template")
    label_logo = fields.Binary(string="Label Logo")
    print_behaviour = fields.Selection([('client', 'Send to Client'),
                                        ('server', 'Send to Printer')], string="Print Send To",
                                       default="client")
    printing_printer_id = fields.Many2one('printer.printer', string='Printer')
    cloud_printer_id = fields.Many2one('cloud.printer.line', string='Printer')
    design_using = fields.Selection([('fields_selection', 'Fields Selection'),
                                     ('xml_design', 'XML Design')],
                                    default='xml_design')
    product_field_lines = fields.One2many('aces.product.field.line', 'wizard_id', string="Product Fields")
    product_field_cloud_lines = fields.One2many('aces.cloud.product.field.line', 'wizard_id', string="Product Field(s)")
    barcode_type = fields.Selection([('Codabar', 'Codabar'), ('Code11', 'Code11'),
                                     ('Code128', 'Code128'), ('EAN13', 'EAN13'),
                                     ('Extended39', 'Extended39'), ('EAN8', 'EAN8'),
                                     ('Extended93', 'Extended93'), ('USPS_4State', 'USPS_4State'),
                                     ('I2of5', 'I2of5'), ('UPCA', 'UPCA'),
                                     ('QR', 'QR')], string="Barcode Type")
    currency_id = fields.Many2one('res.currency', string="Currency", default=_get_currency)
    currency_position = fields.Selection([('before', 'Before'),
                                          ('after', 'After')], string="Currency Position", default="before")
    label_config_option = fields.Selection([('cloud', 'Cloud'),
                                            ('local', 'Local')], string="Label Config Ref.")
    logo_position = fields.Selection([('top', 'Top'), ('bottom', 'Bottom')], string="Logo Position")
    logo_height = fields.Integer(string="Logo Height(px)")
    logo_width = fields.Integer(string="Logo width(px)")

    @api.onchange('design_id')
    def on_change_design_id(self):
        prod_list = []
        zebra_prod_list = []
        if self.design_id:
            self.product_field_lines = False
            for field_line in self.design_id.product_field_lines:
                prod_list.append((0, 0, {'font_size': field_line.font_size,
                                        'font_color': field_line.font_color,
                                        'sequence': field_line.sequence,
                                        'field_id': field_line.field_id.id,
                                        'field_width': field_line.field_width,
                                        'margin_value': field_line.margin_value,
                                        'with_currency': field_line.with_currency}))
            self.product_field_cloud_lines = False
            for field_line in self.design_id.product_field_cloud_lines:
                zebra_prod_list.append((0, 0, {'field_id':field_line.field_id.id,
                                                'x_position':field_line.x_position,
                                                'y_position':field_line.y_position,
                                                'font_size':field_line.font_size,
                                                'font_type': field_line.font_type,
                                                'font_orientation': field_line.font_orientation,
                                                'alignment':field_line.alignment,
                                                'with_currency': field_line.with_currency}))

            self.report_design = self.design_id.template_label_design
            # label format args
            self.label_width = self.design_id.label_width
            self.label_height = self.design_id.label_height
            self.dpi = self.design_id.dpi
            self.margin_top = self.design_id.margin_top
            self.margin_left = self.design_id.margin_left
            self.margin_bottom = self.design_id.margin_bottom
            self.margin_right = self.design_id.margin_right
            # barcode args
            self.with_barcode = self.design_id.with_barcode
            self.barcode_height = self.design_id.barcode_height
            self.barcode_width = self.design_id.barcode_width
            self.humanReadable = self.design_id.humanReadable
            self.display_height = self.design_id.display_height
            self.display_width = self.design_id.display_width
            self.label_logo = self.design_id.label_logo
            self.design_using = self.design_id.design_using
            self.product_field_lines = prod_list
            self.barcode_type = self.design_id.barcode_type
            self.currency_id = self.design_id.currency_id and self.design_id.currency_id.id
            self.currency_position = self.design_id.currency_position
            self.print_text = self.design_id.print_text
            self.text_above = self.design_id.text_above
            self.product_field_cloud_lines = zebra_prod_list
            self.zebra_barcode_type = self.design_id.zebra_barcode_type
            self.logo_position = self.design_id.logo_position
            self.logo_height = self.design_id.logo_height
            self.logo_width = self.design_id.logo_width


    @api.multi
    def save_design(self):
        if not self.make_update_existing:
            view_id = self.env['ir.model.data'].get_object_reference('aspl_product_small_label_zebra',
                                                    'wizard_product_small_label_design_form_view')[1]
            ctx = dict(self.env.context)
            ctx.update({'wiz_id' : self.id})
            return {
                'name': _('Product Small Label Design'),
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'product.small.label.design',
                'type': 'ir.actions.act_window',
                'target': 'new',
                'view_id': view_id,
                'context': ctx,
                'nodestroy': True
            }
        else:
            if self.design_id:
                prod_list = []
                zebra_prod_list = []
                for field_line in self.product_field_lines:
                    prod_list.append((0, 0, {'font_size': field_line.font_size,
                                            'font_color': field_line.font_color,
                                            'sequence': field_line.sequence,
                                            'field_id': field_line.field_id.id,
                                            'field_width': field_line.field_width,
                                            'margin_value': field_line.margin_value,
                                            'with_currency': field_line.with_currency}))
                self.design_id.product_field_lines = False

                for field_line in self.product_field_cloud_lines:
                    zebra_prod_list.append((0, 0, {'field_id':field_line.field_id.id,
                                                'x_position':field_line.x_position,
                                                'y_position':field_line.y_position,
                                                'font_size':field_line.font_size,
                                                'font_type': field_line.font_type,
                                                'font_orientation': field_line.font_orientation,
                                                'alignment':field_line.alignment,
                                                'with_currency': field_line.with_currency}))
                self.design_id.product_field_cloud_lines = False

                self.design_id.write({
                                'template_label_design': self.report_design,
                                'label_width': self.label_width,
                                'label_height': self.label_height,
                                'dpi': self.dpi,
                                'margin_top': self.margin_top,
                                'margin_left': self.margin_left,
                                'margin_bottom': self.margin_bottom,
                                'margin_right': self.margin_right,
                                'humanReadable': self.humanReadable,
                                'barcode_height': self.barcode_height,
                                'barcode_width': self.barcode_width,
                                'display_height': self.display_height,
                                'display_width': self.display_width,
                                'with_barcode': self.with_barcode,
                                'label_logo': self.label_logo,
                                'design_using': self.design_using,
                                'product_field_lines': prod_list,
                                'barcode_type': self.barcode_type,
                                'currency_id': self.currency_id and self.currency_id.id,
                                'currency_position': self.currency_position,
                                'print_text' : self.print_text,
                                'text_above' : self.text_above,
                                'product_field_cloud_lines' : zebra_prod_list,
                                'zebra_barcode_type' : self.zebra_barcode_type,
                                'label_config_option':self.label_config_option,
                                'logo_position': self.logo_position,
                                'logo_width':self.logo_width,
                                'logo_height':self.logo_height
                                })
                return True

    @api.multi
    @api.onchange('dpi')
    def onchange_dpi(self):
        if self.dpi < 80:
            self.dpi = 80

    @api.model
    def action_print_preview(self, record_id):
        encoded_string = ''
        if record_id:
            self = self.browse(record_id)

        if not self.product_ids:
            raise Warning(_('Select any product first.!'))

        if (self.label_height <= 0) or (self.label_width <= 0):
            raise Warning(_('You can not give label width and label height to less then zero(0).'))

        if self.label_config_option == 'cloud':
            encoded_string = self.zebra_print_preview()

        if self.label_config_option == 'local':
            if (self.margin_top < 0) or (self.margin_left < 0) or (self.margin_bottom < 0) or (self.margin_right < 0):
                raise Warning(_('Margin Value(s) for report can not be negative!'))

            if self.with_barcode and (self.barcode_height <= 0 or self.barcode_width <= 0 or
                                      self.display_height <= 0 or self.display_width <= 0):
                raise Warning(_('Give proper barcode height and width value(s) for display'))

            data = self.read()[0]
            data.update({'label_preview': True})
            datas = {
                'ids': self._ids,
                'model': 'wizard.product.small.label.report',
                'form': data
            }
            if self.view_id and self.report_design:
                self.view_id.sudo().write({'arch': self.report_design})
            self._set_paper_format_id()
            if self.design_using == 'xml_design':
                xml_id = self.env['ir.actions.report'].search([('report_name', '=',
                                                        'aspl_product_small_label_zebra.prod_small_label_zebra')])
                pdf_data = xml_id.render_qweb_html(self, data=datas)
                pdf_image = xml_id._run_wkhtmltopdf([pdf_data[0]], header=None, footer=None, landscape=None,
                                                    specific_paperformat_args={}, set_viewport_size=False)

                with Img(blob=pdf_image, resolution=300) as img:
                    filelist = glob.glob("/tmp/*.jpg")
                    for f in filelist:
                        os.remove(f)
                    img.resize(500, 500)
                    img.compression_quality = 99
                    img.save(filename="/tmp/temp.jpg")
                if os.path.exists("/tmp/temp-0.jpg"):
                    with open(("/tmp/temp-0.jpg"), "rb") as image_file:
                        encoded_string = base64.b64encode(image_file.read())
                elif os.path.exists("/tmp/temp.jpg"):
                    with open(("/tmp/temp.jpg"), "rb") as image_file:
                        encoded_string = base64.b64encode(image_file.read())

            if self.design_using == 'fields_selection':
                attributes_flag = False
                for product_line in self.product_ids:
                    if product_line.attribute_ids:
                        attributes_flag = True

                if not self.product_field_lines:
                    raise Warning(_('Select Fields to print into label.'))

                sequence = False
                att_field_flag = False
                fields_list = []
                l = []
                count = len(self.product_field_lines)

                for field in sorted(self.product_field_lines, key=lambda v: v.sequence, reverse=False):

                    if field.with_currency and (not self.currency_id or not self.currency_position):
                        raise Warning(_('To Print value with currency, please select currency position and currency properly.'))

                    if field.field_id.name == 'attribute_value_ids':
                        att_field_flag = True

                    if field.field_id and field.field_id.name == 'barcode':
                        if not self.barcode_type:
                            raise Warning(_("Select barcode type to print barcode from Barcode tab."))
                        if field.with_currency:
                            raise Warning(_("Barcode will not print with Currency."))

                    if field.margin_value:
                        if len(field.margin_value.split(',')) != 4:
                            raise Warning(_('Please enter margin value with Top,Right,Bottom,Left margin parameters.'))

                    if sequence and sequence == field.sequence:
                        raise Warning(_("Sequence cannot repeated."))
    #                     l.append(field.id)
                    if not sequence:
                        l.append(field.id)
                    if sequence and sequence != field.sequence:
                        fields_list.append(l)
                        l = []
                        l.append(field.id)
                    sequence = field.sequence
                    if count == 1:
                        fields_list.append(l)
                    count -= 1
                if not att_field_flag and attributes_flag:
                    raise Warning(_('Please select attribute field from product table to print attributes into label.'))

                if att_field_flag and not attributes_flag:
                    raise Warning(_('Please select attributes from product in product list to print attributes into label.'))

                if self.label_logo and (not self.logo_position or self.logo_height <= 0 or self.logo_width <= 0):
                    raise Warning(_('Define logo position,height and width properly into label tab.'))

                datas.update({'fields_list': fields_list})
                xml_id = self.env['ir.actions.report'].search([('report_name', '=',
                                                        'aspl_product_small_label_zebra.prod_small_fields_label')])
                pdf_data = xml_id.render_qweb_html(self, data=datas)
                pdf_image = xml_id._run_wkhtmltopdf([pdf_data[0]], header=None, footer=None, landscape=None,
                                                    specific_paperformat_args={}, set_viewport_size=False)
                with Img(blob=pdf_image, resolution=300) as img:
                    filelist = glob.glob("/tmp/*.jpg")
                    for f in filelist:
                        os.remove(f)
                    img.resize(500, 500)
                    img.compression_quality = 99
                    img.save(filename="/tmp/temp.jpg")
                if os.path.exists("/tmp/temp-0.jpg"):
                    with open(("/tmp/temp-0.jpg"), "rb") as image_file:
                        encoded_string = base64.b64encode(image_file.read())
                elif os.path.exists("/tmp/temp.jpg"):
                    with open(("/tmp/temp.jpg"), "rb") as image_file:
                        encoded_string = base64.b64encode(image_file.read())
        view_id = self.env['ir.model.data'].get_object_reference('aspl_product_small_label_zebra',
                                                'wizard_report_image_preview_form_view')[1]
        return {
            'name': _('Preview'),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'report.image.preview',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'view_id': view_id,
            'context': {'default_report_image': encoded_string},
        }

    @api.multi
    def action_print(self, record_id):
        if not self.product_ids:
            raise Warning('Select any product first.!')
        for product in self.product_ids:
            if product.qty <= 0:
                raise Warning('%s product label qty should be greater then 0.!'
                           % (product.product_id.name))
        if (self.label_height <= 0) or (self.label_width <= 0):
            raise Warning(_('You can not give label width and label height to less then zero(0).'))

        if self.label_config_option == 'local':
            if (self.margin_top < 0) or (self.margin_left < 0) or (self.margin_bottom < 0) or (self.margin_right < 0):
                raise Warning('Margin Value(s) for report can not be negative!')

            if self.with_barcode and (self.barcode_height <= 0 or self.barcode_width <= 0 or
                                      self.display_height <= 0 or self.display_width <= 0):
                raise Warning('Give proper barcode height and width value(s) for display')

            data = self.read()[0]
            datas = {
                'ids': self._ids,
                'model': 'wizard.product.small.label.report',
                'form': data
            }
            if self.view_id and self.report_design:
                self.view_id.sudo().write({'arch': self.report_design})
            self._set_paper_format_id()
            if self.design_using == 'xml_design':
                return self.env.ref('aspl_product_small_label_zebra.aspl_product_small_label_zebra_report').report_action(self, data=datas)

            if self.design_using == 'fields_selection':
                attributes_flag = False
                for product_line in self.product_ids:
                    if product_line.attribute_ids:
                        attributes_flag = True

                if not self.product_field_lines:
                    raise Warning(_('Select Fields to print into label.'))

                sequence = False
                att_field_flag = False
                fields_list = []
                l = []
                count = len(self.product_field_lines)

                for field in sorted(self.product_field_lines, key=lambda v: v.sequence, reverse=False):

                    if field.with_currency and (not self.currency_id or not self.currency_position):
                        raise Warning(_('To Print value with currency, please select currency position and currency properly.'))

                    if field.field_id.name == 'attribute_value_ids':
                        att_field_flag = True

                    if field.field_id and field.field_id.name == 'barcode':
                        if not self.barcode_type:
                            raise Warning(_("Select barcode type to print barcode from Barcode tab."))
                        if field.with_currency:
                            raise Warning(_("Barcode will not print with Currency."))

                    if field.margin_value:
                        if len(field.margin_value.split(',')) != 4:
                            raise Warning(_('Please enter margin value with Top,Right,Bottom,Left margin parameters.'))

                    if sequence and sequence == field.sequence:
                        raise Warning(_("Sequence cannot repeated."))
    #                     l.append(field.id)
                    if not sequence:
                        l.append(field.id)
                    if sequence and sequence != field.sequence:
                        fields_list.append(l)
                        l = []
                        l.append(field.id)
                    sequence = field.sequence
                    if count == 1:
                        fields_list.append(l)
                    count -= 1
                if not att_field_flag and attributes_flag:
                    raise Warning(_('Please select attribute field from product table to print attributes into label.'))

                if att_field_flag and not attributes_flag:
                    raise Warning(_('Please select attributes from product in product list to print attributes into label.'))

                if self.label_logo and (not self.logo_position or self.logo_height <= 0 or self.logo_width <= 0):
                    raise Warning(_('Define logo position,height and width properly into label tab.'))

                datas.update({'fields_list': fields_list})
                return self.env.ref('aspl_product_small_label_zebra.aspl_product_small_fields_label_zebra_report').report_action(self, data=datas)

    @api.model
    def zebra_print_preview(self):
        data = []

        def add_text(self, zdoc, text, label_width, alignment, x_pos, y_pos, font_size, font_type, font_orientation):
            zdoc.add_field_block(width=label_width, max_lines=5, text_justification=alignment)
            zdoc.add_field_origin(x_pos=x_pos, y_pos=y_pos)
            zdoc.add_font(font_type, font_orientation, font_size)
            zdoc.add_field_data(text)

        def add_barcode(self, zdoc, text, x_pos, y_pos, text_size, barcode_height, orientation, print_text, text_above):
            zdoc.add_field_origin(x_pos=x_pos, y_pos=y_pos)
            if self.zebra_barcode_type == 'QR':
                barcode = QR_Barcode(text, model=2, magnification=10, error_correction='H', mask_value=7)
            else:
                barcode = barcode_dict[self.zebra_barcode_type](text, orientation, barcode_height , print_text, text_above)
            zdoc.add_barcode_default(text_size)
            zdoc.add_barcode(barcode)

        if not self.product_ids:
            raise Warning(_('Select any product first.!'))

        if self.label_width <= 0:
            raise Warning(_('You can not give label width to less then zero(0).'))

        if not self.product_field_cloud_lines:
            raise Warning(_('Select fields to print label.!'))

        field_attr_flag = False
        with_currency_flag = False
        for field in self.product_field_cloud_lines:
            if field.field_id.name == 'attribute_value_ids':
                field_attr_flag = True
            if field.with_currency:
                with_currency_flag = True

        if with_currency_flag and (not self.currency_id or not self.currency_position):
            raise Warning(_('To Print value with currency, please select currency position and currency properly.'))

        attributes_flag = False
        for product_line in self.product_ids[0]:
            if product_line.attribute_ids:
                attributes_flag = True

        if not field_attr_flag and attributes_flag:
            raise Warning(_('Please select attribute field from product table to print attributes into label.'))

        if field_attr_flag and not attributes_flag:
            raise Warning(_('Please select attributes from product in product list to print attributes into label.'))

        for product_line in self.product_ids[0]:
            zdoc = ZPLDocument()
            for field in self.product_field_cloud_lines:

                if field.x_position <= 0 or field.y_position <= 0:
                    raise Warning(_('Enter proper X Position and Y position into field line...!'))

                if field.field_id.ttype not in ('many2many', 'one2many', 'many2one'):
                    if field.field_id.name == 'barcode':
                        if self.barcode_height <= 0:
                            raise Warning(_('Barcode height can not be zero.'))
                        if product_line.product_id.mapped(field.field_id.name)[0] and product_line.stock_production_lot_id:
                            text_value = product_line.product_id.mapped(field.field_id.name)[0] + product_line.stock_production_lot_id.name
                            add_barcode(self, zdoc, text_value, field.x_position, field.y_position, field.font_size,
                                        self.barcode_height, field.font_orientation, self.print_text, self.text_above)
                    else:
                        text_value = ''
                        if product_line.product_id.mapped(field.field_id.name)[0]:
                            text_value = product_line.product_id.mapped(field.field_id.name)[0]
                            if self.pricelist_id and field.field_id.name in ('list_price', 'standard_price', 'lst_price'):
                                text_value = self.pricelist_id.price_get(product_line.product_id.id, 1.0)
                                text_value = text_value.get(self.pricelist_id.id)

                            if field.with_currency:
                                taxes = product_line.product_id.taxes_id.compute_all(text_value,
                                                                                     self.env.user.company_id.currency_id,
                                                                                     1,
                                                                                     product_line.product_id,
                                                                                     self.env.user.partner_id)['taxes']
                                if taxes:
                                    text_value = 0.0
                                    for each in taxes:
                                        text_value += each['amount'] + each['base']
                                if self.currency_position == 'after':
                                    text_value = "Price: " + "%0.3f" % text_value + ' ' + self.currency_id.name
                                if self.currency_position == 'before':
                                    text_value = "Price: " + self.currency_id.name + ' ' + "%0.3f" % text_value
                            add_text(self, zdoc, text_value, self.label_width, field.alignment, field.x_position,
                                        field.y_position, field.font_size, field.font_type, field.font_orientation)
                else:
                    if field.field_id.name == 'company_id':
                        text_val = self.env.user.company_id.name
                        add_text(self, zdoc, text_val, self.label_width, field.alignment, field.x_position,
                                 field.y_position, field.font_size, field.font_type, field.font_orientation)

                if field.field_id.name == 'attribute_value_ids':
                    text_value = ''
                    for attribute in product_line.attribute_ids:
                        text_value += attribute.attribute_id.name + ':' + attribute.name + ';'
                    if text_value:
                        add_text(self, zdoc, text_value, self.label_width, field.alignment, field.x_position,
                                field.y_position, field.font_size, field.font_type, field.font_orientation)

            png = zdoc.render_png(label_width=4, label_height=2)
            encoded_string = base64.b64encode(png)
            return encoded_string

    @api.model
    def zebra_print(self, record_id):
        data = []
        if record_id:
            self = self.browse(record_id)

        def add_text(self, zdoc, text, label_width, alignment, x_pos, y_pos, font_size, font_type, font_orientation):
            zdoc.add_field_block(width=label_width, max_lines=5, text_justification=alignment)
            zdoc.add_field_origin(x_pos=x_pos, y_pos=y_pos)
            zdoc.add_font(font_type, font_orientation, font_size)
            zdoc.add_field_data(text)

        def add_barcode(self, zdoc, text, x_pos, y_pos, text_size, barcode_height, orientation, print_text, text_above):
            zdoc.add_field_origin(x_pos=x_pos, y_pos=y_pos)
            if self.zebra_barcode_type == 'QR':
                barcode = QR_Barcode(text, model=2, magnification=10, error_correction='H', mask_value=7)
            else:
                barcode = barcode_dict[self.zebra_barcode_type](text, orientation, barcode_height , print_text, text_above)
            zdoc.add_barcode_default(text_size)
            zdoc.add_barcode(barcode)

        if not self.product_ids:
            return {'error':'Select any product first.!'}

        if self.label_width <= 0:
            return {'You can not give label width to less then zero(0).'}

        if not self.product_field_cloud_lines:
            return {'error': 'Select fields to print label.!'}

        field_attr_flag = False
        with_currency_flag = False
        for field in self.product_field_cloud_lines:
            if field.field_id.name == 'attribute_value_ids':
                field_attr_flag = True
            if field.with_currency:
                with_currency_flag = True

        if with_currency_flag and (not self.currency_id or not self.currency_position):
            return {'error':'To Print value with currency, please select currency position and currency properly.'}

        attributes_flag = False
        for product_line in self.product_ids:
            if product_line.attribute_ids:
                attributes_flag = True

        if not field_attr_flag and attributes_flag:
            return {'error':'Please select attribute field from product table to print attributes into label.'}

        if field_attr_flag and not attributes_flag:
            return {'error':'Please select attributes from product in product list to print attributes into label.'}

        for product_line in self.product_ids:
            zdoc = ZPLDocument()
            for field in self.product_field_cloud_lines:

                if field.x_position <= 0 or field.y_position <= 0:
                    return {'error': 'Enter proper X Position and Y position into field line...!'}

                if field.field_id.ttype not in ('many2many', 'one2many', 'many2one'):
                    if field.field_id.name == 'barcode':
                        if self.barcode_height <= 0:
                            return {'error': 'Barcode height can not be zero.'}

                        if product_line.product_id.mapped(field.field_id.name)[0]:
                            if product_line.stock_production_lot_id:
                                text_value = product_line.product_id.mapped(field.field_id.name)[0] + \
                                             product_line.stock_production_lot_id.name
                                add_barcode(self, zdoc, text_value, field.x_position, field.y_position, field.font_size,
                                            self.barcode_height, field.font_orientation, self.print_text, self.text_above)
                    else:
                        text_value = ''
                        if product_line.product_id.mapped(field.field_id.name)[0]:
                            text_value = product_line.product_id.mapped(field.field_id.name)[0]

                            if self.pricelist_id and field.field_id.name in ('list_price', 'standard_price', 'lst_price'):
                                text_value = self.pricelist_id.price_get(product_line.product_id.id, 1.0)
                                text_value = text_value.get(self.pricelist_id.id)

                            if field.with_currency:
                                taxes = product_line.product_id.taxes_id.compute_all(text_value,
                                                                                     self.env.user.company_id.currency_id,
                                                                                     1,
                                                                                     product_line.product_id,
                                                                                     self.env.user.partner_id)['taxes']
                                if taxes:
                                    text_value = 0.0
                                    for each in taxes:
                                        text_value += each['amount'] + each['base']
                                    print
                                if self.currency_position == 'after':
                                    text_value = "Price: " + "%0.3f" % text_value + ' ' + self.currency_id.name
                                if self.currency_position == 'before':
                                    text_value = "Price: " + self.currency_id.name + ' ' + "%0.3f" % text_value
                            add_text(self, zdoc, text_value, self.label_width, field.alignment, field.x_position,
                                     field.y_position, field.font_size, field.font_type, field.font_orientation)


                else:
                    if field.field_id.name == 'company_id':
                        text_val = self.env.user.company_id.name
                        add_text(self, zdoc, text_val, self.label_width, field.alignment, field.x_position,
                                 field.y_position, field.font_size, field.font_type, field.font_orientation)
                if field.field_id.name == 'attribute_value_ids':
                    text_value = ''
                    for attribute in product_line.attribute_ids:
                        text_value += attribute.attribute_id.name + ':' + attribute.name + ';'
                    if text_value:
                        add_text(self, zdoc, text_value, self.label_width, field.alignment, field.x_position,
                                field.y_position, field.font_size, field.font_type, field.font_orientation)
            data.append({'label': zdoc.zpl_text, 'qty': product_line.qty})
        if data:
            _logger.info("\n\n\n\data is going to print from here (%s)\n\n(%s).", self.cloud_printer_id.name, str(data))
            return {'printer': self.cloud_printer_id.name, 'data': data}
        return []

    @api.multi
    def _set_paper_format_id(self):
        if self.paper_format_id:
            result = self.paper_format_id.sudo().write({
                        'format': 'custom',
                        'page_width': self.label_width,
                        'page_height': self.label_height,
                        'margin_top': self.margin_top,
                        'margin_left': self.margin_left,
                        'margin_bottom': self.margin_bottom,
                        'margin_right': self.margin_right,
                        'dpi': self.dpi
                    })


class product_label_qty(models.TransientModel):
    _name = 'product.small.label.qty'
    _description = 'product.small.label.qty'

    product_id = fields.Many2one('product.product', string='Product', required=True)
    stock_production_lot_id = fields.Many2one('stock.production.lot', string="Lot")
    qty = fields.Integer(string='Quantity', default=1)
    prod_small_wiz_id = fields.Many2one('wizard.product.small.label.report', string='Product Label Wizard ID')
    line_id = fields.Integer(string='Line ID')
    attribute_ids = fields.Many2many('product.attribute.value', 'wizard_attribute_value_table', 'line_id', 'attribute_id', string="Attributes")

    @api.onchange('product_id', 'stock_production_lot_id')
    def _compute_qty(self):
        quantity = self.env['stock.quant'].search([('product_id', '=', self.product_id.id), ('lot_id', '=', self.stock_production_lot_id.id), ('location_id.usage', 'in', ['internal', 'transit'])], limit=1).quantity
        self.qty = quantity

class aces_product_field_line(models.TransientModel):
    _name = 'aces.product.field.line'
    _description = 'aces.product.field.line'

    font_size = fields.Integer(string="Font Size", default=10)
    font_color = fields.Selection([('black', 'Black'), ('blue', 'Blue'),
                                   ('cyan', 'Cyan'), ('gray', 'Gray'),
                                   ('green', 'Green'), ('lime', 'Lime'),
                                   ('maroon', 'Maroon'), ('pink', 'Pink'),
                                   ('purple', 'Purple'), ('red', 'Red'),
                                   ('yellow', 'Yellow')], string="Font Color", default='black')
    sequence = fields.Integer(string="Sequence")
    field_id = fields.Many2one('ir.model.fields', string="Fields Name")
    wizard_id = fields.Many2one('wizard.product.small.label.report', string="Barcode Label ID")
    field_width = fields.Float(string="Field Width(%)", default=100.00)
    margin_value = fields.Char(string="Field Margin(%)(T,R,B,L)", default='0,0,0,0')
    with_currency = fields.Boolean(string="With Currency")


class aces_cloud_product_field_line(models.TransientModel):
    _name = 'aces.cloud.product.field.line'
    _description = 'aces.cloud.product.field.line'

    field_id = fields.Many2one('ir.model.fields', string="Fields Name", required=True)
    wizard_id = fields.Many2one('wizard.product.small.label.report', string="Barcode Label ID")
    x_position = fields.Integer(string="X Position", default=10)
    y_position = fields.Integer(string="Y Position", default=10)
    font_size = fields.Integer(string="Font Size", default=10, required=True)
    font_type = fields.Selection([('A', 'A'), ('B', 'B'), ('C', 'C'), ('D', 'D'), ('E', 'E'), ('F', 'F'), ('G', 'G'), ('H', 'H'), ('I', 'I'),
                            ('J', 'J'), ('K', 'K'), ('L', 'L'), ('M', 'M'), ('N', 'N'), ('O', 'O'), ('P', 'P'), ('Q', 'Q'), ('R', 'R'), ('S', 'S'),
                            ('T', 'T'), ('U', 'U'), ('V', 'V'), ('W', 'W'), ('X', 'X'), ('Y', 'Y'), ('Z', 'Z'), ('0', '0'), ('1', '1'), ('2', '2'),
                            ('3', '3'), ('4', '4'), ('5', '5'), ('6', '6'), ('7', '7'), ('8', '8'), ('9', '9')],
                            string="Font Type", default='B', required=True)
    font_orientation = fields.Selection([('N', 'Normal'), ('R', 'Rotated 90 clockwise'),
                                    ('I', 'Inverted'), ('B', 'Bottom Up (270 rotate)')],
                                    string="Orientation", required=True, default="N")
    alignment = fields.Selection([('C', 'Center'), ('R', 'Right'), ('L', 'Left'), ('J', 'Justify')],
                                 string="Alignment", required=True, default="C")
    with_currency = fields.Boolean(string="With Currency")


class product_attribute_value(models.Model):
    _inherit = 'product.attribute.value'
    _description = 'product.attribute.value'

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        if self._context.get('from_wizard') and self._context.get('product_id'):
            product_record = self.env['product.product'].browse([self._context.get('product_id')])
            args.append(('id', 'in', [attribute.id for attribute in product_record.attribute_value_ids]))
        return super(product_attribute_value, self).name_search(name, args, operator='ilike', limit=limit)


class ir_model_fields(models.Model):
    _inherit = 'ir.model.fields'
    _description = 'ir.model.fields'

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        if self._context.get('from_wizard'):
            field_record = self.browse([self._context.get('field_id')])
            args += ['|', ('ttype', 'not in', ('many2many', 'one2many', 'many2one')), ('name', '=', 'attribute_value_ids')]
        return super(ir_model_fields, self).name_search(name, args, operator='ilike', limit=limit)

class ProductionLot(models.Model):
    _inherit = 'stock.production.lot'

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        if self._context.get('product_id'):
            product_id = self.env['product.product'].browse(self._context.get('product_id'))
            args += [('product_id', '=', product_id.id)]
        return super(ProductionLot, self).name_search(name, args, operator='ilike', limit=limit)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
