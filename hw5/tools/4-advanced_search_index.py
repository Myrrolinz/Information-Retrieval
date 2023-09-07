# !/usr/bin/env python
# -*- coding: utf-8 -*-

import math
import os
import re
import datetime
import asyncio
import aiofiles
import pandas as pd
import networkx
from parsel import Selector
from jieba import cut_for_search

analyzer = cut_for_search

title_url_df = pd.read_csv("./title_url.csv", index_col=0)

index_df = pd.DataFrame(columns=['title', 'description', 'date_timestamp', 'content', 'editor'])
index_df.index.name = 'url'

sem = asyncio.Semaphore(30)  # 设置协程数

async def create_index(file):
    async with sem:
        async with aiofiles.open(file, mode='r', encoding='utf-8') as f:
            text = await f.read()
            selector = Selector(text)
            title = selector.css('title::text').get()
            _title = title.replace('/', '_')
            url = title_url_df.loc[_title, 'url']
            description = selector.css('meta[name="description"]::attr(content)').get()
            if description is not None:  # 非空描述去除部分字符
                description = description.replace('\r', '').replace('\n', '').replace('\t', '').replace('\n', '').replace('　', '')
            title_url_df.loc[_title, 'description'] = description
            _content = selector.css('p::text').getall()
            content = "".join(_content[:-1])
            if _content != []:  # 非空正文去除部分字符
                content = content.replace('\r', '').replace('\n', '').replace('\t', '').replace(' ', ' ').replace('　', '')
                try:
                    editor = _content[-1].replace('\n', '').replace(' ', '')
                except:
                    print(content, _content)
                    exit()
            else:
                editor = None

            # 新闻发布时间
            regex = re.search(r'(20)\d{2}/(0?[1-9]|1[012])/(0?[1-9]|[12][0-9]|3[01])/', url, re.S)  # 正则匹配YYYY/MM/DD/
            if bool(regex):
                date = regex.group()
                # 将时间转换为时间戳
                date_timestamp = datetime.datetime.strptime(date, '%Y/%m/%d/').timestamp()  # 转换时间戳存储
            else:
                date_timestamp = None

            index_df.loc[url] = [title, description, date_timestamp, content, editor] # 写入df



async def main():
    files = os.listdir('./pages')  # 获取pages文件夹下所有文件名
    tasks = [asyncio.create_task(create_index(f'./pages/{file}')) for file in files]
    await asyncio.gather(*tasks)

    # 写入文件
    index_df.to_csv("./advanced_search_index.csv", encoding='utf-8-sig')


if __name__ == '__main__':
    asyncio.run(main())
