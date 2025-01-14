# -*- coding: utf-8 -*-

"""
Evaluation
封装了评估结果的相关函数，包括加载标签数据、计算平均钓鱼密度、平均导通性和加权平均导通性。
"""

import pandas as pd
import numpy as np
import os
import shutil
import json

class Evaluation:
    '''评估结果类

    Attributes
    ----------
    comm_dir : str
        通信目录路径
    label_dict : dict
        标签字典
    phish_label_set : set
        钓鱼标签集合
    scamdb_seeds : set
        scamdb种子集合
    '''

    def __init__(self, comm_dir):
        '''初始化'''
        self.comm_dir = comm_dir
        self.label_dict, self.phish_label_set, self.scamdb_seeds = self.load_labels()

    def load_labels(self):
        '''加载标签数据
        加载非钓鱼账户标签和钓鱼标签

        Returns
        -------
        label_dict : dict
            标签字典
        phish_label_set : set
            钓鱼标签集合
        scamdb_seeds : set
            scamdb种子集合
        '''
        label_df = pd.read_csv("data/labels_etherscan_33w.csv")
        label_dict = label_df.set_index(["Address"])["Label_1"].to_dict()
        print("load labels_etherscan_33w.csv\n")

        parameters = json.loads(open('params.json', 'r').read())
        phish_label_df = pd.read_csv("data/phishing_label_5362.csv")
        phish_label_set = set(phish_label_df["address"].values)
        print("load phishing_label_5362.csv\n")

        scamdb_seeds = set(os.listdir(parameters['data_path'] + '/APPR_alpha{}_epsilon{}/'.format(parameters['alpha'], parameters['epsilon'])))
        print("load 2056 scamdb seeds\n")

        return label_dict, phish_label_set, scamdb_seeds

    def evaluate_results(self):
        '''评估结果
        计算检测到的地址、真正例、假正例和交易所地址的数量，并计算平均钓鱼密度、平均导通性和加权平均导通性。

        Returns
        -------
        None
        '''
        detected_address = set()
        TP_address = set()
        FP_address = set()
        exchange_address = set()

        for seed in os.listdir(self.comm_dir + "/output_GA/"):
            with open(self.comm_dir + "/output_GA/" + seed + "/comm_nodes_inner.csv", "r") as f:
                for line in f:
                    line = line.rstrip("\n").split(",")
                    if line[0] == "Id": continue

                    addr = line[0]
                    detected_address.add(addr)
                    if addr in (self.phish_label_set - self.scamdb_seeds): TP_address.add(addr)
                    if (addr in self.label_dict) and (self.label_dict[addr] != "phish-hack"): FP_address.add(addr)
                    if (addr in self.label_dict) and (self.label_dict[addr] == "exchange"): exchange_address.add(addr)

        print("#Nodes: {}".format(len(detected_address)))
        print("TP: {}".format(len(TP_address)))
        print("FP: {}".format(len(FP_address)))
        print("#exchanges: {}".format(len(exchange_address)))

        avg_phish_density = self.cal_avg_phish_density(self.phish_label_set, self.scamdb_seeds)
        print("avg_phish_density: {}".format(avg_phish_density))

        avg_conductance = self.cal_avg_conductance()
        print("avg_conductance: {}".format(avg_conductance))

        avg_weighted_conductance = self.cal_avg_weighted_conductance()
        print("avg_weighted_conductance: {}".format(avg_weighted_conductance))

    def cal_avg_phish_density(self, phish_label_set, scamdb_seeds):
        '''计算平均钓鱼密度

        Parameters
        ----------
        phish_label_set : set
            钓鱼标签集合
        scamdb_seeds : set
            scamdb种子集合

        Returns
        -------
        float
            平均钓鱼密度
        '''
        merge_dir = self.comm_dir + "/output_merge_with_clustering/comm_merge_BIRCH/"
        density_list = []

        for gang in os.listdir(merge_dir):
            df = pd.read_csv(merge_dir + gang + "/mrg_comm_nodes_inner.csv")
            num_phish = float(df[df["Id"].isin(phish_label_set | scamdb_seeds)].shape[0])
            num_nodes = float(df.shape[0])
            density_list.append(num_phish / num_nodes)

        return np.mean(density_list)

    def cal_avg_conductance(self):
        '''计算平均导通性

        Returns
        -------
        float
            平均导通性
        '''
        merge_dir = self.comm_dir + "/output_merge_with_clustering/comm_merge_BIRCH/"
        conductance_list = []

        for gang in os.listdir(merge_dir):
            comm_nodes_inner_df = pd.read_csv(merge_dir + gang + "/mrg_comm_nodes_inner.csv")
            comm_edges_df = pd.read_csv(merge_dir + gang + "/mrg_comm_edges.csv")

            if int(comm_nodes_inner_df.shape[0]) == 1:
                conductance_list.append(1.0)
                continue

            comm_nodes_inner = set(comm_nodes_inner_df["Id"].values)
            outer = inner = 0.0

            for i in range(comm_edges_df.shape[0]):
                src, trg = comm_edges_df.loc[i, ["Source", "Target"]]

                if src in comm_nodes_inner: inner += 1
                else: outer += 1
                if trg in comm_nodes_inner: inner += 1
                else: outer += 1

            conductance_list.append(outer / inner)

        return np.mean(conductance_list)

    def cal_avg_weighted_conductance(self):
        '''计算加权平均导通性

        Returns
        -------
        float
            加权平均导通性
        '''
        merge_dir = self.comm_dir + "/output_merge_with_clustering/comm_merge_BIRCH/"
        weighted_conductance_list = []

        for gang in os.listdir(merge_dir):
            comm_nodes_inner_df = pd.read_csv(merge_dir + gang + "/mrg_comm_nodes_inner.csv")
            comm_edges_df = pd.read_csv(merge_dir + gang + "/mrg_comm_edges.csv")

            if int(comm_nodes_inner_df.shape[0]) == 1:
                weighted_conductance_list.append(1.0)
                continue

            comm_nodes_inner = set(comm_nodes_inner_df["Id"].values)
            outer = inner = 0.0

            for i in range(comm_edges_df.shape[0]):
                src, trg = comm_edges_df.loc[i, ["Source", "Target"]]
                value = float(comm_edges_df.loc[i, "Value"])

                if src in comm_nodes_inner: inner += value
                else: outer += value
                if trg in comm_nodes_inner: inner += value
                else: outer += value

            weighted_conductance_list.append(outer / inner)

        return np.mean(weighted_conductance_list)