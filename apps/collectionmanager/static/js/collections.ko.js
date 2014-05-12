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

  self.name = ko.observable().extend({'errors': null});
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

  self.setData = function(data_json) {
    self.data(data_json);
  };
};

var Field = function(collection, name, type) {
  var self = this;

  self.name = ko.observable(name).extend({'errors': null});
  self.type = ko.observable(type).extend({'errors': null});

  self.remove = function() {
    collection.removeField(self);
  };
};

// End Models


// Start Wizard

var Page = function(url, name, next, validate_fn) {
  var self = this;

  self.name = ko.observable(name);
  self.url = ko.observable(url);
  self.next = ko.observable(next);

  self.validate = validate_fn || function() { return true; };
};

var Wizard = function() {
  var self = this;

  self.rootPage = ko.observable();
  self.currentPage = ko.observable(self.rootPage());
  // Stack of previous pages.
  self.previousPages = ko.observableArray();

  self.hasPrevious = ko.computed(function() {
    return self.previousPages().length > 0;
  });

  self.hasNext = ko.computed(function() {
    return !!(self.currentPage() && self.currentPage().next());
  });

  self.pageList = ko.computed(function() {
    var page = self.rootPage();
    var pages = [];
    while(page) {
      pages.push(page);
      page = self.pages[page.next()];
    }
    return pages;
  });

  self.previousUrl = ko.computed(function() {
    if (self.previousPages().length > 0) {
      return self.previousPages()[self.previousPages().length - 1].url();
    } else {
      return null;
    }
  });

  self.nextUrl = ko.computed(function() {
    if (self.currentPage() && self.currentPage().next()) {
      return self.currentPage().next();
    } else {
      return null;
    }
  });

  self.next = function() {
    if (self.hasNext() && self.currentPage().validate()) {
      self.previousPages.push(self.currentPage());
      self.currentPage(self.pages[self.currentPage().next()]);
    }
  };

  self.previous = function() {
    if (self.hasPrevious()) {
      self.currentPage(self.previousPages.pop());
    }
  };

  self.setPageByUrl = function(url) {
    var urls = ko.utils.arrayMap(self.pageList(), function(page) {
      return page.url();
    });
    var previousUrls = ko.utils.arrayMap(self.previousPages(), function(page) {
      return page.url();
    });
    if ($.inArray(url, previousUrls) != -1) {
      var previousPageURL = null;
      self.previous();
      while(self.hasPrevious() && self.currentPage().url() != url && self.currentPage().url() != previousPageURL) {
        previousPageURL = self.currentPage().url();
        self.previous();
      }
    } else if ($.inArray(url, urls) != -1) {
      var previousPageURL = null;
      while(self.hasNext() && self.currentPage().url() != url && self.currentPage().url() != previousPageURL) {
        previousPageURL = self.currentPage().url();
        self.next();
      }
    }
  };
};

ko.utils.extend(Wizard.prototype, {
  'pages': {},
  'getPage': function(url, name, next, validate_fn) {
    if (!this.pages[url]) {
      this.pages[url] = new Page(url, name, next, validate_fn);
    }
    return this.pages[url];
  }
});

// End Wizard


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

ko.extenders.errors = function(target, options) {
  target.errors = ko.observableArray();
  return target;
};

function validateNotNull(obs, message) {
  var ret = true;
  if (!obs()) {
    obs.errors.push(message);
    ret = false;
  } else {
    obs.errors.removeAll();
  }
  return ret;
}

// End utils
