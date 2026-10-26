# coding: utf-8 ceshi
from app import app,socketio
from flask_login import login_required
from flask import render_template,request,redirect,session,jsonify
import app.mod_employee.controllers as c
from app.mod_employee.models import EmployeeInfo
import os,threading,time,copy,datetime,json,shutil
from app.runtime_support import (
    EMPLOYEE_FACES_DIR,
    ensure_directory,
    parse_datetime,
    start_collect_faces,
    sync_person_images,
)

faces_dir = str(ensure_directory(EMPLOYEE_FACES_DIR))
relative_dir = os.path.join('img', 'employee')
_monitor_lock = threading.Lock()
_active_monitors = set()


def _get_static_image_root():
    return str(ensure_directory(os.path.join(app.static_folder, relative_dir)))


def _clear_static_employee_images(employee_id):
    static_dir = os.path.join(_get_static_image_root(), str(employee_id))
    if os.path.exists(static_dir):
        shutil.rmtree(static_dir, True)


def _sync_static_employee_image(employee_id, image_name):
    source_file = os.path.join(faces_dir, str(employee_id), image_name)
    if not os.path.isfile(source_file):
        return False

    static_dir = os.path.join(_get_static_image_root(), str(employee_id))
    if not os.path.exists(static_dir):
        os.makedirs(static_dir)
    shutil.copy2(source_file, os.path.join(static_dir, image_name))
    return True


def _ensure_monitor_started(selectdata):
    employee_id = selectdata.id
    with _monitor_lock:
        if employee_id in _active_monitors:
            return
        _active_monitors.add(employee_id)

    _file_monitor = threading.Thread(
        target=run_file_monitor,
        kwargs={'data': selectdata},
        daemon=True
    )
    _file_monitor.start()


def _list_employee_images(employee_id):
    image_dir = os.path.join(faces_dir, str(employee_id))
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


def _start_capture_for_employee(selectdata):
    employee_id = selectdata.id
    session['employeeid'] = employee_id

    source_dir = os.path.join(faces_dir, str(employee_id))
    if not os.path.exists(source_dir):
        os.makedirs(source_dir)

    _clear_static_employee_images(employee_id)
    _ensure_monitor_started(selectdata)
    start_collect_faces(employee_id, faces_dir)


def _build_monthly_count_map(date_attr):
    counts = {index: 0 for index in range(1, 13)}
    for record in c.get_all_data():
        date_value = getattr(record, date_attr, None)
        if date_value:
            counts[date_value.month] += 1
    return counts


def _monthly_count_list(date_attr):
    counts = _build_monthly_count_map(date_attr)
    return [
        {'name': month(index), 'num': counts[index]}
        for index in range(1, 13)
    ]

#导航页面里的href上使用 <a class="" href="{{ url_for('list_all_employeeinfo') }}"> 或  href="/employeeinfolist"都可以路由到这里
@app.route('/employeeinfolist')
@login_required
def list_all_employeeinfo():
    _listdata = c.get_all_data()
    return render_template("oldperson/employeeinfolist.html",listdata= _listdata)
@app.route('/editemployeeinfo/<int:id>')
@login_required
def edit_employeeinfo(id):
    selectdata = EmployeeInfo()
    if (id != 0):
        selectdata = c.select_by_id(id)
    else:
        selectdata.id = 0
    return render_template("oldperson/employeeinfoform.html",selectdata= selectdata)

@app.route('/saveemployeeinfo',methods=['POST'])
def save_employeeinfo():
    record = EmployeeInfo()
    record.id = int(request.form['record_id'])
    record.username = request.form['username']
    record.phone = request.form['phone']
    record.gender = request.form['gender']
    record.id_card = request.form['id_card']
    record.imgset_dir = request.form['imgset_dir']
    record.profile_photo = request.form['profile_photo']

    if request.form['hire_date'] and request.form['hire_date'] != 'None':
        record.hire_date = parse_datetime(request.form['hire_date'])
    if request.form['birthday'] and request.form['birthday'] != 'None':
        record.birthday = parse_datetime(request.form['birthday'])

    #dict.get() returns None if no key found.....
    if request.form.get('resign_date') and request.form['resign_date'] != 'None':
        record.resign_date = parse_datetime(request.form['resign_date'])

    if record.id == 0:
        #record.imgset_dir = app.static_folder+'/img/employee'
        record.imgset_dir = faces_dir
    print('=======================',record.imgset_dir)
    c.update_insert_data(record)

    listdata = c.get_all_data()
    return render_template("oldperson/employeeinfolist.html", listdata=listdata)

@app.route('/deleteemployeeinfo/<int:id>')
@login_required
def delete_employeeinfo(id):
    c.delete_by_id(id)
    return redirect('/employeeinfolist')


