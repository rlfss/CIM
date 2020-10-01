odoo.define('general_request.form', function (require) {
'use strict';

var core = require('web.core');



$(#mySelect).(function() {

    	/* Half Day Checkbox */
    	function check_from_duration($this){
            var $challenges_details = $('#from_period_div');
            var $challenges_input = $challenges_details.find('#select_from_period');
            if ($this.prop('checked'))
            {
            	$challenges_details.show();
            	$challenges_input.attr('required','required');
            }
            else
            {
            	$challenges_details.hide();
            	$challenges_input.removeAttr('required');
            	$challenges_input.val('')
            }
        }

});