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

analyzer = cut_for_search  # 初始化分词器

title_url_df = pd.read_csv("./title_url.csv", index_col=0)

index_df = pd.DataFrame(columns=['title', 'description', 'date_timestamp', 'content', 'editor'])
index_df.index.name = 'url'

sem = asyncio.Semaphore(30)  # 设置协程数，这边都是本地IO，所以可以设置较高的协程数

punctuation_cn = '＂＃＄％＆＇（）＊＋，－／：；＜＝＞＠［＼］＾＿｀｛｜｝～｟｠｢｣､\u3000、〃〈〉《》「」『』【】〔〕〖〗〘〙〚〛〜〝〞〟〰〾〿–—‘’‛“”„‟…‧﹏﹑﹔·！？｡。'  # 中文标点符号集合，用于去除中文标点符号

url_url_list_dict = {}  # 用于存储以URL为索引的，每个URL中包含的URL的列表


async def create_index(file):
    async with sem:
        async with aiofiles.open(file, mode='r', encoding='utf-8') as f:
            text = await f.read()
            selector = Selector(text)
            title = selector.css('title::text').get()
            _title = title.replace('/', '_')
            url = title_url_df.loc[_title, 'url']  # 从title和url的对应关系中获取爬下来页面的真实url
            description = selector.css('meta[name="description"]::attr(content)').get()  # 获取head内的description
            if description is not None:  # 非空描述去除部分字符
                description = description.replace('\r', '').replace('\n', '').replace('\t', '').replace('\n', '').replace('　', '')
            title_url_df.loc[_title, 'description'] = description
            _content: list = selector.css('p::text').getall()
            content = "".join(_content[:-1])  # 去除最后一个编辑信息
            if _content != []:  # 非空正文去除部分字符
                content = content.replace('\r', '').replace('\n', '').replace('\t', '').replace(' ', ' ').replace('　', '')
                try:
                    editor = _content[-1].replace('\n', '').replace(' ', '')
                except:
                    print(content, _content)  # debug用
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

            # 对title、description、content进行分词
            title = list(analyzer(title))
            if description is not None:
                description = list(analyzer(description))
            if description is not None:
                content = list(analyzer(content))

            # list转str，使用特殊符号分隔，并在删除标点后，删除原有空格并将分隔符号改为空格
            title = (re.sub(rf"[{punctuation_cn}]", '', '✘'.join(title)).replace('-', '')).split('✘')  # 标题需要额外删除用于SEO的-符号
            title = ' '.join([word for word in title if (word != '' and word != ' ')])
            if description is not None:
                description = re.sub(rf"[{punctuation_cn}]", '', '✘'.join(description)).split('✘')
                description = ' '.join([word for word in description if (word != '' and word != ' ')])
            if content is not None:
                content = re.sub(rf"[{punctuation_cn}]", '', '✘'.join(content)).split('✘')
                content = ' '.join([word for word in content if (word != '' and word != ' ')])

            index_df.loc[url] = [title, description, date_timestamp, content, editor]

            # 提取页面中的url
            url_list = []
            url_list.extend(selector.css('a::attr(href)').getall())
            url_url_list_dict[url] = url_list


async def main():
    files = os.listdir('./pages')  # 获取pages文件夹下所有文件名
    tasks = [asyncio.create_task(create_index(f'./pages/{file}')) for file in files]
    await asyncio.gather(*tasks)

    # 写入文件
    index_df.to_csv("./index.csv", encoding='utf-8-sig')

    # 计算PageRank
    digraph = networkx.DiGraph()
    for url, url_list in url_url_list_dict.items():
        for _url in url_list:
            if _url in title_url_df.url.values:
                digraph.add_edge(url, _url)
    result = networkx.pagerank(digraph, alpha=0.85)
    page_rank_df = pd.Series(result, name='page_rank')
    page_rank_df = page_rank_df.apply(lambda x: math.log(x * 10000, 10) + 1)  # 将page_rank列所有数值*10000后，取10的对数，再+1保证数值大于1（用于缩小PageRank极差，避免权重过大）
    page_rank_df.index.name = 'url'
    page_rank_df.to_csv("./page_rank.csv", encoding='utf-8-sig')
    title_url_df.to_csv("./title_url.csv", encoding='utf-8-sig')  # 重新保存带有description的title_url.csv，方便后续使用


if __name__ == '__main__':
    asyncio.run(main())
