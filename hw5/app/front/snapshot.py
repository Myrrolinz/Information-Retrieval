# !/usr/bin/env python
# -*- coding: utf-8 -*-

import json

from flask import render_template, request

from . import front
from app.public_const import *


@front.route('/snapshot')
def _snapshot():
    if url := request.args.get('url'):
        title = url_title_df.loc[url]['title']
        with open(rf'./tools/pages/{title}.html',encoding='utf-8') as f:
            snapshot = f.read()
        # 向前端以网页的形式返回快照
        return render_template(r'snapshot.html', snapshot=snapshot)
    else:
        return "不合法的参数"
