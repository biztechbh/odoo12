odoo.define('aspl_product_small_label_zebra.print', function(require) {
    'use strict';

    var ActionManager = require('web.ActionManager');
    var core = require('web.core');
    var framework = require('web.framework');
    var rpc = require('web.rpc');

    ActionManager.include({
    	_executeReportAction: function(action, options) {
            var _action = _.clone(action);
            var _t = core._t;
            var self = this;
            var _super = this._super;

            if ('report_type' in _action && _action.report_type === 'qweb-pdf') {
                framework.blockUI();
                var params = {
                		model: "ir.actions.report",
                		method: "print_action_for_report_name",
                		args: [[_action.report_name], _action.data]
                	}
                	return rpc.query(params, {async: false})
                	.then(function(print_action){
                        if (print_action && print_action.action === 'server') {
                            framework.unblockUI();
                            var params = {
                            		model: "ir.actions.report",
                            		method: "print_document",
                            		args: [_action.context.active_ids, _action.report_name, 'none', _action.data,
                            		       {
                                                context: _action.context || {},
                                            }]
                            	}
                            	rpc.query(params, {async: false})
                            	.then(function(){
                                    self.do_notify(_t('Report'),
                                                   _t('Document sent to the printer ') + print_action.printer_name);
                                }).fail(function() {
                                    self.do_notify(_t('Report'),
                                                   _t('Error when sending the document to the printer ') + print_action.printer_name);

                                });
                        } else {
                            return self._super.apply(self, [_action, options]);
                        }
                    });
            } else {
                return self._super.apply(self, [_action, options]);
            }
        }
    });
    
    ActionManager.include({
    	_onExecuteAction: function (ev){
    		var self = this;
    		var action_data = ev.data.action_data;
    		var env = ev.data.env;
    		var record_id = env.currentID
    		if(record_id && env.model == 'wizard.product.small.label.report' && action_data.id == 'zebra_node_print_button'){
    			var node_url = '';
    			var url_params = {
            		model: "label.config.settings",
            		method: "search_read",
            		fields: ['node_application_url','odoo_instance_location'],
            		limit: 1,
            		orderBy: [{name: 'id', asc: false}],
            	}
            	rpc.query(url_params, {async: false})
            	.then(function(url_data){
            		if(url_data && url_data[0] && url_data[0].odoo_instance_location == 'cloud'){
            			node_url = url_data[0].node_application_url;
            			var params = {
                    		model: "wizard.product.small.label.report",
                    		method: "zebra_print",
                    		args: [record_id]
                    	}
                    	rpc.query(params, {async: false})
                    	.then(function(label_data){
                    		if (label_data && label_data.error){
                    			alert(label_data.error)
                    		}else{
                        		var list=[]
                        		label_data.data.map(function (data){
                        			list.push({'qty':data.qty,'label':data.label,'printer':label_data.printer})
                        		})
                        		$.ajax({
                	                type: "POST",
                		            url: node_url,
                		            data: {'data':list},
                		            success: function(response) {
                		            },
                	            });
                    		}
                    		if (action_data.id == 'zebra_node_print_button'){
                				$('.zebra_node_print_button').removeAttr('disabled')
                    		}
                    	});
        			} else{
        				return self._super(ev);
            		}
            	});
    			return jQuery.Deferred();
    		} else{
    			return self._super(ev);
    		}
    	},
    });
});
