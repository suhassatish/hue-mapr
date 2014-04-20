
var ImportCollectionViewModel = function(steps) {
  var self = this;

  self.collections = ko.observableArray();
  self.cores = ko.observableArray();

  self.importable = ko.computed(function() {
    return self.collections().concat(self.cores());
  });

  self.selectedImportable = ko.computed(function() {
    return ko.utils.arrayFilter(self.importable(), function(collection_or_core) {
      return collection_or_core.selected();
    });
  });

  self.loadCollectionsAndCores = function() {
    return $.get("/collectionmanager/api/collections_and_cores/").done(function(data) {
      if (data.status == 0) {
        self.collections(ko.utils.arrayMap(data.collections, function(collection) {
          collection = ko.mapping.fromJS(collection);
          collection.selected = ko.observable(false);
          return collection;
        }));
        self.cores(ko.utils.arrayMap(ko.mapping.fromJS(data.cores)(), function(core) {
          core = ko.mapping.fromJS(core);
          core.selected = ko.observable(false);
          return core;
        }));
      } else {
        $(document).trigger("error", data.message);
      }
    })
    .fail(function (xhr, textStatus, errorThrown) {
      $(document).trigger("error", xhr.responseText);
    });
  };

  self.importSelected = function() {
    return $.post("/collectionmanager/api/import/", {
      collections: ko.mapping.toJSON(self.selectedImportable()),
    }).done(function(data) {
      if (data.status == 0) {
        window.location.href = '/collectionmanager';
      } else {
        $(document).trigger("error", data.message);
      }
    })
    .fail(function (xhr, textStatus, errorThrown) {
      $(document).trigger("error", xhr.responseText);
    });
  };
};