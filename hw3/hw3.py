import math
from typing import Union

import numpy as np
import pandas as pd
import os

# 预处理文件
## 新建一个包含name author content 三列的dataframe
df = pd.DataFrame(columns=["name", "author", "content"])
## 遍历文件
path = './dataset'
for file in os.listdir(path):
    with open(path + '/' + file, 'r') as f:
        lines = f.readlines()
        content = ''
        for line in lines:
            if 'Author: ' in line:
                author = line.split('Author: ')[1].replace('\n', '')
            elif line != '\n':
                content += line.replace(',', '').replace(';', '').replace('.', '').replace('?', '').replace('!', '').replace('\'', '').replace('\n', '')  # 删除, ; . ? ! 等标点符号
                content += ' '  # 换行的时候加一个空格
        # 将name author content 加入dataframe
        df = pd.concat([df, pd.DataFrame([[file.replace('.txt', ''), author, content]], columns=["name", "author", "content"])], ignore_index=True)


# 统计词项tj在文档Di中出现的次数，也就是词频。
def computeTF(word_set, split):
    tf = dict.fromkeys(word_set, 0)
    for word in split:
        tf[word] += 1   
    for word, cnt in tf.items():
        tf[word] = math.log10(cnt + 1)  # TF = log10(N + 1) 减少文本长度带来的影响
    return tf


# 计算逆文档频率IDF
def computeIDF(tf_list):
    idf_dict = dict.fromkeys(tf_list[0], 0)  # 词为key，初始值为0
    N = len(tf_list)  # 总文档数量
    for tf in tf_list:  # 遍历字典中每一篇文章
        for word, count in tf.items():  # 遍历当前文章的每一个词
            if count > 0:  # 当前遍历的词语在当前遍历到的文章中出现
                idf_dict[word] += 1  # 包含词项tj的文档的篇数df+1
    for word, Ni in idf_dict.items():  # 利用公式将df替换为逆文档频率idf
        idf_dict[word] = round(math.log10(N / Ni), 4)  # N,Ni均不会为0 IDF = log10(N / df_t)
    return idf_dict  # 返回逆文档频率IDF字典


# 计算tf-idf(term frequency–inverse document frequency)
def computeTFIDF(tf, idfs):  # tf词频,idf逆文档频率
    tfidf = {}
    for word, tfval in tf.items():
        tfidf[word] = tfval * idfs[word]
    return tfidf


def length(key_list):
    num = 0
    for i in range(len(key_list)):
        num = num + key_list[i][1] ** 2
    return round(math.sqrt(num), 2)


def main(input_word: str, selected_region: list):
    """

    Args:
        input_word: keyword
        selected_region: in (name author content). Can select more than one.

    Returns:
        None
    """
    split_input = input_word.split(' ')
    split_input.sort()

    # 遍历selected_region，将符合条件的列加入df_selected
    df_selected = pd.DataFrame()
    for region in selected_region:
        df_selected = pd.concat([df_selected, df[region]], axis=1)

    # 将df_selected中的每一行拼接成一个字符串。索引为第i个文档，内容为选中的域中的内容
    df_selected_dict = {}
    for i in range(len(df_selected)):
        df_selected_dict[i] = ''
        for region in selected_region:
            df_selected_dict[i] += df_selected[region][i] + ' '

    split_dict = {}  # 存储每一行的分词结果，包含所有选定的阈，索引为第i个文档，内容为一个list(文档内所有词)
    word_set = set()  # 新建用于存储的set(set无序不重复)
    for k, v in df_selected_dict.items():
        split_result = v.split(' ')
        # 遍历split_result，全部转化为小写
        for i in range(len(split_result)):
            split_result[i] = split_result[i].lower()
        split_dict[k] = split_result
        word_set = word_set.union(split_result) # 求并集
    # 将分词集合升序排序
    word_set = sorted(word_set)

    tf_dict = {}  # 存储tf(词频)。索引为第i个文档，内容又是一个dict，索引为词，内容为df
    for k, v in split_dict.items():
        tf_dict[k] = computeTF(word_set, v) 

    idfs = computeIDF(list(tf_dict.values()))
    tfidf_dict = {}  # 存储每一篇文档的向量(tf-idf)
    for k, v in tf_dict.items():
        tfidf_dict[k] = computeTFIDF(v, idfs)
    tfidf_list = list(tfidf_dict.values())  # 将结果转化为list，方便后续调用
    # print(tfidf_list)

    key_tfidf_dict = {}  # 存储关键词的tfidf。筛选出tf-idf最大的前100个词，降序排列
    for k, v in tfidf_dict.items():
        key_tfidf_dict[k] = sorted(tfidf_dict[k].items(), key=lambda d: d[1], reverse=True)[:key_valid_number] # d.items() 以列表的形式返回可遍历的元组数组
    key_tfidf_list = list(key_tfidf_dict.values())  # 将结果转化为list，方便后续调用
    # print('1', key_tfidf_list)

    tf_input = computeTF(word_set, split_input) # 查询的tf
    tfidf_input = computeTFIDF(tf_input, idfs)  # 查询的tf-idf
    key_input = sorted(tfidf_input.items(), key=lambda d: d[1], reverse=True)[:key_valid_number]    # 查询的前100个关键词
    len_key_input = length(key_input)

    df_result = pd.DataFrame([*tfidf_list, tfidf_input])    # 将每个文档和查询的向量合成一张表
    print(df_result)
    i = 0
    while i < len(df_result.columns):
        if any(df_result.values.T[i]) == 0:
            df_result = df_result.drop(columns=df_result.columns[i], axis=1)    # 去掉向量全为0的列(即去掉无关单词)
        else:
            i = i + 1
    print('**************************向量空间***************************')
    print(df_result)  # 打印向量空间
    print('************************************************************')

    # 计算余弦相似度并排序
    result = []
    for i in range(len(key_tfidf_list)): # 遍历每个文档
        num = 0
        for j in range(len(key_input)): # 遍历每个关键输入词
            for k in range(len(key_tfidf_list[i])): # 遍历每个文档内的每个关键词
                if key_input[j][0] == key_tfidf_list[i][k][0]:  # 若为相同单词
                    num = num + key_input[j][1] * key_tfidf_list[i][k][1]
        result.append((i, (round(num / (len_key_input * length(key_tfidf_list[i])), 4))))   # 存储第i个文档的余弦相似度
    result = sorted(result, key=lambda d: d[1], reverse=True)
    print('**************************余弦相似度*************************')
    print(result)  # 打印余弦相似度
    print('************************************************************')
    print('**************************文档排序***************************')
    for i in range(len(result)):
        print(df['name'][result[i][0]], result[i][1])
    print('************************************************************')


def select():
    selected_region = []
    for i in range(len(region)):
        if input(f'是否选择{region[i]}？(Y/n)：') in ['y', 'Y', '']:
            selected_region.append(region[i])
    return selected_region


if __name__ == '__main__':
    key_valid_number = 100  # 有效关键词数量
    input_word = input('请输入关键词：')
    # 将输入的关键词全部字母转化为小写
    input_word = input_word.lower()
    print(f'检索关键词为：{input_word}')
    region = ("author", "name", "content") # 作者，诗名，内容
    selected_region = select()
    while len(selected_region) == 0:
        print('至少选择一个域')
        selected_region = select()
    main(input_word, selected_region)
