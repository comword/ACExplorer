from pyUbiForge2.api.game import SubclassBaseFile
from .Event import Event as _Event


class RewardsChangeEvent(SubclassBaseFile):
    ResourceType = 0x17E9504F
    ParentResourceType = _Event.ResourceType
    parent: _Event
