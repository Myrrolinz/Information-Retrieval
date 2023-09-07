# !/usr/bin/env python
# -*- coding: utf-8 -*-

import json

import httpx

from flask import render_template, request, jsonify

from . import front

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
           'referer': 'https://www.baidu.com'}  # 伪装成浏览器访问，通过referer参数伪装来源是百度


@front.route('/suggest')
async def _suggest():
    keywords = request.args.get('keywords')
    if keywords:
        try:
            async with httpx.AsyncClient(timeout=5) as client:
                r = await client.get(f'https://www.baidu.com/sugrec?prod=pc&wd={keywords}', headers=headers) # 利用了百度的搜索建议接口
                return_list = [i['q'] for i in r.json()['g']] # 返回的是json格式的数据，需要用json模块解析

        except Exception as e:
            return_list = []
    else:
        return_list = []
    return jsonify(return_list)
