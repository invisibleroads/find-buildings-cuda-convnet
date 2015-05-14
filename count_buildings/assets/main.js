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
      $('#proj4').html(summary.proj4);
      $('#band_count').html(summary.band_count);
      $('#pixel_dimensions').html(summary.pixel_dimensions[0] + 'x' + summary.pixel_dimensions[0] + ' pixels');
      $('#metric_dimensions').html(summary.metric_dimensions[0] + 'x' + summary.metric_dimensions[1] + ' meters');
      $('#geoimage_properties').data('result_id', result.id).reveal();
      $('#classifier_name_question').reveal().find('select').click(function() {
        $('#check').prop('disabled', false).reveal()
      });
    }

    function process_import_geoimage_error(result) {
      $('#feedback').html('The file format you uploaded is not supported. Please make sure that you upload a GeoTIFF satellite image. The image should ideally contain four bands (red, green, blue, near-infrared) and have a resolution between 0.5 meters per pixel and 0.6 meters per pixel.').show();
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
      }, process_import_geoimage, process_import_geoimage_error);
    });

    $('#source_file').make_upload_button({
    }).on('uploaded', function(e, upload_ids) {
      reset();
      cc.post(import_geoimage_url, {
        source_upload: upload_ids[0]
      }, {
        message: 'Importing satellite image...'
      }, process_import_geoimage, process_import_geoimage_error);
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
        message: '<p>Counting buildings...</p><p>Please be patient as this can take anywhere from five minutes to several hours. You can check progress <a href=/manage target=_blank>here</a>.</p>',
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

    $('#source_method_question').reveal();

  });
});
