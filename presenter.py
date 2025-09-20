class Presenter:
    def __init__(self, model, view):
        self.model = model
        self.view = view
        self.model.set_presenter(self)
        self.view.set_presenter(self)

    def start_simulation(self):
        self.model.start_simulation()

    def show_results(self, results):
        self.view.show_results(results)
