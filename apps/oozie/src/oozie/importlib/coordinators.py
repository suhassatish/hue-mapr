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
import os
import re
from lxml import etree

from django.core import serializers
from django.utils.translation import ugettext as _

from oozie import conf
from oozie.models import Workflow


LOG = logging.getLogger(__name__)

OOZIE_NAMESPACES = ['uri:oozie:coordinator:0.1', 'uri:oozie:coordinator:0.2', 'uri:oozie:coordinator:0.3', 'uri:oozie:coordinator:0.4']

FREQUENCY_REGEX = r'^\$\{coord:(?P<frequency_unit>\w+)\((?P<frequency_number>\d+)\)\}$'


def _set_coordinator_properties(coordinator, root, namespace):
  """
  Get coordinator properties from coordinator XML

  Set properties on ``coordinator`` with attributes from XML etree ``root``.
  """
  coordinator.name = root.get('name')
  coordinator.timezone = root.get('timezone')
  # coordinator.start = root.get('start')
  # coordinator.end = root.get('end')

  # Get frequency number and units from frequency
  # frequency units and number are just different parts of the EL function.
  matches = re.match(FREQUENCY_REGEX, root.get('frequency'))
  coordinator.frequency_number = matches.group('frequency_number')
  coordinator.frequency_unit = matches.group('frequency_unit')


def _set_controls(coordinator, root, namespace):
  """
  Get controls from coordinator XML

  Set properties on ``coordinator`` with controls from XML etree ``root``.
  """
  namespaces = {
    'n': namespace
  }
  controls = root.xpath('n:controls', namespaces=namespaces)[0]
  concurrency = controls.xpath('n:concurrency', namespaces=namespaces)
  timeout = controls.xpath('n:timeout', namespaces=namespaces)
  execution = controls.xpath('n:execution', namespaces=namespaces)
  throttle = controls.xpath('n:throttle', namespaces=namespaces)
  if concurrency:
    coordinator.concurrency = concurrency[0].text
  if timeout:
    coordinator.timeout = timeout[0].text
  if execution:
    coordinator.execution = execution[0].text
  if throttle:
    coordinator.throttle = throttle[0].text


def _reconcile_datasets(coordinator, objects, root, namespace):
  namespaces = {
    'n': namespace
  }
  datasets = {}
  datainputs = []
  dataoutputs = []
  coordinator.save()
  for obj in objects:
    obj.object.coordinator = coordinator
    if str(type(obj.object)).lower() == 'dataset':
      datasets[obj.object.name] = obj.object
      obj.object.save()
    elif str(type(obj.object)).lower() == 'datainput':
      datainputs.append(obj.object)
    elif str(type(obj.object)).lower() == 'dataoutput':
      dataoutputs.append(obj.object)
  for datainput in datainputs:
    datainput_elements = root.xpath('//coordinator:data-in[@name="%s"]' % datainput.name, namespaces=namespaces)
    for datainput_element in datainput_elements:
      datainput.dataset = datasets[datainput_element.get('dataset')]
    datainput.save()
  for dataoutput in dataoutputs:
    dataoutput_elements = root.xpath('//coordinator:data-out[@name="%s"]' % dataoutput.name, namespaces=namespaces)
    for dataoutput_element in dataoutput_elements:
      dataoutput.dataset = datasets[dataoutput_element.get('dataset')]
    dataoutput.save()
  # @TODO(abe): reconcile instance times

def _set_properties(coordinator, root, namespace):
  namespaces = {
    'n': namespace
  }
  properties = []
  props = root.xpath('n:action/workflow/configuration/property', namespaces=namespaces)
  for prop in props:
    name = prop.xpath('n:name', namespaces=namespaces)[0]
    value = prop.xpath('n:value', namespaces=namespaces)[0]
    properties.append({'name': name, 'value': value})
  coordinator.job_properties = json.dumps(properties)


def _process_metadata(coordinator, metadata):
  try:
    coordinator.workflow = Workflow.objects.get(name=metadata['workflow'])
  except Workflow.DoesNotExist:
    # @TODO(abe): Throw exception of log?
    pass


def import_coordinator(coordinator, coordinator_definition, metadata=None):
  xslt_definition_fh = open("%(xslt_dir)s/coordinator.xslt" % {
    'xslt_dir': os.path.join(conf.DEFINITION_XSLT_DIR.get(), 'coordinators')
  })

  # Parse Coordinator Definition
  coordinator_definition_root = etree.fromstring(coordinator_definition)

  if coordinator_definition_root is None:
    raise RuntimeError(_("Could not find any nodes in Coordinator definition. Maybe it's malformed?"))

  tag = etree.QName(coordinator_definition_root.tag)
  schema_version = tag.namespace

  # Ensure namespace exists
  if schema_version not in OOZIE_NAMESPACES:
    raise RuntimeError(_("Tag with namespace %(namespace)s is not valid. Please use one of the following namespaces: %(namespaces)s") % {
      'namespace': coordinator_definition_root.tag,
      'namespaces': ', '.join(OOZIE_NAMESPACES)
    })

  # Get XSLT and Transform XML
  xslt = etree.parse(xslt_definition_fh)
  xslt_definition_fh.close()
  transform = etree.XSLT(xslt)
  transformed_root = transform(coordinator_definition_root)

  # Deserialize XML
  objects = serializers.deserialize('xml', etree.tostring(transformed_root))

  # Resolve coordinator dependencies and node types and link dependencies
  _set_coordinator_properties(coordinator, coordinator_definition_root, schema_version)
  _set_controls(coordinator, coordinator_definition_root, schema_version)
  _reconcile_datasets(coordinator, objects, coordinator_definition_root, schema_version)
  _set_properties(coordinator, coordinator_definition_root, schema_version)
  _process_metadata(coordinator, metadata)

  # Update schema_version
  coordinator.schema_version = schema_version
  coordinator.save()
