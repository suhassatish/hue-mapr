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

"""
import pickle
from desktop.models import Document
from desktop.lib.document_serializers import DocumentSerializer, DocumentDeserializer
print Document.objects.all()
a = DocumentSerializer().serialize(Document.objects.all())
b = DocumentDeserializer(a)
"""

import pickle

from django.core.serializers.base import Serializer
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType


class SerializedObject(object):
  def __init__(self, doc_id, obj):
    self.doc_id = doc_id
    self.obj = obj
    self.m2m = {}
    self.m2o = {}
    self.gfk = {}
    self.saved = False

  def __repr__(self):
    return "<SerializedObject: %s.%s(pk=%s)>" % (self.obj._meta.app_label, self.obj._meta.object_name, self.obj.pk)

  def save_m2o(self, save_m2m=True, save_m2o=True, save_gfk=True):
    if save_m2o:
      m2o = self.m2o
      self.m2o = {}
      for field_name in m2o:
        if field_name in ('owner',):
          setattr(self.obj, field_name, User.objects.get(username=m2o[field_name].obj.username))
        else:
          m2o[field_name].save(save_m2m=save_m2m, save_m2o=save_m2o, save_gfk=save_gfk)

  def save_gfk(self, save_m2m=True, save_m2o=True, save_gfk=True):
    if save_gfk:
      gfk = self.gfk
      self.gfk = {}
      for field_name in gfk:
        gfk[field_name].save(save_m2m=save_m2m, save_m2o=save_m2o, save_gfk=save_gfk)

  def save_m2m(self, save_m2m=True, save_m2o=True, save_gfk=True):
    if save_m2m:
      m2m = self.m2m
      self.m2m = {}
      field_names = m2m.keys()
      for field_name in m2m:
        field_name = field_names.pop()
        field, _, _, _ = self.obj._meta.get_field_by_name(field_name)
        if field.rel.through._meta.auto_created:
          for relation in m2m[field_name]:
            relation.save(save_m2m=save_m2m, save_m2o=save_m2o, save_gfk=save_gfk)
            getattr(self.obj, field_name).add(relation.obj)
        else:
          through_objs = m2m[field_name]
          for through_obj in through_objs:
            through_obj.save()

  def save_after(self, save_m2m=True, save_m2o=True, save_gfk=True):
    pass

  def save(self, save_m2m=True, save_m2o=True, save_gfk=True):
    if not self.saved:
      self.obj.pk = None

      self.save_m2o(save_m2m=save_m2m, save_m2o=save_m2o, save_gfk=save_gfk)
      self.save_gfk(save_m2m=save_m2m, save_m2o=save_m2o, save_gfk=save_gfk)
      self.obj.save()
      self.saved = True
      self.save_m2m(save_m2m=save_m2m, save_m2o=save_m2o, save_gfk=save_gfk)
      self.save_after(save_m2m=save_m2m, save_m2o=save_m2o, save_gfk=save_gfk)


class SerializeInheritance(SerializedObject):
  def save(self, save_m2m=True, save_m2o=True, save_gfk=True):
    if not self.saved:
      self.obj.id = None

      self.save_m2o(save_m2m=save_m2m, save_m2o=save_m2o, save_gfk=save_gfk)
      self.save_gfk(save_m2m=save_m2m, save_m2o=save_m2o, save_gfk=save_gfk)
      self.obj.save()
      self.saved = True
      self.save_m2m(save_m2m=save_m2m, save_m2o=save_m2o, save_gfk=save_gfk)
      self.save_after(save_m2m=save_m2m, save_m2o=save_m2o, save_gfk=save_gfk)


class SerializedDocument(SerializedObject):
  def __init__(self, obj):
    super(SerializedDocument, self).__init__(obj.uid, obj)

  def __repr__(self):
    return "<SerializedDocument: %s.%s(pk=%s)>" % (self.obj._meta.app_label, self.obj._meta.object_name, self.obj.pk)

  def save_m2o(self, save_m2m=True, save_m2o=True, save_gfk=True):
    if save_m2o:
      m2o = self.m2o
      self.m2o = {}
      for field_name in m2o:
        if field_name in ('owner',):
          setattr(self.obj, field_name, User.objects.get(username=m2o[field_name].obj.username))
        elif field_name in ('content_type',):
          setattr(self.obj, field_name, ContentType.objects.get(app_label=m2o[field_name].obj.app_label, model=m2o[field_name].obj.model))
        else:
          m2o[field_name].save(save_m2m=save_m2m, save_m2o=save_m2o, save_gfk=save_gfk)

  def save_m2m(self, save_m2m=True, save_m2o=True, save_gfk=True):
    from desktop.models import DocumentTag

    if save_m2m:
      m2m = self.m2m
      self.m2m = {}
      for field_name in m2m:
        if field_name in ('tags',):
          for relation in m2m[field_name]:
            user = User.objects.get(username=relation.m2o['owner'].obj.username)
            tag, created = DocumentTag.objects.get_or_create(owner=user, tag=relation.obj.tag)
            getattr(self.obj, field_name).add(tag)
        else:
          for relation in m2m[field_name]:
            relation.save(save_m2m=save_m2m, save_m2o=save_m2o, save_gfk=save_gfk)
            getattr(self.obj, field_name).add(relation.obj)

  def save_after(self, save_m2m=True, save_m2o=True, save_gfk=True):
    # Set uid
    self.obj.uid = self.doc_id
    self.obj.save()


