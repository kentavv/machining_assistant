#!/home/dh_6i8v7b/.local/share/virtualenvs/pymachining-iAFu6bf3/bin/python

import random
import urllib

import cv2
import numpy as np
import matplotlib.pyplot as plt
import io
import seaborn as sns

import pymachining as pm
from helper import *
from amazon_links import *

Q_ = pm.getQ()


def drill_assistant_header(env, d):
    print(f'<form action="/machining_assistant/assistant.fcgi?operation=drilling" method="post">'
          f'<table class="styled-table">'
          f'<tr>'
          f'<td><label for="machine">Machine:</label></td>'
          f'<td><select ' + ('style="color:#ff0000" ' if env['machine'] != d['machine'] else '') + 'id="machine" name="machine" value="PM25MV_2.2kW24kRPM">')
    v = [('PM25MV', 'PM25MV'), ('PM25MV_DMMServo', 'PM25MV DMMServo'), ('PM25MV_2.2kW24kRPM', 'PM25MV 2.2kW24kRPM')]
    for a, b in v:
        s = ' selected' if (a == env['machine'] or a == 'PM25MV_DMMServo' and env['machine'] is None) else ''
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


def per_warning2(v):
    return ' (!!!)' if v > 100 else ''


def per_warning(v):
    return ' (!!!)' if v >= 100 else ' (!!)' if v >= 90 else ' (!)' if v >= 80 else ''


def print_introduction(drill_diam, depth, material_name):
    print('<h1 id="section_op">Drilling operation</h1>')
    print(f'<p>Summary (imperial): Drill a {drill_diam.m_as("in"):.3f}in hole {depth.m_as("in"):.3f}in deep into {material_name}.<br>')
    print(f'Summary (metric): Drill a {drill_diam.m_as("mm"):.2f}mm hole {depth.m_as("mm"):.2f}mm deep into {material_name}.<br>')
    print(f'All estimates are based on <a href="https://www.notion.so/Drilling-724f1a6e27984f42be27ac6a63127e71">theory</a> and should not be taken as recommendations.</p>')


