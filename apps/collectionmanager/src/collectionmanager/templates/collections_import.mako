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

${ commonheader(_('Collection Manager'), "collectionmanager", user, "29px") | n,unicode }

<link rel="stylesheet" href="/collectionmanager/static/css/admin.css">  
<link rel="stylesheet" href="/static/ext/chosen/chosen.min.css">

<style>
.importable-table-container {
  max-height: 500px;
  overflow: auto;
}
</style>

<div class="search-bar" style="height: 30px">
  <h4><a href="/collectionmanager">${_('Collection Manager')}</a></h4>
</div>


<div class="container-fluid">
  <div class="row-fluid">

    <div class="span3">
      <div class="sidebar-nav card-small">
        <ul class="nav nav-list">
          <li class="nav-header">${_('Actions')}</li>
          <li><a href="/collectionmanager/import"><i class="fa fa-plus-circle"></i> ${ _('Import an existing collection') }</a></li>
          <li><a href="/collectionmanager/create/file/"><i class="fa fa-files-o"></i> ${_('Create a new collection from a file')}</a></li>
          <li><a href="/collectionmanager/create/manual/"><i class="fa fa-wrench"></i> ${_('Create a new collection manually')}</a></li>
        </ul>
      </div>
    </div>

    <div class="span9">
      <div class="card wizard">
        <h1 class="card-heading simple">${_("Import collection")}</h1>
        <div class="card-body">
          <div class="importable-table-container">
            <table class="importable-table">
              <tbody data-bind="visible: importable().length > 0, foreach: importable">
                <tr>
                  <td width="24">
                    <div data-bind="click: handleSelect, css: {hueCheckbox: true, 'fa': true, 'fa-check': selected}"></div>
                  </td>
                  <td data-bind="text: name"></td>
                </tr>
              </tbody>
            </table>
          </div>

          <br />

          <a href="javascript:void(0)" class="btn" data-dismiss="modal">${ _('Cancel') }</a>
          <a href="javascript:void(0)" class="btn btn-primary disable-feedback" data-bind="enable: selectedImportable().length > 0, click: importSelected">${ _('Import Selected') }</a>
          
          <br />
          <br />
        </div>
      </div>
    </div>


  </div>
</div>


<script src="/static/ext/js/routie-0.3.0.min.js" type="text/javascript" charset="utf-8"></script>
<script src="/static/ext/js/knockout-min.js" type="text/javascript" charset="utf-8"></script>
<script src="/static/ext/js/knockout.mapping-2.3.2.js" type="text/javascript" charset="utf-8"></script>
<script src="/collectionmanager/static/js/collections.ko.js" type="text/javascript" charset="utf-8"></script>
<script src="/collectionmanager/static/js/import-collection.ko.js" type="text/javascript" charset="utf-8"></script>
<script src="/static/ext/chosen/chosen.jquery.min.js" type="text/javascript" charset="utf-8"></script>

<script type="text/javascript">
var vm = new ImportCollectionViewModel();
ko.applyBindings(vm);

vm.loadCollectionsAndCores();

function handleSelect(collection_or_core, event) {
  collection_or_core.selected(!collection_or_core.selected());
}
</script>

${ commonfooter(messages) | n,unicode }
