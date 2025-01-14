# -*- coding: utf-8 -*-
"""
CubeDataTran 类
用于处理AML数据集的转账信息，按指定规则划分三部图（出发节点、目标节点、终点节点）并进行计算。
它读取原始CSV数据，并生成相关的映射关系和处理后的数据。

Attributes
----------
csv_path : str
    数据文件的路径
setting1 : int, optional
    出发节点（AccA）与中间节点（AccM）之间的比较比例，默认为 10
setting2 : int, optional
    转账次数的比较阈值，默认为 2

Methods
-------
diff(listA, listB)
    求两个列表的交集
CHA(listA, listB)
    求差集，返回在 B 中但不在 A 中的元素
BING(listA, listB)
    求并集，返回两个列表的所有唯一元素
myReadData(path)
    读取并解析数据文件
num_to_addr(casename)
    获取从编号到地址的映射关系
addr_to_num(casename)
    获取从地址到编号的映射关系
caldataset(casename, setting1=10, setting2=2)
    计算并构建三部图的数据集
"""


class CubeDataTran:
    """
    处理AML数据集，按规则划分三部图并生成数据。
    """

    def __init__(self, csv_path, setting1=10, setting2=2):
        """
        初始化 CubeDataTran 类。

        Parameters
        ----------
        csv_path : str
            输入数据的路径
        setting1 : int, optional
            出发节点与中间节点的比较比例，默认为 10
        setting2 : int, optional
            转账次数的阈值，默认为 2
        """
        self.csv_path = csv_path
        self.setting1 = setting1
        self.setting2 = setting2

    def diff(self, listA, listB):
        """
        求两个列表的交集。

        Parameters
        ----------
        listA : list
            第一个列表
        listB : list
            第二个列表

        Returns
        -------
        list
            交集元素列表
        """
        return [i for i in listA if i in listB]

    def CHA(self, listA, listB):
        """
        求差集，返回在B中但不在A中的元素。

        Parameters
        ----------
        listA : list
            第一个列表
        listB : list
            第二个列表

        Returns
        -------
        list
            差集元素列表
        """
        return list(set(listB).difference(set(listA)))

    def BING(self, listA, listB):
        """
        求并集，返回两个列表的所有唯一元素。

        Parameters
        ----------
        listA : list
            第一个列表
        listB : list
            第二个列表

        Returns
        -------
        list
            并集元素列表
        """
        return list(set(listA).union(set(listB)))

    def myReadData(self, path):
        """
        读取并解析数据文件。

        Parameters
        ----------
        path : str
            数据文件的路径

        Returns
        -------
        dict
            文件中的数据解析结果
        """
        with open(path, 'r') as f:
            data = eval(f.read())
        return data

    def num_to_addr(self, casename):
        """
        获取从编号到地址的映射关系。

        Parameters
        ----------
        casename : str
            案例名称

        Returns
        -------
        tuple
            三个字典：dict_A, dict_H, dict_B
        """
        path = f'./inputData/AML/data/{casename}/all-normal-tx_A.txt'
        dict_A = self.myReadData(path)
        path = f'./inputData/AML/data/{casename}/all-normal-tx_H.txt'
        dict_H = self.myReadData(path)
        path = f'./inputData/AML/data/{casename}/all-normal-tx_B.txt'
        dict_B = self.myReadData(path)
        return dict_A, dict_H, dict_B

    def addr_to_num(self, casename):
        """
        获取从地址到编号的映射关系。

        Parameters
        ----------
        casename : str
            案例名称

        Returns
        -------
        tuple
            三个字典：new_dict_A, new_dict_H, new_dict_B
        """
        dict_A, dict_H, dict_B = self.num_to_addr(casename)
        dict_A = np.array(dict_A)
        dict_H = np.array(dict_H)
        dict_B = np.array(dict_B)

        new_dict_A = dict(zip(dict_A[:, 1], dict_A[:, 0]))
        new_dict_H = dict(zip(dict_H[:, 1], dict_H[:, 0]))
        new_dict_B = dict(zip(dict_B[:, 1], dict_B[:, 0]))
        return new_dict_A, new_dict_H, new_dict_B

    def caldataset(self, casename):
        """
        计算并构建三部图的数据集。

        Parameters
        ----------
        casename : str
            案例名称

        Returns
        -------
        None
            无返回值，生成处理后的文件
        """
        # 读取原始数据并预处理
        raw_data = pd.read_csv(self.csv_path)
        raw_data[['value']] = raw_data[['value']].astype(float)
        raw_data[['timeStamp']] = raw_data[['timeStamp']].astype(int)

        account_from = raw_data['from'].tolist()
        account_to = raw_data['to'].tolist()
        account_total = self.BING(account_from, account_to)

        AccA = []
        AccM = []
        AccC = []
        # 划分三部图
        for curadd in account_total:
            tmptran = raw_data[raw_data['from'] == curadd]
            Chusum = len(tmptran)
            tmptran = raw_data[raw_data['to'] == curadd]
            Rusum = len(tmptran)

            if Chusum > Rusum * self.setting1:
                AccA.append(curadd)
            if Rusum > Chusum * self.setting1:
                AccC.append(curadd)
            if Chusum > self.setting2 and Rusum > self.setting2:
                AccM.append(curadd)
            else:
                AccM.append(curadd)

        # 生成交易数据
        xy_tran = []
        yz_tran = []
        triA = {}
        triH = {}
        triB = {}
        a2nA = {}
        a2nH = {}
        a2nB = {}
        Ac, Hc, Bc = 0, 0, 0

        for idx, data in raw_data.iterrows():
            if data['value'] == 0.0:
                continue
            getFrom = data['from']
            getTo = data['to']
            getMoney = data['value'] * 1e-18
            getTime = data['timeStamp']

            if getFrom in AccA and getTo in AccM:
                if getFrom not in list(triA.values()):
                    triA[Ac] = getFrom
                    a2nA[getFrom] = Ac
                    Ac += 1
                if getTo not in list(triH.values()):
                    triH[Hc] = getTo
                    a2nH[getTo] = Hc
                    Hc += 1
                relation = [a2nA[getFrom], a2nH[getTo], getTime, getMoney]
                xy_tran.append(relation)

            if getFrom in AccM and getTo in AccC:
                if getFrom not in list(triH.values()):
                    triH[Hc] = getFrom
                    a2nH[getFrom] = Hc
                    Hc += 1
                if getTo not in list(triB.values()):
                    triB[Bc] = getTo
                    a2nB[getTo] = Bc
                    Bc += 1
                relation = [a2nH[getFrom], a2nB[getTo], getTime, getMoney]
                yz_tran.append(relation)

        # 保存映射关系
        A_keys = sorted(triA.keys())
        new_triA_sort = [(key, triA[key]) for key in A_keys]
        H_keys = sorted(triH.keys())
        new_triH_sort = [(key, triH[key]) for key in H_keys]
        B_keys = sorted(triB.keys())
        new_triB_sort = [(key, triB[key]) for key in B_keys]

        # 输出映射文件
        with open(f'./inputData/AML/data/{casename}/all-normal-tx_A.txt', 'w') as f:
            f.write(str(new_triA_sort))
        with open(f'./inputData/AML/data/{casename}/all-normal-tx_H.txt', 'w') as f:
            f.write(str(new_triH_sort))
        with open(f'./inputData/AML/data/{casename}/all-normal-tx_B.txt', 'w') as f:
            f.write(str(new_triB_sort))

        return xy_tran, yz_tran
