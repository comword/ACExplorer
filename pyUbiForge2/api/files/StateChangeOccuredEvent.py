from pyUbiForge2.api.game import SubclassBaseFile
from .Event import Event as _Event


class StateChangeOccuredEvent(SubclassBaseFile):
    ResourceType = 0x0B0095AA
    ParentResourceType = _Event.ResourceType
    parent: _Event
