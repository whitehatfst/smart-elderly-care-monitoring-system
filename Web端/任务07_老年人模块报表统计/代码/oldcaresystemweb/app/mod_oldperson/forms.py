# coding: utf-8
from app import app,socketio
from flask_login import login_required
from flask import render_template,request,redirect,session,jsonify
import app.mod_oldperson.controllers as c
from app.mod_oldperson.models import OldPersoninfo
import os,threading,time,copy,json,datetime,shutil
from app.runtime_support import (
    OLD_PERSON_FACES_DIR,
    ensure_directory,
    parse_datetime,
    start_collect_faces,
    sync_person_images,
)

faces_dir = str(ensure_directory(OLD_PERSON_FACES_DIR))
relative_dir = os.path.join('img', 'oldperson')
_monitor_lock = threading.Lock()
_active_monitors = set()


def _get_static_image_root():
    return str(ensure_directory(os.path.join(app.static_folder, relative_dir)))


def _clear_static_person_images(person_id):
    static_dir = os.path.join(_get_static_image_root(), str(person_id))
    if os.path.exists(static_dir):
        shutil.rmtree(static_dir, True)


def _sync_static_person_image(person_id, image_name):
    source_file = os.path.join(faces_dir, str(person_id), image_name)
    if not os.path.isfile(source_file):
        return False

    static_dir = os.path.join(_get_static_image_root(), str(person_id))
    if not os.path.exists(static_dir):
        os.makedirs(static_dir)
    shutil.copy2(source_file, os.path.join(static_dir, image_name))
    return True


def _ensure_monitor_started(selectdata):
    person_id = selectdata.id
    with _monitor_lock:
        if person_id in _active_monitors:
            return
        _active_monitors.add(person_id)

    _file_monitor = threading.Thread(
        target=run_file_monitor,
        kwargs={'data': selectdata},
        daemon=True
    )
    _file_monitor.start()


def _list_person_images(person_id):
    image_dir = os.path.join(faces_dir, str(person_id))
    if not os.path.exists(image_dir):
        os.makedirs(image_dir)
        return []

    sync_person_images(image_dir, _get_static_image_root())
    return sorted(
        [name for name in os.listdir(image_dir) if os.path.isfile(os.path.join(image_dir, name))],
        reverse=True
    )


def _json_or_redirect(message, redirect_url, status_code=200):
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({'message': message, 'redirect_url': redirect_url}), status_code
    return redirect(redirect_url)


def _start_capture_for_person(selectdata):
    person_id = selectdata.id
    session['oldpersonid'] = person_id

    source_dir = os.path.join(faces_dir, str(person_id))
    if not os.path.exists(source_dir):
        os.makedirs(source_dir)

    _clear_static_person_images(person_id)
    _ensure_monitor_started(selectdata)
    start_collect_faces(person_id, faces_dir)


#导航页面里的href上使用 <a class="" href="{{ url_for('list_all_oldpersoninfo') }}"> 或  href="/oldpersoninfolist"都可以路由到这里
@app.route('/oldpersoninfolist')
@login_required
def list_all_oldpersoninfo():
    _listdata = c.get_all_data()
    return render_template("oldperson/oldpersoninfolist.html",listdata= _listdata)


@app.route('/editoldpersoninfo/<int:id>')
@login_required
def edit_oldpersoninfo(id):
    selectdata = OldPersoninfo()
    if (id != 0):
        selectdata = c.select_by_id(id)
    else:
        selectdata.id = 0
    return render_template("oldperson/oldpersoninfoform.html",selectdata= selectdata)