def print_machining_parameters(m, spindle_limited, spindle_rpm, max_spindle_rpm, requested_spindle_rpm, feed_per_revolution, sfm, material_sfm, plunge_feedrate, max_plunge_feedrate, drill_diam, limits):
    print('<h2 id="section_parameters">Machining parameters</h2>')
    print('''<p>Surface speed and feed per 
          revolution are preferred since these are most accessible from materials and tooling 
          charts. Fusion 360 uses these to calculate spindle RPM and plunge rate.
          In situations where requested RPM is not obtainable by the spindle, 
          spindle RPM should be supplied, and Fusion 360 will calculate surface 
          feed.</p>''')
    if limits:
      print(f'<p>Operation on the machine may be limited by {limits}.'
            f' See <a href="#section_demands">Demands</a> to learn the severity and consider <a href="#section_alternatives">Alternatives</a>.')
    else:
      print(f'<p>Additional productivity may be possible. See <a href="#section_alternatives">Alternatives</a>.')
    print('<table class="styled-table">')
    print('<tbody>')
    print('<tr><td>Supplied to F360</td><td colspan="5"></td></tr>')
    if spindle_limited:
        t_ = (spindle_rpm / max_spindle_rpm).m_as('') * 100
        ts_ = per_warning2(t_)
        print(f'<tr>'
              f'<td></td>'
              f'<td>Spindle RPM'
              f'<td>{spindle_rpm.m_as("rpm"):.0f} rpm</td>'
              f'<td></td>'
              f'<td class="small_td">{t_:.1f}%<br>Max Spindle RPM</td>'
              f'<td>Requested {requested_spindle_rpm.m_as("rpm"):,.0f} rpm limited by spindle</td>'
              f'</tr>')
    else:
        t_ = (sfm / material_sfm).m_as('') * 100
        print(f'<tr>'
              f'<td></td>'
              f'<td>Surface speed</td>'
              f'<td>{sfm.m_as("ft * rpm"):.2f} ft&middot;rpm</td>'
              f'<td>{sfm.m_as("m * rpm"):.2f} m&middot;rpm</td>'
              f'<td class="small_td">{t_:.1f}%<br>Max Material Speed</td>'
              f'</tr>')

    t_ = ((feed_per_revolution.to("inch / turn") * spindle_rpm) / m.max_z_rate).m_as('') * 100
    print(f'<tr>'
          f'<td></td>'
          f'<td>Feed per revolution</td>'
          f'<td>{feed_per_revolution.m_as("inch / turn"):.4f} in/turn</td>'
          f'<td>{feed_per_revolution.m_as("mm / turn"):.2f} mm/turn</td>'
          f'<td class="small_td">{t_:.1f}%<br>Max Z Feedrate</td>'
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
              f'<td class="small_td">{t_:.1f}%<br>Max Material Speed</td>'
              f'<td>limited by maximum spindle speed</td>'
              f'</tr>')
    else:
        t_ = (spindle_rpm / max_spindle_rpm).m_as('') * 100
        ts_ = per_warning2(t_)
        print(f'<tr>'
              f'<td></td>'
              f'<td>Spindle RPM{ts_}</td>'
              f'<td>{spindle_rpm.m_as("rpm"):.0f} rpm</td>'
              f'<td></td>'
              f'<td class="small_td">{t_:.1f}%<br>Max Spindle RPM</td>'
              f'<td>calculated by f360 using tool diam and sfm</td>'
              f'</tr>')
    t_ = (plunge_feedrate / max_plunge_feedrate).m_as('') * 100
    ts_ = per_warning(t_)
    print(f'<tr>'
          f'<td></td><td>Plunge feedrate{ts_}</td>'
          f'<td>{plunge_feedrate.m_as("inch / minute"):.2f} in/min</td>'
          f'<td>{plunge_feedrate.m_as("mm / minute"):.2f} mm/min</td>'
          f'<td class="small_td">{t_:.1f}%<br>Max Z Feedrate</td>'
          f'<td>calculated by f360 using feed/rev and spindle rpm</td>'
          f'</tr>')
    print('</tbody>')
    print('</table>')

    if True:
        print('<p>')
        ss = f'{spindle_limited}\t{drill_diam.m_as("in"):.4f}in drill\t{spindle_rpm.m_as("rpm"):.0f} rpm\t{sfm.m_as("ft * rpm"):.2f} ft/min\t{plunge_feedrate.m_as("inch / minute"):.2f} in/min\t{feed_per_revolution.m_as("inch / turn"):.4f} in'
        ss = urllib.parse.quote_plus(ss)
        print(f'<img src="/machining_assistant/assistant.fcgi?operation=drilling&amp;graph=graph1&amp;args={ss}">')
        # print('<img src="/machining_assistant/assistant.fcgi?operation=drilling&amp;graph=graph2">')
        # print('<img src="/machining_assistant/assistant.fcgi?operation=drilling&amp;graph=graph3">')
        print('<img src="/machining_assistant/assistant.fcgi?operation=drilling&amp;graph=graph4">')
        print('</p>')


def print_operation_analysis(depth, drill_diam, sfm, material_sfm, limits, spindle_rpm, requested_spindle_rpm):
    print('<h2 id="section_analysis">Operation analysis</h2>')
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
    if 'spindle' in limits:
        print(f'<tr><td></td><td>Limited by spindle RPM: requested spindle rpm {requested_spindle_rpm.m_as("rpm"):.2f} rpm changed to {spindle_rpm.m_as("rpm"):.2f} rpm</td></tr>')
        t_ = True
    if 'torque' in limits:
        print('<tr><td></td><td>Limited by spindle torque</td></tr>')
        t_ = True
    if 'thrust' in limits:
        print('<tr><td></td><td>Limited by thrust</td></tr>')
        t_ = True
    if 'plunge' in limits:
        print('<tr><td></td><td>Limited by plunge feedrate</td></tr>')
        t_ = True
    if not t_:
        print('<tr><td></td><td>Not limited.</td></tr>')
    print(f'</tbody>'
          f'</table>')


