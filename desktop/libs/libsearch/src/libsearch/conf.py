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

from django.utils.translation import ugettext_lazy as _t

from desktop.lib.conf import Config


BATCH_INDEXER_PATH = Config(
  key="batch_indexer_path",
  help=_t("Batch indexer path in HDFS."),
  type=str,
  default="/var/lib/search/search-mr-job.jar")

# @TODO(Abe): Magic with __file__
CONFIG_TEMPLATE_PATH = Config(
  key="config_template_path",
  help=_t("The contents of this directory will be copied over to the solrctl host to its temporary directory."),
  private=True,
  type=str,
  default=__file__)

SOLRCTL_HOST = Config(
  key="solrctl_host",
  help=_t("Hostname or IP of the machine that has the solrctl binary."),
  type=str,
  default="localhost")

SOLRCTL_PATH = Config(
  key="solrctl_path",
  help=_t("Location of the solrctl binary."),
  type=str,
  default="localhost")

SOLRCTL_USER = Config(
  key="solrctl_user",
  help=_t("The user that will execute solrctl commands. This user will require passwordless SSH priviliges to the solrctl host."),
  type=str,
  default="hue")

SOLRCTL_TMP_DIR = Config(
  key="solrctl_tmp_dir",
  help=_t("The search configuration template will be copied to this directory on the solrctl host machine."),
  type=str,
  default="/tmp")
