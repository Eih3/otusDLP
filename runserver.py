#!/usr/bin/env python
# -*- coding: utf-8 -*-

# .########.####.##.....##..#######.
# .##........##..##.....##.##.....##
# .##........##..##.....##........##
# .######....##..#########..#######.
# .##........##..##.....##........##
# .##........##..##.....##.##.....##
# .########.####.##.....##..#######.

import os
from app import app
from flask import render_template, request, url_for
from flask_socketio import SocketIO

io = SocketIO(app)

####################################
#             VARIABLES
####################################

IP_SERVER = '192.168.1.93'
PORT_SERVER = 8080

global slice_process
global slices_path
global slice_actual
global slice_total
global print_process
global exposure_delay
global black_delay
global print_delay

slice_process = 'disabled'
slices_path = 'app/static/uploads/slices/'
slice_actual = 1
slice_total = 0
print_process = "stop"
exposure_delay = 1000
black_delay = 5000
print_delay = 0


####################################
#             ROUTING
####################################

@app.route('/')
@app.route('/index')
def dash():
    return render_template('printer/dash.html', title='Dashboard', printing_process=print_process)

# ----------------------------------

@app.route('/slacer')
def slacer():
    return render_template('printer/slacer.html', title='SLAcer.js', printing_process=print_process)

@app.route('/slacer/delete', methods=["POST"])
def slice_delete():
    folder = slices_path

    if not os.path.exists(folder):
        os.makedirs(folder)

    for the_file in os.listdir(folder):
        file_path = os.path.join(folder, the_file)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
        except Exception as e:
            print(e)
    return 'ok'

@app.route("/slacer/upload", methods=["POST"])
def slice_upload():
    filename = request.form['name']
    dataimg = request.form['img']

    fh = open(slices_path + filename, "wb")
    fh.write(dataimg.decode('base64'))
    fh.close()
    return 'ok'

@app.route("/slacer/stop", methods=["POST"])
def slice_stop():
    global slice_process
    slice_process = 'enable'
    return 'ok'

# ----------------------------------

@app.route('/print')
def printing():
    print slice_process
    return render_template('printer/print.html', title='Impression', slices=slice_total, slice_process=slice_process,
                           printing_process=print_process)

@app.route('/print/variables', methods=["POST"])
def print_variables():
    content = request.get_json(silent=True)

    if 'exposure_delay' in content:
        global exposure_delay
        exposure_delay = content['exposure_delay']
        print exposure_delay

    if 'black_delay' in content:
        global black_delay
        black_delay = content['black_delay']
        print black_delay

    if 'slices' in content:
        global slice_total
        slice_total = content['slices']
        print slice_total

    return 'ok'

@app.route("/print/process", methods=["POST"])
def print_process():
    global print_process
    global slice_actual
    global black_delay
    global print_delay

    print slice_actual
    print slice_total

    print_delay = int(slice_total) * int(exposure_delay) + int(black_delay)

    path = url_for('static', filename='uploads/slices/%d.png' % slice_actual)

    if print_process == 'start':
        if slice_actual <= slice_total:
            data = {
                'action': 'slice',
                'url': path,
                'slice': slice_actual,
                'totalSlice': slice_total,
                'delay': exposure_delay,
                'printDelay': print_delay
            }
            io.emit('projector-view', data)
        else:
            io.emit('print-stop')
    return 'ok'

@app.route("/print/process/black", methods=["POST"])
def print_process_black():
    global black_delay
    global slice_actual
    global print_delay

    path = url_for('static', filename='img/calibration/black.png')
    data = {
        'action': 'black',
        'url': path,
        'slice': slice_actual,
        'totalSlice': slice_total,
        'delay': black_delay,
        'printDelay': print_delay
    }
    slice_actual += 1
    io.emit('projector-view', data)
    return 'ok'

@app.route("/print/<status>", methods=["POST"])
def print_status(status):
    global print_process
    global slice_actual

    print status

    print_process = status

    if status == 'start':
        io.emit('print-start')

    if status == 'stop':
        path = '/static/img/calibration/black.png'
        data = {
            'action': 'black',
            'url': path,
            'slice': '0',
            'totalSlice': slice_total,
            'delay': '0',
            'print': 'Finish'
        }
        io.emit('projector-view', data)
        slice_actual = 1
    return 'ok'

# ----------------------------------

@app.route('/projector')
@app.route('/projector/view')
def projector_view():
    return render_template('printer/projector.html')

# ----------------------------------

@app.route('/configuration/calibration/dlp')
def config_dlp():
    return render_template('printer/dlp.html', title='Calibration DLP', menu='config',
                           printing_process=print_process)

@app.route('/configuration/calibration/<frame>', methods=["POST"])
def dlp_calibration(frame):
    path = "/static/img/calibration/%s.png" % frame
    io.emit('calibration-view', path)
    return 'ok'

@app.route('/configuration/plateau')
def config_plate():
    return render_template('printer/plate.html', title='Plateau', menu='config',  printing_process=print_process)


####################################
#              SERVER
####################################

if __name__ == '__main__':
    port = int(os.environ.get("PORT", PORT_SERVER))
    io.run(app, IP_SERVER, port=port)
