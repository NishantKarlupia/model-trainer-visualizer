import sys
from PyQt5 import uic
from PyQt5.QtWidgets import QMainWindow,QApplication,QHBoxLayout,QFrame
from PyQt5.QtCore import QPropertyAnimation
from PyQt5.QtSvg import QSvgWidget
from PyQt5.QtGui import QPixmap,QIcon
from PyQt5.QtCore import QSize,Qt,QPoint

from graph_between_variables import MainWindow as Graph
from show_data_model import MainWindow as DataModel

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("dashboard.ui",self)

        self.previous_pos=self.pos()

        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        self.operational.setMaximumHeight(50)
        self.sidebar.setMaximumWidth(200)

        self.operational.setLayout(self.operational_layout)
        self.body_frame.setLayout(self.layout_on_body_frame)

        self.toggle_sidebar.clicked.connect(self.toggle_window)
        self.visualize_data_btn.clicked.connect(self.visualize_data_function)
        self.minimize_btn.clicked.connect(self.showMinimized)
        self.maximize_btn.clicked.connect(self.showMaximized)
        self.close_btn.clicked.connect(self.close)
        self.view_data_btn.clicked.connect(self.show_data_model_function)

        self.mainLayout.setContentsMargins(0,0,0,0)
        self.mainLayout.setSpacing(0)

        self.sidebar.setLayout(self.itemLayout)

    

        self.doStyling()
        self.apply_stylesheet()

        self.centralwidget.setLayout(self.mainLayout)

        self.setCentralWidget(self.centralwidget)

    def apply_stylesheet(self):
        stylesheet=None
        with open("dashboard.qss","r") as f:
            stylesheet=f.read()
        f.close()

        self.setStyleSheet(stylesheet)

    def visualize_data_function(self):
        self.toggle_window()

        self.clear_layout(self.layout_on_body_frame)

        graph_widget=Graph()
        
        self.layout_on_body_frame.addWidget(graph_widget)

    def show_data_model_function(self):
        self.toggle_window()
        self.clear_layout(self.layout_on_body_frame)
        data_model_widget=DataModel()
        self.layout_on_body_frame.addWidget(data_model_widget)

    def clear_layout(self,layout):
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.setParent(None)
            else:
                nested_layout = item.layout()
                if nested_layout:
                    self.clear_layout(nested_layout)
            del item

    


    def toggle_window(self):
        width,newWidth=self.sidebar.width(),0

        newWidth=[200,0][width>=150]

        # print(width,newWidth)

        self.animation=QPropertyAnimation(self.sidebar,b'maximumWidth')
        self.animation.setDuration(500)
        self.animation.setStartValue(width)
        self.animation.setEndValue(newWidth)
        self.animation.start()


        


    def doStyling(self):

        toggle=QPixmap("icons/align-left.svg")
        toggle = QIcon(toggle)
        self.toggle_sidebar.setIcon(toggle)
        # self.toggle_sidebar.setIconSize(self.toggle_sidebar.size())

        minimize=QPixmap("icons/minus.svg")
        minimize=QIcon(minimize)
        self.minimize_btn.setIcon(minimize)

        maximize=QPixmap("icons/arrow-up-right.svg")
        maximize=QIcon(maximize)
        self.maximize_btn.setIcon(maximize)

        close=QPixmap("icons/x.svg")
        close=QIcon(close)
        self.close_btn.setIcon(close)


    def mousePressEvent(self,event):
        """previous position"""
        self.previous_pos=event.globalPos()

    
    def mouseMoveEvent(self,event):
        """new position"""
        new_pos=QPoint(event.globalPos()-self.previous_pos)
        self.move(self.x()+new_pos.x(),self.y()+new_pos.y())
        self.previous_pos=event.globalPos()





if __name__=="__main__":
    app=QApplication(sys.argv)
    window=MainWindow()
    window.show()
    sys.exit(app.exec_())