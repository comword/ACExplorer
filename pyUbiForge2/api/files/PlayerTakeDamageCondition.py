from pyUbiForge2.api.game import SubclassBaseFile
from .AICondition import AICondition as _AICondition


class PlayerTakeDamageCondition(SubclassBaseFile):
    ResourceType = 0x5D5D9F44
    ParentResourceType = _AICondition.ResourceType
    parent: _AICondition