def print_machine_demands(thrust1, max_thrust, thrust2, limits, spindle_rpm, max_spindle_rpm, P, max_P, T, max_T, Q, op_time):
    limits = []
    print('<h2 id="section_demands">Machine demands</h2>')
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
    if 'spindle' in limits:
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


def print_specifications(stock_material, material_sfm, m, P, max_P, max_thrust, spindle_rpm, material_name, drill_diam):
    print('<h2 id="section_specifications">Specifications</h2>')
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
        print('<h2 id="section_capacity">Capacity</h2>')
        args = f'{m.name}\t{P}\t{spindle_rpm}'
        args = urllib.parse.quote_plus(args)
        print(f'<img src="/machining_assistant/assistant.fcgi?operation=drilling&amp;graph=graph5&amp;args={args}"><br>')
        args = f'{material_name}\t{m.max_feed_force}\t{drill_diam}'
        args = urllib.parse.quote_plus(args)
        print(f'<img src="/machining_assistant/assistant.fcgi?operation=drilling&amp;graph=graph6&amp;args={args}">')


def calc_alternatives(m, mat, diam, tool, op):
    Vc_r = mat.sfm(tool.tool_material)
    fr_r = tool.feed_rate(mat)
    
    options = []
    thrust = tool.thrust(mat)
    for Vc in np.linspace(Vc_r * .01, Vc_r * 1.5, 20):
        N = (Vc / (np.pi * diam)).to('rpm')
        P_avail_cont = m.power_continuous(N)
        P_avail_int = m.power_intermittent(N)
        for fr in np.linspace(fr_r * .01, fr_r * 1.5, 20):
            P_req = op.net_power(fr, N).to('watt')
            thrust2 = tool.thrust2(mat, fr)
            mrr = op.metal_removal_rate2(fr, Vc)
            
            if P_req < P_avail_cont:
                if fr * N < m.max_z_rate:
                    if m.min_rpm <= N <= m.max_rpm:
                        options += [(Vc, fr, mrr)]
    #             print(
    #               Vc, fr, '\n',
    #               fr * N, m.max_z_rate, '\n',
    #               N, m.min_rpm, m.max_rpm, '\n',
    #               P_req, P_avail_cont, P_avail_int, '\n',
    #               thrust, thrust2, m.max_feed_force, '\n',
    #              mrr.to('in ** 3 / min'))

    options = sorted(options, key=lambda x: x[2], reverse=True)

    options2 = []
    for Vc, fr, mrr in options[:100]:
#         mrr = op.metal_removal_rate2(fr, Vc)
        N = (Vc / (np.pi * diam)).to('rpm')
        P_avail_cont = m.power_continuous(N)
        P_avail_int = m.power_intermittent(N)
        P_req = op.net_power(fr, N).to('watt')
        thrust2 = tool.thrust2(mat, fr)
        options2 += [(Vc, fr, mrr, N, P_avail_cont, P_avail_int, P_req, thrust2)]

    return Vc_r, fr_r, options2


