# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (c) 2021 Cloudroits (info.cloudroits@gmail.com)
#    You can modify it under the terms of the GNU LESSER
#    GENERAL PUBLIC LICENSE (LGPL v3), Version 3.
#
#    It is forbidden to publish, distribute, sublicense, or sell copies
#    of the Software or modified copies of the Software.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU LESSER GENERAL PUBLIC LICENSE (LGPL v3) for more details.
#
#    You should have received a copy of the GNU LESSER GENERAL PUBLIC LICENSE
#    GENERAL PUBLIC LICENSE (LGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from odoo import api, fields, models

#Add serial no in Purchase Order lines
class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    sl_no = fields.Integer(string='Sl. No.', compute='_compute_serial_number')

    @api.depends('sequence', 'order_id')
    def _compute_serial_number(self):
        for order_line in self:
            serial_no = 1
            for line in order_line.mapped('order_id').order_line:
                if line.product_id:
                    line.sl_no = serial_no
                    serial_no += 1                    
                else:
                    line.sl_no = 0
