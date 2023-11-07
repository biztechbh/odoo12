odoo.define('preview_purchase_history.list_renderer', function (require) {
    "use strict";

    var core  = require('web.core');
    var _t = core._t;
    var rpc = require('web.rpc');
    var ListRenderer = require('web.ListRenderer');

    ListRenderer.include({
        _renderButton: function (record, node) {
            var self = this;
            var $button = this._renderButtonFromNode(node, {
                extraClass: node.attrs.icon ? 'o_icon_button' : undefined,
                textAsTitle: !!node.attrs.icon,
            });
            this._handleAttributes($button, node);
            this._registerModifiers(node, record, $button);

            if (record.res_id) {
                // TODO this should be moved to a handler
                $button.on("click", function (e) {
                    e.stopPropagation();
                    self.trigger_up('button_clicked', {
                        attrs: node.attrs,
                        record: record,
                    });
                });
            } else {
                if (node.attrs.options.warn) {
                    $button.on("click", function (e) {
                        e.stopPropagation();
                        self.do_warn(_t("Warning"), _t('Please click on the "save" button first.'));
                    });
                } else if (node.attrs.options.do_open && record.model == "purchase.order.line") {
                    $button.on("click", function (e) {
                        e.stopPropagation();
                        if(record.data.product_id.data){
                            rpc.query({
                            model:'purchase.order.line',
                            method:'action_purchase_history',
                            args:[record.data.product_id.data.id],
                            }).then(function(result){
                                 self.do_open_purchase_history(result);
                            });
                        }else{
                            self.do_warn(_t("Warning"), _t('Please click outside of Line to Register the record.'));
                        }
                    });
                }else {
                    $button.prop('disabled', true);
                }
            }
            return $button;
        },
        do_open_purchase_history : function(result){
            var self = this;
            this.do_action({
	    		name: 'Purchase History',
	            type: 'ir.actions.act_window',
	            target: 'new',
	            view_type: 'form',
	            view_mode: 'form',
	            views: [[result[1] || false, 'form']],
	            res_model: 'purchase.history.wizard',
	            context: {'default_preview_history': [[6, 0, result[0]]]},
	        });
        },
    });
});