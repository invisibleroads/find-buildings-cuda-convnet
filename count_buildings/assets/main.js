require.config({
  paths: {
    base: static_url + 'base',
    'stripe.checkout': [
      '//checkout.stripe.com/checkout'
    ],
    'select2': [
      '//cdnjs.cloudflare.com/ajax/libs/select2/4.0.0/js/select2.min'
    ]
  }
});
require(['base', 'stripe.checkout', 'select2'], function(base) {
  require(['cc'], function(cc) {

    function reset() {
      $('#import_source_url').prop('disabled', false);
      $('#geoimage_properties').hide();
      $('#geoimage_preview').hide();
      $('#classifier_name_question').hide();
      $('#results > *').hide();
      $('#run').hide();
    }
    $('#source_method_url_link').click(function() {
      $('#source_method_url').click();
    });
    $('#source_method_url').click(function() {
      $('#geoimage_properties').hide();
      $('#geoimage_preview').hide();

      $('#source_url_question').reveal();
      $('#source_url').prop('disabled', false);
      $('#source_file_question').hide();
      reset();
    });

    $('#source_method_upload').click(function() {
      $('#geoimage_properties').hide();
      $('#geoimage_preview').hide();

      $('#source_url_question').hide();
      $('#source_file').prop('disabled', false);
      $('#source_file_question').reveal();
      reset();
    });

    function process_import_geoimage(result) {
      var summary = result.summary;
      $('#proj4').html(summary.proj4);
      $('#band_count').html(summary.band_count);
      $('#pixel_dimensions').html(summary.pixel_dimensions[0] + 'x' + summary.pixel_dimensions[0] + ' pixels');
      $('#metric_dimensions').html((summary.metric_dimensions[0]).toFixed(0) + 'x' + (summary.metric_dimensions[1]).toFixed(0) + ' meters');
      $('#geoimage_properties').data('result_id', result.id).reveal();

      $('#geoimage_preview').html('');
      for (var i = 0; i < summary.preview_image_names.length; i++) {
        $('#geoimage_preview').append('<p><img id=geoimage_preview' + i + ' src=/download/' + result.id + '/' + summary.preview_image_names[i] + '></p>');
      }
      var area_in_square_km = (summary.metric_dimensions[0] / 1000) * (summary.metric_dimensions[1] / 1000);
      $('#geoimage_preview' + (i - 1)).load(function() {
        $('#classifier_name_question').reveal();
        $('#preview').reveal();
        $('#price').html('$' + (area_in_square_km * 0.5).toFixed(2));
        $('#run').prop('disabled', false).reveal();
      });
      $('#geoimage_preview').reveal();
    }

    function process_import_geoimage_error(result) {
      var message;
      switch(result.summary.exception_arguments[0]) {
        case 'invalid_url':
          message = 'The URL does not exist or has restricted permissions.';
          break;
        case 'unsupported_format':
          message = 'The file format you uploaded is not supported. Please make sure that you upload a GeoTIFF satellite image. The image should ideally contain four bands (red, green, blue, near-infrared) and have a resolution between 0.5 meters per pixel and 0.6 meters per pixel.';
          break;
      }
      $('#feedback').html(message).reveal();
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
    }).on('uploading', function(e) {
      reset();
      $('#feedback').html('Uploading satellite image (this could take some time)...').reveal();
    }).on('uploaded', function(e, upload_ids) {
      reset();
      cc.post(import_geoimage_url, {
        source_upload: upload_ids[0]
      }, {
        message: 'Importing satellite image...'
      }, process_import_geoimage, process_import_geoimage_error);
    });

    $('#preview').click(function() {
      $('#preview').prop('disabled', true);
      $('#run').prop('disabled', true);
      cc.post(run_url, {
        source_geoimage: $('#geoimage_properties').data('result_id'),
        classifier_name: $('#classifier_name').val(),
        is_preview: 1
      }, {
        message: '<p>Generating preview...</p>'
      }, function(result) {
        var summary = result.summary;

        $('#preview_images').html('').reveal();
        for (var i = 0; i < summary.preview_image_names.length; i++) {
          $('#preview_images').append("<p><img id=preview_image" + i + " src=/download/" + result.id + "/" + summary.preview_image_names[i] + "><br>Estimated count in the above image = " + summary.estimated_counts[i] + "</p>");
        }
        $('#preview_image' + (i - 1)).load(function() {
          $('#run').reveal();
        });

        $('#preview').prop('disabled', false);
        $('#run').prop('disabled', false);
      });
    });

    $('#run').click(function() {
      $('#preview').prop('disabled', true);
      $('#run').prop('disabled', true);
      $('#credit').hide();
      cc.post(run_url, {
        source_geoimage: $('#geoimage_properties').data('result_id'),
        classifier_name: $('#classifier_name').val()
      }, {
        message: '<p>Counting buildings...</p><p>Please be patient as this can take anywhere from five minutes to several hours. You can check progress <a href=/manage target=_blank>here</a>.</p>',
        end: true
      }, function(result) {
        var summary = result.summary;

        $('#preview_images').html('<p><img id=preview_image src=/download/' + result.id + '/' + summary.preview_image_name + '><br>Estimated count over the whole image = ' + summary.estimated_count + '</p>').reveal();
        $('#preview_image').load(function() {
          $('.download').reveal();
        });

        $('#preview').prop('disabled', false).hide();
        $('#run').prop('disabled', false).hide();
      });
    });

    $('#source_url').select2({tags: true});
    $('#source_method_question').reveal();

  });
});
