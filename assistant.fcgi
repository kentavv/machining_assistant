#!/home/dh_6i8v7b/.local/share/virtualenvs/pymachining-iAFu6bf3/bin/python

# import cgitb
# cgitb.enable()

import io
import os
import sys
import traceback
import urllib.parse

from flup.server.fcgi import WSGIServer

sys.path.append('../pymachining/')

import pymachining as pm
from drilling import drill_assistant_main, drill_assistant_header, drill_assistant_graphs

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
    print('<p>Return to <a href="https://kvvcreates.com/machining_assistant/assistant.fcgi">Machining Assistant</a> or <a href="https://kvvcreates.com">KvvCreates</a></p>')


def print_footer():
    print('<hr>')
    print('<p>Copyright (c) 2020 Kent A. Vander Velden&nbsp;&nbsp;&nbsp;&nbsp;')
    print('Powered by <a href="https://github.com/kentavv/pymachining">PyMachining</a></p>')


def main(env, form):
    # What are the Fusion 360 settings for...

    op = env['operation'] if 'operation' in env else None
    if op == 'drilling':
        drill_assistant_main(env, form)
    else:
        d = {'machine': None,
             'operation': None,
             'stock_mat': None,
             'tool_mat': None,
             'input_units': None,
             'output_units': None,
             'drill_diam': None,
             'hole_depth': None}
        print('<body>')
        drill_assistant_header(d, d)
        print('</body>')


def application(environ, start_response):
    try:
        status = '200 OK'

        d = urllib.parse.parse_qs(environ['QUERY_STRING'])
        env = {k: v[0].strip() for k, v in d.items()}

        request_body = environ['wsgi.input'].read()
        d = urllib.parse.parse_qs(request_body)
        form = {k.decode('utf-8'): v[0].decode('utf-8').strip() for k, v in d.items()}
        op = env['operation'] if 'operation' in env else None
        if op is not None and op.startswith('drilling_graph'):
            if False:
                saved_stdout = sys.stdout

                sys.stdout = io.StringIO()
                sys.stderr = sys.stdout
                img = drill_assistant_graphs(env, form)
                html = sys.stdout.getvalue()

                sys.stdout = saved_stdout

                response_header = [('Content-type', 'text/html')]
                start_response(status, response_header)

                yield html.encode('utf-8')
            else:
                img = drill_assistant_graphs(env, form)
                response_header = [('Content-type', 'image/png')]
                start_response(status, response_header)
                yield img
        else:
            saved_stdout = sys.stdout

            sys.stdout = io.StringIO()
            sys.stderr = sys.stdout

            print('<html>')
            print_head()
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
    except Exception:
        import traceback
        fn = f'exception_{os.getpid()}.txt'
        with open(fn, 'w') as f:
            # print(f'env: {env}', file=f)
            # print(f'\n\nform: {form}', file=f)
            print(f'environ: {environ}', file=f)

            exc_type, exc_value, exc_traceback = sys.exc_info()

            # print("\n\n*** print_tb:", file=f)
            # traceback.print_tb(exc_traceback, file=f)

            print("\n\n*** print_exception:", file=f)
            # exc_type below is ignored on 3.5 and later
            traceback.print_exception(exc_type, exc_value, exc_traceback, file=f)

            # print("\n\n*** print_exc:", file=f)
            # traceback.print_exc(file=f)

            # print("\n\n*** format_exc, first and last line:", file=f)
            # formatted_lines = traceback.format_exc().splitlines()
            # print(formatted_lines[0], file=f)
            # print(formatted_lines[-1], file=f)

            # print("\n\n*** format_exception:", file=f)
            ## exc_type below is ignored on 3.5 and later
            # print(repr(traceback.format_exception(exc_type, exc_value, exc_traceback)), file=f)

            # print("\n\n*** extract_tb:", file=f)
            # print(repr(traceback.extract_tb(exc_traceback)), file=f)

            # print("\n\n*** format_tb:", file=f)
            # print(repr(traceback.format_tb(exc_traceback)), file=f)

            # print("\n\n*** tb_lineno:", exc_traceback.tb_lineno, file=f)

        status = '500 Internal Server Error'
        response_header = [('Content-type', 'text/html')]
        start_response(status, response_header)
        yield ''


def start_test(environ, start_response):
    env = {'machine': 'PM25MV_DMMServo',
           'operation': 'drilling_graph1',
           'stock_mat': 'aluminum',
           'tool_mat': 'hss',
           'input_units': 'imperial',
           'output_units': 'imperial',
           'drill_diam': '0.25',
           'hole_depth': '0.5'}
    form = {}

    print('<html>')
    print_head()
    print_header()

    main(env, env)

    print_footer()
    print('</html>')


if __name__ == '__main__':
    if os.getenv('MA_LOCAL'):
        start_test({}, {})
    else:
        WSGIServer(application).run()
