import datetime
import json
import requests
from Query_train_info import Query_train_info
from PyQt6 import QtCore, QtGui, QtWidgets


# 查询火车站信息的函数
def Query_information(station_name):
    with open("station_telecodes.json", "r", encoding="utf-8") as f:
        station_telecodes = json.load(f)

    station_telecode = station_telecodes.get(station_name, "null")

    json_data = {
        "params": {
            "stationCode": station_telecode,
            "type": "D"
        },
        "isSign": 0
    }

    res = requests.post("https://tripapi.ccrgt.com/crgt/trip-server-app/screen/getStationScreenByStationCode",
                        json=json_data).json()

    data = []
    lists = res["data"]["list"]
    for list in lists:
        trainCode = list["trainCode"]
        startDepartTime = list["startDepartTime"]
        startStation = list["startStation"]
        endStation = list["endStation"]
        wicket = list["wicket"]
        status = int(list["status"])
        if status == 1:
            if list["delay"] < 0:
                delay = str(abs(list["delay"]))
                status = "早点" + delay + "分"
            else:
                status = "正点"
        elif status == 2:
            status = "正在检票"
        elif status == 3:
            status = "停止检票"
        elif status == 5:
            delay = str(list["delay"])
            status = "晚点" + delay + "分"
        else:
            status = "--"
        startTime = datetime.datetime.fromtimestamp(startDepartTime).strftime('%Y-%m-%d %H:%M:%S')
        data.append([trainCode, startStation, endStation, startTime, wicket, status])

    return data


class TrainInfoDialog(QtWidgets.QDialog):
    def __init__(self, train_info, train_code, parent=None):
        super().__init__(parent)
        self.train_code = train_code
        self.train_info = train_info
        self.setupUi(self.train_code)

    def setupUi(self, train_code):
        self.setWindowTitle(f"{train_code} 信息")
        self.resize(400, 400)

        # 创建主布局
        main_layout = QtWidgets.QVBoxLayout(self)

        # 创建 QScrollArea
        scroll_area = QtWidgets.QScrollArea(self)
        scroll_area.setWidgetResizable(True)  # 设置自适应窗口大小
        main_layout.addWidget(scroll_area)

        # 创建内容窗口
        content_widget = QtWidgets.QWidget()
        scroll_layout = QtWidgets.QVBoxLayout(content_widget)

        # 显示车次信息
        for key, value in list(self.train_info.items())[:-1]:
            label = QtWidgets.QLabel(f"{key}: {value}", parent=content_widget)
            scroll_layout.addWidget(label)

        # 添加停站信息标题
        label = QtWidgets.QLabel("停站信息:", parent=content_widget)
        scroll_layout.addWidget(label)

        # 横向排列每组停站信息
        for station_info in self.train_info["停站信息"]:
            # 创建一个横向布局用于每组信息
            h_layout = QtWidgets.QHBoxLayout()

            # 将停站信息横向排列
            for key, value in station_info.items():
                label = QtWidgets.QLabel(f"{key}: {value}", parent=content_widget)
                h_layout.addWidget(label)

            # 将每个横向布局添加到垂直布局中
            scroll_layout.addLayout(h_layout)

        # 将内容窗口设置为 scroll_area 的 widget
        scroll_area.setWidget(content_widget)

        # 将主布局设置到窗口
        self.setLayout(main_layout)


