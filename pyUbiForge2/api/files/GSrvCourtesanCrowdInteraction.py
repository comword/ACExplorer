from pyUbiForge2.api.game import SubclassBaseFile
from .Statechart import Statechart as _Statechart


class GSrvCourtesanCrowdInteraction(SubclassBaseFile):
    ResourceType = 0xCF19CE15
    ParentResourceType = _Statechart.ResourceType
    parent: _Statechart