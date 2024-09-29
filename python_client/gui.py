import sys
import random
from PyQt6.QtWidgets import QApplication, QMainWindow, QTabWidget, QWidget, QVBoxLayout, QPushButton
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtCore import QUrl
import plotly.graph_objs as go
from plotly.subplots import make_subplots
from plotly.io import to_html
from training_server_proxy import TrainingServerProxy
import grpc

from plots import plot_fitness_trend, plot_activities



class PlotTab(QWidget):
    def __init__(self, server):
        super().__init__()
        self.server = server

        self.layout = QVBoxLayout()

        # Create a QWebEngineView to display the plot
        self.browser = QWebEngineView()
        self.redraw_graph()

        # Create a button to redraw the graph
        self.redraw_button = QPushButton("Redraw Graph")
        self.redraw_button.clicked.connect(self.redraw_graph)

        # Add the browser and button to the layout
        self.layout.addWidget(self.browser)
        self.layout.addWidget(self.redraw_button)

        self.setLayout(self.layout)

    def redraw_graph(self):
        fitness_trend_df = self.server.get_fitness_trend()
        raw_trend_data_df = self.server.get_raw_trend_data()
        print(fitness_trend_df.to_string())
        print(raw_trend_data_df.to_string())
        fig = plot_fitness_trend(fitness_trend_df, raw_trend_data_df, '2022-09-10')
        self.browser.setHtml(to_html(fig))


class MainWindow(QMainWindow):
    def __init__(self, server):
        super().__init__()
        self.setWindowTitle("Plotly Graphs in Tabs")

        # Create a tab widget
        self.tabs = QTabWidget()

        # Add tabs
        self.tab1 = PlotTab(server)
        self.tab2 = PlotTab(server)

        self.tabs.addTab(self.tab1, "Tab 1")
        self.tabs.addTab(self.tab2, "Tab 2")

        self.setCentralWidget(self.tabs)


if __name__ == "__main__":
    app = QApplication(sys.argv)

    with grpc.insecure_channel("localhost:50051") as channel:
        server = TrainingServerProxy(channel)
        server.update_data()

        mainWindow = MainWindow(server)
        mainWindow.show()

    sys.exit(app.exec())
