from pyUbiForge2.api.game import SubclassBaseFile
from .ManagedObject import ManagedObject as _ManagedObject


class Mission(SubclassBaseFile):
    ResourceType = 0x5FDACBA0
    ParentResourceType = _ManagedObject.ResourceType
    parent: _ManagedObject
