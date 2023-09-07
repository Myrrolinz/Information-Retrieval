# !/usr/bin/env python
# -*- coding: utf-8 -*-

import json

from flask import render_template, request

from . import front


@front.route('/')
def _index():
    if request.cookies.get('search_history'):
        search_history: list = json.loads(request.cookies.get('search_history'))  # 从cookie中获取搜索历史
    else:
        search_history = []
    return render_template(r'index.html',search_history=search_history)
