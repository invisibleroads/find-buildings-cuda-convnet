require.config({
  paths: {
    base: static_url + 'base'
  }
});
require(['base'], function(base) {
  require(['cc'], function(cc) {

    function reset() {
      $('#import_source_url').prop('disabled', false);
      $('#geoimage_properties').hide();
      $('#classifier_name_question').hide();
      $('#results > *').hide();
      $('#check').hide();
      $('#run').hide();
      $('#acknowledgments').hide();
    }

    $('#source_method_url').click(function() {
      $('#source_url_question').reveal();
      $('#source_url').prop('disabled', false);
      $('#source_file_question').hide();
      reset();
    });

    $('#source_method_upload').click(function() {
      $('#source_url_question').hide();
      $('#source_file_question').reveal();
      reset();
    });

    function process_import_geoimage(result) {
        var summary = result.summary;
        try {
          var units = /\+units=(\S+)/.exec(summary.proj4)[1];
        } catch(e) {
          var units = '';
        }
        $('#proj4').html(summary.proj4);
        $('#band_count').html(summary.band_count);
        $('#pixel_dimensions').html(summary.pixel_dimensions[0] + 'x' + summary.pixel_dimensions[0] + ' pixels');
        $('#dimensions').html(summary.dimensions[0] + 'x' + summary.dimensions[1] + ' ' + units);
        $('#geoimage_properties').data('result_id', result.id).reveal();
        $('#classifier_name_question').reveal().find('select').click(function() {
          $('#check').prop('disabled', false).reveal()
        });
    }

    $('#import_source_url').click(function() {
      if (!window.user_id) {
        window.location = login_url;
        return;
      }
      $(this).prop('disabled', true);
      reset();
      cc.post(import_geoimage_url, {
        source_url: $('#source_url').val()
      }, {
        message: 'Importing satellite image...'
      }, process_import_geoimage);
    });

    $('#source_file').make_upload_button({
    }).on('uploaded', function(e, upload_ids) {
      reset();
      cc.post(import_geoimage_url, {
        source_upload: upload_ids[0]
      }, {
        message: 'Importing satellite image...'
      }, process_import_geoimage);
    });

    $('#check').click(function() {
      $('#check').prop('disabled', true);
      $.post(run_url, {
        check: 1,
        source_geoimage: $('#geoimage_properties').data('result_id'),
        classifier_name: $('#classifier_name').val()
      }, function(data) {
        $('#price').html('$' + (data.price / 100).toFixed(2));
        $('#run').reveal();
      });
    });

    $('#run').click(function() {
      $('#run').prop('disabled', true);
      cc.post(run_url, {
        source_geoimage: $('#geoimage_properties').data('result_id'),
        classifier_name: $('#classifier_name').val()
      }, {
        message: 'Counting buildings...',
        end: true
      }, function(result) {
        var summary = result.summary;
        $('#estimated_count').html(summary.estimated_count);
        $('#target_table').data('result_id', result.id).reveal();
        $('#run').prop('disabled', false);
      });
    });

    $('#credit').click(function() {
      if (!window.user_id) {
        window.location = login_url;
        return;
      };
      window.location = '/manage';
    });

    $('#source_method_question').show();

  });
});
