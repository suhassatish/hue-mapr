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

import logging
import os

from django.core.management.base import NoArgsCommand
from django.utils.translation import ugettext as _

from hadoop import cluster

from desktop.models import Document
from liboozie.submittion import create_directories
from oozie.conf import LOCAL_SAMPLE_DATA_DIR, LOCAL_SAMPLE_DIR,\
  REMOTE_SAMPLE_DIR
from oozie.models import Workflow, Coordinator, Bundle
from oozie.importlib.workflows import import_workflow
from oozie.importlib.coordinators import import_coordinator
from oozie.importlib.bundles import import_bundle
from useradmin.models import install_sample_user


LOG = logging.getLogger(__name__)

class Command(NoArgsCommand):
  def _import_workflows(self, directory):
    imported = []
    for example_directory_name in os.listdir(directory):
      with open(os.path.join(directory, example_directory_name, 'workflow.zip')) as fp:
        workflow_xml, metadata = Workflow.decompress(fp)
        workflow = Workflow.objects.new_workflow(owner=self.user)
        Workflow.objects.initialize(workflow, self.fs)
        import_workflow(workflow=workflow, workflow_definition=workflow_xml, metadata=metadata, fs=self.fs)
        imported.append(workflow)

  def _import_coordinators(self, directory):
    imported = []
    for example_directory_name in os.listdir(directory):
      with open(os.path.join(directory, example_directory_name, 'coordinator.zip')) as fp:
        coordinator_xml, metadata = Coordinator.decompress(fp)
        coordinator = Coordinator.objects.create(owner=self.user)
        import_coordinator(coordinator=coordinator, coordinator_definition=coordinator_xml, metadata=metadata)
        imported.append(coordinator)

  def _import_bundles(self, directory):
    imported = []
    for example_directory_name in os.listdir(directory):
      with open(os.path.join(directory, example_directory_name, 'bundle.xml')) as fp:
        bundle_xml = fp.read()
      bundle = Bundle.objects.create(owner=self.user)
      import_bundle(bundle=bundle, bundle_definition=bundle_xml)
      imported.append(bundle)

  def install_examples(self):
    data_dir = LOCAL_SAMPLE_DIR.get()

    managed_dir = os.path.join(data_dir, 'managed')
    managed_imported = self._import_workflows(managed_dir)
    for workflow in managed_imported:
      workflow.managed = True
      workflow.save()

    # unmanaged_dir = os.path.join(data_dir, 'unmanaged')
    # unmanaged_imported = self._import_workflows(unmanaged_dir)
    # for workflow in unmanaged_imported:
    #   workflow.managed = False
    #   workflow.save()

    coordinators_dir = os.path.join(data_dir, 'coordinators')
    self._import_coordinators(coordinators_dir)

    bundles_dir = os.path.join(data_dir, 'bundles')
    self._import_bundles(bundles_dir)

  def handle_noargs(self, **options):
    self.user = install_sample_user()
    self.fs = cluster.get_hdfs()

    create_directories(self.fs, [REMOTE_SAMPLE_DIR.get()])
    remote_dir = REMOTE_SAMPLE_DIR.get()

    # Copy examples binaries
    for name in os.listdir(LOCAL_SAMPLE_DIR.get()):
      local_dir = self.fs.join(LOCAL_SAMPLE_DIR.get(), name)
      remote_data_dir = self.fs.join(remote_dir, name)
      LOG.info(_('Copying examples %(local_dir)s to %(remote_data_dir)s\n') % {
                  'local_dir': local_dir, 'remote_data_dir': remote_data_dir})
      self.fs.do_as_user(self.fs.DEFAULT_USER, self.fs.copyFromLocal, local_dir, remote_data_dir)

    # Copy sample data
    local_dir = LOCAL_SAMPLE_DATA_DIR.get()
    remote_data_dir = self.fs.join(remote_dir, 'data')
    LOG.info(_('Copying data %(local_dir)s to %(remote_data_dir)s\n') % {
                'local_dir': local_dir, 'remote_data_dir': remote_data_dir})
    self.fs.do_as_user(self.fs.DEFAULT_USER, self.fs.copyFromLocal, local_dir, remote_data_dir)

    # Load jobs
    self.install_examples()
    Document.objects.sync()
