import requests
import datetime
from api import API


def Format_time(time) -> str:
    return time[:2] + ":" + time[2:]


def Format_date(date) -> str:
    return datetime.datetime.strptime(date, "%Y%m%d").strftime("%Y-%m-%d").lstrip('0').replace('-0', '-')


def Query_train_info(train_code) -> dict:
    train_code = train_code.upper()
    startDay = datetime.date.today().strftime("%Y%m%d")
    data = {
        "trainCode": train_code,
        "startDay": startDay
    }
    res = requests.post(API.api_12306, data=data).json()

    datas = {}
    try:
        start_train_date = Format_date(res['data']['startTrainDate'])
        start_Time = Format_time(res['data']['startTime'])
        arrive_Time = Format_time(res['data']['arriveTime'])
        datas.setdefault("车次", train_code)
        datas.setdefault("出发日期", start_train_date)
        datas.setdefault("开车时间", start_Time)
        datas.setdefault("到达时间", arrive_Time)

        stop_times = res['data']['trainDetail']['stopTime']
        start_station_name = stop_times[0]["start_station_name"]
        end_station_name = stop_times[0]["end_station_name"]
        datas.setdefault("始发站", start_station_name)
        datas.setdefault("终到站", end_station_name)

        jiaolu_corporation_code = stop_times[0]["jiaolu_corporation_code"]
        jiaolu_train_style = stop_times[0]["jiaolu_train_style"]
        jiaolu_dept_train = stop_times[0]["jiaolu_dept_train"]
        datas.setdefault("客运担当", jiaolu_corporation_code)
        datas.setdefault("车底类型", jiaolu_train_style)
        datas.setdefault("车底配属", jiaolu_dept_train)

        trainsetTypeInfo = res['data']['trainDetail']["trainsetTypeInfo"]
        fullLength = trainsetTypeInfo["fullLength"]
        currentSpeed = trainsetTypeInfo["currentSpeed"]
        coachOrganization = trainsetTypeInfo["coachOrganization"]
        capacity = trainsetTypeInfo["capacity"]
        mealCoach = trainsetTypeInfo["mealCoach"]
        coachCount = trainsetTypeInfo["coachCount"] + "节"
        datas.setdefault("车辆全长", fullLength)
        datas.setdefault("最高速度", currentSpeed)
        datas.setdefault("车辆组成", coachOrganization)
        datas.setdefault("定员", capacity)
        datas.setdefault("餐车", mealCoach)
        datas.setdefault("编组", coachCount)
    except Exception:
        pass

    stop_inf = []
    stop_dict = {}
    try:
        for stop in stop_times:
            station = stop['stationName']
            arrive_time = Format_time(stop['arriveTime'])
            start_time = Format_time(stop['startTime'])
            stopover_time = stop['stopover_time'] + "分"
            stop_dict.setdefault("站点", station)
            stop_dict.setdefault("到达时间", arrive_time)
            stop_dict.setdefault("发车时间", start_time)
            stop_dict.setdefault("停留时间", stopover_time)
            stop_inf.append(stop_dict)
            stop_dict = {}
        datas.setdefault("停站信息", stop_inf)
    except Exception:
        pass
    return datas