@app.route('/saveoldpersoninfo',methods=['POST'])
def save_oldpersoninfo():
    record = OldPersoninfo()
    record.id = int(request.form['record_id'])
    record.username = request.form['username']
    record.room_number = request.form['room_number']
    record.gender = request.form['gender']
    record.health_state = request.form['health_state']
    record.imgset_dir = faces_dir
    record.profile_photo = request.form['profile_photo']

    if request.form['checkin_date'] and request.form['checkin_date'] != 'None':
        record.checkin_date = parse_datetime(request.form['checkin_date'])
    if request.form['birthday'] and request.form['birthday'] != 'None':
        record.birthday = parse_datetime(request.form['birthday'])
    if request.form['idcard'] and request.form['idcard'] != '':
        record.id_card = request.form['idcard']

    if request.form['secondguardian_name'] and request.form['secondguardian_name'] != '':
        record.secondguardian_name = request.form['secondguardian_name']

    if request.form['firstguardian_name'] and request.form['firstguardian_name'] != '':
        record.firstguardian_name= request.form['firstguardian_name']

    record.firstguardian_relationship =  request.form['firstguardian_relationship']
    record.secondguardian_relationship  =  request.form['secondguardian_relationship']
    record.firstguardian_phone = request.form['firstguardian_phone']
    record.firstguardian_wechat = request.form['firstguardian_wechat']
    record.secondguardian_phone = request.form['secondguardian_phone']
    record.secondguardian_wechat = request.form['secondguardian_wechat']

    if record.id == 0:
        #如果部署在windows系统上，和后端不在一块，则用下面的路径存放头像文件
        # record.imgset_dir = app.static_folder+'\\img\\oldperson'

        # 如果部署在linux系统上，并且和后端在一块，则用下面的路径存放头像文件
        record.imgset_dir = faces_dir

    c.update_insert_data(record)


    listdata = c.get_all_data()
    return render_template("oldperson/oldpersoninfolist.html", listdata=listdata)

@app.route('/deleteoldpersoninfo/<int:id>')
@login_required
def delete_oldpersoninfo(id):
    c.delete_by_id(id)
    return redirect('/oldpersoninfolist')


@app.route('/oldpersonimagelist')
@login_required
def list_all_oldpersonimage():
    requested_id = request.args.get('id', type=int)
    selected_id = requested_id or session.get('oldpersonid')
    listdata = c.get_all_data()
    selectdata = c.select_by_id(selected_id) if selected_id else None

    if requested_id and selectdata:
        session['oldpersonid'] = requested_id

    imagelist = _list_person_images(selectdata.id) if selectdata else []
    if imagelist:
        print('the image list is ==================', imagelist)

    return render_template(
        "oldperson/oldpersonimagelist.html",
        selectdata=selectdata,
        imagelist=imagelist,
        listdata=listdata,
    )

#在列表页面点 获取头像链接
@app.route('/setoldpersonid/<int:id>')
@login_required
def set_id_session(id):
    selectdata = c.select_by_id(id)
    if not selectdata:
        return redirect('/oldpersoninfolist')

    _start_capture_for_person(selectdata)
    return redirect('/oldpersonimagelist?id=%s' % id)


@app.route('/startoldpersoncapture/<int:id>')
@login_required
def start_oldperson_capture(id):
    selectdata = c.select_by_id(id)
    if not selectdata:
        return _json_or_redirect('老人信息不存在', '/oldpersoninfolist', 404)

    _start_capture_for_person(selectdata)
    return _json_or_redirect('已启动头像采集程序', '/oldpersonimagelist?id=%s' % id)

#set image title
@app.route('/setImage/<imageFile>')
@login_required
def set_image_file(imageFile):
    _id = session.get('oldpersonid')
    if not _id:
        return redirect('/oldpersoninfolist')

    selectdata = c.select_by_id(_id)
    if not selectdata:
        return redirect('/oldpersoninfolist')

    if os.path.basename(imageFile) != imageFile:
        return _json_or_redirect('头像文件名不合法', '/oldpersonimagelist?id=%s' % _id, 400)

    record = copy.deepcopy(selectdata)
    if not _sync_static_person_image(_id, imageFile):
        return _json_or_redirect('头像文件不存在', '/oldpersonimagelist?id=%s' % _id, 404)

    record.profile_photo = imageFile

    c.update_insert_data(record)
    return _json_or_redirect('头像设置成功', '/oldpersonimagelist?id=%s' % _id)

#web socket listner
@socketio.on('connect', namespace='/oldpersonimage')
def on_connect():
    print('oldpersonimage web connected..................')

