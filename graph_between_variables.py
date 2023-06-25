import sys
import pandas as pd
import numpy as np
from PyQt5.QtWidgets import QWidget, QMainWindow,QApplication,QComboBox,QGraphicsView,QVBoxLayout,QHBoxLayout,QPushButton,QFileDialog,QLineEdit,QTextEdit,QDockWidget,QCheckBox,QTableView,QHeaderView,QFormLayout,QLabel,QGraphicsDropShadowEffect
from PyQt5.QtChart import QChart,QChartView,QValueAxis,QLineSeries,QScatterSeries
from PyQt5.QtGui import QPainter,QColor,QFont
from PyQt5.QtCore import Qt



class ChartView(QChartView):
    def __init__(self,chart):
        super().__init__(chart)
        self.chart=chart
        self.start_pos=None


    def wheelEvent(self, event):
        # print("yes")
        zoom,scale=1,1.10

        if event.angleDelta().y()>=120 and zoom<3:
            zoom*=1.25
            self.chart.zoom(scale)

        elif event.angleDelta().y()<=-120 and zoom>0.5:
            zoom*=0.8
            self.chart.zoom(1/scale)

        
    def mousePressEvent(self, event):
        if event.button()==Qt.LeftButton:
            self.setDragMode(QGraphicsView.ScrollHandDrag)
            self.start_pos=event.pos()

    def mouseMoveEvent(self, event):
        if event.buttons()==Qt.LeftButton:
            delta=self.start_pos-event.pos()
            self.chart.scroll(delta.x(),-delta.y())
            self.start_pos=event.pos()

    def mouseReleaseEvent(self, event):
        self.setDragMode(QGraphicsView.NoDrag)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Graph between variables")
        self.setMinimumSize(1000,600)

        self.dataFrame=None
        self.first_time_change=True

        self.left_layout=QVBoxLayout()
        self.right_layout=QVBoxLayout()

        self.combo_first=QComboBox()
        # self.combo_first.setMinimumWidth(150)
        self.combo_first.currentIndexChanged.connect(self.make_plot)
        
        self.combo_second=QComboBox()
        self.combo_second.currentIndexChanged.connect(self.make_plot)

        self.left_layout.addWidget(self.combo_first)
        self.left_layout.addWidget(self.combo_second)


        self.open_btn=QPushButton("Open File")
        self.open_btn.clicked.connect(self.open_file_function)
        self.open_btn.setObjectName("open_btn")
        self.open_btn.setCursor(Qt.PointingHandCursor)
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(8)
        shadow.setColor(QColor(0, 0, 0, 100))
        shadow.setOffset(0, 2)
        self.open_btn.setGraphicsEffect(shadow)


        self.sep=QLineEdit()
        self.sep.setPlaceholderText("Enter the separator (; , ...etc)")
        self.sep.setObjectName("separator")

        self.right_up=QHBoxLayout()
        self.right_up.addWidget(self.open_btn)
        self.right_up.addWidget(self.sep)
        # left-top-right-bottom
        self.right_layout.setContentsMargins(5,10,0,5)

        # self.chart_view=QChartView()
        # **********************************************
        self.x_min,self.x_max,self.y_min,self.y_max=0,1,0,1
        self.chart=QChart() 
        self.chart.legend().hide()
        self.chart.setTheme(1)
        self.axis_x=QValueAxis()
        self.axis_x.setRange(self.x_min,self.x_max)
        
        self.axis_y=QValueAxis()
        self.axis_y.setRange(self.y_min,self.y_max)

        self.chart.addAxis(self.axis_x,Qt.AlignBottom)
        self.chart.addAxis(self.axis_y,Qt.AlignLeft)


        self.chart_view=ChartView(self.chart)
        self.chart_view.setStyleSheet("background-color: transparent;")

        # ***********************************************

        widget=QWidget()

        right_widget=QWidget()
        right_widget.setObjectName("container")

        self.main_layout=QHBoxLayout()

        self.right_layout.addLayout(self.right_up)
        self.right_layout.addWidget(self.chart_view)
        right_widget.setLayout(self.right_layout)

        # self.main_layout.addLayout(self.left_layout)
        # self.main_layout.addLayout(self.right_layout)
        self.main_layout.addWidget(right_widget)

        self.main_layout.setContentsMargins(0,0,0,0)
        self.main_layout.setSpacing(0)

        widget.setLayout(self.main_layout)

        self.setCentralWidget(widget)

        self.setupToolsDockWidget()
        self.setupMenu()

        
        self.apply_stylesheet()


    def apply_stylesheet(self):
        stylesheet=None
        with open('graph.qss', 'r') as f:
            stylesheet = f.read()
        self.setStyleSheet(stylesheet)
        f.close()

    
    def open_file_function(self):
        self.first_time_change=True
        
        filename,_=QFileDialog.getOpenFileName(self,"Open File","","All Files(*)")
        if filename:
            get=False
            sep=self.sep.text()
            if filename.endswith(".csv"):
                if len(sep)>0:
                    self.dataFrame=pd.read_csv(filename,sep=sep)
                else:
                    self.dataFrame=pd.read_csv(filename)
                get=True
            if filename.endswith(".xlsx"):
                if len(sep)>0:
                    self.dataFrame=pd.read_excel(filename,sep=sep)
                else:
                    self.dataFrame=pd.read_csv(filename)
                get=True
            
            if not get:
                print("Not able to open data file")
                return
            
            self.combo_first.blockSignals(True)
            self.combo_first.clear()
            self.combo_first.blockSignals(False)
            self.combo_second.blockSignals(True)
            self.combo_second.clear()
            self.combo_second.blockSignals(False)
            self.combo_first.addItems(self.dataFrame.columns)
            self.combo_second.addItems(self.dataFrame.columns)


    def make_plot(self):
        if self.first_time_change:
            self.first_time_change=False
            return
        x_dim=self.combo_first.currentText()
        y_dim=self.combo_second.currentText()

        x_dtype=self.dataFrame[x_dim].dtype
        y_dtype=self.dataFrame[y_dim].dtype

        self.x_min,self.x_max,self.y_min,self.y_max=10**18,-10**18,10**18,-10**18

        print(x_dim,y_dim)

        line_series=QLineSeries()
        line_series=QScatterSeries()
        

        for x,y in zip(self.dataFrame[x_dim],self.dataFrame[y_dim]):
            if (type(x)!=int and type(x)!=float) or (type(y)!=int and type(y)!=float):
                # print(x,y,type(x),type(y))
                return
            self.x_min=min(self.x_min,x)
            self.x_max=max(self.x_max,x)
            self.y_min=min(self.y_min,y)
            self.y_max=max(self.y_max,y)
            line_series.append(x,y)

        

        # print("yes")
        int_types=[int,np.int64,np.int32,np.int16,np.int8]

        self.axis_x=QValueAxis()
        self.axis_x.setRange(self.x_min,self.x_max)
        self.axis_x.setTitleText(str(x_dim))
        self.axis_x.setTitleFont(QFont("consolas",13))
        if x_dtype in int_types:
            self.axis_x.setLabelFormat("%i")

        self.axis_y=QValueAxis()
        self.axis_y.setRange(self.y_min,self.y_max)
        self.axis_y.setTitleText(str(y_dim))
        self.axis_y.setTitleFont(QFont("consolas",13))
        if y_dtype in int_types:
            self.axis_y.setLabelFormat("%i")
        
        


        self.chart=QChart()
        self.chart.legend().hide()
        self.chart.setTheme(1)
        self.chart.addAxis(self.axis_x,Qt.AlignBottom)
        self.chart.addAxis(self.axis_y,Qt.AlignLeft)


        self.chart.addSeries(line_series)
        line_series.attachAxis(self.axis_x)
        line_series.attachAxis(self.axis_y)

        self.chart_view=ChartView(self.chart)
        self.chart_view.setStyleSheet("background-color: transparent;")

        self.refresh_plot()

    
    def refresh_plot(self):

        self.left_layout=QVBoxLayout()
        self.right_layout=QVBoxLayout()


        self.sep=QLineEdit()
        self.sep.setPlaceholderText("Enter the seperator")
        self.sep.setObjectName("separator")

        self.right_up=QHBoxLayout()
        self.right_up.addWidget(self.open_btn)
        self.right_up.addWidget(self.sep)


        widget=QWidget()
        self.main_layout=QHBoxLayout()
        right_widget=QWidget()
        right_widget.setObjectName("container")


        self.right_layout.addLayout(self.right_up)
        self.right_layout.addWidget(self.chart_view)

        right_widget.setLayout(self.right_layout)
        
        self.main_layout.addWidget(right_widget)

        widget.setLayout(self.main_layout)        

        self.main_layout.setContentsMargins(0,0,0,0)
        self.main_layout.setSpacing(0)

        self.setCentralWidget(widget)




    def setupToolsDockWidget(self):
        tools_dock=QDockWidget()
        tools_dock.setWindowTitle("Tools")
        tools_dock.setMinimumWidth(300)
        tools_dock.setMaximumWidth(300)

        tools_dock.setAllowedAreas(Qt.LeftDockWidgetArea|Qt.RightDockWidgetArea)

        themes_cb=QComboBox()
        themes_cb.addItems(["Cerulean Blue","Light", "Dark", "Sand Brown", "NCS Blue", "High Contrast", "Icy Blue", "Qt"])
        themes_cb.currentTextChanged.connect(self.changeChartTheme)
        # themes_cb.setStyleSheet("")

        self.animations_cb=QComboBox()
        self.animations_cb.addItem("No Animation",QChart.NoAnimation)
        self.animations_cb.addItem("Grid Animation",QChart.GridAxisAnimations)
        self.animations_cb.addItem("Series Animation",QChart.SeriesAnimations)
        self.animations_cb.addItem("All Animations",QChart.AllAnimations)

        self.animations_cb.currentIndexChanged.connect(self.changeAnimations)

        self.legend_cb=QComboBox()
        self.legend_cb.addItem("No Legend")
        self.legend_cb.addItem("Align Left",Qt.AlignLeft)
        self.legend_cb.addItem("Align Top",Qt.AlignTop)
        self.legend_cb.addItem("Align Right",Qt.AlignRight)
        self.legend_cb.addItem("Align Bottom",Qt.AlignBottom)
        self.legend_cb.currentTextChanged.connect(self.changeLegend)

        self.antialiasing_cb=QCheckBox()
        self.antialiasing_cb.toggled.connect(self.toggleAntialiasing)

        reset_button=QPushButton("Reset Chart Axes")
        reset_button.setObjectName("reset_btn")
        reset_button.setCursor(Qt.PointingHandCursor)
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(8)
        shadow.setColor(QColor(0, 0, 0, 100))
        shadow.setOffset(0, 2)
        reset_button.setGraphicsEffect(shadow)
        
        reset_button.clicked.connect(self.resetChartZoom)

        # data_table_view=QTableView()
        # data_table_view.setModel(self.model)
        # data_table_view.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        # data_table_view.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)

        dock_form=QFormLayout()
        dock_form.setAlignment(Qt.AlignTop)
        # label=QLabel("Themes")
        dock_form.addRow(QLabel("Themes: "),themes_cb)
        # label.setText("Animations: ")
        dock_form.addRow(QLabel("Animations: "),self.animations_cb)
        # dock_form.addRow(QLabel("Legend: "),self.legend_cb)
        dock_form.addRow(QLabel("Anti-Aliasing: "),self.antialiasing_cb)
        dock_form.addRow(reset_button)
        dock_form.addRow(self.combo_first)
        dock_form.addRow(self.combo_second)
        # dock_form.addChildLayout(self.left_layout)
        # dock_form.addRow(data_table_view)

        tools_container=QWidget()
        tools_container.setObjectName("tools_container")
        tools_container.setLayout(dock_form)
        tools_dock.setWidget(tools_container)
        # print(tools_dock.width())
        # print(tools_dock.width())

        self.addDockWidget(Qt.LeftDockWidgetArea,tools_dock)

        self.toggle_dock_tools_act=tools_dock.toggleViewAction()

    
    def changeChartTheme(self,text):
        themes_dict = {"Light": 0, "Cerulean Blue": 1, "Dark": 2, "Sand Brown": 3, "NCS Blue": 4, "High Contrast": 5, "Icy Blue": 6, "Qt": 7}
        theme = themes_dict.get(text)

        self.chart.setTheme(theme)

    def changeAnimations(self):
        animation=QChart.AnimationOptions(self.animations_cb.itemData(self.animations_cb.currentIndex()))
        self.chart.setAnimationOptions(animation)

    def changeLegend(self,text):
        alignment = self.legend_cb.itemData(self.legend_cb.currentIndex())
        if text=='No Legend':
            self.chart.legend().hide()
        else:
            self.chart.legend().setAlignment(Qt.Alignment(alignment))
            self.chart.legend().show()

    def toggleAntialiasing(self,state):
        if state:
            self.chart_view.setRenderHint(QPainter.Antialiasing, on=True)
        else:
            self.chart_view.setRenderHint(QPainter.Antialiasing, on=False)

    def resetChartZoom(self):
        self.chart.zoomReset()
        # print(self.x_min,self.x_max)
        # print(self.y_min,self.y_max)
        self.axis_x.setRange(self.x_min,self.x_max)
        self.axis_y.setRange(self.y_min,self.y_max)

    def setupMenu(self):
        menu_bar=self.menuBar()
        menu_bar.setNativeMenuBar(False)

        view_menu=menu_bar.addMenu('View')
        view_menu.addAction(self.toggle_dock_tools_act)
            





if __name__=='__main__':
    app=QApplication(sys.argv)
    window=MainWindow()
    window.show()
    sys.exit(app.exec_())