from pyUbiForge2.api.game import SubclassBaseFile
from .Event import Event as _Event


class CharacterFleeEvent(SubclassBaseFile):
    ResourceType = 0x5AB8E003
    ParentResourceType = _Event.ResourceType
    parent: _Event
