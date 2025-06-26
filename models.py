import uuid
from datetime import datetime as dt

class BaseEntity:
    def __init__(self):
        self.id = self._gerar_id()
        self.data_criacao = dt.now()
    
    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.id == other.id

    def _gerar_id(self):
        return uuid.uuid4()

    def __hash__(self):
        return hash(self.id)
