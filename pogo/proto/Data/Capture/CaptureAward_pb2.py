# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: Data/Capture/CaptureAward.proto

import sys
_b=sys.version_info[0]<3 and (lambda x:x) or (lambda x:x.encode('latin1'))
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
from google.protobuf import descriptor_pb2
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from Enums import ActivityType_pb2 as Enums_dot_ActivityType__pb2


DESCRIPTOR = _descriptor.FileDescriptor(
  name='Data/Capture/CaptureAward.proto',
  package='POGOProtos.Data.Capture',
  syntax='proto3',
  serialized_pb=_b('\n\x1f\x44\x61ta/Capture/CaptureAward.proto\x12\x17POGOProtos.Data.Capture\x1a\x18\x45nums/ActivityType.proto\"r\n\x0c\x43\x61ptureAward\x12\x35\n\ractivity_type\x18\x01 \x03(\x0e\x32\x1e.POGOProtos.Enums.ActivityType\x12\n\n\x02xp\x18\x02 \x03(\x05\x12\r\n\x05\x63\x61ndy\x18\x03 \x03(\x05\x12\x10\n\x08stardust\x18\x04 \x03(\x05\x62\x06proto3')
  ,
  dependencies=[Enums_dot_ActivityType__pb2.DESCRIPTOR,])
_sym_db.RegisterFileDescriptor(DESCRIPTOR)




_CAPTUREAWARD = _descriptor.Descriptor(
  name='CaptureAward',
  full_name='POGOProtos.Data.Capture.CaptureAward',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='activity_type', full_name='POGOProtos.Data.Capture.CaptureAward.activity_type', index=0,
      number=1, type=14, cpp_type=8, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='xp', full_name='POGOProtos.Data.Capture.CaptureAward.xp', index=1,
      number=2, type=5, cpp_type=1, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='candy', full_name='POGOProtos.Data.Capture.CaptureAward.candy', index=2,
      number=3, type=5, cpp_type=1, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='stardust', full_name='POGOProtos.Data.Capture.CaptureAward.stardust', index=3,
      number=4, type=5, cpp_type=1, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=86,
  serialized_end=200,
)

_CAPTUREAWARD.fields_by_name['activity_type'].enum_type = Enums_dot_ActivityType__pb2._ACTIVITYTYPE
DESCRIPTOR.message_types_by_name['CaptureAward'] = _CAPTUREAWARD

CaptureAward = _reflection.GeneratedProtocolMessageType('CaptureAward', (_message.Message,), dict(
  DESCRIPTOR = _CAPTUREAWARD,
  __module__ = 'Data.Capture.CaptureAward_pb2'
  # @@protoc_insertion_point(class_scope:POGOProtos.Data.Capture.CaptureAward)
  ))
_sym_db.RegisterMessage(CaptureAward)


# @@protoc_insertion_point(module_scope)
