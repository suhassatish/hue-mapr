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

from django.http import HttpResponse
from django.utils.translation import ugettext as _

from desktop.lib.django_util import render

from controller import CollectionManagerController


LOG = logging.getLogger(__name__)


def no_collections(request):
  return render('no_collections.mako', request, {})


def collections(request, is_redirect=False):
  return render('collections.mako', request, {})


def collections_create_manual(request):
  return render('collections_create_manual.mako', request, {})


def collections_create_file(request):
  return render('collections_create_file.mako', request, {})


def collections_import(request):
  return render('collections_import.mako', request, {})
