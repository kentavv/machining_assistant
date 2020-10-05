#!/home/dh_6i8v7b/.local/share/virtualenvs/pymachining-iAFu6bf3/bin/python

import base64
import io
import os
import re
import sys
import traceback
import urllib.parse

import cv2
import numpy as np
from flup.server.fcgi import WSGIServer

import pymachining as pm

Q_ = pm.getQ()


def print_style():
    print('''
<style>
.styled-table {
    border-collapse: collapse;
    margin: 25px 0;
    font-size: 0.9em;
    font-family: sans-serif;
    min-width: 400px;
    box-shadow: 0 0 20px rgba(0, 0, 0, 0.15);
}

.styled-table thead tr {
    background-color: #009879;
    color: #ffffff;
    text-align: left;
}

.styled-table th,
.styled-table td {
    padding: 12px 15px;
}

.styled-table tbody tr {
    border-bottom: 1px solid #dddddd;
}

.styled-table tbody tr:nth-of-type(even) {
    background-color: #f3f3f3;
}

.styled-table tbody tr:last-of-type {
    border-bottom: 2px solid #009879;
}

.styled-table tbody tr.active-row {
    font-weight: bold;
    color: #009879;
}

h1 { font-size: 48px; font-family: 'Signika', sans-serif; padding-bottom: 2px; }
h2 { font-size: 32px; font-family: 'Signika', sans-serif; padding-bottom: 2px; }
h3 { font-size: 24px; font-family: 'Signika', sans-serif; padding-bottom: 2px; }


p { font-family: 'Inder', sans-serif; line-height: 28px; margin-bottom: 15px; }
</style>
''')


def print_head():
    print('<head>')
    print('<title>Machining Assistant by KvvCreates, powered by PyMachining</title>')
    print_style()
    print('<script data-ad-client="ca-pub-8377109266905414" async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js"></script>')
    print('</head>')


def print_header():
    print('<h1>Machining Assistant</h1>')
    print('<p>Return to <a href="https://kvvcreates.com/pymachining/assistant.fcgi">Machining Assistant</a> or <a href="https://kvvcreates.com">KvvCreates</a></p>')


def print_footer():
    print('<hr>')
    print('<p>Copyright (c) 2020 Kent A. Vander Velden&nbsp;&nbsp;&nbsp;&nbsp;')
    print('Powered by <a href="https://github.com/kentavv/pymachining">PyMachining</a></p>')


