from pyUbiForge2.api.game import SubclassBaseFile
from .Event import Event as _Event


class DrownEvent(SubclassBaseFile):
    ResourceType = 0x3C9861C9
    ParentResourceType = _Event.ResourceType
    parent: _Event
