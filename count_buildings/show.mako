<%! script_url = '/count-buildings/_/main' %>
<%inherit file='crosscompute:templates/base.mako'/>

<h1>${title}</h1>
<p>Reveal regional population density.</p>
<p>Thanks to
<a target=_blank href=https://github.com/sherpashaky>Shaky Sherpa</a>,
<a target=_blank href=http://www.earth.columbia.edu/articles/view/2770>Vijay Modi</a>,
<a target=_blank href=https://www.linkedin.com/in/jruda>Jennifer Ruda</a>,
<a target=_blank href=https://code.google.com/u/108586368378757621796/>Alex Krizhevsky</a>,
<a target=_blank href=https://github.com/dnouri>Daniel Nouri</a>,
<a target=_blank href=http://www.cs.toronto.edu/~ilya/>Ilya Sutskever</a>,
<a target=_blank href=http://www.cs.toronto.edu/~ranzato/>Marc'Aurelio Ranzato</a> and
<a target=_blank href=http://yann.lecun.com/>Yann LeCun</a>.
</p>

<form id=questions role=form>

  <div id=source_method_question class='form-group hidden'>
    <div><label class=control-label>Where is the satellite image?</label></div>
    <div class="btn-group" data-toggle="buttons">
      <label class="btn btn-default" id="source_method_url"><input type="radio"> On the internet</label>
      <label class="btn btn-default" id="source_method_upload"><input type="radio"> In my computer</label>
    </div>
  </div>

  <div id=source_url_question class='form-group hidden'>
    <p><b>Paste the URL</b> of your satellite image</p>
    <select id=source_url class='form-control' style="width: 100%">
      <option value='http://backpack.invisibleroads.com/count-buildings/myanmar4-201200,2314700,201500,2314400.tif'>http://backpack.invisibleroads.com/count-buildings/myanmar4-201200,2314700,201500,2314400.tif</option>
      <option value='http://backpack.invisibleroads.com/count-buildings/myanmar4-204500,2314400,205500,2313800.tif'>http://backpack.invisibleroads.com/count-buildings/myanmar4-204500,2314400,205500,2313800.tif</option>
      <option value='http://backpack.invisibleroads.com/count-buildings/ethiopia0-0.tif'>http://backpack.invisibleroads.com/count-buildings/ethiopia0-0.tif</option>
      <option value='http://backpack.invisibleroads.com/count-buildings/ghana0-5.tif'>http://backpack.invisibleroads.com/count-buildings/ghana0-5.tif</option>
      <option value='http://backpack.invisibleroads.com/count-buildings/kenya0-0.tif'>http://backpack.invisibleroads.com/count-buildings/kenya0-0.tif</option>
      <option value='http://backpack.invisibleroads.com/count-buildings/malawi0-7.tif'>http://backpack.invisibleroads.com/count-buildings/malawi0-7.tif</option>
      <option value='http://backpack.invisibleroads.com/count-buildings/mali0-4.tif'>http://backpack.invisibleroads.com/count-buildings/mali0-4.tif</option>
      <option value='http://backpack.invisibleroads.com/count-buildings/myanmar0-8.tif'>http://backpack.invisibleroads.com/count-buildings/myanmar0-8.tif</option>
      <option value='http://backpack.invisibleroads.com/count-buildings/nigeria0-3.tif'>http://backpack.invisibleroads.com/count-buildings/nigeria0-3.tif</option>
      <option value='http://backpack.invisibleroads.com/count-buildings/rwanda0-8.tif'>http://backpack.invisibleroads.com/count-buildings/rwanda0-8.tif</option>
      <option value='http://backpack.invisibleroads.com/count-buildings/senegal0-7.tif'>http://backpack.invisibleroads.com/count-buildings/senegal0-7.tif</option>
      <option value='http://backpack.invisibleroads.com/count-buildings/tanzania0-7.tif'>http://backpack.invisibleroads.com/count-buildings/tanzania0-7.tif</option>
      <option value='http://backpack.invisibleroads.com/count-buildings/uganda0-9.tif'>http://backpack.invisibleroads.com/count-buildings/uganda0-9.tif</option>
    </select>

    <button type="button" class="btn btn-primary" id=import_source_url>
      Import satellite image from this URL
    </button>
    % if not user:
      (requires login)
    % endif
  </div>

  <div id=source_file_question class=hidden>
    <p><b>If your image is larger than 500mb</b>, please upload it to <a href="https://www.dropbox.com">Dropbox</a> or <a href="https://drive.google.com">Drive</a>.</p><p>Then you can paste the resulting URL <a id=source_method_url_link style="cursor:pointer">here</a>.</p>
    <span class="btn btn-primary fileinput-button">
      <span>Upload satellite image from my computer</span>
      <input id="source_file" type="file">
    </span>
    % if not user:
      (requires login)
    % endif
    <div id="progress" class="progress">
      <div class="progress-bar progress-bar-success"></div>
    </div>
  </div>

  <table id=geoimage_properties class='table hidden'>
    <tr><td>Proj4</td><td id=proj4></td></tr>
    <tr><td>Band count</td><td id=band_count></td></tr>
    <tr><td>Pixel dimensions</td><td id=pixel_dimensions></td></tr>
    <tr><td>Metric dimensions</td><td id=metric_dimensions></td></tr>
  </table>

  <div id=geoimage_preview></div>

  <div id=classifier_name_question class='form-group hidden'>
    <label for=classifier_name class=control-label>Which classifier will we use?</label>
    <select id=classifier_name class=form-control>
      <option value='generic-20150507-123711'>generic-20150507-123711</option>
    </select>
  </div>

</form>

<div id=results>
  <button id=preview type=button class='btn btn-info hidden'>
    Preview building locations in part of the image
  </button>
  <div id=preview_images class=hidden></div>
  <div id=feedback class=hidden></div>
  <button id=run type=button class='btn btn-primary hidden'>
    Get building locations over the whole image as a shapefile for <span id=price>$100</span>
  </button>
  <button id=credit type=button class='btn btn-danger hidden'>
    Add credit and run
  </button>

  <button type=button class='btn btn-success download hidden'>Download building locations as a shapefile</button>
</div>

<script>
var run_url = '${request.route_path("count-buildings")}';
var import_geoimage_url = "${request.route_path('import-geoimage')}";
</script>
