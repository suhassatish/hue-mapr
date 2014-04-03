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
import urllib

from desktop.lib.exceptions_renderable import PopupException
from desktop.lib.rest.http_client import HttpClient, RestException
from desktop.lib.rest import resource
from django.utils.translation import ugettext as _

from libsolr.api import SolrApi as BaseSolrApi

from search.examples import demo_handler
from search.conf import EMPTY_QUERY, SECURITY_ENABLED


LOG = logging.getLogger(__name__)

DEFAULT_USER = 'hue'


def utf_quoter(what):
  return urllib.quote(unicode(what).encode('utf-8'), safe='~@#$&()*!+=;,.?/\'')


class SolrApi(BaseSolrApi):
  """
  http://wiki.apache.org/solr/CoreAdmin#CoreAdminHandler
  """
  def __init__(self, solr_url, user):
    super(SolrApi, self).__init__(solr_url, user, SECURITY_ENABLED.get())

  def _get_params(self):
    if self.security_enabled:
      return (('doAs', self._user ),)
    return (('user.name', DEFAULT_USER), ('doAs', self._user),)

  @demo_handler
  def query(self, solr_query, hue_core):
    try:
      params = self._get_params() + (
          ('q', solr_query['q'] or EMPTY_QUERY.get()),
          ('wt', 'json'),
          ('rows', solr_query['rows']),
          ('start', solr_query['start']),
      )

      params += hue_core.get_query(solr_query)

      fqs = solr_query['fq'].split('|')
      for fq in fqs:
        if fq:
          params += (('fq', urllib.unquote(utf_quoter(fq))),)

      response = self._root.get('%(collection)s/select' % solr_query, params)

      return self._get_json(response)
    except RestException, e:
      raise PopupException(e, title=_('Error while accessing Solr'))
