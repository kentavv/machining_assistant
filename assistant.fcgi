#!/home/dh_6i8v7b/.local/share/virtualenvs/pymachining-iAFu6bf3/bin/python

# import cgitb
# cgitb.enable()

import io
import os
import random
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

.styled-table td.small_td {
        font-size: 0.7em;
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
    op = env['operation'] if 'operation' in env else None
    if op == 'drilling':
        drill_assistant_main(form, form)
    else:
        amazon_links_refs = [
            '<a target="_blank"  href="https://www.amazon.com/gp/product/0367868199/ref=as_li_tl?ie=UTF8&camp=1789&creative=9325&creativeASIN=0367868199&linkCode=as2&tag=pioneer00-20&linkId=5854dcddc31f2891e77e0b396cf5cd9a"><img border="0" src="//ws-na.amazon-adsystem.com/widgets/q?_encoding=UTF8&MarketPlace=US&ASIN=0367868199&ServiceVersion=20070822&ID=AsinImage&WS=1&Format=_SL250_&tag=pioneer00-20" ></a><img src="//ir-na.amazon-adsystem.com/e/ir?t=pioneer00-20&l=am2&o=1&a=0367868199" width="1" height="1" border="0" alt="" style="border:none !important; margin:0px !important;" />',
            '<a target="_blank"  href="https://www.amazon.com/gp/product/0831136316/ref=as_li_tl?ie=UTF8&camp=1789&creative=9325&creativeASIN=0831136316&linkCode=as2&tag=pioneer00-20&linkId=d9451d9d61856a3bc16f569b9dd9c491"><img border="0" src="//ws-na.amazon-adsystem.com/widgets/q?_encoding=UTF8&MarketPlace=US&ASIN=0831136316&ServiceVersion=20070822&ID=AsinImage&WS=1&Format=_SL250_&tag=pioneer00-20" ></a><img src="//ir-na.amazon-adsystem.com/e/ir?t=pioneer00-20&l=am2&o=1&a=0831136316" width="1" height="1" border="0" alt="" style="border:none !important; margin:0px !important;" />'
        ]
        amazon_links_others = [
            '<a target="_blank"  href="https://www.amazon.com/gp/product/0831134771/ref=as_li_tl?ie=UTF8&camp=1789&creative=9325&creativeASIN=0831134771&linkCode=as2&tag=pioneer00-20&linkId=bb8879404110dd1ba94a44ca14627c90"><img border="0" src="//ws-na.amazon-adsystem.com/widgets/q?_encoding=UTF8&MarketPlace=US&ASIN=0831134771&ServiceVersion=20070822&ID=AsinImage&WS=1&Format=_SL250_&tag=pioneer00-20" ></a><img src="//ir-na.amazon-adsystem.com/e/ir?t=pioneer00-20&l=am2&o=1&a=0831134771" width="1" height="1" border="0" alt="" style="border:none !important; margin:0px !important;" />',
            '<a target="_blank"  href="https://www.amazon.com/gp/product/0831135026/ref=as_li_tl?ie=UTF8&camp=1789&creative=9325&creativeASIN=0831135026&linkCode=as2&tag=pioneer00-20&linkId=5d9ef4b5f13cb3edafa12272202cbf02"><img border="0" src="//ws-na.amazon-adsystem.com/widgets/q?_encoding=UTF8&MarketPlace=US&ASIN=0831135026&ServiceVersion=20070822&ID=AsinImage&WS=1&Format=_SL250_&tag=pioneer00-20" ></a><img src="//ir-na.amazon-adsystem.com/e/ir?t=pioneer00-20&l=am2&o=1&a=0831135026" width="1" height="1" border="0" alt="" style="border:none !important; margin:0px !important;" />',
            '<a target="_blank"  href="https://www.amazon.com/gp/product/0831133473/ref=as_li_tl?ie=UTF8&camp=1789&creative=9325&creativeASIN=0831133473&linkCode=as2&tag=pioneer00-20&linkId=bc4159befd4eca7fa82e01f1ca66b0d8"><img border="0" src="//ws-na.amazon-adsystem.com/widgets/q?_encoding=UTF8&MarketPlace=US&ASIN=0831133473&ServiceVersion=20070822&ID=AsinImage&WS=1&Format=_SL250_&tag=pioneer00-20" ></a><img src="//ir-na.amazon-adsystem.com/e/ir?t=pioneer00-20&l=am2&o=1&a=0831133473" width="1" height="1" border="0" alt="" style="border:none !important; margin:0px !important;" />',
            '<a target="_blank"  href="https://www.amazon.com/gp/product/B011T7X4EG/ref=as_li_tl?ie=UTF8&camp=1789&creative=9325&creativeASIN=B011T7X4EG&linkCode=as2&tag=pioneer00-20&linkId=4e58a854e2ff34306fd5ed94be8d853f"><img border="0" src="//ws-na.amazon-adsystem.com/widgets/q?_encoding=UTF8&MarketPlace=US&ASIN=B011T7X4EG&ServiceVersion=20070822&ID=AsinImage&WS=1&Format=_SL250_&tag=pioneer00-20" ></a><img src="//ir-na.amazon-adsystem.com/e/ir?t=pioneer00-20&l=am2&o=1&a=B011T7X4EG" width="1" height="1" border="0" alt="" style="border:none !important; margin:0px !important;" />',
            '<a target="_blank"  href="https://www.amazon.com/gp/product/0831134763/ref=as_li_tl?ie=UTF8&camp=1789&creative=9325&creativeASIN=0831134763&linkCode=as2&tag=pioneer00-20&linkId=67ac09dd132d76a2667d2c3b41b07663"><img border="0" src="//ws-na.amazon-adsystem.com/widgets/q?_encoding=UTF8&MarketPlace=US&ASIN=0831134763&ServiceVersion=20070822&ID=AsinImage&WS=1&Format=_SL250_&tag=pioneer00-20" ></a><img src="//ir-na.amazon-adsystem.com/e/ir?t=pioneer00-20&l=am2&o=1&a=0831134763" width="1" height="1" border="0" alt="" style="border:none !important; margin:0px !important;" />',
            '<a target="_blank"  href="https://www.amazon.com/gp/product/0831135247/ref=as_li_tl?ie=UTF8&camp=1789&creative=9325&creativeASIN=0831135247&linkCode=as2&tag=pioneer00-20&linkId=9bd7ac5190e5043660d0b6aff501d527"><img border="0" src="//ws-na.amazon-adsystem.com/widgets/q?_encoding=UTF8&MarketPlace=US&ASIN=0831135247&ServiceVersion=20070822&ID=AsinImage&WS=1&Format=_SL250_&tag=pioneer00-20" ></a><img src="//ir-na.amazon-adsystem.com/e/ir?t=pioneer00-20&l=am2&o=1&a=0831135247" width="1" height="1" border="0" alt="" style="border:none !important; margin:0px !important;" />'
        ]
        random.shuffle(amazon_links_refs)
        random.shuffle(amazon_links_others)
        print(f'<body>'
              f'<h1>Select an operation</h1>'
              f'<p><a href="assistant.fcgi?operation=drilling"><img src="ops/drilling.png" width="160px"><br>Drilling</a></p>'
              f'<br><br><br>'
              f'<h1>Favorite references</h1>'
              f'<p>Amazon Affiliate links<br>'
              f'{amazon_links_refs[0]}'
              f'{amazon_links_refs[1]}'
              f'{amazon_links_others[0]}'
              f'{amazon_links_others[1]}'
              f'</p>'
              f'</body>')


def application_main(environ, start_response):
    status = '200 OK'

    d = urllib.parse.parse_qs(environ['QUERY_STRING'])
    env = {k: v[0].strip() for k, v in d.items()}

    request_body = environ['wsgi.input'].read()
    d = urllib.parse.parse_qs(request_body)
    form = {k.decode('utf-8'): v[0].decode('utf-8').strip() for k, v in d.items()}
    
    graph = env['graph'] if 'graph' in env else None
    op = env['operation'] if 'operation' in env else None
    if op == 'drilling' and graph is not None:
        img = drill_assistant_graphs(env, form)
        response_header = [('Content-type', 'image/png')]
        start_response(status, response_header)
        return img
    else:
        saved_stdout = sys.stdout

        sys.stdout = io.StringIO()
        sys.stderr = sys.stdout

        print('<html>')
        print_head()
        print_header()
        try:
            main(env, form)
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

        return html.encode('utf-8')


def application(environ, start_response):
    try:
        yield application_main(environ, start_response)
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
