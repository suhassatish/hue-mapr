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

<%namespace name="macros" file="macros.mako" />
<%namespace name="actionbar" file="actionbar.mako" />

${ commonheader(_('Search'), "search", user, "29px") | n,unicode }

<link rel="stylesheet" href="/search/static/css/admin.css">

<div class="search-bar" style="height: 30px">
  <div class="pull-right" style="margin-top: 4px; margin-right: 20px">
    <a href="${ url('search:index') }"><i class="fa fa-share"></i> ${ _('Search page') }</a>
  </div>
  <h4>${_('Collection Manager')}</h4>
</div>


<div class="container-fluid">
  <div class="row-fluid">

    <div class="span3">
      <div class="sidebar-nav card-small">
        <ul class="nav nav-list">
          <li class="nav-header">${_('Actions')}</li>
          <li><a href=""><i class="fa fa-files-o"></i> ${_('Create a new collection from a file')}</a></li>
          <li><a href=""><i class="fa fa-wrench"></i> ${_('Create a new collection manually')}</a></li>
        </ul>
      </div>
    </div>

    <div class="span9">
      <div class="card wizard">
        <h1 class="card-heading simple">${_("Create collection manually")}</h1>
        <div class="card-body">
          <form class="form form-horizontal">
            <div data-bind="template: { 'name': wizard.current().name }"></div>
            <br />
            <a data-bind="routie: 'wizard/' + wizard.previous().url(), visible: wizard.hasPrevious" class="btn btn-info" href="javascript:void(0)">${_('Previous')}</a>
            <a data-bind="routie: 'wizard/' + wizard.next().url(), visible: wizard.hasNext" class="btn btn-info" href="javascript:void(0)">${_('Next')}</a>
            <a data-bind="click: save, visible: !wizard.hasNext()" class="btn btn-info" href="javascript:void(0)">${_('Finish')}</a>
          </form>
        </div>
      </div>
    </div>

  </div>
</div>


<!-- Start Wizard -->
<script type="text/html" id="step-1">
  <div class="control-group">
    <label for="name" class="control-label">${_("Name")}</label>
    <div class="controls">
      <input data-bind="value: collection.name" name="name" type="text" placeholder="${_('Name of collection')}" />
    </div>
  </div>
</script>

<script type="text/html" id="step-2">
  <formset data-bind="foreach: collection.fields">
    <div class="control-group">
      <label for="name" class="control-label">${_("Name")}</label>
      <div class="controls">
        <input data-bind="value: name" name="name" type="text" placeholder="${_('Name of field')}" />
      </div>
    </div>

    <div class="control-group">
      <label for="type" class="control-label">${_("Type")}</label>
      <div class="controls">
        <input data-bind="value: type" name="type" type="text" placeholder="${_('Type of field')}" />
      </div>
    </div>

    <a data-bind="click: remove" href="javascript:void(0)" class="btn btn-error"><i class="fa fa-minus"></i>&nbsp;${_("Remove field")}</a>
  </formset>

  <br />
  <br />
  <a data-bind="click: collection.newField" href="javascript:void(0)" class="btn btn-info"><i class="fa fa-plus"></i>&nbsp;${_("Add field")}</a>
</script>
<!-- End Wizard -->


<script src="/static/ext/js/routie-0.3.0.min.js" type="text/javascript" charset="utf-8"></script>
<script src="/static/ext/js/knockout-min.js" type="text/javascript" charset="utf-8"></script>
<script src="/static/ext/js/knockout.mapping-2.3.2.js" type="text/javascript" charset="utf-8"></script>
<script src="/search/static/js/create-collections.ko.js" type="text/javascript" charset="utf-8"></script>

<script type="text/javascript">
var vm = new CreateCollectionViewModel([
  {'name': 'step-1', 'url': 'name'},
  {'name': 'step-2', 'url': 'fields'}
]);

routie({
  "wizard/:step": function(step) {
    vm.wizard.setIndexByUrl(step);
  },
  "*": function() {
    routie('wizard/step-1');
  },
});

ko.applyBindings(vm);
</script>

${ commonfooter(messages) | n,unicode }
