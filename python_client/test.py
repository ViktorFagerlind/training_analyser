import sys
import plotly.graph_objs as go
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QTabWidget, QPushButton
from PyQt6.QtGui import QAction  # Correct import for QAction in PyQt6
from PyQt6.QtWebEngineWidgets import QWebEngineView

# Function to create the first Plotly figure
def create_plotly_figure_1():
    x_data = [1, 2, 3, 4, 5]
    y_data = [10, 15, 13, 17, 14]

    fig = go.Figure(
        data=[go.Scatter(x=x_data, y=y_data, mode='lines+markers')],
        layout=go.Layout(title='First Plotly Graph')
    )

    return fig

# Function to create the second Plotly figure
def create_plotly_figure_2():
    categories = ['A', 'B', 'C', 'D', 'E']
    values = [5, 7, 3, 8, 6]

    fig = go.Figure(
        data=[go.Bar(x=categories, y=values)],
        layout=go.Layout(title='Second Plotly Graph')
    )

    return fig

# Widget for displaying a Plotly graph in a tab with a redraw button
class PlotlyTab(QWidget):
    def __init__(self, create_figure_func):
        super().__init__()

        self.create_figure_func = create_figure_func

        layout = QVBoxLayout()
        self.setLayout(layout)

        # Create a QWebEngineView widget to display the plot
        self.browser = QWebEngineView()
        layout.addWidget(self.browser)

        # Create a redraw button
        self.redraw_button = QPushButton("Redraw")
        self.redraw_button.clicked.connect(self.redraw_plot)
        layout.addWidget(self.redraw_button)

        # Initial plot rendering
        self.redraw_plot()

    def redraw_plot(self):
        # Generate the plotly graph and set it in the browser
        fig = self.create_figure_func()
        html_content = fig.to_html(include_plotlyjs='cdn')
        self.browser.setHtml(html_content)

# Main application window
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Plotly in PyQt6 with Tabs, Redraw, and Menu")
        self.setGeometry(100, 100, 800, 600)

        # Create a tab widget
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        # Create the first tab with the first plot and redraw button
        tab1 = PlotlyTab(create_plotly_figure_1)
        self.tabs.addTab(tab1, "Tab 1")

        # Create the second tab with the second plot and redraw button
        tab2 = PlotlyTab(create_plotly_figure_2)
        self.tabs.addTab(tab2, "Tab 2")

        # Create a menu bar
        menu_bar = self.menuBar()

        # Add a "File" menu
        file_menu = menu_bar.addMenu("File")

        # Add a "Redraw" action
        redraw_action = QAction("Redraw", self)
        redraw_action.triggered.connect(self.redraw_current_tab)
        file_menu.addAction(redraw_action)

    def redraw_current_tab(self):
        # Get the current tab and trigger its redraw function
        current_tab = self.tabs.currentWidget()
        if isinstance(current_tab, PlotlyTab):
            current_tab.redraw_plot()

# Main entry point
if __name__ == "__main__":
    # Create the application object
    app = QApplication(sys.argv)

    # Create and show the main window
    main_window = MainWindow()
    main_window.show()

    # Execute the application's main loop
    sys.exit(app.exec())
    