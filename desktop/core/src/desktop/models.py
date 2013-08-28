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

from django.db import models
from django.contrib.auth import models as auth_models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.utils.translation import ugettext as _, ugettext_lazy as _t
from desktop.lib.i18n import force_unicode
from desktop.lib.exceptions_renderable import PopupException


class UserPreferences(models.Model):
  """Holds arbitrary key/value strings."""
  user = models.ForeignKey(auth_models.User)
  key = models.CharField(max_length=20)
  value = models.TextField(max_length=4096)


class Settings(models.Model):
  collect_usage = models.BooleanField(db_index=True, default=True)
  tours_and_tutorials = models.BooleanField(db_index=True, default=True)

  @classmethod
  def get_settings(cls):
    settings, created = Settings.objects.get_or_create(id=1)
    return settings


class DocumentTag(models.Model):
  owner = models.ForeignKey(auth_models.User, db_index=True)
  tag = models.SlugField()

  def __unicode__(self):
    return force_unicode('%s') % (self.tag,)

  @classmethod
  def get_trash_tag(cls, user):
    tag, created = DocumentTag.objects.get_or_create(owner=user, tag='trashed')
    return tag


class DocumentManager(models.Manager):
  
  def link(self, content_object, owner, name='', description=''):
    doc = Document.objects.create(
              content_object=content_object,
              owner=owner,
              name=name,
              description=description
          )

    tag, created = DocumentTag.objects.get_or_create(owner=owner, tag='default')
    doc.tags.add(tag)

    return doc

  def sync(self):
    try:
      from oozie.models import Workflow

      for job in Workflow.objects.exclude(name='pig-app-hue-script'):
        if not job.doc.exists():
          doc = Document.objects.link(job, owner=job.owner, name=job.name, description=job.description)
          tag, created = DocumentTag.objects.get_or_create(owner=job.owner, tag='default')
          doc.tags.add(tag)
          if job.is_trashed:
            doc.send_to_trash()
    except Exception, e:
      print e
       

class Document(models.Model):
  owner = models.ForeignKey(auth_models.User, db_index=True, verbose_name=_t('Owner'), help_text=_t('User who can own the job.'), related_name='doc_owner')
  name = models.TextField(default='')
  description = models.TextField(default='')
  last_modified = models.DateTimeField(auto_now=True, db_index=True, verbose_name=_t('Last modified'))  
  # todo delete, replaced by tags?
  status = models.TextField(
      default='active', choices=(('active', 'active'),
                                 ('trashed', 'trashed'),
                                 ('history', 'history'),),)    
  version = models.SmallIntegerField(default=1, verbose_name=_t('Schema version')) # get latest? cf status
  
  tags = models.ManyToManyField(DocumentTag, db_index=True)
  
  content_type = models.ForeignKey(ContentType)
  object_id = models.PositiveIntegerField()
  content_object = generic.GenericForeignKey('content_type', 'object_id')

  objects = DocumentManager()
  unique_together = ('content_type', 'object_id')

  def __unicode__(self):
    return force_unicode('%s %s') % (self.owner, self.name)
      
  def is_editable(self, user):
    return user.is_superuser or self.owner == user

  def can_edit_or_exception(self, user, exception_class=PopupException):
    if self.is_editable(user):
      return True
    else:
      raise exception_class(_('Only superusers and %s are allowed to modify this document.') % user)      
      
  def send_to_trash(self):
    tag = DocumentTag.get_trash_tag(user=self.owner)
    self.tags.add(tag)

  def restore_from_trash(self):
    tag = DocumentTag.get_trash_tag(user=self.owner)
    self.tags.remove(tag)

#class DocumentPermission(models.Model):
#  
#  users = models.ManyToManyField(auth_models.User, db_index=True)
#  groups = models.ManyToManyField(auth_models.Group, db_index=True) 
      