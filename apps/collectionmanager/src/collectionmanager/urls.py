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

from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('collectionmanager.views',
  url(r'^$', 'collections', name='index'),

  url(r'^create/manual/$', 'collections_create_manual', name='collections_create_manual'),
  url(r'^create/file/$', 'collections_create_file', name='collections_create_file'),
  url(r'^import/$', 'collections_import', name='collections_import'),
)

urlpatterns += patterns('collectionmanager.api',
  url(r'^api/fields/parse/$', 'parse_fields', name='api_parse_fields'),
  url(r'^api/collections_and_cores/$', 'collections_and_cores', name='api_collections_and_cores'),
  url(r'^api/create/start/$', 'collections_create_start', name='api_collections_create_start'),
  url(r'^api/create/watch/(?P<job_id>[-\w]+)/$', 'collections_create_watch', name='api_collections_create_watch'),
  url(r'^api/create/finish/$', 'collections_create_finish', name='api_collections_create_finish'),
  url(r'^api/import/$', 'collections_import', name='api_collections_import')
)