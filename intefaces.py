from abc import ABC, abstractmethod

class IModel(ABC):
    @abstractmethod
    def set_presenter(self, presenter):
        pass

    @abstractmethod
    def start_simulation(self):
        pass

class IView(ABC):
    @abstractmethod
    def set_presenter(self, presenter):
        pass

    @abstractmethod
    def show_results(self, results):
        pass

class IPresenter(ABC):
    @abstractmethod
    def start_simulation(self):
        pass

    @abstractmethod
    def show_results(self, results):
        pass