def print_alternatives(m, mat, diam, tool, op, limits):
    Vc_r, fr_r, options2 = calc_alternatives(m, mat, diam, tool, op)
              
    print('<h2 id="section_alternatives">Alternative machining parameters</h2>')
    if not options2:
        print(f'<p>No alternatives to consider within the limits of the machine or recommendations of material or tool.</p>')
        return
    if limits:
        print(f'<p>Here are alternatives to consider, organized by MRR.'
              f' The "standard parameters" are limited by the machine\'s {limits}.'
              f' Selection from the list of alternatives may be required for success.</p>')
    else:
        print(f'<p>Here are alternatives to consider, organized by MRR.'
              f' The "standard parameters" are not limited by the machine\'s capacity.'
              f' Greater productivity may be possible, at possible expense of tool life.</p>')
    print(f'<table class="styled-table" id="alt_table">'
          f'<thead>'
          f'<tr>'
          f'<th>MRR (in^3/min)</th>',
          f'<th>% of Avail.<br>Power</th>'
          f'<th>Vc (ft/min)<br>% of {Vc_r.m_as("ft * tpm"):.0f}</th>'
          f'<th>fr (in/rev)<br>% of {fr_r.m_as("in / turn"):.4f}</th>'
          f'<th>N (rpm)<br>% of {m.max_rpm.m_as("rpm"):.0f}</th>'
          f'<th>Zf (in/min)<br>% of {m.max_z_rate.m_as("in / min"):.0f}</th>'
          f'<th>Ff (lbs)<br>% of {m.max_feed_force.m_as("lbs"):.0f}</th>'
          f'</tr>'
          f'<tbody')

    thrust = tool.thrust(mat)
    for xx in options2[:100]:
            Vc, fr, mrr, N, P_avail_cont, P_avail_int, P_req, thrust2 = xx

            print(f'<tr>'
                  f'<td>{mrr.m_as("in ** 3 / min"):.2f}</td>'
                  f'<td>{(P_req / P_avail_cont).m_as("") * 100:.0f}% ({P_req.m_as("watt"):.1f} W)</td>'
                  f'<td>{Vc.m_as("ft * tpm"):.1f} ({(Vc / Vc_r).m_as("") * 100:.0f}%)</td>'
                  f'<td>{fr.m_as("in / turn"):.4f} ({(fr / fr_r).m_as("") * 100:.0f}%)</td>'
                  f'<td>{N.m_as("rpm"):.0f} ({(N / m.max_rpm).m_as("") * 100:.0f}%)</td>'
                  f'<td>{(fr * N).m_as("in / min"):.2f} ({((fr * N) / m.max_z_rate).m_as("") * 100:.0f}%)</td>'
                  f'<td>{thrust2.m_as("lbs"):.1f} ({(thrust2 / m.max_feed_force).m_as("") * 100:.0f}%)</td>'
                  f'</tr>')
            # print(f'<tr>'
            #       f'<td>{mrr.m_as("in ** 3 / min"):.2f} in^3/min</td>'
            #       f'<td>{Vc.m_as("ft * tpm"):.1f} ft/min ({(Vc / Vc_r).m_as("") * 100:.1f} %)</td>'
            #       f'<td>{fr.m_as("in / turn"):.4f} in/rev ({(fr / fr_r).m_as("") * 100:.1f} %)</td>'
            #       f'<td>{(fr * N).m_as("in / min"):.2f} in/min ({((fr * N) / m.max_z_rate).m_as("") * 100:.1f} %)</td>'
            #       f'<td>{N.m_as("rpm"):.0f} rpm ({(N / m.max_rpm).m_as("") * 100:.1f} %)</td>'
            #       f'<td>{P_req.m_as("watt"):.1f} W ({(P_req / P_avail_cont).m_as("") * 100:.1f} %)</td>'
            #       f'<td>{thrust2.m_as("lbs"):.1f} lbs ({(thrust2 / m.max_feed_force).m_as("") * 100:.1f} %)</td>'
            #       f'</tr>')
    #         print(f'{mrr.m_as("in ** 3 / min"):.2f} in^3/min',
    #               f' {Vc.m_as("ft * tpm"):.1f} ft/min ({(Vc / Vc_r).m_as("") * 100:.1f} %)',
    #               f' {fr.m_as("in / turn"):.4f} in/rev ({(fr / fr_r).m_as("") * 100:.1f} %)',
    #               f' {(fr * N).m_as("in / min"):.2f} in/min ({((fr * N) / m.max_z_rate).m_as("") * 100:.1f} %)',
    #               f' {N.m_as("rpm"):.0f} rpm ({(N / m.max_rpm).m_as("") * 100:.1f} %)',
    #               f' {P_req.m_as("watt"):.1f} W ({(P_req / P_avail_cont).m_as("") * 100:.1f} %)',
    #               f' {thrust2.m_as("lbs"):.1f} lbs ({(thrust2 / m.max_feed_force).m_as("") * 100:.1f} %)')
    #         print(f'{mrr.m_as("in ** 3 / min"):.2f} in^3/min',
    #               f'Vc={Vc.m_as("ft * tpm"):.1f} ft/min ({(Vc / Vc_r).m_as("") * 100:.1f} %)',
    #               f'fr={fr.m_as("in / turn"):.4f} in/rev ({(fr / fr_r).m_as("") * 100:.1f} %)',
    #               f'Zf={(fr * N).m_as("in / min"):.2f} in/min < {m.max_z_rate.m_as("in / min"):.2f} in/min ({((fr * N) / m.max_z_rate).m_as("") * 100:.1f} %)',
    #               f'N={N.m_as("rpm"):.0f} rpm {m.min_rpm.m_as("rpm"):.0f} rpm {m.max_rpm.m_as("rpm"):.0f} rpm ({(N / m.max_rpm).m_as("") * 100:.1f} %)',
    #               f'P_req={P_req.m_as("watt"):.1f} W <= {P_avail_cont:.1f} {P_avail_int:.1f} ({(P_req / P_avail_cont).m_as("") * 100:.1f} %)',
    #               f'Ff={thrust2.m_as("lbs"):.1f} lbs < {m.max_feed_force.m_as("lbs"):.1f} lbs ({(thrust2 / m.max_feed_force).m_as("") * 100:.1f} %)')

    print('</tbody></table>')

    ss = f'{m.name}\t{mat.name}\t{diam.m_as("in"):.4f} in'
    ss = urllib.parse.quote_plus(ss)
    print(f'<img src="/machining_assistant/assistant.fcgi?operation=drilling&amp;graph=graph7&amp;args={ss}">')


