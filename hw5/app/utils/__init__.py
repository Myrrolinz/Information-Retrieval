# !/usr/bin/env python
# -*- coding: utf-8 -*-

import re


def input_fuzzy_finder(input_word, words_list):
    """
    模糊查找
    Args:
        input_word: 输入的关键词
        word_list: 需要匹配的词库

    Returns:
        返回一个列表，列表中的元素为元组，元组中的第一个元素为匹配到的词，第二个元素为匹配到的词的相似度
    """
    suggestions = []
    regex = re.compile('.*?'.join(input_word))  # 完成正则表达式的创建
    for word in words_list:
        match = regex.search(word)  # 通过正则表达式进行匹配
        if match:
            suggestions.append((len(match.group()), match.start(), word))
    return [x for _, _, x in sorted(suggestions)]