def drill_assistant_header(env, d):
    print(f'<form action="/pymachining/assistant.fcgi" method="post">'
          f'<table class="styled-table">'
          f'<tr>'
          f'<td><label for="machine">Machine:</label></td>'
          f'<td><select ' + ('style="color:#ff0000" ' if env['machine'] != d['machine'] else '') + 'id="machine" name="machine" value="PM25MV_HS">')
    v = [('PM25MV', 'PM25MV'), ('PM25MV_DMMServo', 'PM25MV DMMServo'), ('PM25MV_HS', 'PM25MV HS')]
    for a, b in v:
        s = ' selected' if (a == env['machine'] or a == 'PM25MV_DMMServo' and env['machine'] is None) else ''
        print('    <option value="' + a + '"' + s + '>' + b + '</option>')
    print(f'</select></td>'
          f'</tr>'
          f''
          f'<tr>'
          f'<td><label for="operation">Operation:</label></td>'
          f'<td><select ' + ('style="color:#ff0000" ' if env['operation'] != d['operation'] else '') + 'id="operation" name="operation">')
    v = [('drilling', 'Drilling')]
    for a, b in v:
        s = ' selected' if a == env['operation'] else ''
        print('    <option value="' + a + '"' + s + '>' + b + '</option>')
    print(f'</select></td>'
          f'</tr>'
          f''
          f'<tr>'
          f'<td><label for="stock_mat">Stock material:</label></td>'
          f'<td><select ' + ('style="color:#ff0000" ' if env['stock_mat'] != d['stock_mat'] else '') + 'id="stock_mat" name="stock_mat">')
    v = [('aluminum', 'aluminum'),
         ('6061', 'Aluminum - 6061'),
         ('steel', 'Steel'),
         ('steel-mild', 'Steel-mild'),
         ('12l14', '12L14'),
         ('steel-medium', 'Steel-medium'),
         ('steel-high', 'Steel-high')]
    for a, b in v:
        s = ' selected' if a == env['stock_mat'] else ''
        print('<option value="' + a + '"' + s + '>' + b + '</option>')
    print(f'</select></td>'
          f'</tr>'
          f''
          f'<tr>'
          f'<td><label for="tool_mat">Tool material:</label></td>'
          f'<td><select ' + ('style="color:#ff0000" ' if env['tool_mat'] != d['tool_mat'] else '') + 'id="tool_mat" name="tool_mat">')
    v = [('hss', 'HSS'), ('carbide', 'Carbide')]
    for a, b in v:
        s = ' selected' if a == env['tool_mat'] else ''
        print('<option value="' + a + '"' + s + '>' + b + '</option>')
    print(f'</select></td>'
          f'</tr>')

    #    print(f''
    #          f'<tr>'
    #          f'<td><label for="input_units">Input units:</label></td>'
    #          f'<td><select id="input_units" name="input_units">')
    #    v = [('metric', 'Metric'), ('imperial', 'Imperial')]
    #    for a, b in v:
    #        s = ' selected' if (a == env['input_units'] or a == 'imperial' and env['input_units'] is None) else ''
    #        print('<option value="' + a + '"' + s + '>' + b + '</option>')
    #    print(f'</select></td>'
    #          f'</tr>'
    #          f''
    #          f'<tr>'
    #          f'<td><label for="output_units">Output units:</label></td>'
    #          f'<td><select id="output_units" name="output_units">')
    #    v = [('metric', 'Metric'), ('imperial', 'Imperial')]
    #    for a, b in v:
    #        s = ' selected' if (a == env['output_units'] or a == 'imperial' and env['output_units'] is None) else ''
    #        print('<option value="' + a + '"' + s + '>' + b + '</option>')
    #    print(f'</select></td>'
    #          f'</tr>'

    print(f''
          f'<tr>'
          f'<td><label for="drill_diam">Drill diam:</label></td>')
    s = env['drill_diam'] if env['drill_diam'] is not None else '0.25 in'
    print(f'<td><input ' + (
        'style="color:#ff0000" ' if env['drill_diam'] is not None and d['drill_diam'] is None else '') + 'type="text" id="drill_diam" name="drill_diam" value="' + str(
        s) + '"></td>'
             f'</tr>'
             f''
             f'<tr>'
             f'<td><label for="hole_depth">Hole depth:</label></td>')
    s = env['hole_depth'] if env['hole_depth'] is not None else '0.50 in'
    print(f'<td><input ' + (
        'style="color:#ff0000" ' if env['hole_depth'] is not None and d['hole_depth'] is None else '') + 'type="text" id="hole_depth" name="hole_depth" value="' + str(
        s) + '"></td>'
             f'</tr>'
             f''
             f'<tr>'
             f'<td colspan="2"><input type="submit" value="Submit"></td>'
             f'</tr>')

    print(f'</table>'
          f'</form>')


def embed_png(img, width=b'100%'):
    ss = ''
    if img is not None:
        ss = base64.b64encode(img)
        if type(ss) == bytes:
            ss = ss.decode('utf-8')

        # ss = b'<img style="max-width:{0:s};" alt="Embedded Image" src="data:image/png;base64,'.format(width) + ss + b'" />'
        ss = '<img style="max-width:100%;" alt="Embedded Image" src="data:image/png;base64,\n' + ss + '\n">'
        # ss = '<img style="max-width:100%;max-height:100%;object-fit:contain;" alt="Embedded Image" src="data:image/png;base64,' + ss + '" />'
        # ss = '<img style="max-height:100%;object-fit:contain;" alt="Embedded Image" src="data:image/png;base64,' + ss + '" />'
        # ss = '<img style="height:auto;width:auto;max-height:100%;max-height:100%;" alt="Embedded Image" src="data:image/png;base64,' + ss + '" />'
    return ss


