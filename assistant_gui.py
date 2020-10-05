#!/usr/bin/env python

from io import StringIO
import sys
import numpy as np
import pymachining as pm
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QLabel
from PyQt5.QtWidgets import QMainWindow, QApplication, QPushButton, QWidget, QAction, QTabWidget, QVBoxLayout, QComboBox, QHBoxLayout, QLineEdit, QPlainTextEdit
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import pyqtSlot

Q_ = pm.getQ()


def drill_assistant_html(m, material_name, drill_diam, depth, generate_graphs=False, out_units='imperial'):
    stock_material = pm.Material(material_name)
    tool = pm.DrillHSSStub(drill_diam)
    op = pm.DrillOp(tool, stock_material)

    sfm = stock_material.sfm(tool.tool_material)
    material_sfm = sfm

    print('<h1>Operation</h1>')
    print('<h2>Stock material</h2>')
    print('', stock_material, '<br>')
    if out_units == 'imperial':
        v = material_sfm.to('foot rpm')
        s = f'<mathjax>\\({v.m:.2f}\\ ft / min\\)</mathjax>'
        print(f'  SFM: {s}<br>')
    elif out_units == 'metric':
        v = material_sfm.to('m rpm')
        s = f'<mathjax>\\({v.m:.2f}\\ m / min\\)</mathjax>'
        print(f'  SMM: {s}<br>')
    print('', tool, '<br>')
    print('', op, '<br>')

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

    print('\n<h1>Machining parameters</h1>')
    print('<h2>Supplied to F360</h2>')
    v = spindle_rpm.to('rpm')
    spindle_rpm_t = f'<mathjax>\\({v.m:.2f}\\ RPM\\)</mathjax>'
    if spindle_limited:
        print(f'  Spindle RPM (limited): {spindle_rpm_t}<br>')
    else:
        t_ = (sfm / material_sfm).m_as('') * 100
        print(f'  Surface speed ({t_:.1f}%): {sfm:.2f}', '<br>')
    print(f'  Feed per revolution: {feed_per_revolution.to("inch / turn"):.4f} {feed_per_revolution.to("mm / turn"):.4f}', '<br>')
    print(' Calculated by F360:', '<br>')
    if spindle_limited:
        t_ = (sfm / material_sfm).m_as('') * 100
        print(f'  Surface speed ({t_:.1f}%): {sfm:.2f} (limited by maximum spindle speed)<br>')
    else:
        t_ = (spindle_rpm / max_spindle_rpm).m_as('') * 100
        ts_ = per_warning2(t_)
        print(f'  Spindle RPM{ts_}: {spindle_rpm_t} (calculated by f360 using tool diam and sfm)<br>')
    t_ = (plunge_feedrate / max_plunge_feedrate).m_as('') * 100
    ts_ = per_warning(t_)
    print(
        f'  Plunge feedrate{ts_} ({t_:.1f}%): {plunge_feedrate.to("inch / minute"):.2f} {plunge_feedrate.to("mm / minute"):.2f} (calculated by f360 using feed/rev and spindle rpm)',
        '<br>')

    print('<h1>Operation analysis</h1>')
    t_ = (depth / drill_diam).m_as('')
    print(f'<h2>Cycle type</h2>')
    print(f'  D / diam: {t_:.2f}', '<br>')
    if t_ < 4:
        print('  Standard drilling may be fine.', '<br>')
        print('  Peck drilling may still be preferred to break chips.', '<br>')
        print('  One retraction before final breakthrough may be preferred to allow coolant to hole bottom.', '<br>')
        # Before the final breakthrough, there is minimal material remaining and the heat carrying capacity
        # of the stock is low.

    print('<h2>Limited by</h2>')
    if sfm > material_sfm:
        print(f'  Warning: SFM ({sfm:.1f}) exceeds material SFM ({material_sfm:.1f})', '<br>')
    t_ = False
    if spindle_limited:
        print(f'  Limited by spindle RPM: requested spindle rpm {requested_spindle_rpm:.2f} changed to {spindle_rpm:.2f}', '<br>')
        t_ = True
    if torque_limited:
        print('  Limited by spindle torque', '<br>')
        t_ = True
    if thrust_limited:
        print('  Limited by thrust', '<br>')
        t_ = True
    if plunge_limited:
        print('  Limited by plunge feedrate', '<br>')
        t_ = True
    if not t_:
        print('  Not limited.', '<br>')

    print('<h2>Machine demands</h2>')
    t_ = (thrust1 / max_thrust).m_as('') * 100
    ts_ = per_warning(t_)
    print(f'  Thrust1{ts_}: {t_:.1f}% ({thrust1.to("pound"):.2f} {thrust1.to("kg"):.2f})', '<br>')
    t_ = (thrust2 / max_thrust).m_as('') * 100
    ts_ = per_warning(t_)
    print(f'  Thrust2{ts_}: {t_:.1f}% ({thrust2.to("pound"):.2f} {thrust2.to("kg"):.2f})', '<br>')
    if spindle_limited:
        print(f'  Spindle RPM (limited): {spindle_rpm:.2f}', '<br>')
    else:
        t_ = (spindle_rpm / max_spindle_rpm).m_as('') * 100
        ts_ = per_warning2(t_)
        print(f'  Spindle RPM{ts_}: {spindle_rpm:.2f}', '<br>')
    t_ = (P / max_P).m_as('') * 100
    ts_ = per_warning(t_)
    print(f'  Power{ts_}: {t_:.1f}% ({P.to("watt"):.2f})', '<br>')
    t_ = (T / max_T).m_as('') * 100
    ts_ = per_warning(t_)
    print(f'  Torque{ts_}: {t_:.1f}% ({T.to("ft lbf"):.2f} {T.to("N m"):.2f})', '<br>')

    print('<h2>Efficiency</h2>')
    print(f'  Material removal rate: {Q.to("in^3 / min"):.2f} {Q.to("cm^3 / min"):.2f}', '<br>')
    print(f'  Minimal machining time: {op_time:.2f}', '<br>')

    print('<br>')

    if generate_graphs:
        m.plot_torque_speed_curve(highlight_power=P, highlight_rpm=spindle_rpm)
        tool.plot_thrust(stock_material, highlight=m.max_feed_force)


