#!/usr/bin/env python
# -- coding: utf-8 --
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

import csv
import logging
import os
import pytz
import re
import shutil
import StringIO
import tempfile
from dateutil.parser import parse
from datetime import datetime

from django.utils.encoding import smart_str
from django.utils.translation import ugettext as _

from desktop.lib.i18n import force_unicode
from hadoop.fs.webhdfs import WebHdfsException

from collectionmanager import conf

LOG = logging.getLogger(__name__)
TIMESTAMP_PATTERN = '\[([\w\d\s\-\/\:\+]*?)\]'
FIELD_XML_TEMPLATE = '<field name="%(name)s" type="%(type)s" indexed="%(indexed)s" stored="%(stored)s" required="%(required)s" />'
DEFAULT_FIELD = {
  'name': None,
  'type': 'text',
  'indexed': 'true',
  'stored': 'true',
  'required': 'true'
}

def schema_xml_with_fields(schema_xml, fields):
  fields_xml = ''
  for field in fields:
    field_dict = DEFAULT_FIELD.copy()
    field_dict.update(field)
    fields_xml += FIELD_XML_TEMPLATE % field_dict + '\n'
  return force_unicode(force_unicode(schema_xml).replace(u'<!-- REPLACE FIELDS -->', force_unicode(fields_xml)))

def schema_xml_with_unique_key_field(schema_xml, unique_key_field):
  return force_unicode(force_unicode(schema_xml).replace(u'<!-- REPLACE UNIQUE KEY -->', force_unicode(unique_key_field)))

def schema_xml_with_fields_and_unique_key(schema_xml, fields, unique_key_field):
  return schema_xml_with_unique_key_field(schema_xml_with_fields(schema_xml, fields), unique_key_field)

def example_schema_xml_with_fields_and_unique_key(fields, unique_key_field):
  # Get complete schema.xml
  with open(os.path.join(conf.CONFIG_TEMPLATE_PATH.get(), 'conf/schema.xml')) as f:
    return schema_xml_with_fields_and_unique_key(f.read(), fields, unique_key_field)

def copy_config_with_fields_and_unique_key(fields, unique_key_field):
  # Get complete schema.xml
  with open(os.path.join(conf.CONFIG_TEMPLATE_PATH.get(), 'conf/schema.xml')) as f:
    schema_xml = schema_xml_with_fields_and_unique_key(f.read(), fields, unique_key_field)

  # Create temporary copy of solr configs
  tmp_path = tempfile.mkdtemp()
  solr_config_path = os.path.join(tmp_path, os.path.basename(conf.CONFIG_TEMPLATE_PATH.get()))
  shutil.copytree(conf.CONFIG_TEMPLATE_PATH.get(), solr_config_path)

  # Write complete schema.xml to copy
  with open(os.path.join(solr_config_path, 'conf/schema.xml'), 'w') as f:
    f.write(smart_str(schema_xml))

  return tmp_path, solr_config_path


def get_field_types(row):
  def test_boolean(value):
    if value.lower() not in ('false', 'true'):
      raise ValueError(_("%s is not a boolean value") % value)

  def test_timestamp(value):
    if len(value) > 50:
      raise ValueError()

    if value.startswith('[') and value.endswith(']'):
      value = value[1:-1]

    try:
      parse(value)
    except:
      raise ValueError()

  test_fns = [('int', int),
              ('float', float),
              ('boolean', test_boolean),
              ('date', test_timestamp)]
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
    field_types.append(field_type or 'text_general')
  return field_types


def get_type_from_morphline_type(morphline_type):
  if morphline_type in ('POSINT', 'INT', 'BASE10NUM', 'NUMBER'):
    return 'integer'
  else:
    return 'string'


# def fields_from_log(fh):
#   fields_reader = csv.reader(StringIO.StringIO(fh.read()), delimiter=' ', quotechar='"')
#   row = next(fields_reader)

#   # Need to join any split [] statements (ie timestamp)
#   new_row = []
#   new_cell = []
#   start = True
#   for cell in row:
#     if start:
#       if cell.startswith('['):
#         new_cell.append(cell)
#         start = False
#       else:
#         new_row.append(cell)
#     else:
#       if cell.endswith(']'):
#         new_row.append(' '.join(new_cell))
#         break
#       else:
#         new_cell.append(cell)

#   field_types = get_field_types(row)
#   field_names = []
#   counters = {}
#   for field_type in field_types:
#     counters[field_type] = counters.get(field_type, 0) + 1
#     field_names.append('%s%d' % (field_type, counters[field_type]))

#   return zip(field_names, field_types)


def field_values_from_log(fh):
  content = fh.read()
  rows = ""
  while content:
    rows += content
    content = fh.read()

  data = []
  rows = rows.split('\n')
  for row in rows:
    if row:
      data.append({})
      matches = re.search(TIMESTAMP_PATTERN, row)
      if matches:
        data[-1]['timestamp'] = parse(matches.groups()[0]).astimezone(pytz.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
      data[-1]['message'] = row

  return data


def fields_from_log(fh):
  """
  Only timestamp and message
  """
  rows = fh.read()
  row = rows.split('\n')[0]

  # Extract timestamp
  fields = []
  matches = re.search(TIMESTAMP_PATTERN, row)
  if matches:
    fields.append(('timestamp', 'date'))
  fields.append(('message', 'text_general'))

  return fields
