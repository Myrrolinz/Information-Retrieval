# !/usr/bin/env python
# -*- coding: utf-8 -*-

import time
import json

from flask import render_template, request, redirect, url_for, Response

from . import front

from app.utils.search_func import main
from app.public_const import *


@front.route('/search')
def _result_page():
    t = time.perf_counter()  # 计时
    keywords = request.args.get('keywords')
    if request.cookies.get('search_history'):
        search_history: list = json.loads(request.cookies.get('search_history'))  # 从cookie中获取搜索历史
    else:
        search_history = []

    if not keywords:
        return redirect(url_for('front._index'))  # 如果keywords参数为空或者不存在，则返回首页
    else:
        try:
            result_list: list[tuple[str, float]] = main(keywords, search_history)  # [(url,cos_sim_score),...]
            results: list[tuple] = []  # [(title, url, description, cos_sim_score * page_rank_score),...]
            for result in result_list:
                url = result[0]
                temp_series = url_title_df.loc[url].fillna('')
                title = temp_series['title'].replace('_', '/')  # 还原文件名无法使用/用下划线代替的情况
                description = temp_series['description']
                cos_sim_score = result[1]
                page_rank_score = page_rank_df.loc[url]['page_rank']
                results.append((title, url, description, cos_sim_score * page_rank_score))  # 余弦相似度和PageRank进行乘算加权
            # 按照cos_sim_score*page_rank_score，从大到小排序
            results.sort(key=lambda x: x[3], reverse=True)
        except KeyError :
            cost_time = f'{time.perf_counter() - t: .2f}'
            return render_template(r'no_result_page.html', keywords=keywords, cost_time=cost_time)
        cost_time = f'{time.perf_counter() - t: .2f}'

    resp = Response(render_template(r'result_page.html', keywords=keywords, results=results, len_results=len(results), cost_time=cost_time, search_history=search_history))

    if keywords not in search_history:
        search_history.append(keywords)  # 将搜索关键词添加到历史记录中
    if len(search_history) > 12:
        search_history.pop(0)  # 如果历史记录超过12条，则删除最早的一条

    resp.set_cookie('search_history', json.dumps(search_history), max_age=60 * 60 * 24 * 30)  # 设置cookie,有效期为30天
    return resp
