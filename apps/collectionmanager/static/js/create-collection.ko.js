
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
    // 'log',
    // 'regex',
  ];

  // Models
  self.fieldTypes = ko.mapping.fromJS(fieldTypes);
  self.fieldSeparators = ko.mapping.fromJS(fieldSeparators);
  self.fileTypes = ko.mapping.fromJS(fileTypes);
  self.collection = new Collection(self);
  self.file = ko.observable().extend({'errors': null});
  self.fileType = ko.observable().extend({'errors': null});
  self.fieldSeparator = ko.observable().extend({'errors': null});
  self.regex = ko.observable().extend({'errors': null});

  // UI
  self.wizard = wizard;

  self.inferFields = function(data) {
    var fields = [];
    var field_names = data[0];
    var first_row = data[1];
    $.each(first_row, function(index, value) {
      var type = null;
      if ($.isNumeric(value)) {
        if (value.toString().indexOf(".") == -1) {
          type = 'integer';
        } else {
          type = 'float';
        }
      } else {
        if (value.toLowerCase().indexOf("true") > -1 || value.toLowerCase().indexOf("false") > -1) {
          type = 'boolean';
        }
        else {
          type = 'string';
        }
      }
      fields.push(new Field(self.collection, field_names[index], type));
    });

    self.collection.fields(fields);
  };

  self.fetchFields = function() {
    return $.post("/collectionmanager/api/fields/parse/", {
      'field-separator': self.fieldSeparator(),
      'file-type': self.fileType(),
      'file-path': self.file()
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
        collection: ko.toJSON(self.collection),
        'file-path': self.file()
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
