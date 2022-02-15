from abc import ABC, abstractstaticmethod, abstractmethod
from typing import Dict


class DataModel(ABC):

    @abstractmethod
    def to_dict(self) -> Dict:
        pass

    @abstractstaticmethod
    def from_dict(dict_data: Dict):
        pass
