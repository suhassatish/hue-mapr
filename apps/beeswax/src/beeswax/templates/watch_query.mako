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

<%namespace name="layout" file="layout.mako" />

${ commonheader(_('Query'), app_name, user) | n,unicode }
${layout.menubar(section='query')}

<div id="logs" class="card">
  <h1 class="card-heading simple">${_("Executing query...")}</h1>
  <div class="card-body">
    <pre data-bind="text: $root.design.watch.logs().join('\n')"></pre>
  </div>
</div>

<script src="/static/ext/js/knockout-min.js" type="text/javascript" charset="utf-8"></script>
<script src="/static/ext/js/knockout.mapping-2.3.2.js" type="text/javascript" charset="utf-8"></script>
<script src="/beeswax/static/js/beeswax.vm.js"></script>


<style type="text/css">
html, body {
  height: 100%;
}

body {
  padding-top: 0px;
}

#logs {
  position: absolute;
  top: 90px;
  right: 0px;
  bottom: 20px;
  left: 0px;

  overflow: auto;
}

h1 {
  margin-bottom: 5px;
}
</style>

<link href="/static/ext/css/leaflet.css" rel="stylesheet">

<script src="/static/ext/js/jquery/plugins/jquery-fieldselection.js" type="text/javascript"></script>
<script src="/beeswax/static/js/autocomplete.utils.js" type="text/javascript" charset="utf-8"></script>

<link rel="stylesheet" href="/static/ext/chosen/chosen.min.css">
<script src="/static/ext/chosen/chosen.jquery.min.js" type="text/javascript" charset="utf-8"></script>

<script type="text/javascript" charset="utf-8">

// Knockout
var viewModel = new BeeswaxViewModel("${app_name}");
viewModel.design.history.id(${query.id});
viewModel.fetchQueryHistory();
$(document).on('fetched.query', function(e) {
  viewModel.watchQueryLoop();
});
$(document).on('stop_watch.query.query', function(e) {
  if (viewModel.design.results.errors().length == 0) {
    window.location.href = "${success_url}";
  }
});
ko.applyBindings(viewModel);

</script>

${ commonfooter(messages) | n,unicode }