class App(QMainWindow):

    def __init__(self):
        super().__init__()
        self.title = 'PyMachining Assistant'
        # self.left = 0
        # self.top = 0
        # self.width = 300
        # self.height = 200
        self.setWindowTitle(self.title)
        # self.setGeometry(self.left, self.top, self.width, self.height)

        self.table_widget = MyTableWidget(self)
        self.setCentralWidget(self.table_widget)

        self.show()


class DrillingAssistantTab(QWidget):

    def __init__(self, parent):
        super(QWidget, self).__init__(parent)
        self.layout = QVBoxLayout(self)

        self.resize(800, 600)

        self.cb0 = QComboBox()
        la = QLabel('Machine')
        self.cb0.addItem('PM25MV')
        self.cb0.addItem('PM25MV DMMServo')
        self.cb0.addItem('PM25MV HS')
        # self.cb1.activated[str].connect(self.onChanged)
        l2 = QHBoxLayout(self)
        l2.addWidget(la)
        l2.addWidget(self.cb0)
        self.layout.addLayout(l2)

        self.cb1 = QComboBox()
        la = QLabel('Tool units')
        self.cb1.addItem('Imperial')
        self.cb1.addItem('Metric')
        # self.cb1.activated[str].connect(self.onChanged)
        l2 = QHBoxLayout(self)
        l2.addWidget(la)
        l2.addWidget(self.cb1)
        self.layout.addLayout(l2)

        self.cb2 = QComboBox()
        la = QLabel('Results units')
        self.cb2.addItem('Imperial')
        self.cb2.addItem('Metric')
        # self.cb2.activated[str].connect(self.onChanged)
        l2 = QHBoxLayout(self)
        l2.addWidget(la)
        l2.addWidget(self.cb2)
        self.layout.addLayout(l2)

        self.cb = QComboBox()
        la = QLabel('Stock material')
        for x in ['aluminum', '6061', 'steel', 'steel-mild', '12l14', 'steel-medium', 'steel-high']:
            self.cb.addItem(x)
        # self.cb.activated[str].connect(self.onChanged)
        l2 = QHBoxLayout(self)
        l2.addWidget(la)
        l2.addWidget(self.cb)
        self.layout.addLayout(l2)

        self.cb3 = QComboBox()
        la = QLabel('Tool material')
        for x in ['HSS', 'Carbide']:
            self.cb.addItem(x)
        # self.cb.activated[str].connect(self.onChanged)
        l2 = QHBoxLayout(self)
        l2.addWidget(la)
        l2.addWidget(self.cb3)
        self.layout.addLayout(l2)

        self.diam = QLineEdit('.25')
        la = QLabel('Drill diameter')
        # self.cb.activated[str].connect(self.onChanged)
        l2 = QHBoxLayout(self)
        l2.addWidget(la)
        l2.addWidget(self.diam)
        self.diam_la = QLabel('inches')
        l2.addWidget(self.diam_la)
        self.layout.addLayout(l2)

        self.depth = QLineEdit('.5')
        la = QLabel('Depth')
        # self.cb.activated[str].connect(self.onChanged)
        l2 = QHBoxLayout(self)
        l2.addWidget(la)
        l2.addWidget(self.depth)
        self.depth_la = QLabel('inches')
        l2.addWidget(self.depth_la)
        self.layout.addLayout(l2)

        self.textBox = QPlainTextEdit()
        self.textBox.setMinimumHeight(300)
        self.layout.addWidget(self.textBox)

        self.we = QWebEngineView()
        self.we.setMinimumHeight(300)
        self.we.setZoomFactor(2.0)
        self.layout.addWidget(self.we)

        self.pushButton1 = QPushButton('Calculate')
        self.layout.addWidget(self.pushButton1)
        self.pushButton1.clicked.connect(self.on_click)

        pageSource = """
                     <html><head>
                     <script type="text/javascript" src="https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.5/MathJax.js?config=TeX-AMS-MML_HTMLorMML">                     
                     </script></head>
                     <body>
                     <p><mathjax style="font-size:2.3em">$$u = \int_{-\infty}^{\infty}(awesome)\cdot du$$</mathjax></p>
                     </body></html>
                     """
        self.we.setHtml(pageSource)

        self.setLayout(self.layout)

    @pyqtSlot()
    def on_click(self):
        # print('\n')
        # for currentQTableWidgetItem in self.tableWidget.selectedItems():
        #     print(currentQTableWidgetItem.row(), currentQTableWidgetItem.column(), currentQTableWidgetItem.text())
        m = None
        if self.cb0.currentText() == 'PM25MV':
            m = pm.MachinePM25MV()
        elif self.cb0.currentText() == 'PM25MV DMMServo':
            m = pm.MachinePM25MV_DMMServo()
        elif self.cb0.currentText() == 'PM25MV HS':
            m = pm.MachinePM25MV_HS()

        material_name = self.cb.currentText()
        drill_diam = self.diam.text()
        depth = self.diam.text()
        drill_diam = Q_(float(drill_diam), 'inch')
        depth = Q_(float(depth), 'inch')
        temp_out = StringIO()
        sys.stdout = temp_out
        drill_assistant_html(m, material_name, drill_diam, depth, False, self.cb2.currentText().lower())
        sys.stdout = sys.__stdout__
        ss = temp_out.getvalue()
        self.textBox.setPlainText(ss)
        ss2 = """
                             <html><head>
                             <script type="text/javascript" src="https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.5/MathJax.js?config=TeX-AMS-MML_HTMLorMML">                     
                             </script></head>
                             <body>
                             """ + ss + """
                             </body></html>
                             """
        self.we.setHtml(ss2)

    def onChanged(self, text):
        self.calculate()

    def calculate(self):
        material = self.cb.currentText()


class MyTableWidget(QWidget):

    def __init__(self, parent):
        super(QWidget, self).__init__(parent)
        self.layout = QVBoxLayout(self)

        self.tabs = QTabWidget()
        self.tab1 = DrillingAssistantTab(self)
        self.tab2 = DrillingAssistantTab(self)
        # self.tabs.resize(800, 600)

        self.tabs.addTab(self.tab1, 'Drilling')
        self.tabs.addTab(self.tab2, 'Thread milling')

        # Create first tab
        # self.tab1.layout = QVBoxLayout(self)
        # self.pushButton1 = QPushButton('Calculate')
        # self.tab1.layout.addWidget(self.pushButton1)
        # self.tab1.setLayout(self.tab1.layout)

        # Add tabs to widget
        self.layout.addWidget(self.tabs)
        self.setLayout(self.layout)

    @pyqtSlot()
    def on_click(self):
        print('\n')
        for currentQTableWidgetItem in self.tableWidget.selectedItems():
            print(currentQTableWidgetItem.row(), currentQTableWidgetItem.column(), currentQTableWidgetItem.text())


def main():
    # What are the Fusion 360 settings for...

    app = QApplication(sys.argv)
    ex = App()
    # ex.move(100, 100)
    ex.activateWindow()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
