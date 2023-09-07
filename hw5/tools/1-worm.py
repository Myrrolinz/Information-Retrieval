# !/usr/bin/env python
# -*- coding: utf-8 -*-

import os

import asyncio
import aiofiles

import pandas as pd
import httpx
from parsel import Selector

url_list = [f'http://news.nankai.edu.cn/ywsd/system/count//0003000/000000000000/000/000/c0003000000000000000_000000{i}.shtml' for i in range(467 + 50, 567)]  # 生成50页新闻列表页的url
url_list.append('http://news.nankai.edu.cn/ywsd/index.shtml')  # 单独插入首页

sem = asyncio.Semaphore(10)  # 设置协程数，爬虫协程限制较低，减少被爬服务器的压力
asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy()) # 解决windows下的RuntimeError: This event loop is already running

result_dict = {}

# 创建title_url_df，用于存储title和url，以便后续使用，索引是title，列是url
title_url_df = pd.DataFrame(columns=['url'])
title_url_df.index.name = 'title'


async def parse_catalogs_page(url):
    async with sem:
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            selector = Selector(response.text)
            temp_dict = zip(selector.css('a::attr(href)').getall(), selector.css('a::text').getall())
            result_dict.update(temp_dict)


async def parse_page(url):
    async with sem:
        try:
            async with httpx.AsyncClient(follow_redirects=True, timeout=10,
                                         headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36'}) as client:
                if url.startswith('http') or url.startswith('https'):
                    response = await client.get(url)
                    selector = Selector(response.text)
                    title = selector.css('title::text').get()
                    try:
                        if "/" in title:
                            title = title.replace("/", "_")
                        async with aiofiles.open(f'./pages/{title}.html', mode='w', encoding='utf-8') as f:
                            await f.write(response.text)
                        title_url_df.loc[title] = url  # 建立标题和url的映射关系

                    except Exception as e:
                        print(f'{e}: {url}|{title}')
        except:
            print(f'error: {url}')


async def main():
    # 检查pages文件夹是否存在，不存在则创建
    if not os.path.exists('./pages'):
        os.mkdir('./pages')

    tasks = [asyncio.create_task(parse_catalogs_page(url)) for url in url_list]
    await asyncio.gather(*tasks)

    tasks = [asyncio.create_task(parse_page(url)) for url in result_dict.keys()]
    await asyncio.gather(*tasks)

    # 写入文件
    title_url_df.to_csv("./title_url.csv")


if __name__ == '__main__':
    asyncio.run(main())
