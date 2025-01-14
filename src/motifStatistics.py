# -*- coding: utf-8 -*-

"""
MotifStatistics
封装了计算图中motif统计特征的功能。
"""

import pandas as pd
import numpy as np
import os
import json
from numba.typed import List, Dict
from numba import njit, types

class MotifStatistics:
    '''计算图中motif统计特征的类

    Attributes
    ----------
    delta : int
        Motif的时间窗口大小
    save_path : str
        保存路径
    datasets_dir : str
        数据集目录
    '''

    def __init__(self, parameters):
        '''初始化'''
        self.delta = parameters['motif_delta']
        self.save_path = parameters['motif_path'] + '/motif' + str(self.delta) + '/' + 'APPR_alpha{}_epsilon{}/'.format(parameters['alpha'], parameters['epsilon'])
        self.datasets_dir = parameters['data_path'] + '/APPR_alpha{}_epsilon{}/'.format(parameters['alpha'], parameters['epsilon'])

        if not os.path.exists(self.save_path):
            os.makedirs(self.save_path)

    @staticmethod
    @njit(cache=True, locals={'cnt_phish': types.int64})
    def motif_cnt(node, parents, children, motif_matrix, delta):
        '''计算单个节点的motif数量

        Parameters
        ----------
        node : int
            节点索引
        parents : Dict
            父节点字典
        children : Dict
            子节点字典
        motif_matrix : Dict
            Motif矩阵
        delta : int
            时间窗口大小
        '''
        if node in parents and node in children:
            for child in children[node]:
                for parent in parents[node]:
                    if child[0] != parent[0] and parent[1] <= child[1] <= parent[1] + delta:
                        if node in motif_matrix:
                            motif_matrix[node].append(child[0])
                            motif_matrix[node].append(parent[0])
                        else:
                            L = List()
                            L.append(child[0])
                            L.append(parent[0])
                            motif_matrix[node] = L

                        if child[0] in motif_matrix:
                            motif_matrix[child[0]].append(node)
                            motif_matrix[child[0]].append(parent[0])
                        else:
                            L = List()
                            L.append(node)
                            L.append(parent[0])
                            motif_matrix[child[0]] = L

                        if parent[0] in motif_matrix:
                            motif_matrix[parent[0]].append(node)
                            motif_matrix[parent[0]].append(child[0])
                        else:
                            L = List()
                            L.append(node)
                            L.append(child[0])
                            motif_matrix[parent[0]] = L

                    elif parent[1] > child[1]:
                        break

    @staticmethod
    @njit(cache=True)
    def cal_motif(parents, children, delta, motif_matrix, nodes):
        '''计算所有节点的motif

        Parameters
        ----------
        parents : Dict
            父节点字典
        children : Dict
            子节点字典
        delta : int
            时间窗口大小
        motif_matrix : Dict
            Motif矩阵
        nodes : List
            节点列表
        '''
        for k, node in enumerate(nodes):
            MotifStatistics.motif_cnt(node, parents, children, motif_matrix, delta)

    def process_subgraph(self, seed):
        '''处理子图

        Parameters
        ----------
        seed : str
            种子节点

        Returns
        -------
        parents : Dict
            父节点字典
        children : Dict
            子节点字典
        add2idx : Dict
            地址到索引的映射
        idx2add : Dict
            索引到地址的映射
        '''
        subgraph_df = pd.read_csv(self.datasets_dir + seed + "/" + seed + ".csv", low_memory=False)
        appr_node_df = pd.read_csv(self.datasets_dir + seed + "/importance/" + seed + ".csv")

        subgraph_df = subgraph_df.drop_duplicates(subset=["hash"])
        subgraph_df = subgraph_df.reset_index(drop=True)

        del_idx = set()
        del_idx |= set(subgraph_df[subgraph_df["from"] == subgraph_df["to"]].index)
        del_idx |= set(subgraph_df[subgraph_df["isError"] == 1].index)

        subgraph_df = subgraph_df.drop(del_idx)
        subgraph_df = subgraph_df.reset_index(drop=True)

        parents, children = {}, {}
        add2idx, idx2add = {}, {}
        idx = types.int64(0)

        for i in range(subgraph_df.shape[0]):
            hash, src, trg = subgraph_df.loc[i, ["hash", "from", "to"]]
            timeStamp = types.int64(subgraph_df.loc[i, "timeStamp"])

            if src not in add2idx:
                add2idx[src] = idx
                idx2add[idx] = src
                idx += 1
            if trg not in add2idx:
                add2idx[trg] = idx
                idx2add[idx] = trg
                idx += 1

            idx_src = add2idx[src]
            idx_trg = add2idx[trg]

            if src != trg:
                if idx_src not in children:
                    children[idx_src] = [[idx_trg, timeStamp]]
                else:
                    children[idx_src].append([idx_trg, timeStamp])

                if idx_trg not in parents:
                    parents[idx_trg] = [[idx_src, timeStamp]]
                else:
                    parents[idx_trg].append([idx_src, timeStamp])

        for key in parents:
            parents[key] = sorted(parents[key], key=lambda x: x[1], reverse=True)
        for key in children:
            children[key] = sorted(children[key], key=lambda x: x[1], reverse=True)

        P = Dict.empty(key_type=types.int64, value_type=types.ListType(types.ListType(types.int64)))
        C = Dict.empty(key_type=types.int64, value_type=types.ListType(types.ListType(types.int64)))

        for key, value in parents.items():
            L = List()
            for item in value: L.append(List(item))
            P[key] = L

        for key, value in children.items():
            L = List()
            for item in value: L.append(List(item))
            C[key] = L

        print("finish graph construction of seed {}".format(seed))
        return P, C, add2idx, idx2add

    def feature_extraction(self):
        '''特征提取'''
        datasets = os.listdir(self.datasets_dir)

        for seed in datasets:
            parents, children, add2idx, idx2add = self.process_subgraph(seed)
            nodes = np.array(list(set(parents.keys()) | set(children.keys())), dtype=np.int64)

            motif_matrix = Dict.empty(key_type=types.int64, value_type=types.ListType(types.int64))
            MotifStatistics.cal_motif(parents, children, self.delta, motif_matrix, nodes)

            motif_matrix_dict = {}

            for node1 in motif_matrix:
                for node2 in motif_matrix[node1]:
                    if idx2add[node1] not in motif_matrix_dict:
                        motif_matrix_dict[idx2add[node1]] = {idx2add[node2]: 1}
                    elif idx2add[node2] not in motif_matrix_dict[idx2add[node1]]:
                        motif_matrix_dict[idx2add[node1]][idx2add[node2]] = 1
                    else:
                        motif_matrix_dict[idx2add[node1]][idx2add[node2]] += 1

            np.save(self.save_path + seed + ".npy", motif_matrix_dict)

