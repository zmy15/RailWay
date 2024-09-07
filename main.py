import datetime
import json
import requests
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


# PyQt6 GUI 类
class Ui_Dialog(QtWidgets.QDialog):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(903, 706)

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
