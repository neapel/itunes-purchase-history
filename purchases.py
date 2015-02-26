#!/usr/bin/env python

import xml.etree.ElementTree as ET
import csv
import re


def all_orders(t):
    NS = 'http://www.apple.com/itms/'
    ns = {'i': NS}
    # the form has a name, nice.
    form = t.find('.//i:VBoxView[@viewName="purchaseHistoryForm"]', ns)
    # our table is the last matrix
    matrix = list(form.findall('i:MatrixView', ns))[-1]
    for row in zip(*[iter(matrix)] * 5):
        # ignore headers
        if row[0].tag != '{' + NS + '}GotoURL':
            continue
        order_date = row[1].text.strip()
        order_id = row[2].text.strip()
        titles = row[3].text.strip()
        price = row[4].text.strip()
        # consistent currency format: #,# $ -> $#.#
        price = re.sub('^(\d+)[.,](\d+)\s*(\D+)$', '\\3\\1.\\2', price).strip()
        yield (order_date, order_id, titles, price)


def start(ctx, argv):
    if len(argv) != 2:
        raise ValueError('Usage: -s "' + argv[0] + ' output.csv"')
    ctx.outname = argv[1]
    ctx.rows = set()


def response(ctx, flow):
    if 'MZFinance.woa' in flow.request.path:
        try:
            # try to parse and extract, ignore on error
            tree = ET.fromstring(flow.response.get_decoded_content())
            ctx.rows.update(all_orders(tree))
        except:
            pass


def done(ctx):
    with open(ctx.outname, 'w') as f:
        w = csv.writer(f)
        w.writerow(['date', 'id', 'titles', 'price'])
        for row in ctx.rows:
            w.writerow([r.encode('utf-8') for r in row])
