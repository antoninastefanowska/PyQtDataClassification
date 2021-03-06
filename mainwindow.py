from PyQt5 import uic
from PyQt5.QtWidgets import QMainWindow, QFileDialog, QTableView, QTreeView
from PyQt5.QtCore import pyqtSlot, QPoint

from data.tablemodel import TableModel
from data.loaddatadialog import LoadDataDialog
from metrics.precalculateddistance import PrecalculatedDistance

from preprocessing.gui.texttonumberdialog import TextToNumberDialog
from preprocessing.gui.discretizedialog import DiscretizeDialog
from preprocessing.gui.normalizedialog import NormalizeDialog
from preprocessing.gui.normalizealldialog import NormalizeAllDialog
from preprocessing.gui.scaledialog import ScaleDialog
from preprocessing.gui.classcolumndialog import ClassColumnDialog

from analysis.gui.highlightdialog import HighlightDialog
from analysis.gui.comparecolumnsdialog import CompareColumnsDialog
from analysis.gui.comparecolumnsresultwindow import CompareColumnsResultWindow

from visualization.gui.chart2ddialog import Chart2DDialog
from visualization.gui.chart3ddialog import Chart3DDialog
from visualization.gui.chart2dhyperplanesdialog import Chart2DHyperplanesDialog
from visualization.gui.histogramdialog import HistogramDialog
from visualization.gui.chartwindow import ChartWindow
from visualization.chartcanvas import ChartCanvas

from classification.leaveoneouttester import LeaveOneOutTester
from classification.utils.testingmanager import TestingManager

from classification.knn.knnclassifier import KNNClassifier
from classification.knn.gui.knnclassifierdialog import KNNClassifierDialog
from classification.knn.utils.knntestingmanager import KNNTestingManager

from classification.hyperplane.hyperplaneclassifier import HyperplaneClassifier

from classification.decisiontree.decisiontreeclassifier import DecisionTreeClassifier
from classification.decisiontree.gui.classifiertreeoutputwindow import ClassifierTreeOutputWindow

from classification.gui.newobjectdialog import NewObjectDialog
from classification.gui.classificationresultwindow import ClassificationResultWindow
from classification.hyperplane.gui.classifiertableoutputwindow import ClassifierTableOutputWindow

from preprocessing.gui.clusteranalysisdialog import ClusterAnalysisDialog

