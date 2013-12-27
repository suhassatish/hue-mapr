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

from django.utils.translation import ugettext as _


LOG = logging.getLogger(__name__)


class Credentials(object):
  NAME_TO_CLASS_MAPPING = {
      "hcat": "org.apache.oozie.action.hadoop.HCatCredentials",
      "hive2": "org.apache.oozie.action.hadoop.Hive2Credentials",
      "hbase": "org.apache.oozie.action.hadoop.HbaseCredentials",
  }

  def __init__(self, credentials=None):
    self.credentials = credentials

  def fetch(self, oozie_api):
    configuration = oozie_api.get_configuration()
    self.credentials = self._parse_oozie(configuration)

  def _parse_oozie(self, configuration_dic):
    return dict([cred.strip().split('=') for cred in configuration_dic.get('oozie.credentials.credentialclasses', '').strip().split(',') if cred])

  @property
  def class_to_name_credentials(self):
    return dict((v,k) for k, v in self.credentials.iteritems())

  def get_properties(self, metastore=None):
    properties = {}
    from beeswax import hive_site

    if metastore is None:
      metastore = hive_site.get_metastore()

    if not metastore:
      metastore = {}
      LOG.info('Could not get all the Oozie credentials: hive-site.xml required on the Hue host.')

    properties.update({
       'credential_hcat_name': self.hive_name,
       'credential_hcat_xml_name': self.hive_name, # Same for now
       'credential_hcat_uri': metastore.get('thrift_uri'),
       'credential_hcat_principal': metastore.get('kerberos_principal')
    })

    properties.update({
       'credential_hive2_name': self.hiveserver2_name,
       'credential_hive2_xml_name': self.hiveserver2_name, # Same for now
       'credential_hive2_url': hive_site.hiveserver2_jdbc_url(),
       'credential_hive2_principal': metastore.get('kerberos_principal')
    })

    properties.update({
       'credential_hbase_name': self.hbase_name,
       'credential_hbase_xml_name': self.hbase_name, # Same for now
    })

    return properties

  @property
  def hive_name(self):
    return self.class_to_name_credentials.get('org.apache.oozie.action.hadoop.HCatCredentials')

  @property
  def hiveserver2_name(self):
    return self.class_to_name_credentials.get('org.apache.oozie.action.hadoop.Hive2Credentials')

  @property
  def hbase_name(self):
    return self.class_to_name_credentials.get('org.apache.oozie.action.hadoop.HbaseCredentials')
