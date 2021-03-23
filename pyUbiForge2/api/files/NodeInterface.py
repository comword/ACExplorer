from pyUbiForge2.api.game import SubclassBaseFile
from .ManagedObject import ManagedObject as _ManagedObject


class NodeInterface(SubclassBaseFile):
    ResourceType = 0xD4F37221
    ParentResourceType = _ManagedObject.ResourceType
    parent: _ManagedObject
