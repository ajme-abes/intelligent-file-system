from abc import ABC, abstractmethod
class BaseProcessor(ABC):

    @abstractmethod
    def load(self, file_path: str):
        pass
    
    @abstractmethod
    def process(self, data):
        pass

    @abstractmethod
    def save(self, data, output_path: str):
        pass