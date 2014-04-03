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

// Start Models

var Collection = function(viewModel) {
  var self = this;

  self.name = ko.observable();
  self.fields = ko.observableArray();

  self.removeField = function(field) {
    self.fields.remove(field);
  };

  self.addField = function(name, type) {
    self.fields.push(new Field(self, name, type));
  };

  self.newField = function() {
    self.addField('', '');
  };
};

var Field = function(collection, name, type) {
  var self = this;

  self.name = ko.observable(name);
  self.type = ko.observable(type);

  self.remove = function() {
    collection.removeField(self);
  };
};

// End Models


// Start Wizard

var Page = function(name, url) {
  var self = this;

  self.name = ko.observable(name);
  self.url = ko.observable(url);
};

var Wizard = function(pages) {
  var self = this;

  self.pages = ko.observableArray();

  $.each(pages, function(index, page) {
    self.pages.push(new Page(page.name, page.url));
  });

  self.index = ko.observable(0);

  self.hasPrevious = ko.computed(function() {
    return self.index() > 0;
  });

  self.hasNext = ko.computed(function() {
    return self.index() + 1 < self.pages().length;
  });

  self.current = ko.computed(function() {
    return self.pages()[self.index()];
  });

  self.next = function() {
    if (self.hasNext()) {
      return self.pages()[self.index() + 1];
    }
  };

  self.previous = function() {
    if (self.hasPrevious()) {
      return self.pages()[self.index() - 1];
    }
  };

  self.setIndexByUrl = function(url) {
    $.each(self.pages(), function(index, step) {
      if (step.url() == url) {
        self.index(index);
      }
    });
  };
};

// End Wizard

var CreateCollectionViewModel = function(steps) {
  var self = this;

  // Models
  self.collection = new Collection(self);

  // UI
  self.wizard = new Wizard(steps);

  self.save = function () {
    return $.post("/search/admin/collections/create", {
      collection: ko.toJSON(self.collection),
    })
    .success(function(data) {
      if (data.status == 0) {
        $(document).trigger("info", data.message);
      } else {
        $(document).trigger("error", data.message);
      }
    })
    .fail(function (xhr, textStatus, errorThrown) {
      $(document).trigger("error", xhr.responseText);
    });
  };
};


// Start utils

ko.bindingHandlers.routie = {
  init: function(element, valueAccessor, allBindingsAccessor, viewModel, bindingContext) {
    $(element).click(function() {
      var obj = ko.utils.unwrapObservable(valueAccessor());
      var url = null;
      var bubble = false;
      if ($.isPlainObject(obj)) {
        url = obj.url;
        bubble = !!obj.bubble;
      } else {
        url = obj;
      }
      routie(url);
      return bubble;
    });
  }
};

// End utils