def drill_assistant(m, material_name, drill_diam, depth, generate_graphs=False):
    stock_material = pm.Material(material_name)
    tool = pm.DrillHSSStub(drill_diam)
    op = pm.DrillOp(tool, stock_material)

    sfm = stock_material.sfm(tool.tool_material)
    material_sfm = sfm

    limits = []

    feed_per_revolution = tool.feed_rate(stock_material)
    max_spindle_rpm = m.max_rpm
    requested_spindle_rpm = op.rrpm(sfm)
    spindle_rpm = min(requested_spindle_rpm, max_spindle_rpm)
    spindle_limited = False
    if spindle_rpm < requested_spindle_rpm:
        # SFM is now limited by the spindle RPM
        sfm = (drill_diam * np.pi * spindle_rpm).to('foot * tpm')
        limits += ['spindle']
    if spindle_rpm < m.min_rpm:
        spindle_rpm = m.min_rpm
        sfm = (drill_diam * np.pi * spindle_rpm).to('foot * tpm')
        limits += ['spindle']
        # May now exceed the material SFM

    P = op.net_power(feed_per_revolution, spindle_rpm).to('watt')
    max_P = m.power_continuous(spindle_rpm).to('watt')
    Q = op.metal_removal_rate(feed_per_revolution, spindle_rpm)
    T = op.torque(P.to('watt'), spindle_rpm)
    max_T = m.torque_intermittent(spindle_rpm)
    if T > max_T:
        limits += ['torque']
    thrust1 = tool.thrust(stock_material).to('lbs')
    thrust2 = tool.thrust2(stock_material, feed_per_revolution).to('lbs')
    max_thrust = m.max_feed_force.to('lbs')
    if thrust1 > max_thrust:
        limits += ['thrust']
    op_time = op.machining_time(depth, feed_per_revolution * spindle_rpm).to('min')
    plunge_feedrate = (feed_per_revolution * spindle_rpm).to('inch / minute')
    max_plunge_feedrate = m.max_z_rate
    if plunge_feedrate > max_plunge_feedrate:
        limits += ['plunge']

    print_introduction(drill_diam, depth, material_name)

    print_machining_parameters(m, spindle_limited, spindle_rpm, max_spindle_rpm, requested_spindle_rpm, feed_per_revolution, sfm, material_sfm, plunge_feedrate, max_plunge_feedrate, drill_diam, limits)

    print_operation_analysis(depth, drill_diam, sfm, material_sfm, limits, spindle_rpm, requested_spindle_rpm)

    print_machine_demands(thrust1, max_thrust, thrust2, limits, spindle_rpm, max_spindle_rpm, P, max_P, T, max_T, Q, op_time)

    print_alternatives(m, stock_material, drill_diam, tool, op, limits)

    print_specifications(stock_material, material_sfm, m, P, max_P, max_thrust, spindle_rpm, material_name, drill_diam)


