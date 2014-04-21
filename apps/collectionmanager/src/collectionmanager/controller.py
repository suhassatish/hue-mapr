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

import json
import logging
import tablib

from desktop.lib.exceptions_renderable import PopupException

from libsearch.api import SolrApi
from search.conf import SOLR_URL, SECURITY_ENABLED
from search.models import Collection
from django.utils.translation import ugettext as _


LOG = logging.getLogger(__name__)


class CollectionManagerController(object):
  """
  Glue the models to the views.
  """
  def __init__(self, user):
    self.user = user

  def get_new_collections(self):
    try:
      solr_collections = SolrApi(SOLR_URL.get(), self.user, SECURITY_ENABLED.get()).collections()
      for name in Collection.objects.values_list('name', flat=True):
        solr_collections.pop(name, None)
    except Exception, e:
      LOG.warn('No Zookeeper servlet running on Solr server: %s' % e)
      solr_collections = []

    return solr_collections

  def get_new_cores(self):
    try:
      solr_cores = SolrApi(SOLR_URL.get(), self.user, SECURITY_ENABLED.get()).cores()
      for name in Collection.objects.values_list('name', flat=True):
        solr_cores.pop(name, None)
    except Exception, e:
      solr_cores = []
      LOG.warn('No Single core setup on Solr server: %s' % e)

    return solr_cores

  
  def add_new_collection(self, attrs):
    if attrs['type'] == 'collection':
      collections = self.get_new_collections()
      collection = collections[attrs['name']]

      hue_collection, created = Collection.objects.get_or_create(name=attrs['name'], solr_properties=collection, is_enabled=True, user=self.user)
      return hue_collection
    elif attrs['type'] == 'core':
      cores = self.get_new_cores()
      core = cores[attrs['name']]

      hue_collection, created = Collection.objects.get_or_create(name=attrs['name'], solr_properties=core, is_enabled=True, is_core_only=True, user=self.user)
      return hue_collection
    else:
      raise PopupException(_('Collection type does not exist: %s') % attrs)

  def create_new_collection(self, name, fields):
    api = SolrApi(SOLR_URL.get(), self.user, SECURITY_ENABLED.get())
    if api.create_collection(name):
      # Create only new fields
      # Fields that already exist, do not overwrite since there is no way to do that, currently.
      old_field_names = api.fields(name)['schema']['fields'].keys()
      new_fields = filter(lambda field: field['name'] not in old_field_names, fields)
      api.add_fields(name, new_fields)

      hue_collection, created = Collection.objects.get_or_create(name=name, solr_properties='{}', is_enabled=True, user=self.user)
    else:
      raise PopupException(_('Could not create collection. Check error logs for more info.'))

  def update_collection_index(self, collection_or_core_name, data):
    api = SolrApi(SOLR_URL.get(), self.user, SECURITY_ENABLED.get())
    # 'data' first line should be headers.
    if not api.update(collection_or_core_name, data, content_type='csv'):
      raise PopupException(_('Could not update index. Check error logs for more info.'))
