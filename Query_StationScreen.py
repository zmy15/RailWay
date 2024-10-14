import json
import requests
from api import API
from datetime import datetime
# from encoded_station_telecode import encoded_json
# import base64


def Query_StationScreen(station_name):
    # decoded_data = base64.b64decode(encoded_json.encode('utf-8')).decode('utf-8')
    # station_telecodes = json.loads(decoded_data)

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

    res = requests.post(API.api_StationScreen,json=json_data).json()

    data = []
    lists = res["data"]["list"]
    for list in lists:
        trainCode = list["trainCode"]
        startDepartTime = list["startDepartTime"]
        startStation = list["startStation"]
        endStation = list["endStation"]
        wicket = list["wicket"]
        stop = list["stop"]
        if stop:
            status = list["stopTitle"]
        else:
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
        startTime = datetime.fromtimestamp(startDepartTime).strftime('%Y-%m-%d %H:%M:%S')
        data.append([trainCode, startStation, endStation, startTime, wicket, status])

    return data
