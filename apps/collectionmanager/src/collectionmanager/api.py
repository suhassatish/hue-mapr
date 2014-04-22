#!/usr/bin/env python
# Licensed to Cloudera, Inc. under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  Cloudera, Inc. licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import json
import logging
import re

from django.http import HttpResponse
from django.utils.translation import ugettext as _

from desktop.lib import i18n
from desktop.lib.exceptions_renderable import PopupException

from beeswax.create_table import _parse_fields, FILE_READERS, DELIMITERS

from controller import CollectionManagerController


LOG = logging.getLogger(__name__)


def _get_field_types(row):
  def test_boolean(value):
    if value.lower() not in ('false', 'true'):
      raise ValueError(_("%s is not a boolean value") % value)

  test_fns = [('integer', int), ('float', float), ('boolean', test_boolean)]
  field_types = []
  for field in row:
    field_type = None
    for test_fn in test_fns:
      try:
        test_fn[1](field)
        field_type = test_fn[0]
        break
      except ValueError:
        pass
    field_types.append(field_type or 'string')
  return field_types


def _get_type_from_morphline_type(morphline_type):
  if morphline_type in ('POSINT', 'INT', 'BASE10NUM', 'NUMBER'):
    return 'integer'
  else:
    return 'string'


def parse_fields(request):
  result = {'status': -1, 'message': ''}

  content_type = request.POST.get('type')
  try:
    if content_type == 'separated':
      file_obj = request.fs.open(request.POST.get('file-path'))
      delimiter = [request.POST.get('field-separator', ',')]
      delim, reader_type, fields_list = _parse_fields(
                                          'collections-file',
                                          file_obj,
                                          i18n.get_site_encoding(),
                                          [reader.TYPE for reader in FILE_READERS],
                                          delimiter)
      file_obj.close()

      field_names = fields_list[0]
      field_types = _get_field_types(fields_list[1])
      result['data'] = zip(field_names, field_types)
      result['status'] = 0
    elif content_type == 'morphlines':
      morphlines = json.loads(request.POST.get('morphlines'))
      # Look for entries that take on the form %{SYSLOGTIMESTAMP:timestamp}
      field_results = re.findall(r'\%\{(?P<type>\w+)\:(?P<name>\w+)\}', morphlines['expression'])
      if field_results:
        result['data'] = []

        for field_result in field_results:
          result['data'].append( (field_result[1], _get_type_from_morphline_type(field_result[0])) )

        result['status'] = 0
      else:
        result['status'] = 1
        result['message'] = _('Could not detect any fields.')
    else:
      result['status'] = 1
      result['message'] = _('Type %s not supported.') % content_type
  except Exception, e:
    LOG.exception(e.message)
    result['message'] = e.message

  return HttpResponse(json.dumps(result), mimetype="application/json")


def collections_and_cores(request):
  searcher = CollectionManagerController(request.user)
  new_solr_collections = searcher.get_new_collections()
  massaged_collections = []
  for coll in new_solr_collections:
    massaged_collections.append({
      'type': 'collection',
      'name': coll
    })
  new_solr_cores = searcher.get_new_cores()
  massaged_cores = []
  for core in new_solr_cores:
    massaged_cores.append({
      'type': 'core',
      'name': core
    })
  response = {
    'status': 0,
    'collections': list(massaged_collections),
    'cores': list(massaged_cores)
  }
  return HttpResponse(json.dumps(response), mimetype="application/json")


def collections_create(request):
  if request.method != 'POST':
    raise PopupException(_('POST request required.'))

  response = {'status': -1}

  collection = json.loads(request.POST.get('collection', '{}'))

  if collection:
    # Create collection and add fields
    searcher = CollectionManagerController(request.user)
    searcher.create_new_collection(collection.get('name', ''), collection.get('fields', []))

    # Index data
    fh = request.fs.open(request.POST.get('file-path'))
    if request.POST.get('type') == 'separated':
      indexing_strategy = 'upload'
    else:
      indexing_strategy = 'mapreduce-batch-indexer'
    searcher.update_collection_index(collection.get('name', ''), fh.read(), indexing_strategy)
    fh.close()

    response['status'] = 0
    response['message'] = _('Page saved!')
  else:
    response['message'] = _('Collection missing.')

  return HttpResponse(json.dumps(response), mimetype="application/json")


def collections_import(request):
  if request.method != 'POST':
    raise PopupException(_('POST request required.'))

  searcher = CollectionManagerController(request.user)
  imported = []
  not_imported = []
  status = -1
  message = ""
  importables = json.loads(request.POST["collections"])
  for imp in importables:
    try:
      searcher.add_new_collection(imp)
      imported.append(imp['name'])
    except Exception, e:
      not_imported.append(imp['name'] + ": " + unicode(str(e), "utf8"))

  if len(imported) == len(importables):
    status = 0;
    message = _('Collection(s) or core(s) imported successfully!')
  elif len(not_imported) == len(importables):
    status = 2;
    message = _('There was an error importing the collection(s) or core(s)')
  else:
    status = 1;
    message = _('Collection(s) or core(s) partially imported')

  result = {
    'status': status,
    'message': message,
    'imported': imported,
    'notImported': not_imported
  }

  return HttpResponse(json.dumps(result), mimetype="application/json")