def drill_graph1(args):
    ss = args.split('\t')
    spindle_limited, drill_diam, spindle_rpm, sfm, plunge_feedrate, feed_per_revolution = ss

    fn = 'ops/drilling1.png'
    pos = {'name': ((220, 185), (352, 202)),
           'spindle_speed': ((196, 374), (326, 374 + 26)),
           'surface_speed': ((196, 419), (326, 419 + 26)),
           'plunge_feedrate': ((196, 464), (326, 464 + 26)),
           'feed_per_revolution': ((196, 509), (326, 509 + 26)),
           'retract_feedrate': ((196, 555), (326, 555 + 26))}
    font = cv2.FONT_HERSHEY_SIMPLEX
    img = cv2.imread(fn)
    if spindle_limited == 'True':
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
    cv2.putText(img, drill_diam, (pos['name'][0][0] + 3, pos['name'][1][1] - 3), font, .5, c['name'], 1, cv2.LINE_AA)
    cv2.putText(img, spindle_rpm, (pos['spindle_speed'][0][0] + 3, pos['spindle_speed'][1][1] - 8), font, .5, c['spindle_speed'], 1, cv2.LINE_AA)
    cv2.putText(img, sfm, (pos['surface_speed'][0][0] + 3, pos['surface_speed'][1][1] - 8), font, .5, c['surface_speed'], 1, cv2.LINE_AA)
    cv2.putText(img, plunge_feedrate, (pos['plunge_feedrate'][0][0] + 3, pos['plunge_feedrate'][1][1] - 8), font, .5,
                c['plunge_feedrate'], 1, cv2.LINE_AA)
    cv2.putText(img, feed_per_revolution, (pos['feed_per_revolution'][0][0] + 3, pos['feed_per_revolution'][1][1] - 8), font, .5,
                c['feed_per_revolution'], 1, cv2.LINE_AA)
    cv2.putText(img, 'max', (pos['retract_feedrate'][0][0] + 3, pos['retract_feedrate'][1][1] - 8), font, .5, (0, 0, 255), 1, cv2.LINE_AA)
    cv2.rectangle(img, pos['name'][0], pos['name'][1], c['name'], 1)
    cv2.rectangle(img, pos['spindle_speed'][0], pos['spindle_speed'][1], c['spindle_speed'], 1)
    cv2.rectangle(img, pos['surface_speed'][0], pos['surface_speed'][1], c['surface_speed'], 1)
    cv2.rectangle(img, pos['plunge_feedrate'][0], pos['plunge_feedrate'][1], c['plunge_feedrate'], 1)
    cv2.rectangle(img, pos['feed_per_revolution'][0], pos['feed_per_revolution'][1], c['feed_per_revolution'], 1)
    cv2.rectangle(img, pos['retract_feedrate'][0], pos['retract_feedrate'][1], c['retract_feedrate'], 1)
    rv, img_str = cv2.imencode('.png', img)
    return img_str.tobytes()


