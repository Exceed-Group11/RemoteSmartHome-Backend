from abc import ABC, abstractclassmethod
from typing import Dict


class ResponseModel(ABC):

    @abstractclassmethod
    def to_dict(self) -> Dict:
        pass

    @staticmethod
    @abstractclassmethod
    def from_dict(dict_data: Dict):
        pass
