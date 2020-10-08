#!/home/dh_6i8v7b/.local/share/virtualenvs/machining_assistant-5Q48g--X/bin/python

import base64
import re

import pymachining as pm

Q_ = pm.getQ()


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
