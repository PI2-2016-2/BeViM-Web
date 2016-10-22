$(document).ready(function() {

  $('#add_more').click(function() {
      var form_idx = $('#id_form-TOTAL_FORMS').val();
      $('#form_set').append($('#empty_form').html().replace(/__prefix__/g, form_idx));
      $('#buttons').append($('#column_remove_button').html().replace(/__prefix__/g, form_idx));
      $("#column_add_button").attr('class', 'col-md-1');
      $('#id_form-TOTAL_FORMS').val(parseInt(form_idx) + 1);
  });

  (function($) {

	  removeFrequency = function(row) {
		
		var frequency_field = "id_form-" + row + "-choose_frequency";
		var time_field = "id_form-" + row + "-job_time";
		var remove_button = "remove_button-" + row
		
		document.getElementById(frequency_field).remove();
		document.getElementById(time_field).remove();
		document.getElementById(remove_button).remove();

	    return false;
	  };
	})(jQuery);

});


