<%! script_url = '/count-buildings/_/main' %>
<%inherit file='crosscompute:templates/base.mako'/>

<h1>${title}</h1>
<p>Reveal regional population density.</p>

<form id=questions role=form>

  <div id=classifier_name_question class=form-group>
    <label for=classifier_name class=control-label>Which classifier will we use?</label>
    <select id=classifier_name class=form-control>
      <option value='myanmar4-20140708-001953'>myanmar4</option>
      <option value='uganda1-20140715-061930'>uganda1</option>
    </select>
  </div>

  <div id=image_url_question class=form-group>
    <label for=image_url class=control-label>From which URL will we download the image?</label>
    <input id=image_url type=text class=form-control value='http://backpack.invisibleroads.com/count-buildings/images/myanmar4-201200,2314700,201500,2314400.tif'>
  </div>

  <button id=run type=button class='btn btn-primary'>Count buildings</button>

</form>

<div id=results>
  <table id=target_table class=table></table>
  <button type=button class='btn btn-success download'>Download</button>
</div>

<div id=acknowledgments>
Thanks to
<a target=_blank href=https://github.com/sherpashaky>Shaky Sherpa</a>,
<a target=_blank href=http://www.earth.columbia.edu/articles/view/2770>Vijay Modi</a>,
<a target=_blank href=https://code.google.com/u/108586368378757621796/>Alex Krizhevsky</a>,
<a target=_blank href=https://github.com/dnouri>Daniel Nouri</a> and
<a target=_blank href=http://www.cs.toronto.edu/~ilya/<a/>Ilya Sutskever</a>.
</div>

<script>
var run_url = '${request.route_path("count-buildings")}';
</script>
