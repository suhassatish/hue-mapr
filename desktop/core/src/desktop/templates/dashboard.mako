## Licensed to Cloudera, Inc. under one
## or more contributor license agreements.  See the NOTICE file
## distributed with this work for additional information
## regarding copyright ownership.  Cloudera, Inc. licenses this file
## to you under the Apache License, Version 2.0 (the
## "License"); you may not use this file except in compliance
## with the License.  You may obtain a copy of the License at
##
##     http://www.apache.org/licenses/LICENSE-2.0
##
## Unless required by applicable law or agreed to in writing, software
## distributed under the License is distributed on an "AS IS" BASIS,
## WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
## See the License for the specific language governing permissions and
## limitations under the License.
<%!
  from desktop.views import commonheader, commonfooter
  from django.utils.translation import ugettext as _
%>

${ commonheader(_('My Dashboard'), "dashboard", user) | n,unicode }

<style type="text/css">
  .card .card-heading.simple {
    font-size: 16px;
    line-height: 30px;
  }
</style>

<div class="navbar navbar-inverse navbar-fixed-top nokids">
  <div class="navbar-inner">
    <div class="container-fluid">
      <div class="nav-collapse">
        <ul class="nav">
          <li class="currentApp">
            <a href="${ url('desktop.views.home') }">
              <img src="/static/art/home.png" />
              ${ _('My dashboard') }
            </a>
           </li>
        </ul>
      </div>
    </div>
  </div>
</div>

<div class="container-fluid">
  <div class="row-fluid">
    <div class="span4">
      <div class="card card-home" style="margin-top: 0">
        <h2 class="card-heading simple">${_('Awesome lines')}</h2>
        <div class="card-body">
          <p>
          <div id="linesample"></div>
          </p>
        </div>
      </div>
    </div>

    <div class="span4">
      <div class="card card-home" style="margin-top: 0">
        <h2 class="card-heading simple">${_('Awesome points')}</h2>
        <div class="card-body">
          <p>
          <div id="pointsample"></div>
          </p>
        </div>
      </div>
    </div>

    <div class="span4">
      <div class="card card-home" style="margin-top: 0">
        <h2 class="card-heading simple">${_('Awesome bars')}</h2>
        <div class="card-body">
          <p>
          <div id="barsample"></div>
          </p>
        </div>
      </div>
    </div>

  </div>
</div>

<link href="/static/ext/css/leaflet.css" rel="stylesheet">

<script src="/static/ext/js/jquery/plugins/jquery.flot.min.js" type="text/javascript" charset="utf-8"></script>
<script src="/static/ext/js/jquery/plugins/jquery.flot.categories.min.js" type="text/javascript" charset="utf-8"></script>
<script src="/static/ext/js/leaflet/leaflet.js" type="text/javascript" charset="utf-8"></script>
<script src="/static/js/jquery.blueprint.js"></script>

<script type="text/javascript" charset="utf-8">
  var d1 = [];
		for (var i = 0; i < 14; i += 0.5) {
			d1.push([i, Math.sin(i)]);
		}
  var d6 = [];
  for (var i = 0; i < 14; i += 0.5 + Math.random()) {
    d6.push([i, Math.sqrt(2*i + Math.sin(i) + 5)]);
  }


  var piedata = [
		{ label: "Series1",  data: 10, color: $.jHueBlueprint.COLORS.GREEN},
		{ label: "Series2",  data: 30, color: $.jHueBlueprint.COLORS.ORANGE},
		{ label: "Series3",  data: 90, color: $.jHueBlueprint.COLORS.BLUE}
  ];


  $(document).ready(function () {

    $("#linesample").jHueBlueprint({
    data: d6,
    type: $.jHueBlueprint.TYPES.LINECHART,
    color: $.jHueBlueprint.COLORS.GREEN
  });
  $("#linesample").jHueBlueprint("add", {
    data: d1,
    type: $.jHueBlueprint.TYPES.LINECHART,
    color: $.jHueBlueprint.COLORS.ORANGE,
    fill: true
  });

  $("#barsample").jHueBlueprint({
    data: d6,
    type: $.jHueBlueprint.TYPES.BARCHART,
    color: $.jHueBlueprint.COLORS.GREEN,
    fill: true
  });
  $("#barsample").jHueBlueprint("add", {
    data: d1,
    type: $.jHueBlueprint.TYPES.BARCHART,
    color: $.jHueBlueprint.COLORS.ORANGE,
    fill: false
  });

    $("#pointsample").jHueBlueprint({
    data: d1,
    type: $.jHueBlueprint.TYPES.POINTCHART,
    color: $.jHueBlueprint.COLORS.ORANGE,
    fill: false
  });

    $("#pointsample").jHueBlueprint("add", {
    data: d6,
    type: $.jHueBlueprint.TYPES.POINTCHART,
    color: $.jHueBlueprint.COLORS.BLUE,
    fill: true
  });

##    $("#piesample").jHueBlueprint({
##      data: piedata,
##      type: $.jHueBlueprint.TYPES.PIECHART
##    });

  });
</script>

${ commonfooter(messages) | n,unicode }
