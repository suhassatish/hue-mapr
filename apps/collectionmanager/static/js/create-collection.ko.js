
var HiveViewModel = function() {
  var Database = function(name) {
    var self = this;

    self.name = ko.observable(name).extend({'errors': null});
    self.tables = ko.observableArray();
    self.table = ko.observable().extend({'errors': null});

    self.table.subscribe(function(table) {
      table.loadColumns();
    });

    self.loadTables = function() {
      return $.get("/beeswax/api/autocomplete/" + self.name()).done(function(data) {
        if (data.tables.length > 0) {
          self.tables($.map(data.tables, function(table) { return new Table(self, table); }));
          self.table(self.tables()[0]);
        }
      })
      .fail(function (xhr, textStatus, errorThrown) {
        $(document).trigger("error", xhr.responseText);
      });
    };
  };

  var Table = function(database, name) {
    var self = this;

    self.database = database;
    self.name = ko.observable(name).extend({'errors': null});
    self.columns = ko.observableArray();

    self.loadColumns = function() {
      return $.get("/beeswax/api/autocomplete/" + self.database.name() + '/' + self.name()).done(function(data) {
        if (data.columns.length > 0) {
          self.columns(data.columns);
        }
      })
      .fail(function (xhr, textStatus, errorThrown) {
        $(document).trigger("error", xhr.responseText);
      });
    };
  };

  var self = this;

  self.databases = ko.observableArray();
  self.database = ko.observable().extend({'errors': null});

  self.database.subscribe(function(database) {
    database.loadTables();
  });

  self.loadDatabases = function() {
    return $.get("/beeswax/api/autocomplete").done(function(data) {
      if (data.databases.length > 0) {
        self.databases($.map(data.databases, function(database) { return new Database(database); }));
        self.database(self.databases()[0]);
      }
    })
    .fail(function (xhr, textStatus, errorThrown) {
      $(document).trigger("error", xhr.responseText);
    });
  };

  self.loadDatabases();
};

var CreateCollectionViewModel = function() {
  var self = this;

  var sources = [
    'file',
    'hbase',
    'hive'
  ];

  var fieldTypes = [
    'string',
    'integer',
    'float',
    'boolean'
  ];
  var fieldSeparators = [
    ',',
    '\t'
  ];
  var fileTypes = [
    'separated',
    'morphlines'
  ];

  // Models
  self.collection = new Collection(self);
  self.hive = new HiveViewModel();
  self.hbase = ko.mapping.fromJS({'databases': []});

  self.sources = ko.mapping.fromJS(sources);
  self.source = ko.observable(sources[0]).extend({'errors': null});

  self.fieldTypes = ko.mapping.fromJS(fieldTypes);
  self.fieldSeparators = ko.mapping.fromJS(fieldSeparators);
  self.fileTypes = ko.mapping.fromJS(fileTypes);
  self.fieldSeparator = ko.observable().extend({'errors': null});
  self.file = ko.observable().extend({'errors': null});
  self.fileType = ko.observable().extend({'errors': null});
  self.morphlines = ko.mapping.fromJS({'name': 'message', 'expression': null});
  self.morphlines.name = self.morphlines.name.extend({'errors': null});
  self.morphlines.expression = self.morphlines.expression.extend({'errors': null});

  // UI
  self.wizard = new Wizard();

  self.inferFields = function(data) {
    var fields = [];
    $.each(data, function(index, value) {
      // 0 => name
      // 1 => type
      fields.push(new Field(self.collection, value[0], value[1]));
    });

    self.collection.fields(fields);
  };

  self.fetchFields = function() {
    if (self.source() == 'file') {
      return $.post("/collectionmanager/api/fields/parse/", {
        'field-separator': self.fieldSeparator(),
        'type': self.source(),
        'content-type': self.fileType(),
        'file-path': self.file(),
        'morphlines': ko.mapping.toJSON(self.morphlines)
      }).done(function(data) {
        if (data.status == 0) {
          self.inferFields(data.data);
        } else {
          $(document).trigger("error", data.message);
        }
      })
      .fail(function (xhr, textStatus, errorThrown) {
        $(document).trigger("error", xhr.responseText);
      });
    }
  };

  self.save = function() {
    if (self.wizard.currentPage().validate()) {
      switch(self.source()) {
        case 'file':
        return $.post("/collectionmanager/api/create/", {
          'collection': ko.toJSON(self.collection),
          'type': self.fileType(),
          'path': self.file(),
          'source': self.source()
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

        case 'hive':
        return $.post("/collectionmanager/api/create/", {
          'collection': ko.toJSON(self.collection),
          'database': self.hive.database().name(),
          'table': self.hive.database().table().name(),
          'source': self.source()
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
      }
    }
  };
};


function getFileBrowseButton(inputElement) {
  return $("<button>").addClass("btn").addClass("fileChooserBtn").text("..").click(function (e) {
    e.preventDefault();
    $("#filechooser").jHueFileChooser({
      initialPath: inputElement.val(),
      onFileChoose: function (filePath) {
        inputElement.val(filePath);
        inputElement.trigger("change");
        $("#chooseFile").modal("hide");
      },
      selectFolder: false,
      createFolder: false
    });
    $("#chooseFile").modal("show");
  });
}