@app.route('/employeeimagelist')
@login_required
def list_all_employeeimage():
    requested_id = request.args.get('id', type=int)
    selected_id = requested_id or session.get('employeeid')
    listdata = c.get_all_data()
    selectdata = c.select_by_id(selected_id) if selected_id else None

    if requested_id and selectdata:
        session['employeeid'] = requested_id

    imagelist = _list_employee_images(selectdata.id) if selectdata else []
    if imagelist:
        print('the employee image list is ==================', imagelist)

    return render_template(
        "oldperson/employeeimagelist.html",
        selectdata=selectdata,
        imagelist=imagelist,
        listdata=listdata,
    )

# 查询工作人员信息的API，供外部调用
@app.route('/employeemanagement/api/getinfolist', methods=['GET'])
def get_employee_info_list():
    _listdata = c.get_all_data()
    
    json_list = []
    
    for i in _listdata:
        json_list.append({'id': i.id,'name': i.username})
    
    employee_info = {'json_list': json_list}
    
    return jsonify(employee_info), 201

@app.route('/setemployeeid/<int:id>')
@login_required
def set_employeeid_session(id):
    selectdata = c.select_by_id(id)
    if not selectdata:
        return redirect('/employeeinfolist')

    _start_capture_for_employee(selectdata)
    return redirect('/employeeimagelist?id=%s' % id)


@app.route('/startemployeecapture/<int:id>')
@login_required
def start_employee_capture(id):
    selectdata = c.select_by_id(id)
    if not selectdata:
        return _json_or_redirect('工作人员信息不存在', '/employeeinfolist', 404)

    _start_capture_for_employee(selectdata)
    return _json_or_redirect('已启动头像采集程序', '/employeeimagelist?id=%s' % id)


#set image title
@app.route('/setEmployeeImage/<imageFile>')
@login_required
def set_employeeimage_file(imageFile):
    _id = session.get('employeeid')
    if not _id:
        return redirect('/employeeinfolist')

    selectdata = c.select_by_id(_id)
    if not selectdata:
        return redirect('/employeeinfolist')

    if os.path.basename(imageFile) != imageFile:
        return _json_or_redirect('头像文件名不合法', '/employeeimagelist?id=%s' % _id, 400)

    record = copy.deepcopy(selectdata)
    if not _sync_static_employee_image(_id, imageFile):
        return _json_or_redirect('头像文件不存在', '/employeeimagelist?id=%s' % _id, 404)

    record.profile_photo = imageFile

    c.update_insert_data(record)
    return _json_or_redirect('头像设置成功', '/employeeimagelist?id=%s' % _id)

#统计分析报表
@app.route('/employeestatistic')
@login_required
def run_employee_statistic():
    return render_template("oldperson/employeestatistic.html")

@app.route('/employeestatistic/checkin')
@login_required
def run_employee_checkin():
    return jsonify({'list': _monthly_count_list('hire_date')})

@app.route('/employeestatistic/resign')
@login_required
def run_employee_resign():
    return jsonify({'list': _monthly_count_list('resign_date')})


@app.route('/employeestatistic/compare')
@login_required
def run_employee_compare():
    hire_counts = _build_monthly_count_map('hire_date')
    resign_counts = _build_monthly_count_map('resign_date')

    return jsonify({
        'months': [month(index) for index in range(1, 13)],
        'hire': [hire_counts[index] for index in range(1, 13)],
        'resign': [resign_counts[index] for index in range(1, 13)],
    })

#web socket listner
@socketio.on('connect', namespace='/employeeimage')
def on_connect():
    print('employee image web connected..................')

def month(var):
    return {
            1: '一月',
            2: '二月',
            3: '三月',
        4: '四月',
        5: '五月',
        6: '六月',
        7: '七月',
        8: '八月',
        9: '九月',
        10: '十月',
        11: '十一月',
        12: '十二月'
    }.get(var,'0')

def run_file_monitor(**name):
    employee_id = name['data'].id
    path_to_watch = os.path.join(faces_dir, str(employee_id))
    try:
        before = dict([(f, None) for f in os.listdir(path_to_watch)]) if os.path.exists(path_to_watch) else {}
        print('begin monitor folder====================',path_to_watch)
        while 1:
            time.sleep(2)
            after = dict([(f, None) for f in os.listdir(path_to_watch)]) if os.path.exists(path_to_watch) else {}
            added = sorted([f for f in after if not f in before])
            removed = [f for f in before if not f in after]
            if added:
                print("Added: ", added)
                for image_name in added:
                    if _sync_static_employee_image(employee_id, image_name):
                        socketio.emit('image_data', {'id': employee_id,'image': image_name}, namespace='/employeeimage')
            if removed:
                print("Removed: ", ", ".join(removed))
            before = after
    finally:
        with _monitor_lock:
            _active_monitors.discard(employee_id)