def drill_graph2(args):
    fn = 'ops/drilling2.png'
    img = cv2.imread(fn)
    rv, img_str = cv2.imencode('.png', img)
    return img_str.tobytes()


def drill_graph3(args):
    fn = 'ops/drilling3.png'
    img = cv2.imread(fn)
    rv, img_str = cv2.imencode('.png', img)
    return img_str.tobytes()


def drill_graph4(args):
    fn = 'ops/drilling4.png'
    img = cv2.imread(fn)
    rv, img_str = cv2.imencode('.jpg', img)
    return img_str.tobytes()


def drill_graph5(args):
    ss = args.split('\t')
    # print(ss)
    machine, P, spindle_rpm = ss
    u, v = P.split(maxsplit=1)
    P = Q_(float(u), v)
    u, v = spindle_rpm.split(maxsplit=1)
    spindle_rpm = Q_(float(u), v)

    if machine == 'PM25MV':
        m = pm.MachinePM25MV()
    elif machine == 'PM25MV_DMMServo':
        m = pm.MachinePM25MV_DMMServo()
    elif machine == 'PM25MV_2.2kW24kRPM':
        m = pm.MachinePM25MV_HS()
    else:
        m = None

    img_str = m.plot_torque_speed_curve(highlight_power=P, highlight_rpm=spindle_rpm, embed=True, full_title=False)

    return img_str


def drill_graph6(args):
    ss = args.split('\t')
    material_name, max_feed_force, drill_diam = ss
    stock_material = pm.Material(material_name)
    u, v = max_feed_force.split(maxsplit=1)
    max_feed_force = Q_(float(u), v)
    u, v = drill_diam.split(maxsplit=1)
    drill_diam = Q_(float(u), v)
    tool = pm.DrillHSSStub(drill_diam)
    img_str = tool.plot_thrust(stock_material, highlight=max_feed_force, embed=True)
    return img_str


def drill_graph7(args):
    ss = args.split('\t')
    machine, material_name, drill_diam = ss

    stock_material = pm.Material(material_name)
    u, v = drill_diam.split(maxsplit=1)
    drill_diam = Q_(float(u), v)
    tool = pm.DrillHSSStub(drill_diam)
    op = pm.DrillOp(tool, stock_material)

    if machine == 'PM25MV':
        m = pm.MachinePM25MV()
    elif machine == 'PM25MV_DMMServo':
        m = pm.MachinePM25MV_DMMServo()
    elif machine == 'PM25MV_2.2kW24kRPM':
        m = pm.MachinePM25MV_HS()
    else:
        m = None

    Vc_r, fr_r, options2 = calc_alternatives(m, stock_material, drill_diam, tool, op)

    # Vc, fr, mrr, N, P_avail_cont, P_avail_int, P_req, thrust2 = xx

    options_ = options2[:100]
    x = np.array([x[0].m_as("ft * tpm") for x in options_])
    y = np.array([x[1].m_as("in / turn") for x in options_])
    # z = np.array([x[2].m_as("in ** 3 / min") for x in options_]) * 10
    z0 = np.array([x[4].m_as("watt") for x in options_])
    z = np.array([x[6].m_as("watt") for x in options_]) / z0 * 100

    # fig, ax = plt.subplots(figsize=(12,8), dpi= 100)
    fig, ax = plt.subplots(dpi=100)
    plt.scatter(x, y, s=1, c='red') #, s=z)
    plt.xlabel('SFM [ft * min]')
    plt.ylabel('IPR [in / turn]')
    plt.title('Power-RPM Requirement for Speed-Feed')
    for i, txt in enumerate(options_):
        Vc, fr, mrr, N, P_avail_cont, P_avail_int, P_req, thrust2 = options_[i]
        txt = f'{(P_req / P_avail_cont).m_as("") * 100:.0f}%\n{N.m_as("rpm"):.0f}'
        ax.annotate(txt, (x[i], y[i]), size=6)
    plt.show()
    imgdata = io.BytesIO()
    plt.savefig(imgdata, format='png', bbox_inches='tight')
    imgdata.seek(0)
    img_str = imgdata.getvalue()
    plt.close()
    # s = embed_png(img_str)
    # print(len(s))
    # print(embed_png(img_str))
    return img_str


