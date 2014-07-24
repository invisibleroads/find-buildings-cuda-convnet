require.config({
  paths: {
    common: static_url + 'common'
  }
});
require(['common'], function(common) {
  require(['cc'], function(cc) {

    $('#classifier_name_question').show().find('select').click(function() {
      $('#image_url_question, #run').reveal();
    });

    $('#run').click(function() {

      if (!window.user_id) {
        window.location = login_url;
        return false;
      }

      $('#run').prop('disabled', true);

      var $target = $('#target_table').html('Counting buildings...').reveal();
      $('html').animate({scrollTop: $target.offset().top}, 500);

      cc.post(run_url, {
        classifier_name: $('#classifier_name').val(),
        image_url: $('#image_url').val()
      }, {
        end: true
      }, function(result) {
        var summary = result.summary;
        var columns = summary.columns, rows = summary.rows;
        $target
          .data('result_id', result.id)
          .fill_table(columns, rows);
        $('#run').prop('disabled', false);
      });
    });

  });
});
