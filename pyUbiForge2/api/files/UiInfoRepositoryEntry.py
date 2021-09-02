from pyUbiForge2.api.game import SubclassBaseFile
from .ManagedObject import ManagedObject as _ManagedObject


class UiInfoRepositoryEntry(SubclassBaseFile):
    ResourceType = 0xF1B07933
    ParentResourceType = _ManagedObject.ResourceType
    parent: _ManagedObject