class SerializedWorkflow(SerializeInheritance):
  def __init__(self, *args, **kwargs):
    super(SerializedWorkflow, self).__init__(*args, **kwargs)
    self.nodes = []
    self.start = None
    self.end = None

  def __repr__(self):
    return "<SerializedWorkflow: %s.%s(pk=%s)>" % (self.obj._meta.app_label, self.obj._meta.object_name, self.obj.pk)

  def save_m2o(self, save_m2m=True, save_m2o=True, save_gfk=True):
    if save_m2o:
      m2o = self.m2o
      self.m2o = {}
      for field_name in m2o:
        # Update start and end later (circular dependency)
        if field_name in ('start', 'end'):
          setattr(self, field_name, m2o[field_name])
          setattr(self.obj, field_name, None)
        else:
          m2o[field_name].save(save_m2m=save_m2m, save_m2o=save_m2o, save_gfk=save_gfk)

  def save_after(self, save_m2m=True, save_m2o=True, save_gfk=True):
    if save_m2o:
      if self.start:
        start = self.start
        self.start = None
        start.save(save_m2m=save_m2m, save_m2o=save_m2o, save_gfk=save_gfk)
        self.obj.start = start.obj.get_full_node()
      if self.end:
        end = self.end
        self.end = None
        end.save(save_m2m=save_m2m, save_m2o=save_m2o, save_gfk=save_gfk)
        self.obj.end = end.obj.get_full_node()
      self.obj.save()

    # Save any unlinked nodes
    nodes = self.nodes
    self.nodes = []
    for node in nodes:
      node.save(save_m2m=save_m2m, save_m2o=save_m2o, save_gfk=save_gfk)


class SerializedNode(SerializeInheritance):
  def __repr__(self):
    return "<SerializedNode: %s.%s(pk=%s)>" % (self.obj._meta.app_label, self.obj._meta.object_name, self.obj.pk)


class ObjectSerializer(Serializer):
  def __init__(self, doc, objects_map={}):
    self.doc = doc
    self.objects_map = objects_map

  def serialize_object(self, obj):
    from oozie.models import Workflow, Node

    if isinstance(obj, Node):
      obj = obj.get_full_node()

    if obj in self.objects_map:
      return self.objects_map[obj]
    else:
      if isinstance(obj, Workflow):
        ObjectSerializerClass = WorkflowSerializer
        SerializedObjectClass = SerializedWorkflow
      elif isinstance(obj, Node):
        ObjectSerializerClass = ObjectSerializer
        SerializedObjectClass = SerializedNode
      else:
        ObjectSerializerClass = ObjectSerializer
        SerializedObjectClass = SerializedObject
      self.objects_map[obj] = SerializedObjectClass(self.doc.uid, obj) # Cycle check
      ObjectSerializerClass(self.doc, self.objects_map).serialize([obj])[0]
      return self.objects_map[obj]

  def start_serialization(self):
    self.objects = []
    self.current = None

  def end_serialization(self):
    pass

  def start_object(self, obj):
    from oozie.models import Workflow, Node

    if isinstance(obj, Workflow):
      SerializedObjectClass = SerializedWorkflow
    elif isinstance(obj, Node):
      SerializedObjectClass = SerializedNode
      obj = obj.get_full_node()
    else:
      SerializedObjectClass = SerializedObject

    self.current = SerializedObjectClass(self.doc.uid, obj)
    self.objects_map[self.current.obj] = self.current

  def end_object(self, obj):
    self.objects.append(self.current)
    self.current = None

  def handle_field(self, obj, field):
    pass

  def handle_fk_field(self, obj, field):
    self.current.m2o[field.name] = self.serialize_object(getattr(obj, field.name))

  def handle_m2m_field(self, obj, field):
    if field.rel.through._meta.auto_created:
      # If the "through" model is automatically managed (through was not specified in the field)
      self.current.m2m[field.name] = [self.serialize_object(related) for related in getattr(obj, field.name).iterator()]
    else:
      # If the "through" model is managed (through was specified in the field)
      kwargs = {
        field.m2m_field_name(): self.current.obj
      }
      through_objs = field.rel.through._default_manager.filter(**kwargs)
      self.current.m2m[field.name] = [self.serialize_object(through_obj) for through_obj in through_objs]

  def getvalue(self):
    return self.objects


class WorkflowSerializer(ObjectSerializer):
  def handle_fk_field(self, obj, field):
    if field.name in ('start', 'end'):
      node = getattr(obj, field.name)
      ObjectSerializer(self.doc, self.objects_map).serialize([node])[0]
      self.current.m2o[field.name] = self.objects_map[node]
    else:
      super(WorkflowSerializer, self).handle_fk_field(obj, field)

  def end_object(self, obj):
    from oozie.models import Node

    for node in Node.objects.filter(workflow=self.current.obj):
      node = node.get_full_node()
      if node not in self.objects_map:
        self.objects_map[node] = SerializedObject(self.doc.uid, node)
        self.current.nodes.append(self.objects_map[node])

    super(WorkflowSerializer, self).end_object(obj)


class DocumentSerializer(ObjectSerializer):
  """
  Serialize in a hierarchical fashion so that Documents are the only
  objects seen at the root.
  """
  def __init__(self, objects_map=None):
    self.objects_map = objects_map or {}

  def end_serialization(self):
    pass

  def start_object(self, obj):
    self.current = SerializedDocument(obj)
    self.doc = obj
    self.add_content_object()

  def end_object(self, obj):
    super(DocumentSerializer, self).end_object(obj)
    self.doc = None

  def add_content_object(self):
    self.current.gfk['content_object'] = self.serialize_object(self.current.obj.content_object)

  def getvalue(self):
    return pickle.dumps(self.objects)


def DocumentDeserializer(stream_or_string, **options):
  return pickle.loads(stream_or_string)
