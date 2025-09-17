from intefaces import IPresenter, IModel, IView

class Presenter(IPresenter):
    def __init__(self, model: IModel, view: IView):
        self.model: IModel = model
        self.view: IView = view
        self.model.set_presenter(self)
        self.view.set_presenter(self)

    def start_simulation(self):
        self.model.start_simulation()

    def show_results(self, results):
        self.view.show_results(results)