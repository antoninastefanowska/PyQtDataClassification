from abc import ABC, abstractmethod

class Classifier(ABC):
    def __init__(self, data, class_column_name):
        self.data = data
        self.class_column_name = class_column_name

    def update_data(self, data):
        self.data = data

    @abstractmethod
    def classify(self, data_object):
        pass

    def prepare(self):
        pass