def embed_jpg(img, width=b'100%'):
    ss = ''
    if img is not None:
        ss = base64.b64encode(img)
        if type(ss) == bytes:
            ss = ss.decode('utf-8')

        # ss = b'<img style="max-width:{0:s};" alt="Embedded Image" src="data:image/png;base64,'.format(width) + ss + b'" />'
        ss = '<img style="max-width:100%;" alt="Embedded Image" src="data:image/jpg;base64,\n' + ss + '\n">'
        # ss = '<img style="max-width:100%;max-height:100%;object-fit:contain;" alt="Embedded Image" src="data:image/png;base64,' + ss + '" />'
        # ss = '<img style="max-height:100%;object-fit:contain;" alt="Embedded Image" src="data:image/png;base64,' + ss + '" />'
        # ss = '<img style="height:auto;width:auto;max-height:100%;max-height:100%;" alt="Embedded Image" src="data:image/png;base64,' + ss + '" />'
    return ss


def drill_assistant(m, material_name, drill_diam, depth, generate_graphs=False):
    stock_material = pm.Material(material_name)
    tool = pm.DrillHSSStub(drill_diam)
    op = pm.DrillOp(tool, stock_material)

    sfm = stock_material.sfm(tool.tool_material)
    material_sfm = sfm

    feed_per_revolution = tool.feed_rate(stock_material)
    max_spindle_rpm = m.max_rpm
    requested_spindle_rpm = op.rrpm(sfm)
    spindle_rpm = min(requested_spindle_rpm, max_spindle_rpm)
    spindle_limited = False
    if spindle_rpm < requested_spindle_rpm:
        # SFM is now limited by the spindle RPM
        sfm = (drill_diam * np.pi * spindle_rpm).to('foot * tpm')
        spindle_limited = True
    if spindle_rpm < m.min_rpm:
        spindle_rpm = m.min_rpm
        sfm = (drill_diam * np.pi * spindle_rpm).to('foot * tpm')
        spindle_limited = True
        # May now exceed the material SFM

    P = op.net_power(feed_per_revolution, spindle_rpm).to('watt')
    max_P = m.power_continuous(spindle_rpm).to('watt')
    Q = op.metal_removal_rate(feed_per_revolution, spindle_rpm)
    T = op.torque(P.to('watt'), spindle_rpm)
    max_T = m.torque_intermittent(spindle_rpm)
    torque_limited = False
    if T > max_T:
        torque_limited = True
    thrust1 = tool.thrust(stock_material).to('lbs')
    thrust2 = tool.thrust2(stock_material, feed_per_revolution).to('lbs')
    max_thrust = m.max_feed_force.to('lbs')
    thrust_limited = False
    if thrust1 > max_thrust:
        thrust_limited = True
    op_time = op.machining_time(depth, feed_per_revolution * spindle_rpm).to('min')
    plunge_feedrate = (feed_per_revolution * spindle_rpm).to('inch / minute')
    max_plunge_feedrate = m.max_z_rate
    plunge_limited = False
    if plunge_feedrate > max_plunge_feedrate:
        plunge_limited = True

    def per_warning2(v):
        return ' (!!!)' if t_ > 100 else ''

    def per_warning(v):
        return ' (!!!)' if t_ >= 100 else ' (!!)' if t_ >= 90 else ' (!)' if t_ >= 80 else ''

    print('<h1>Drilling operation</h1>')
    print(f'<p>Summary: drilling a {drill_diam.m_as("in"):.3f}in hole {depth.m_as("in"):.3f}in deep into {material_name}.<br>')
    print(f'Summary: drilling a {drill_diam.m_as("mm"):.2f}mm hole {depth.m_as("mm"):.2f}mm deep into {material_name}.<br>')
    print(f'All estimates are based on <a href="https://www.notion.so/Drilling-724f1a6e27984f42be27ac6a63127e71">theory</a> and should not be taken as recommendations.</p>')

    print('<h2>Machining parameters</h2>')
    print('''<p>Surface speed and feed per 
          revolution are preferred since these are most accessible from materials and tooling 
          charts. Fusion 360 uses these to calculate spindle RPM and plunge rate.
          In situations where requested RPM is not obtainable by the spindle, 
          spindle RPM should be supplied, and Fusion 360 will calculate surface 
          feed.</p>''')
    print('<table class="styled-table">')
    print('<tbody>')
    print('<tr><td>Supplied to F360</td><td colspan="5"></td></tr>')
    if spindle_limited:
        print(f'<tr>'
              f'<td></td>'
              f'<td>Spindle RPM'
              f'<td>{spindle_rpm.m_as("rpm"):.0f} rpm</td>'
              f'<td colspan="2"></td>'
              f'<td>Requested {requested_spindle_rpm.m_as("rpm"):,.0f} rpm limited by spindle</td>'
              f'</tr>')
    else:
        t_ = (sfm / material_sfm).m_as('') * 100
        print(f'<tr>'
              f'<td></td>'
              f'<td>Surface speed</td>'
              f'<td>{sfm.m_as("ft * rpm"):.2f} ft&middot;rpm</td>'
              f'<td>{sfm.m_as("m * rpm"):.2f} m&middot;rpm</td>'
              f'<td>{t_:.1f}%</td>'
              f'</tr>')
    print(f'<tr>'
          f'<td></td>'
          f'<td>Feed per revolution</td>'
          f'<td>{feed_per_revolution.m_as("inch / turn"):.4f} in/turn</td>'
          f'<td>{feed_per_revolution.m_as("mm / turn"):.2f} mm/turn</td>'
          f'</tr>')
    print('<tr>'
          f'<td>Calculated by F360</td>'
          f'<td colspan="5"></td>'
          f'</tr>')
    if spindle_limited:
        t_ = (sfm / material_sfm).m_as('') * 100
        print(f'<tr>'
              f'<td></td>'
              f'<td>Surface speed</td>'
              f'<td>{sfm.m_as("ft * rpm"):.2f} ft&middot;rpm</td>'
              f'<td>{sfm.m_as("m * rpm"):.2f} m&middot;rpm</td>'
              f'<td>{t_:.1f}%</td>'
              f'<td>limited by maximum spindle speed</td>'
              f'</tr>')
    else:
        t_ = (spindle_rpm / max_spindle_rpm).m_as('') * 100
        ts_ = per_warning2(t_)
        print(f'<tr>'
              f'<td></td>'
              f'<td>Spindle RPM{ts_}</td>'
              f'<td>{spindle_rpm.m_as("rpm"):.0f} rpm</td>'
              f'<td colspan="2"></td>'
              f'<td>calculated by f360 using tool diam and sfm</td>'
              f'</tr>')
    t_ = (plunge_feedrate / max_plunge_feedrate).m_as('') * 100
    ts_ = per_warning(t_)
    print(f'<tr>'
          f'<td></td><td>Plunge feedrate{ts_}</td>'
          f'<td>{plunge_feedrate.m_as("inch / minute"):.2f} in/min</td>'
          f'<td>{plunge_feedrate.m_as("mm / minute"):.2f} mm/min</td>'
          f'<td>{t_:.1f}%</td>'
          f'<td>calculated by f360 using feed/rev and spindle rpm</td>'
          f'</tr>')
    print('</tbody>')
    print('</table>')

    if True:
        print('<p>')

        def a():
            fn = 'ops/drilling1.png'
            pos = {'name': ((220, 185), (352, 202)),
                   'spindle_speed': ((196, 374), (326, 374 + 26)),
                   'surface_speed': ((196, 419), (326, 419 + 26)),
                   'plunge_feedrate': ((196, 464), (326, 464 + 26)),
                   'feed_per_revolution': ((196, 509), (326, 509 + 26)),
                   'retract_feedrate': ((196, 555), (326, 555 + 26))}
            # import os
            # print(os.getcwd())
            font = cv2.FONT_HERSHEY_SIMPLEX
            img = cv2.imread(fn)
            if spindle_limited:
                c = {'name': (0, 0, 255),
                     'spindle_speed': (0, 0, 255),
                     'surface_speed': (255, 0, 0),
                     'plunge_feedrate': (255, 0, 0),
                     'feed_per_revolution': (0, 0, 255),
                     'retract_feedrate': (0, 0, 255)}
            else:
                c = {'name': (0, 0, 255),
                     'spindle_speed': (255, 0, 0),
                     'surface_speed': (0, 0, 255),
                     'plunge_feedrate': (255, 0, 0),
                     'feed_per_revolution': (0, 0, 255),
                     'retract_feedrate': (0, 0, 255)}
            cv2.putText(img, f'{drill_diam.m_as("in"):.4f}in drill', (pos['name'][0][0] + 3, pos['name'][1][1] - 3), font, .5, c['name'], 1, cv2.LINE_AA)
            cv2.putText(img, f'{spindle_rpm.m_as("rpm"):.0f} rpm', (pos['spindle_speed'][0][0] + 3, pos['spindle_speed'][1][1] - 8), font, .5, c['spindle_speed'], 1, cv2.LINE_AA)
            cv2.putText(img, f'{sfm.m_as("ft * rpm"):.2f} ft/min', (pos['surface_speed'][0][0] + 3, pos['surface_speed'][1][1] - 8), font, .5, c['surface_speed'], 1, cv2.LINE_AA)
            cv2.putText(img, f'{plunge_feedrate.m_as("inch / minute"):.2f} in/min', (pos['plunge_feedrate'][0][0] + 3, pos['plunge_feedrate'][1][1] - 8), font, .5,
                        c['plunge_feedrate'], 1, cv2.LINE_AA)
            cv2.putText(img, f'{feed_per_revolution.m_as("inch / turn"):.4f} in', (pos['feed_per_revolution'][0][0] + 3, pos['feed_per_revolution'][1][1] - 8), font, .5,
                        c['feed_per_revolution'], 1, cv2.LINE_AA)
            cv2.putText(img, 'max', (pos['retract_feedrate'][0][0] + 3, pos['retract_feedrate'][1][1] - 8), font, .5, (0, 0, 255), 1, cv2.LINE_AA)
            cv2.rectangle(img, pos['name'][0], pos['name'][1], c['name'], 1)
            cv2.rectangle(img, pos['spindle_speed'][0], pos['spindle_speed'][1], c['spindle_speed'], 1)
            cv2.rectangle(img, pos['surface_speed'][0], pos['surface_speed'][1], c['surface_speed'], 1)
            cv2.rectangle(img, pos['plunge_feedrate'][0], pos['plunge_feedrate'][1], c['plunge_feedrate'], 1)
            cv2.rectangle(img, pos['feed_per_revolution'][0], pos['feed_per_revolution'][1], c['feed_per_revolution'], 1)
            cv2.rectangle(img, pos['retract_feedrate'][0], pos['retract_feedrate'][1], c['retract_feedrate'], 1)
            rv, img_str = cv2.imencode('.jpg', img)
            print(embed_png(img_str))

        def b():
            fn = 'ops/drilling2.png'
            img = cv2.imread(fn)
            rv, img_str = cv2.imencode('.png', img)
            print(embed_png(img_str))

        def c():
            fn = 'ops/drilling3.png'
            img = cv2.imread(fn)
            rv, img_str = cv2.imencode('.png', img)
            print(embed_png(img_str))

        def d():
            fn = 'ops/drilling4.png'
            img = cv2.imread(fn)
            rv, img_str = cv2.imencode('.jpg', img)
            print(embed_png(img_str))

        a()
        # b()
        # c()
        d()
        print('</p>')

    print('<h2>Operation analysis</h2>')
    print(f'<table class="styled-table">'
          f'<tbody>')
    t_ = (depth / drill_diam).m_as('')
    print(f'<tr>'
          f'<td>Depth / diameter</td>'
          f'<td>{t_:.2f}</td>'
          f'</tr>'
          f''
          f'<tr>'
          f'<td>Cycle type</td>'
          f'</tr>')
    if t_ < 4:
        print('<tr><td></td><td>Standard drilling may be fine.</td></tr>')
        print('<tr><td></td><td>Peck drilling may still be preferred to break chips.</td></tr>')
        print('<tr><td></td><td>One retraction before final breakthrough may be preferred to allow coolant to hole bottom.</td></tr>')
        # Before the final breakthrough, there is minimal material remaining and the heat carrying capacity
        # of the stock is low.
    else:
        print('<tr><td></td><td>Peak drilling needed.</td></tr>')

    print('<tr><td>Limited by</td></tr>')
    if sfm > material_sfm:
        print(f'<tr><td></td><td>Warning: SFM ({sfm:.1f}) exceeds material SFM ({material_sfm:.1f})</td></tr>')
    t_ = False
    if spindle_limited:
        print(f'<tr><td></td><td>Limited by spindle RPM: requested spindle rpm {requested_spindle_rpm.m_as("rpm"):.2f} rpm changed to {spindle_rpm.m_as("rpm"):.2f} rpm</td></tr>')
        t_ = True
    if torque_limited:
        print('<tr><td></td><td>Limited by spindle torque</td></tr>')
        t_ = True
    if thrust_limited:
        print('<tr><td></td><td>Limited by thrust</td></tr>')
        t_ = True
    if plunge_limited:
        print('<tr><td></td><td>Limited by plunge feedrate</td></tr>')
        t_ = True
    if not t_:
        print('<tr><td></td><td>Not limited.</td></tr>')
    print(f'</tbody>'
          f'</table>')

    print('<h2>Machine demands</h2>')
    print(f'<table class="styled-table">'
          f'<tbody>')
    t_ = (thrust1 / max_thrust).m_as('') * 100
    ts_ = per_warning(t_)
    print(f'<tr>'
          f'<td>Thrust1</td>'
          f'<td>{t_:.1f}%{ts_}</td>'
          f'<td>{thrust1.m_as("pound"):.2f} lbs</td>'
          f'<td>{thrust1.m_as("kg"):.2f} kg</td>'
          f'</tr>')
    t_ = (thrust2 / max_thrust).m_as('') * 100
    ts_ = per_warning(t_)
    print(f'<tr>'
          f'<td>Thrust2</td>'
          f'<td>{t_:.1f}%{ts_}</td>'
          f'<td>{thrust2.m_as("pound"):.2f} lbs</td>'
          f'<td>{thrust2.m_as("kg"):.2f} kg</td>'
          f'</tr>')
    if spindle_limited:
        print(f'<tr>'
              f'<td>Spindle RPM (limited)</td>'
              f'<td>{spindle_rpm.m_as("rpm"):.2f} rpm</td>'
              f'</tr>')
    else:
        t_ = (spindle_rpm / max_spindle_rpm).m_as('') * 100
        ts_ = per_warning2(t_)
        print(f'<tr>'
              f'<td>Spindle RPM</td>'
              f'<td>{t_:.1f}%{ts_}</td>'
              f'<td>{spindle_rpm.m_as("rpm"):.2f} rpm</td>'
              f'</tr>')
    t_ = (P / max_P).m_as('') * 100
    ts_ = per_warning(t_)
    print(f'<tr>'
          f'<td>Power</td>'
          f'<td>{t_:.1f}%{ts_}</td>'
          f'<td>{P.m_as("hp"):.2f} hp</td>'
          f'<td>{P.m_as("watt"):.2f} W</td>'
          f'</tr>')
    t_ = (T / max_T).m_as('') * 100
    ts_ = per_warning(t_)
    print(f'<tr>'
          f'<td>Torque</td>'
          f'<td>{t_:.1f}%{ts_}</td>'
          f'<td>{T.m_as("ft lbf"):.2f} ft&middot;lbf</td>'
          f'<td>{T.m_as("N m"):.2f} N&middot;m</td>'
          f'</tr>')

    print(f'<tr>'
          f'<td>'
          f'Efficiency'
          f'</td>'
          f'</tr>')
    print(f'<tr>'
          f'<td></td>'
          f'<td>Material removal rate</td>'
          f'<td>{Q.m_as("in^3 / min"):.2f} in^3/min</td>'
          f'<td>{Q.m_as("cm^3 / min"):.2f} cm^3/min</td>'
          f'</tr>')
    print(f'<tr>'
          f'<td></td>'
          f'<td>Minimal machining time</td>'
          f'<td>{op_time.m_as("min"):.2f} min</td>'
          f'<td></td>'
          f'</tr>')
    print(f'</tbody>'
          f'</table>')

    print('<h2>Specifications</h2>')
    print('<table class="styled-table">')
    print('<tbody>')
    print(f'<tr>'
          f'<td>Material</td>'
          f'</tr>'
          f''
          f'<tr>'
          f'<td></td>'
          f'<td>Name</td>'
          f'<td>{stock_material.name}</td>'
          f'</tr>'
          f''
          f'<tr>'
          f'<td></td>'
          f'<td>Description</td>'
          f'<td>{stock_material.description}</td>'
          f'</tr>'
          f''
          f'<tr>'
          f'<td></td>'
          f'<td>Machinability</td>'
          f'<td>{stock_material.machinability()}</td>'
          f''
          f'<tr>'
          f'<td></td>'
          f'<td>Specific cutting energy</td>'
          f'<td>{stock_material.specific_cutting_energy.m_as("hp * min / in ** 3"):.2f} HP&middot;min/in^3</td>'
          f'<td>{stock_material.specific_cutting_energy.m_as("J / mm ** 3"):.2f} J/mm^3</td>'
          f''
          f'<tr>'
          f'<td></td>'
          f'<td>cutting speed</td>'
          f'<td>SFM {material_sfm.m_as("ft * rpm"):.2f} ft&middot;rpm</td>'
          f'<td>MPM {material_sfm.m_as("m * rpm"):.2f} m&middot;rpm</td>'
          f'</tr>')
    print(f'<tr>'
          f'<td>Machine</td>'
          f'</tr>'
          f''
          f'<tr>'
          f'<td></td>'
          f'<td>Spindle RPM range</td>'
          f'<td>{m.min_rpm.m_as("rpm"):.0f} rpm</td>'
          f'<td>{m.max_rpm.m_as("rpm"):.0f} rpm</td>'
          f'</tr>'
          f''
          f'<tr>'
          f'<td></td>'
          f'<td>Max power (at {spindle_rpm.m_as("rpm"):.0f} rpm)</td>'
          f'<td>{max_P.m_as("hp"):.2f} hp</td>'
          f'<td>{max_P.m_as("watt"):.2f} W</td>'
          f'</tr>'
          f''
          f'<tr>'
          f'<td></td>'
          f'<td>Max thrust</td>'
          f'<td>{max_thrust.m_as("lbs"):.2f} lbs</td>'
          f'<td>{max_thrust.m_as("kg"):.2f} kg</td>'
          f'</tr>'
          f''
          f'<tr>'
          f'<td></td>'
          f'<td>Max feedrate</td>'
          f'<td>{m.max_z_rate.m_as("in / minute"):.2f} in/min</td>'
          f'<td>{m.max_z_rate.m_as("mm / minute"):.2f} mm/min</td>'
          f'</tr>'
          f'')
    print('</tbody>')
    print('</table>')
    # print(stock_material)
    # print(tool)
    # print(op)

    if True:
        print('<h2>Capacity</h2>')

        img_str = m.plot_torque_speed_curve(highlight_power=P, highlight_rpm=spindle_rpm, embed=True, full_title=False)
        print(embed_png(img_str), '<br>')
        img_str = tool.plot_thrust(stock_material, highlight=m.max_feed_force, embed=True)
        print(embed_png(img_str))