class Ui_Dialog(QtWidgets.QDialog):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(900, 700)

        Dialog.setWindowFlags(Dialog.windowFlags() | QtCore.Qt.WindowType.WindowMinMaxButtonsHint)

        # 创建主垂直布局
        main_layout = QtWidgets.QVBoxLayout(Dialog)

        # 标题标签
        self.title = QtWidgets.QLabel("火车站大屏查询", parent=Dialog)
        font = QtGui.QFont()
        font.setPointSize(24)
        font.setBold(True)
        self.title.setFont(font)
        main_layout.addWidget(self.title, alignment=QtCore.Qt.AlignmentFlag.AlignCenter)

        # 创建水平布局用于输入
        input_layout = QtWidgets.QHBoxLayout()
        self.station_name = QtWidgets.QLabel("车站：", parent=Dialog)
        self.station_input = QtWidgets.QLineEdit(parent=Dialog)
        self.station_input.setFixedHeight(30)
        self.pushButton = QtWidgets.QPushButton("查询", parent=Dialog)
        self.pushButton.setFixedSize(100, 30)

        # 添加控件到输入布局
        input_layout.addWidget(self.station_name)
        input_layout.addWidget(self.station_input)
        input_layout.addWidget(self.pushButton)

        main_layout.addLayout(input_layout)

        # 创建表格
        self.tableWidget = QtWidgets.QTableWidget(parent=Dialog)
        self.tableWidget.setColumnCount(6)
        self.tableWidget.setHorizontalHeaderLabels(["车次", "始发站", "终点站", "开车时间", "检票口", "状态"])
        self.tableWidget.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.Fixed)

        # 设置初始列宽
        self.update_column_widths()

        self.tableWidget.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOn)

        # 将表格添加到主布局
        main_layout.addWidget(self.tableWidget)

        # 连接按钮点击事件
        self.pushButton.clicked.connect(self.on_click)
        self.tableWidget.cellClicked.connect(self.on_table_click)

        # 设置主布局
        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)
        Dialog.setLayout(main_layout)

    # 更新列宽方法
    def update_column_widths(self):
        total_width = self.size().width()  # 窗口总宽度
        self.tableWidget.setColumnWidth(0, int(total_width * 0.10))
        self.tableWidget.setColumnWidth(1, int(total_width * 0.10))
        self.tableWidget.setColumnWidth(2, int(total_width * 0.10))
        self.tableWidget.setColumnWidth(3, int(total_width * 0.20))
        self.tableWidget.setColumnWidth(4, int(total_width * 0.60))
        self.tableWidget.setColumnWidth(5, int(total_width * 0.15))

    def on_click(self):
        station_name = self.station_input.text()
        if station_name:
            try:
                result = Query_information(station_name)
                self.display_data(result)
            except Exception as e:
                self.show_error(f"获取数据时出错: {str(e)}")
        else:
            self.show_error("请输入车站名称！")

    # 弹出错误信息框
    def show_error(self, message):
        msg_box = QtWidgets.QMessageBox()
        msg_box.setIcon(QtWidgets.QMessageBox.Icon.Warning)
        msg_box.setWindowTitle("错误")
        msg_box.setText(message)
        msg_box.setStandardButtons(QtWidgets.QMessageBox.StandardButton.Ok)
        msg_box.exec()

    # 在表格中显示数据
    def display_data(self, data):
        self.tableWidget.setRowCount(len(data))
        for row_idx, row_data in enumerate(data):
            for col_idx, item in enumerate(row_data):
                table_item = QtWidgets.QTableWidgetItem(item)

                if col_idx == 5 and item.startswith("晚点") or item.startswith("停止"):
                    table_item.setForeground(QtGui.QColor("red"))
                if col_idx == 5 and item.startswith("早点") or item.startswith("正在"):
                    table_item.setForeground(QtGui.QColor("green"))

                self.tableWidget.setItem(row_idx, col_idx, table_item)

    def on_table_click(self, row, column):
        if column == 0:  # 如果点击的是车次列
            train_code = self.tableWidget.item(row, column).text()
            train_info = Query_train_info(train_code)  # 查询车次详细信息
            self.show_train_info_dialog(train_info, train_code)

    def show_train_info_dialog(self, train_info, train_code):
        try:
            dialog = TrainInfoDialog(train_info, train_code, self)
            dialog.exec()
        except Exception as e:
            print(114514)
            print(e)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "火车站大屏查询"))
        self.title.setText(_translate("Dialog", "火车站大屏查询"))
        self.station_name.setText(_translate("Dialog", "车站："))
        self.pushButton.setText(_translate("Dialog", "查询"))


# 主函数运行应用
if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    Dialog = QtWidgets.QDialog()
    ui = Ui_Dialog()
    ui.setupUi(Dialog)
    Dialog.show()
    sys.exit(app.exec())
