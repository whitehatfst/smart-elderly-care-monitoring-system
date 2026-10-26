# coding: utf-8
from app import app,socketio
from flask_login import login_required
from flask import render_template,request,redirect,abort,jsonify
import app.mod_eventinfo.controllers as c
from app.mod_eventinfo.models import EventInfo
import datetime,json,subprocess,re
from app.runtime_support import parse_datetime, run_detector
from pathlib import Path
import urllib.request


def _get_chart_subject_name(event):
    oldperson = getattr(event, 'oldperson', None)
    if oldperson and oldperson.username:
        return oldperson.username

    event_desc = (event.event_desc or '').strip()
    if event_desc:
        match = re.match(r'(.+?)(正在与义工交互|正在笑)', event_desc)
        if match:
            return match.group(1)

    if event.oldperson_id not in (None, ''):
        return '老人ID%s' % event.oldperson_id

    return '未关联老人'


def _debug_report(hypothesis_id: str, location: str, msg: str, data=None) -> None:
    # #region debug-point shared:event-forms
    _env_path = Path(__file__).resolve().parents[3] / ".dbg" / "volunteer-video-flash.env"
    _url = "http://127.0.0.1:7777/event"
    _session = "volunteer-video-flash"
    try:
        if _env_path.exists():
            _content = _env_path.read_text(encoding="utf-8")
            for _line in _content.splitlines():
                if _line.startswith("DEBUG_SERVER_URL="):
                    _url = _line.split("=", 1)[1].strip()
                elif _line.startswith("DEBUG_SESSION_ID="):
                    _session = _line.split("=", 1)[1].strip()
        _payload = {
            "sessionId": _session,
            "runId": "pre-fix",
            "hypothesisId": hypothesis_id,
            "location": location,
            "msg": msg,
            "data": data or {},
        }
        urllib.request.urlopen(
            urllib.request.Request(
                _url,
                data=json.dumps(_payload).encode("utf-8"),
                headers={"Content-Type": "application/json"},
            ),
            timeout=1,
        ).read()
    except Exception:
        pass
    # #endregion


@app.route('/datamanage')
@login_required
def list_realtime_data():

    _datalist = c.select_by_multieventtype()
    print('listdata is ====================',_datalist[0:5])
    started = request.args.get('started', '')
    started_video = request.args.get('video', '')
    return render_template(
        "oldperson/datamanagement.html",
        listdata=_datalist[0:5],
        listdata2=_datalist[5:10],
        started=started,
        started_video=started_video,
    )


# 插入事件的API，供外部调用
@app.route('/datamanage/api/insertevent', methods=['POST'])
def create_events():
    if not request.json:
        print('no post data')
        abort(400)

    _data = request.json
    record = EventInfo()
    # print(_data, type(_data), type(record))
    record.id = _data.get('id', 0) # id=0:新增       id=1:修改
    record.event_type = _data.get('event_type')
    record.event_date = parse_datetime(_data.get('event_date'))
    record.event_location = _data.get('event_location', '')
    record.event_desc = _data.get('event_desc', '')
    record.oldperson_id = _data.get('oldperson_id')

    record.event_name  = _data.get('event_name', '事件')
    
    c.update_insert_data(record)
    
    socketio.emit('realtime_data', {'id': record.id}, namespace='/realtimedata')

    # emit messsage based event_type
    if record.event_type == 0:  # smile event
        socketio.emit('smile_data', {'id': record.id}, namespace='/realtimedata')
    elif record.event_type == 1:  # volunteer event
        socketio.emit('volunteer_data', {'id': record.id}, namespace='/realtimedata')
    elif record.event_type in [2, 3, 4]:  # stranger event,推送到页面上危险预警区域
        socketio.emit('stranger_data', {'id': record.id}, namespace='/realtimedata')

    return jsonify(request.json), 201

#实时检测入侵事件
@app.route('/datamanage/checkfence')
def checkfence():
    run_detector('checkingfence.py', 'yard_01.mp4')

    return redirect('/datamanage?started=fence&video=yard_01.mp4')

#实时检测摔倒事件
@app.route('/datamanage/checkfall')
def checkfall():
    run_detector('checkingfalldetection.py', 'corridor_01.avi')

    return redirect('/datamanage?started=fall&video=corridor_01.avi')

#实时检测面部表情事件
@app.route('/datamanage/checksmile')
def checksmile():
    run_detector('testingfacialexpression.py', 'room_01.mp4')

    return redirect('/datamanage?started=smile&video=room_01.mp4')

#实时义工交互事件
@app.route('/datamanage/checkinteract')
def checkinteract():
    # #region debug-point D:route-enter
    _debug_report(
        "D",
        "forms.checkinteract:127",
        "[DEBUG] interact route entered",
        {"path": request.path, "method": request.method},
    )
    # #endregion
    run_detector('testingvolunteeractivity.py', 'desk_01.mp4')
    # #region debug-point D:route-exit
    _debug_report(
        "D",
        "forms.checkinteract:135",
        "[DEBUG] interact route finished run_detector call",
        {"redirect_video": "desk_01.mp4"},
    )
    # #endregion

    return redirect('/datamanage?started=interact&video=desk_01.mp4')



# 测试API
@app.route('/datamanage/api/test', methods=['GET'])
def has_a_test():

    event = {
        'id': 1,
        'title': '你好',
        'description': '我爱Flask'
    }
    print(event)
    #return json.dumps(event,ensure_ascii=False) , 201
    return jsonify(event)


#get event data based event_type
@app.route('/datamanage/<int:event_type>')
@login_required
def list_data_byevent(event_type):
    print('event_type=%d' %(event_type))
    _datalist = c.select_by_eventtype(event_type)


    total_dict = {}
    total_list = []
    _namelist = []

    #get all names
    for d in _datalist:
        print(d.oldperson)
        _namelist.append(_get_chart_subject_name(d))

    #assemble data like {'list': [{'name': '示例老人01', 'num': 3}, {'name': '示例老人03', 'num': 1}]}
    _added = []
    for n in _namelist:
        name_dict = {}
        name_dict['name'] = n
        name_dict['num'] = _namelist.count(n)
        print(n,'--',_added)
        if n not in _added:
            total_list.append(name_dict)
            _added.append(n)



    '''
    _dict1 = {'name':'示例老人03','num':5}
    _dict2 = {'name':'示例老人01','num':2}
    _dict3 = {'name':'示例老人04','num':3}
    total_list.append(_dict1)
    total_list.append(_dict2)
    total_list.append(_dict3)
    '''

    total_dict['list'] = total_list
    print(total_dict)

    return json.dumps(total_dict,ensure_ascii=False)


