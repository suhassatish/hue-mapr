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


function sparkViewModel() {
  var self = this;

  self.appNames = ko.observableArray(); // list of jars
  self.selectedAppName = ko.observable(0);
  self.classPathes = ko.observableArray(); // read from upload or edit manually or better API
  self.classPath = ko.observable('spark.jobserver.WordCountExample');
  self.query = ko.mapping.fromJS({
    'id': -1,
    'query': '', // query == params
    'name': null,
    'description': null,
    'errors': []
  });
  self.rows = ko.observableArray();
  //self.columns = ko.observableArray();
  self.resultsEmpty = ko.observable(false);

  self.appName = ko.computed({
    'read': function() {
      if (self.appNames().length > 0) {
        return self.appNames()[self.selectedAppName()];
      } else{
        return null;
      }
    },
    'write': function(value) {
      var filtered = $.each(self.appNames(), function(index, appName) {
        if (appName.name() == value) {
          self.selectedAppName(index);
        }
      });
    }
  });

  self.updateResults = function(results) {
    var rows = [];
    //self.columns.removeAll();  // Needed for datatables to refresh properly.
    //self.columns(results.columns);
    self.rows.removeAll();
    var newRows = [];
    $.each(results.result, function(key, value) {
      newRows.push([key, value]);
    });     
    self.rows(newRows);
  };

  self.updateAppNames = function(appNames) {
    var newAppNames = [];
    $.each(appNames, function(key, value) {
    	newAppNames.push({
        'name': ko.observable(key),
        'nice_name': ko.observable(key)
      });
    });//alert(ko.utils.stringifyJson(newAppNames));
    self.appNames(newAppNames); 

    var last = $.totalStorage('hueSparkLastAppName') || ((newAppNames[0].length > 0) ? newAppNames[0].name() : null);
    if (last) {
      self.appName(last);
    }
  };

  self.updateDatabases = function(databases) {
    self.databases(databases);

    var key = 'huesparkLastDatabase-' + self.server().name();
    var last = $.totalStorage(key) || ((databases.length > 0) ? databases[0] : null);
    if (last) {
      self.database(last);
    }
  };

  self.updateQuery = function(design) {
    self.query.query(design.query);
    self.query.id(design.id);
    self.query.name(design.name);
    self.query.description(design.desc);
    self.database(design.database);
    self.server(design.server);
  };

  self.chooseAppName = function(value, e) {
    $.each(self.appNames(), function(index, appName) {
      if (appName.name() == value.name()) {
        self.selectedAppName(index);
      }
    });
    $.totalStorage('hueSparkLastAppName', self.server().name());
  };

  self.chooseDatabase = function(value, e) {
    var key = 'huesparkLastDatabase-' + self.server().name();
    self.selectedDatabase(self.databases.indexOf(value));
    $.totalStorage(key, value);
  };

  var error_fn = function(jqXHR, status, errorThrown) {
    try {
      $(document).trigger('server.error', $.parseJSON(jqXHR.responseText));
    } catch(e) {
      $(document).trigger('server.unmanageable_error', jqXHR.responseText);
    }
  };

  self.fetchQuery = function(id) {
    var _id = id || self.query.id();
    if (_id && _id != -1) {
      var request = {
        url: '/spark/api/query/' + _id + '/get',
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
      data['server'] = self.server().name();
      data['database'] = self.database();
      var url = '/spark/api/query/';
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
    var data = ko.mapping.toJS(self.query);
    data.appName = self.appName().name;
    data.classPath = self.classPath();
    var request = {
      url: '/spark/api/execute',
      dataType: 'json',
      type: 'POST',
      success: function(data) {
        self.query.errors.removeAll();
        if (data.status == 0) {
          $(document).trigger('execute.query', data);
          self.updateResults(data.results);
          self.query.id(data.design);
          self.resultsEmpty($.isEmptyObject(data.results.result));
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

  self.fetchAppNames = function() {
    var request = {
      url: '/spark/api/jars',
      dataType: 'json',
      type: 'GET',
      success: function(data) {
        self.updateAppNames(data.jars);
      },
      error: error_fn
    };
    $.ajax(request);
  };
}