def main(env, form):
    # What are the Fusion 360 settings for...

    d0 = {}
    d0['machine'] = env['machine'] if 'machine' in env else None
    d0['operation'] = env['operation'] if 'operation' in env else None
    d0['stock_mat'] = env['stock_mat'] if 'stock_mat' in env else None
    d0['tool_mat'] = env['tool_mat'] if 'tool_mat' in env else None
    #    d0['input_units'] = env['input_units'] if 'input_units' in env else None
    #    d0['output_units'] = env['output_units'] if 'output_units' in env else None

    d0['drill_diam'] = env['drill_diam'] if 'drill_diam' in env else None
    d0['hole_depth'] = env['hole_depth'] if 'hole_depth' in env else None

    d = dict(d0)

    if d['machine'] not in ['PM25MV', 'PM25MV_DMMServo', 'PM25MV_HS']:
        d['machine'] = None

    if d['operation'] not in ['drilling']:
        d['operation'] = None

    if d['stock_mat'] not in ['aluminum', '6061', 'steel', 'steel-mild', '12l14', 'steel-medium', 'steel-high']:
        d['stock_mat'] = None

    if d['tool_mat'] not in ['carbide', 'hss']:
        d['tool_mat'] = None

    #    if d['input_units'] not in ['metric', 'imperial']:
    #        d['input_units'] = None
    #
    #    if d['output_units'] not in ['metric', 'imperial']:
    #        d['output_units'] = None

    print_head()

    def parse_quant(s):
        rv = False
        try:
            try:
                a = re.fullmatch(r'^\s*((?P<number>#\d+)|(?P<letter>[A-Za-z])|(?P<decimal>((\.?\d+)|(\d+\.\d+))(\s*/\s*(\d+|\d+\.\d*))?\s*(\w+)?))\s*$', s)
                if a is None:
                    print('No match')
                if a.groupdict()['number'] is not None:
                    v = pm.Drill.letters_and_numbers_and_fractions[a.groupdict()['number']][0]
                    u = 'in'
                elif a.groupdict()['letter'] is not None:
                    v = pm.Drill.letters_and_numbers_and_fractions[a.groupdict()['letter']][0]
                    u = 'in'
                elif a.groupdict()['decimal'] is not None:
                    a = re.fullmatch(r'^(\d+|\d+\.\d*|\.\d+)(\s*/\s*(\d+|\d+\.\d*))?\s*(\w+)?$', a.groupdict()['decimal'])
                    n, d, u = a.group(1), a.group(3), a.group(4)
                    v = float(n)
                    if d is not None:
                        v /= float(d)
                    if u is None:
                        u = 'in'
                        rv = True
            except ValueError:
                v = float(s)
                u = 'in'
            q = Q_(v, u)
        except (AttributeError, TypeError, ValueError):
            q = None
        return rv, q

    rv, d['drill_diam'] = parse_quant(d['drill_diam'])
    if rv and d['drill_diam']:
        if 'in' not in d0['drill_diam'] and 'mm' not in d0['drill_diam']:
            d0['drill_diam'] += ' in'
    rv, d['hole_depth'] = parse_quant(d['hole_depth'])
    if rv and d['hole_depth']:
        if 'in' not in d0['hole_depth'] and 'mm' not in d0['hole_depth']:
            d0['hole_depth'] += ' in'

    if (d['machine'] is not None
            and d['stock_mat'] is not None
            and d['tool_mat'] is not None
            and d['operation'] is not None
            and d['drill_diam'] is not None
            and d['hole_depth'] is not None):
        print('<body>')
        drill_assistant_header(d0, d)

        if d['machine'] == 'PM25MV':
            m = pm.MachinePM25MV()
        elif d['machine'] == 'PM25MV_DMMServo':
            m = pm.MachinePM25MV_DMMServo()
        elif d['machine'] == 'PM25MV_HS':
            m = pm.MachinePM25MV_HS()
        else:
            m = None
        tool = d['drill_diam']
        depth = d['hole_depth']
        gen_graphs = False
        drill_assistant(m, d['stock_mat'], tool, depth, gen_graphs)
        print('</body>')
    else:
        print('<body>')
        drill_assistant_header(d0, d)
        print('</body>')


