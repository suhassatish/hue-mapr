// Licensed to Cloudera, Inc. under one
// or more contributor license agreements.  See the NOTICE file
// distributed with this work for additional information
// regarding copyright ownership.  Cloudera, Inc. licenses this file
// to you under the Apache License, Version 2.0 (the
// "License"); you may not use this file except in compliance
// with the License.  You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.


function BeeswaxViewModel(server) {
  var self = this;

  self.server = ko.observable(server);
  self.databases = ko.observableArray();
  self.selectedDatabase = ko.observable(0);
  self.query = ko.mapping.fromJS({
    'id': -1,
    'query': '',
    'name': null,
    'description': null,
    'errors': []
  });
  self.rows = ko.observableArray();
  self.columns = ko.observableArray();
  self.resultsEmpty = ko.observable(false);
  self.settings = ko.observableArray();
  self.fileResources = ko.observableArray();
  self.functions = ko.observableArray();

  self.database = ko.computed({
    'read': function() {
      if (self.databases()) {
        return self.databases()[self.selectedDatabase()];
      } else{
        return "";
      }
    },
    'write': function(value) {
      self.selectedDatabase(self.databases.indexOf(value));
    }
  });

  self.getFirstDatabase = function() {
    if (self.databases()) {
      return self.databases()[0];
    } else {
      return null;
    }
  };

  self.updateResults = function(results) {
    var rows = [];
    self.columns.removeAll();  // Needed for datatables to refresh properly.
    self.columns(results.columns);
    self.rows.removeAll();
    self.rows(results.rows);
  };

  self.updateDatabases = function(databases) {
    self.databases(databases);

    var key = 'hueBeeswaxLastDatabase-' + self.server();
    var last = $.totalStorage(key) || ((databases.length > 0) ? databases[0] : null);
    if (last) {
      self.database(last);
    }
  };

  self.updateSettings = function(settings) {
    self.settings(settings);
  };

  self.updateFileResources = function(file_resources) {
    self.fileResources(file_resources);
  };

  self.updateFunctions = function(functions) {
    self.functions(functions);
  };

  self.updateQuery = function(design) {
    self.query.query(design.query);
    self.query.id(design.id);
    self.query.name(design.name);
    self.query.description(design.desc);
    self.database(design.database);
  };

  self.chooseDatabase = function(value, e) {
    var key = 'hueBeeswaxLastDatabase-' + self.server().name();
    self.selectedDatabase(self.databases.indexOf(value));
    $.totalStorage(key, value);
  };

  self.getSettingsFormData = function() {
    var data = {
      'settings-next_form_id': self.settings().length
    };
    var index = 0;
    ko.utils.arrayForEach(self.fileResources, function(setting) {
      data['settings-' + index + '-key'] = setting.key();
      data['settings-' + index + '-value'] = setting.value();
    });
    return data;
  };

  self.getFileResourcesFormData = function() {
    var data = {
      'file_resources-next_form_id': self.fileResources().length
    };
    var index = 0;
    ko.utils.arrayForEach(self.fileResources, function(file_resource) {
      data['file_resources-' + index + '-key'] = file_resource.key();
      data['file_resources-' + index + '-value'] = file_resource.value();
    });
    return data;
  };

  self.getFunctionsFormData = function() {
    var data = {
      'functions-next_form_id': self.functions().length
    };
    var index = 0;
    ko.utils.arrayForEach(self.functions, function(_function) {
      data['functions-' + index + '-key'] = _function.key();
      data['functions-' + index + '-value'] = _function.value();
    });
    return data;
  };

  var error_fn = function(jqXHR, status, errorThrown) {
    try {
      $(document).trigger('server.error', $.parseJSON(jqXHR.responseText));
    } catch(e) {
      $(document).trigger('server.unmanageable_error', jqXHR.responseText);
    }
  };

  self.explainQuery = function() {
    var data = ko.mapping.toJS(self.query);
    data.database = self.database();
    var request = {
      url: '/' + self.server() + '/api/explain/',
      dataType: 'json',
      type: 'POST',
      success: function(data) {
        self.query.errors.removeAll();
        if (data.status === 0) {
          $(document).trigger('explain.query', data);
          self.updateResults(data.results);
          self.query.id(data.design);
          self.resultsEmpty(data.results.rows.length === 0);
          $(document).trigger('explained.query', data);
        } else {
          self.query.errors.push(data.message);
        }
      },
      error: error_fn,
      data: data
    };
    $.ajax(request);
  };

  self.fetchQuery = function(id) {
    var _id = id || self.query.id();
    if (_id && _id != -1) {
      var request = {
        url: '/beeswax/api/query/' + _id + '/get',
        dataType: 'json',
        type: 'GET',
        success: function(data) {
          self.updateQuery(data.design);
        },
        error: error_fn
      };
      $.ajax(request);
    }
  };

  self.saveQuery = function() {
    var self = this;
    if (self.query.query() && self.query.name()) {
      var data = ko.mapping.toJS(self.query);
      data['desc'] = data['description'];
      data['database'] = self.database();
      var url = '/' + self.server() + '/api/query/';
      if (self.query.id() && self.query.id() != -1) {
        url += self.query.id() + '/';
      }
      var request = {
        url: url,
        dataType: 'json',
        type: 'POST',
        success: function(data) {
          $(document).trigger('saved.query', data);
        },
        error: function() {
          $(document).trigger('error.query');
        },
        data: data
      };
      $.ajax(request);
    }
  };

  self.executeQuery = function() {
    var data = {
      'query-query': self.query.query(),
      'query-database': self.database()
    }
    $.extend(data, self.getSettingsFormData());
    $.extend(data, self.getFileResourcesFormData());
    $.extend(data, self.getFunctionsFormData());
    var request = {
      url: '/' + self.server() + '/api/execute/',
      dataType: 'json',
      type: 'POST',
      success: function(data) {
        self.query.errors.removeAll();
        if (data.status == 0) {
          $(document).trigger('execute.query', data);
          self.updateResults(data.results);
          self.query.id(data.design);
          self.resultsEmpty(data.results.rows.length === 0);
          $(document).trigger('executed.query', data);
        } else {
          self.query.errors.push(data.message);
        }
      },
      error: error_fn,
      data: data
    };
    $.ajax(request);
  };

  self.watchQuery = function() {
    
  };

  self.fetchDatabases = function() {
    var request = {
      url: '/' + self.server() + '/api/databases',
      dataType: 'json',
      type: 'GET',
      success: function(data) {
        self.updateDatabases(data.databases);
      },
      error: error_fn
    };
    $.ajax(request);
  };
}