# 查询老人信息的API，供外部调用
@app.route('/oldpeoplemanagement/api/getinfolist', methods=['GET'])
def get_old_people_info_list():
    _listdata = c.get_all_data()
    
    json_list = []
    
    for i in _listdata:
        json_list.append({'id': i.id,'name': i.username})
    
    old_people_info = {'json_list': json_list}
    
    return jsonify(old_people_info), 201

def run_file_monitor(**name):
    #path_to_watch = "D:/oldperson/app/static/img/oldperson"
    person_id = name['data'].id
    path_to_watch = os.path.join(faces_dir, str(person_id))
    print('path_to_watch=====',path_to_watch)
    try:
        before = dict([(f, None) for f in os.listdir(path_to_watch)]) if os.path.exists(path_to_watch) else {}
        print('begin monitor folder====================')
        while 1:
            time.sleep(2)
            after = dict([(f, None) for f in os.listdir(path_to_watch)]) if os.path.exists(path_to_watch) else {}
            added = sorted([f for f in after if not f in before])
            removed = [f for f in before if not f in after]
            if added:
                print("Added: ", added)
                for image_name in added:
                    if _sync_static_person_image(person_id, image_name):
                        socketio.emit('image_data', {'id': person_id,'image': image_name}, namespace='/oldpersonimage')
            if removed:
                print("Removed: ", ", ".join(removed))
            before = after
    finally:
        with _monitor_lock:
            _active_monitors.discard(person_id)


@app.route('/oldpersonstatistic')
def run_oldperson_statistic():

    return render_template("oldperson/oldpersonstatistic.html")


@app.route('/oldpersonstatistic/age')
def run_oldperson_statistic_age():
    total_dict = {}
    total_list = []
    _agelist = []

    _data_list = c.get_all_data()
    for d in _data_list:
        _temp = (datetime.datetime.now()-d.birthday).days/365
        if _temp <= 60:
            _agelist.append('60岁以下')
        elif _temp > 60 and _temp <=70:
            _agelist.append('60-70岁')
        elif _temp > 70 and _temp <=80:
            _agelist.append('70-80岁')
        elif _temp > 80 :
            _agelist.append('80岁以上')

    # assemble data like {'list': [{'name': '60岁以下', 'num': 5}, {'name': '60-70岁', 'num': 2}, {'name': '70-80岁', 'num': 3}]}
    _added = []
    for n in _agelist:
        name_dict = {}
        name_dict['name'] = n
        name_dict['num'] = _agelist.count(n)
        if n not in _added:
            total_list.append(name_dict)
            _added.append(n)

    total_dict['list'] = total_list

    return json.dumps(total_dict, ensure_ascii=False)


@app.route('/oldpersonstatistic/relationship')
def run_oldperson_relationship():
    total_dict = {}
    total_list = []
    _agelist = []

    _data_list = c.get_all_data()
    for d in _data_list:
        _agelist.append(d.firstguardian_relationship)
        #_agelist.append(d.secondguardian_relationship)

    # assemble data like {'list': [{'name': '60岁以下', 'num': 5}, {'name': '60-70岁', 'num': 2}, {'name': '70-80岁', 'num': 3}]}
    _added = []
    for n in _agelist:
        name_dict = {}

        if n =='女儿' or n == '儿子':
            name_dict['name'] = '儿子/女儿'
            name_dict['value'] = _agelist.count('女儿') + _agelist.count('儿子')
            n = '儿子/女儿'
        elif n == '外甥' or n == '侄子':
            name_dict['name'] = '外甥/侄子'
            name_dict['value'] = _agelist.count('外甥') + _agelist.count('侄子')
            n = '外甥/侄子'
        elif n == '女婿' or n == '儿媳':
            name_dict['name'] = '女婿/儿媳'
            name_dict['value'] = _agelist.count('女婿') + _agelist.count('儿媳')
            n = '女婿/儿媳'
        else:
            name_dict['name'] = n
            name_dict['value'] = _agelist.count(n)
        if n not in _added:
            total_list.append(name_dict)
            _added.append(n)

    total_dict['list'] = total_list
    print(total_dict)

    return json.dumps(total_dict, ensure_ascii=False)