def print_amazon_links():
    # random.shuffle(amazon_links_drills)
    print(f'<br><br><br>'
          f'<h2 id="section_ads">Favorite related tools</h2>'
          f'<p>{amazon_disclosure}<br>'
          f'{amazon_links_drills[2]}<br>'
          f'{amazon_links_drills[1]}</p>')


def drill_assistant_graphs(env, form):
    d0 = {}
    d0['graph'] = env['graph'] if 'graph' in env else None
    d0['args'] = env['args'] if 'args' in env else None

    if d0['graph'] == 'graph1':
        return drill_graph1(d0['args'])
    elif d0['graph'] == 'graph2':
        return drill_graph2(d0['args'])
    elif d0['graph'] == 'graph3':
        return drill_graph3(d0['args'])
    elif d0['graph'] == 'graph4':
        return drill_graph4(d0['args'])
    elif d0['graph'] == 'graph5':
        return drill_graph5(d0['args'])
    elif d0['graph'] == 'graph6':
        return drill_graph6(d0['args'])
    elif d0['graph'] == 'graph7':
        return drill_graph7(d0['args'])
    return None


def drill_assistant_main(env, form):
    d0 = {}
    d0['machine'] = env['machine'] if 'machine' in env else None
    d0['stock_mat'] = env['stock_mat'] if 'stock_mat' in env else None
    d0['tool_mat'] = env['tool_mat'] if 'tool_mat' in env else None
    #    d0['input_units'] = env['input_units'] if 'input_units' in env else None
    #    d0['output_units'] = env['output_units'] if 'output_units' in env else None

    d0['drill_diam'] = env['drill_diam'] if 'drill_diam' in env else None
    d0['hole_depth'] = env['hole_depth'] if 'hole_depth' in env else None

    d = dict(d0)

    if d['machine'] not in ['PM25MV', 'PM25MV_DMMServo', 'PM25MV_2.2kW24kRPM']:
        d['machine'] = None

    if d['stock_mat'] not in ['aluminum', '6061', 'steel', 'steel-mild', '12l14', 'steel-medium', 'steel-high']:
        d['stock_mat'] = None

    if d['tool_mat'] not in ['carbide', 'hss']:
        d['tool_mat'] = None

    #    if d['input_units'] not in ['metric', 'imperial']:
    #        d['input_units'] = None
    #
    #    if d['output_units'] not in ['metric', 'imperial']:
    #        d['output_units'] = None

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
            and d['drill_diam'] is not None
            and d['hole_depth'] is not None):
        print('<body>')
        drill_assistant_header(d0, d)

        if d['machine'] == 'PM25MV':
            m = pm.MachinePM25MV()
        elif d['machine'] == 'PM25MV_DMMServo':
            m = pm.MachinePM25MV_DMMServo()
        elif d['machine'] == 'PM25MV_2.2kW24kRPM':
            m = pm.MachinePM25MV_HS()
        else:
            m = None
        tool = d['drill_diam']
        depth = d['hole_depth']
        gen_graphs = False
        drill_assistant(m, d['stock_mat'], tool, depth, gen_graphs)
        print_amazon_links()
        print('</body>')
    else:
        print('<body>')
        drill_assistant_header(d0, d)
        print_amazon_links()
        print('</body>')
