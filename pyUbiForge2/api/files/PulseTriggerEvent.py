from pyUbiForge2.api.game import SubclassBaseFile
from .Event import Event as _Event


class PulseTriggerEvent(SubclassBaseFile):
    ResourceType = 0x511A8DED
    ParentResourceType = _Event.ResourceType
    parent: _Event