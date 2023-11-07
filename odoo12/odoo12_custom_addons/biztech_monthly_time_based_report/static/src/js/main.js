odoo.define('biztech_monthly_time_based_report.main', function (require) {
    "use strict";

    var ControlPanelMixin = require('web.ControlPanelMixin');
    var AbstractAction = require('web.AbstractAction');
    var Widget = require('web.Widget');
    var rpc = require('web.rpc');
    var core = require('web.core');
    var _t = core._t;

    var MonthlyTimeBasedReport = AbstractAction.extend(ControlPanelMixin, {
        title: core._t('Monthly Time Based Report'),
        template: 'MonthlyTimeBasedReport',
        events: {
            'click .export_to_excel': 'export_as_excel',
            'click .export_to_pdf': 'export_as_pdf',
            'click .click_to_refresh': 'reopen_report',
        },
        init: function (parent, params) {
            this._super.apply(this, arguments);
            var self = this;
            this.action_manager = parent;
            this.params = params;
        },
        start: function () {
            this._super.apply(this, arguments);
            var breadcrumbs = this.action_manager && this.action_manager._getBreadcrumbs() || [{
                title: this.title,
                action: this
            }];
            this.update_control_panel({breadcrumbs: breadcrumbs, search_view_hidden: true}, {clear: true});
        },
        export_as_excel : function(){
            var self = this;
            var context = self.params.context;
            rpc.query({
                model: 'pos.order',
                method: 'export_as_excel_report_monthly_time_based',
                args: [[], context.from_date ? context.from_date : false, context.to_date ? context.to_date : false, context.categ_id ? context.categ_id : false, context.product_id ? context.product_id : false, context.shop_id ? context.shop_id : false],
                },$.blockUI({
					css: {
						cursor:'wait',
						border:'none',
						backgroundColor:'transparent'
					},
					message: '<img src="/biztech_monthly_time_based_report/static/src/img/loading_icon.gif" width="150" height="150" style="border:unset !important;"/>'
				}), {async: false}).then(function (res) {
                if (res && res.report_id){
                    $.unblockUI();
                    self.do_action({
                        name: _t('Report'),
                        type: 'ir.actions.act_window',
                        res_model: 'report.monthly.time.based.wizard.download',
                        views: [[false, 'form']],
                        target: 'new',
                        res_id: res.report_id,
                    });
                }
            });
        },
        export_as_pdf : function(){
            var self = this;
            var context = self.params.context;
            rpc.query({
                model: 'pos.order',
                method: 'export_as_pdf_report_monthly_time_based',
                args: [[], context.from_date ? context.from_date : false, context.to_date ? context.to_date : false, context.categ_id ? context.categ_id : false, context.product_id ? context.product_id : false, context.shop_id ? context.shop_id : false],
                },$.blockUI({
					css: {
						cursor:'wait',
						border:'none',
						backgroundColor:'transparent'
					},
					message: '<img src="/biztech_monthly_time_based_report/static/src/img/loading_icon.gif" width="150" height="150" style="border:unset !important;"/>'
				}), {async: false}).then(function (res) {
                if (res){
                    $.unblockUI();
                    self.do_action('biztech_monthly_time_based_report.action_monthly_dashboard_report',{additional_context:{
                        active_ids:[res],
                    }})
                }
            });
        },
        reopen_report : function(){
            var self = this;
            self.do_action('biztech_monthly_time_based_report.action_monthly_dashboard_wizard')
        },
        renderElement: function () {
            var self = this;
            this._super.apply(this, arguments);
            var context = self.params.context;
            if (context.from_date && context.to_date){
                $(self.$el.find('.summary')).show();
                $(self.$el.find('.report_name')).html('<span><b>Monthly Time Based Report</b></span>');
                if (context.from_date && context.to_date ){
                    var d = context.from_date + '<b> TO </b>' + context.to_date;
                }
                else{
                    d = ''
                }
                $(self.$el.find('.dates')).html('<span><b>Date:</b>'+ d +'</span>');
                rpc.query({
                    model: 'pos.order',
                    method: 'get_monthly_time_based_data',
                    args: [[], context.from_date ? context.from_date : false, context.to_date ? context.to_date : false, context.categ_id ? context.categ_id : false, context.product_id ? context.product_id : false, context.shop_id ? context.shop_id : false],
                    },{async: false}).then(function (res) {
                        if (res){
                        	$.unblockUI();
                        	var g_tot_count = 0;var g_tot_sale = 0;var g_tot_cost = 0;var g_tot_profit = 0;var g_tot_profit_per = 0;
//                            for (var prop in res) {
								var columns = [
									  {"name":"month_year","title":"Month-Year"},
									  {"name":"count","title":"No. of Patients"},
									  {"name":"total_sale","title":"Total Sale","type": "number","decimalSeparator": ".","thousandSeparator":","},
									  {"name":"cost","title":"Cost of Sale","type": "number","decimalSeparator": ".","thousandSeparator":","},
									  {"name":"profit","title":"Profit Amount","type": "number","decimalSeparator": ".","thousandSeparator":","},
									  {"name":"profit_per","title":"Profit %","type": "number","decimalSeparator": ".","thousandSeparator":","}
								]
//								var class_name = res[prop][0]['categ_name'] || 'Non-Defined';
								var html = '<div class="card">';
								html += '<div class="card-header">';
								html += '<h4 class="card-title">';
//								html += '<a class="accordion-toggle" data-toggle="collapse" href="#'+class_name+'">';
//								html += res[prop][0]['categ_name'].replace('_', ' ');
								html += '</a>';
								html += '</h4>';
								html += '</div>';
//								html += '<div id="'+class_name+'" class="panel-collapse collapse show">';
								html += '<div class="card-body">';
								html += '<table class="table table-bordered table-hover monthly_time_based_report per_table" data-paging="true" data-filtering="true" data-sorting="true"/>'
								html += '</div>';
								html += '</div>';
								html += '</div>';
								self.$el.find('.table_per_date_container').append(html)
								var selected_total_amount_list = [];
							var g_selected_total_amount_list = [];
							var selected_list = [];
							var g_selected_list = [];
								self.$el.find('.monthly_time_based_report').footable({
									"columns": columns,
									"rows": res,
									'on': {
//										'after.ft.paging': function(e, ft, filter) {
//											if (filter && filter.total == filter.page){
//												var rows = ft.rows.all;
//												var tot_count = 0;var tot_sale = 0;var tot_cost = 0;var tot_profit = 0;var tot_profit_per = 0;
//												for (var i = 0, l = rows.length, row; i < l; i++){
//													row = rows[i].val();
//													tot_count += parseFloat(row["count"]);
//													tot_sale += parseFloat(row["total_sale"]);
//													tot_cost += parseFloat(row["cost"]);
//													tot_profit += parseFloat(row["profit"]);
//													tot_profit_per += parseFloat(row["profit_per"]);
//												}
//												var html = '<tr class=total_due_table_'+ class_name +'>';
//												html += '<td></td>';
//												html += '<td><b>Total: '+ tot_count.toFixed(3).toLocaleString('en') +'</b></td>';
//												html += '<td><b>Total: '+ tot_sale.toFixed(3).toLocaleString('en') +'</b></td>';
//												html += '<td><b>Total: '+ tot_cost.toFixed(3).toLocaleString('en') +'</b></td>';
//												html += '<td><b>Total: '+ tot_profit.toFixed(3).toLocaleString('en') +'</b></td>';
//												html += '<td></td>';
//												html += '</tr>';
//												var foot = self.$el.find('.' + ft.classes[3] + ' tfoot');
//												foot.prepend(html);
//											}
//											else{
//                                            if (typeof self.$el.find('.total_due_table_'+ class_name +'').html() !== 'undefined'){
//                                                self.$el.find('.total_due_table_'+ class_name +'').remove();
//                                            }
//                                        }
//										},
//										'after.ft.filtering': function(e, ft, filter) {
//											if (typeof filter !== 'undefined' && filter.length > 0) {
//												if (typeof self.$el.find('.' + ft.classes[3] + ' tfoot .total_due_table_'+ft.classes[3]).html() !== 'undefined'){
//													self.$el.find('.' + ft.classes[3] + ' tfoot .total_due_table_'+ft.classes[3]).hide();
//												}
//											}
//											else{
//												if (typeof self.$el.find('.' + ft.classes[3] + ' tfoot .total_due_table_'+ft.classes[3]).html() !== 'undefined'){
//													self.$el.find('.' + ft.classes[3] + ' tfoot .total_due_table_'+ft.classes[3]).show();
//												}
//											}
//										},
										'ready.ft.table': function(e, ft) {
//										    console.log(res[prop][0])
											var rows = ft.rows.all;
//											if (rows.length <= 10){
//												var tot_count = 0;var tot_sale = 0;var tot_cost = 0;var tot_profit = 0;var tot_profit_per = 0;
//												for (var i = 0, l = rows.length, row; i < l; i++){
//													row = rows[i].val();
//													tot_count += parseFloat(row["count"]);
//													tot_sale += parseFloat(row["total_sale"]);
//													tot_cost += parseFloat(row["cost"]);
//													tot_profit += parseFloat(row["profit"]);
//													tot_profit_per += parseFloat(row["profit_per"]);
//												}
//												var html = '<tr class=total_due_table_'+ class_name +'>';
//												html += '<td></td>';
//												html += '<td><b>Total: '+ tot_count.toFixed(3) +'</b></td>';
//												html += '<td><b>Total: '+ tot_sale.toFixed(3) +'</b></td>';
//												html += '<td><b>Total: '+ tot_cost.toFixed(3) +'</b></td>';
//												html += '<td><b>Total: '+ tot_profit.toFixed(3) +'</b></td>';
//												html += '<td></td>';
//												html += '</tr>';
//												var foot = self.$el.find('.' + ft.classes[3] + ' tfoot');
//												foot.prepend(html);
//											}
											for (var i = 0, l = rows.length, row; i < l; i++){
												row = rows[i].val();
												g_tot_count += parseFloat(row["count"]);
												g_tot_sale += parseFloat(row["total_sale"]);
												g_tot_cost += parseFloat(row["cost"]);
												g_tot_profit += parseFloat(row["profit"]);
												g_tot_profit_per += parseFloat(row["profit_per"]);
											}
										},
									}
								});
//							}
                            var g_html = '<th/>';
							g_html += '<th/>';
							g_html += '<th/>';
							g_html += '<th/>';
							g_html += '<th>'+ g_tot_count.toFixed(3).toLocaleString('en') +'</th>';
							g_html += '<th>'+ g_tot_sale.toFixed(3).toLocaleString('en') +'</th>';
							g_html += '<th>'+ g_tot_cost.toFixed(3).toLocaleString('en') +'</th>';
							g_html += '<th>'+ g_tot_profit.toFixed(3).toLocaleString('en') +'</th>';
							self.$el.find('.grand_table_per_date_container .tr_grand_total').append(g_html);
							self.$el.find('.grand_table_per_date_container').show();
                        }
                });
            }
            else{
                self.do_action('biztech_monthly_time_based_report.action_monthly_dashboard_wizard')
            }
        },
    });
    core.action_registry.add('open_monthly_time_based_report_view', MonthlyTimeBasedReport);
    return {
        MonthlyTimeBasedReport: MonthlyTimeBasedReport,
    };
});
