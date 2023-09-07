# !/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import math
import os

import pandas as pd

path = r'./tools/frequency'
path2 = r'./tools'

advanced_search_index = pd.read_csv(os.path.join(path2, 'advanced_search_index.csv'))
advanced_search_index.fillna('', inplace=True) # 读取保存有完整内容的csv文件用于高级搜索。空值替换为空字符串
advanced_search_index.set_index('url', inplace=True)

# 读取倒排索引
with open(os.path.join(path, 'inverted_index.json'), 'r', encoding='utf-8') as f:
    inverted_index = json.load(f)

# 读取词频
with open(os.path.join(path, 'word_frequency.json'), 'r', encoding='utf-8') as f:
    word_frequency = json.load(f)
    word_set = sorted(set(word_frequency.keys()))

# 读取逆文档频率
with open(os.path.join(path, 'word_idf.json'), 'r', encoding='utf-8') as f:
    idf = json.load(f)

# 读取tf
with open(os.path.join(path, 'tf.json'), 'r', encoding='utf-8') as f:
    tf = json.load(f)

# 读取tf-idf
with open(os.path.join(path, 'tf-idf.json'), 'r', encoding='utf-8') as f:
    tf_idf = json.load(f)

# 读取url-title-description
url_title_df = pd.read_csv(os.path.join(path2, 'title_url.csv'), encoding='utf-8-sig', index_col=1)

# 读取title_only相关
with open(os.path.join(path, 'inverted_index_title_only.json'), 'r', encoding='utf-8') as f:
    inverted_index_title_only = json.load(f)

with open(os.path.join(path, 'word_frequency_title_only.json'), 'r', encoding='utf-8') as f:
    word_frequency_title_only = json.load(f)
    word_set_title_only = sorted(set(word_frequency_title_only.keys()))

with open(os.path.join(path, 'word_idf_title_only.json'), 'r', encoding='utf-8') as f:
    idf_title_only = json.load(f)

with open(os.path.join(path, 'tf_title_only.json'), 'r', encoding='utf-8') as f:
    tf_title_only = json.load(f)

with open(os.path.join(path, 'tf-idf_title_only.json'), 'r', encoding='utf-8') as f:
    tf_idf_title_only = json.load(f)

# 读取url频率
page_rank_df = pd.read_csv(os.path.join(path2, 'page_rank.csv'), encoding='utf-8-sig', index_col=0)