from data.classifieritemmodel import ClassifierItemModel

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.data = None
        self.table_model = None
        self.testing_manager = None

        self.classifier_tree_model = ClassifierItemModel(self)

        self.load_ui()

    def load_ui(self):
        uic.loadUi("ui/mainwindow.ui", self)
        classifier_tree_view = self.findChild(QTreeView, "classifierTreeView")
        classifier_tree_view.setModel(self.classifier_tree_model)

    @pyqtSlot(QPoint)
    def open_classifier_menu(self, position):
        classifier_tree_view = self.findChild(QTreeView, "classifierTreeView")
        indexes = classifier_tree_view.selectedIndexes()
        if len(indexes) > 0:
            index = indexes[0]
            node = index.internalPointer()
            menu = node.menu
            if menu:
                menu.exec_(classifier_tree_view.viewport().mapToGlobal(position))

    @pyqtSlot()
    def open_file(self):
        filename, _ = QFileDialog.getOpenFileName(self, "Otwórz...", "", "Wszystkie pliki (*);;Pliki CSV (*.csv);;Pliki tekstowe (*.txt)", options=QFileDialog.Options())
        if filename:
            dialog = LoadDataDialog(self, filename)
            if dialog.exec_():
                table_view = self.findChild(QTableView, "tableView")
                self.data = dialog.data
                self.table_model = TableModel(self.data)
                table_view.setModel(self.table_model)

    @pyqtSlot()
    def save_file(self):
        filename, _ = QFileDialog.getSaveFileName(self, "Zapisz jako...", "", "Wszystkie pliki (*);;Pliki CSV (*.csv);;Pliki tekstowe (*.txt)", options=QFileDialog.Options())
        if filename:
            self.data.to_csv(filename, sep=';', header=True, index=False)

    @pyqtSlot()
    def text_to_numbers(self):
        dialog = TextToNumberDialog(self, self.data)
        if dialog.exec_():
            self.table_model.layoutChanged.emit()

    @pyqtSlot()
    def discretize(self):
        dialog = DiscretizeDialog(self, self.data)
        if dialog.exec_():
            self.table_model.layoutChanged.emit()

    @pyqtSlot()
    def normalize(self):
        dialog = NormalizeDialog(self, self.data)
        if dialog.exec_():
            self.table_model.layoutChanged.emit()

    @pyqtSlot()
    def normalize_all(self):
        dialog = NormalizeAllDialog(self, self.data)
        if dialog.exec_():
            self.table_model.layoutChanged.emit()

    @pyqtSlot()
    def scale(self):
        dialog = ScaleDialog(self, self.data)
        if dialog.exec_():
            self.table_model.layoutChanged.emit()

    @pyqtSlot()
    def highlight(self):
        dialog = HighlightDialog(self, self.data)
        if dialog.exec_():
            self.table_model.green_rows = dialog.smallest_indexes
            self.table_model.red_rows = dialog.biggest_indexes
            self.table_model.layoutChanged.emit()

    @pyqtSlot()
    def remove(self):
        table_view = self.findChild(QTableView, "tableView")
        selected_columns = table_view.selectionModel().selectedColumns()
        columns = [self.data.columns[index.column()] for index in selected_columns]
        self.data = self.data.drop(columns, axis='columns')
        self.table_model.set_data(self.data)
        self.table_model.layoutChanged.emit()

    @pyqtSlot()
    def show_chart2d(self):
        chart_canvas = ChartCanvas(subplots=1)
        dialog = Chart2DDialog(self, self.data, chart_canvas)
        if dialog.exec_():
            chart_window = ChartWindow(self, chart_canvas)
            chart_window.show()

    @pyqtSlot()
    def show_chart3d(self):
        chart_canvas = ChartCanvas(subplots=1, projection="3d")
        dialog = Chart3DDialog(self, self.data, chart_canvas)
        if dialog.exec_():
            chart_window = ChartWindow(self, chart_canvas)
            chart_window.show()

    @pyqtSlot()
    def show_chart2d_hyperplanes(self):
        chart_canvas = ChartCanvas(subplots=1)
        dialog = Chart2DHyperplanesDialog(self, self.data, chart_canvas)
        if dialog.exec_():
            chart_window = ChartWindow(self, chart_canvas, dialog.hyperplanes, dialog.xlims, dialog.ylims)
            chart_window.show()

    @pyqtSlot()
    def show_histogram(self):
        chart_canvas = ChartCanvas(subplots=1)
        chart = chart_canvas.get_subplot(0)
        dialog = HistogramDialog(self, self.data, chart)
        if dialog.exec_():
            chart_window = ChartWindow(self, chart_canvas)
            chart_window.show()

    def add_classifier(self, classifier):
        self.classifier_tree_model.add_classifier(classifier)
        self.classifier_tree_model.layoutChanged.emit()
        classifier_tree_view = self.findChild(QTreeView, "classifierTreeView")
        classifier_tree_view.setColumnWidth(0, 200)

    @pyqtSlot()
    def create_knn_classifier(self):
        dialog = KNNClassifierDialog(self, self.data)
        if dialog.exec_():
            class_column_name = dialog.class_column_name
            metrics = dialog.metrics
            k_value = dialog.k_value
            classifier = KNNClassifier(self.data, class_column_name, metrics, k_value)
            classifier.build()
            self.add_classifier(classifier)

    @pyqtSlot()
    def create_hyperplane_classifier(self):
        dialog = ClassColumnDialog(self, self.data)
        if dialog.exec_():
            class_column_name = dialog.class_column_name
            classifier = HyperplaneClassifier(self.data, class_column_name)
            classifier.build()
            self.add_classifier(classifier)

    @pyqtSlot()
    def create_decision_tree_classifier(self):
        dialog = ClassColumnDialog(self, self.data)
        if dialog.exec_():
            class_column_name = dialog.class_column_name
            classifier = DecisionTreeClassifier(self.data, class_column_name)
            classifier.build()
            self.add_classifier(classifier)

    def show_classifier_output(self, classifier):
        if isinstance(classifier, DecisionTreeClassifier):
            window = ClassifierTreeOutputWindow(self, classifier.get_classifier_output_data())
            window.show()
        elif isinstance(classifier, HyperplaneClassifier):
            window = ClassifierTableOutputWindow(self, classifier.get_classifier_output_data())
            window.show()
            if len(self.data.columns) == 3:
                no_class_data = self.data.drop(classifier.class_column_name, axis=1)
                x_column_name = no_class_data.columns[0]
                y_column_name = no_class_data.columns[1]

                x_min = no_class_data[x_column_name].min()
                x_max = no_class_data[x_column_name].max()
                y_min = no_class_data[y_column_name].min()
                y_max = no_class_data[y_column_name].max()

                xlims = (x_min, x_max)
                ylims = (y_min, y_max)
                hyperplanes = [hyperplane for hyperplane in classifier.hyperplanes]

                chart_canvas = ChartCanvas(subplots=1)
                chart_canvas.generate_2d_chart(self.data, classifier.class_column_name, x_column_name, y_column_name)
                chart_window = ChartWindow(self, chart_canvas, hyperplanes, xlims, ylims)
                chart_window.show()

    def classify_new_object(self, classifier):
        dialog = ClassColumnDialog(self, self.data)
        if dialog.exec_():
            class_column_name = dialog.class_column_name
            new_object_dialog = NewObjectDialog(self, self.data, class_column_name)
            if new_object_dialog.exec_():
                new_object = new_object_dialog.new_object
                result_window = ClassificationResultWindow(self, new_object, classifier)
                result_window.show()

    def classify_loaded_object(self, classifier):
        dialog = ClassColumnDialog(self, self.data)
        if dialog.exec_():
            class_column_name = dialog.class_column_name

            filename, _ = QFileDialog.getOpenFileName(self, "Otwórz...", "", "Wszystkie pliki (*);;Pliki CSV (*.csv);;Pliki tekstowe (*.txt)", options=QFileDialog.Options())
            if filename:
                dialog = LoadDataDialog(self, filename)
                if dialog.exec_():
                    columns = self.data.columns
                    columns = columns[columns != class_column_name]
                    loaded_data = dialog.data
                    loaded_data.columns = columns
                    new_object = loaded_data.iloc[0]
                    result_window = ClassificationResultWindow(self, new_object, classifier)
                    result_window.show()

    @pyqtSlot()
    def test_knn_classifier(self):
        dialog = KNNClassifierDialog(self, self.data)
        if dialog.exec_():
            class_column_name = dialog.class_column_name
            metrics = dialog.metrics
            k_value = dialog.k_value

            self.testing_manager = KNNTestingManager(self, self.data, class_column_name)
            distances = PrecalculatedDistance(self.data, class_column_name, metrics)
            classifier = KNNClassifier(self.data, class_column_name, distances, k_value)
            tester = LeaveOneOutTester(self.data, class_column_name)

            self.testing_manager.run_single_test(tester, classifier)

    @pyqtSlot()
    def test_hyperplane_classifier(self):
        dialog = ClassColumnDialog(self, self.data)
        if dialog.exec_():
            class_column_name = dialog.class_column_name

            self.testing_manager = TestingManager(self, self.data, class_column_name)
            classifier = HyperplaneClassifier(self.data, class_column_name)
            tester = LeaveOneOutTester(self.data, class_column_name)
            self.testing_manager.run_single_test(tester, classifier)

    @pyqtSlot()
    def test_decision_tree_classifier(self):
        dialog = ClassColumnDialog(self, self.data)
        if dialog.exec_():
            class_column_name = dialog.class_column_name

            self.testing_manager = TestingManager(self, self.data, class_column_name)
            classifier = DecisionTreeClassifier(self.data, class_column_name)
            tester = LeaveOneOutTester(self.data, class_column_name)
            self.testing_manager.run_single_test(tester, classifier)

    @pyqtSlot()
    def test_knn_parameters(self):
        dialog = ClassColumnDialog(self, self.data)
        if dialog.exec_():
            class_column_name = dialog.class_column_name
            self.testing_manager = KNNTestingManager(self, self.data, class_column_name)
            self.testing_manager.run_parameter_testing()

    @pyqtSlot()
    def cluster_analysis(self):
        dialog = ClusterAnalysisDialog(self, self.data)
        if dialog.exec_():
            self.table_model.layoutChanged.emit()

    @pyqtSlot()
    def compare_columns(self):
        dialog = CompareColumnsDialog(self, self.data)
        if dialog.exec_():
            column1_name = dialog.column1_name
            column2_name = dialog.column2_name
            similarity_metrics_name = dialog.similarity_metrics_name
            result = dialog.result

            result_window = CompareColumnsResultWindow(self, column1_name, column2_name, result, "Miara: " + similarity_metrics_name)
            result_window.show()