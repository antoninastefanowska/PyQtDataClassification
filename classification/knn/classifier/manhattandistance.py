from .distancemetrics import DistanceMetrics

class ManhattanDistance(DistanceMetrics):
    def __init__(self):
        pass

    def get_distance(self, data_object1, data_object2):
        sum = 0.0
        for column_name in data_object1.index:
            value1 = data_object1[column_name]
            value2 = data_object2[column_name]
            if (isinstance(value1, int) or isinstance(value1, float)) and (isinstance(value2, int) or isinstance(value2, float)):
                sum += abs(value1 - value2)
        return sum

    def get_name(self):
        return "Manhattan"