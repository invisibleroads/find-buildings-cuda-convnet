<%! script_url = '/count-buildings/_/main' %>
<%inherit file='crosscompute:templates/base.mako'/>

<h1>${title}</h1>
<p>Reveal regional population density.</p>

<form id=questions role=form>

  <div id=source_method_question class='form-group hidden'>
    <div><label class=control-label>Where is the satellite image?</label></div>
    <div class="btn-group" data-toggle="buttons">
      <label class="btn btn-default" id="source_method_url"><input type="radio"> URL</label>
      <label class="btn btn-default" id="source_method_upload"><input type="radio"> Upload</label>
    </div>
  </div>

  <div id=source_url_question class='form-group hidden'>
    <input id=source_url type=text class=form-control value='http://backpack.invisibleroads.com/count-buildings/images/myanmar4-201200,2314700,201500,2314400.tif'>
    <button type="button" class="btn btn-primary" id=import_source_url>Import satellite image</button>
  </div>

  <div id=source_file_question class=hidden>
    <div class='btn btn-primary fileinput-button'>
      <span>Upload satellite image</span>
      <input id=source_file type=file>
    </div>
  </div>

  <table id=geoimage_properties class='table hidden'>
    <tr><td>Proj4</td><td id=proj4></td></tr>
    <tr><td>Band count</td><td id=band_count></td></tr>
    <tr><td>Pixel dimensions</td><td id=pixel_dimensions></td></tr>
    <tr><td>Dimensions</td><td id=dimensions></td></tr>
  </table>

  <div id=classifier_name_question class='form-group hidden'>
    <label for=classifier_name class=control-label>Which classifier will we use?</label>
    <select id=classifier_name class=form-control>
      <option value='myanmar4-20140708-001953'>myanmar4-20140708-001953</option>
    </select>
  </div>

  <button id=check type=button class='btn btn-info hidden'>
    Check price
  </button>

  <button id=run type=button class='btn btn-primary hidden'>
    Count buildings for <span id=price>free</span>
  </button>

  <button id=credit type=button class='btn btn-danger hidden'>
    Add credit 
  </button>

</form>

<div id=results>
  <div id=feedback class=hidden></div>
  <table id=target_table class='table hidden'>
    <tr><td>Estimated count</td><td id=estimated_count></td></tr>
  </table>
  <button type=button class='btn btn-success download hidden'>Download</button>
</div>

<div id=acknowledgments class=hidden>
Thanks to
<a target=_blank href=https://github.com/sherpashaky>Shaky Sherpa</a>,
<a target=_blank href=http://www.earth.columbia.edu/articles/view/2770>Vijay Modi</a>,
<a target=_blank href=https://code.google.com/u/108586368378757621796/>Alex Krizhevsky</a>,
<a target=_blank href=https://github.com/dnouri>Daniel Nouri</a>,
<a target=_blank href=http://www.cs.toronto.edu/~ilya/>Ilya Sutskever</a>,
<a target=_blank href=http://www.cs.toronto.edu/~ranzato/>Marc'Aurelio Ranzato</a>,
<a target=_blank href=http://yann.lecun.com/>Yann LeCun</a>.
</div>

<script>
var run_url = '${request.route_path("count-buildings")}';
var import_geoimage_url = "${request.route_path('import-geoimage')}";
</script>
