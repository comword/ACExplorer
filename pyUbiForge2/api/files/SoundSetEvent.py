from pyUbiForge2.api.game import SubclassBaseFile
from .Event import Event as _Event


class SoundSetEvent(SubclassBaseFile):
    ResourceType = 0x0EFFFE90
    ParentResourceType = _Event.ResourceType
    parent: _Event
