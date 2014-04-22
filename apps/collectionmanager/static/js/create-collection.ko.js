
var CreateCollectionViewModel = function(wizard) {
  var self = this;

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
  self.fieldTypes = ko.mapping.fromJS(fieldTypes);
  self.fieldSeparators = ko.mapping.fromJS(fieldSeparators);
  self.fileTypes = ko.mapping.fromJS(fileTypes);
  self.collection = new Collection(self);
  self.file = ko.observable().extend({'errors': null});
  self.fileType = ko.observable().extend({'errors': null});
  self.fieldSeparator = ko.observable().extend({'errors': null});
  self.morphlines = ko.mapping.fromJS({'name': 'message', 'expression': null});
  self.morphlines.name = self.morphlines.name.extend({'errors': null});
  self.morphlines.expression = self.morphlines.expression.extend({'errors': null});

  // UI
  self.wizard = new Wizard();

  self.inferFields = function(data) {
    var fields = [];
    console.log(data);
    $.each(data, function(index, value) {
      // 0 => name
      // 1 => type
      fields.push(new Field(self.collection, value[0], value[1]));
    });

    self.collection.fields(fields);
  };

  self.fetchFields = function() {
    return $.post("/collectionmanager/api/fields/parse/", {
      'field-separator': self.fieldSeparator(),
      'type': self.fileType(),
      'file-path': self.file(),
      'morphlines': ko.mapping.toJSON(self.morphlines)
    })
    .done(function(data) {
      if (data.status == 0) {
        self.inferFields(data.data);
      } else {
        $(document).trigger("error", data.message);
      }
    })
    .fail(function (xhr, textStatus, errorThrown) {
      $(document).trigger("error", xhr.responseText);
    });
  };

  self.save = function() {
    if (self.wizard.currentPage().validate()) {
      return $.post("/collectionmanager/api/create/", {
        'collection': ko.toJSON(self.collection),
        'file-path': self.file(),
        'type': self.fileType()
      })
      .done(function(data) {
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