def application(environ, start_response):
    status = '200 OK'

    saved_stdout = sys.stdout

    sys.stdout = io.StringIO()
    sys.stderr = sys.stdout

    d = urllib.parse.parse_qs(environ['QUERY_STRING'])
    env = {k: v[0].strip() for k, v in d.items()}

    request_body = environ['wsgi.input'].read()
    d = urllib.parse.parse_qs(request_body)
    form = {k.decode('utf-8'): v[0].decode('utf-8').strip() for k, v in d.items()}
    print('<html>')
    print_header()
    try:
        # main(env, form)
        main(form, form)
    except:
        print('\n\n<pre>')
        traceback.print_exc()
        print('\n\n</pre>')
    print_footer()
    print('</html>')
    html = sys.stdout.getvalue()

    sys.stdout = saved_stdout

    response_header = [('Content-type', 'text/html')]
    start_response(status, response_header)

    yield html.encode('utf-8')


def start_test(environ, start_response):
    env = {'machine': 'PM25MV_DMMServo',
           'operation': 'drilling',
           'stock_mat': 'aluminum',
           'tool_mat': 'hss',
           'input_units': 'imperial',
           'output_units': 'imperial',
           'drill_diam': '0.25',
           'hole_depth': '0.5'}
    form = {}

    main(env, form)


if __name__ == '__main__':
    if os.getenv('MA_LOCAL'):
        start_test({}, {})
    else:
        WSGIServer(application).run()
