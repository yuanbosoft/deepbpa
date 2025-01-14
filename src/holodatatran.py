# -*- coding: utf-8 -*-

"""HoloDataTran类
这个类用于处理交易数据，计算交易可疑度，账户可疑度等，并提供数据映射和输出功能。
"""



class HoloDataTran:
    """HoloDataTran 类用于处理交易数据并计算可疑度
    Attributes
    ----------
    casename : str
        原始数据集的名称
    timeinterval : int, optional
        交易可疑度计算的时间间隔，默认为2592000秒（1个月）
    """

    def __init__(self, casename, timeinterval=2592000):
        """初始化HoloDataTran类
        Parameters
        ----------
        casename : str
            数据集名称
        timeinterval : int, optional
            时间间隔，默认为2592000秒（1个月）
        """
        self.casename = casename
        self.timeinterval = timeinterval

    def myReadData(self, path):
        """读取数据文件
        从给定路径读取数据并返回。

        Parameters
        ----------
        path : str
            文件路径

        Returns
        -------
        dict
            文件中的数据，以字典形式返回
        """
        with open(path, 'r') as f:
            data = eval(f.read())
        return data

    def num_to_addr(self):
        """获取编号到地址的映射
        通过读取交易数据文件，获取从编号到地址的映射关系。

        Returns
        -------
        dict, dict
            返回两个字典，分别是从编号到地址的映射（dict_from），
            以及从编号到地址的映射（dict_to）
        """
        path_from = f'./inputData/AML/data/{self.casename}/all-normal-tx_from.txt'
        dict_from = self.myReadData(path_from)
        path_to = f'./inputData/AML/data/{self.casename}/all-normal-tx_to.txt'
        dict_to = self.myReadData(path_to)
        return dict_from, dict_to

    def addr_to_num(self):
        """获取地址到编号的映射
        通过读取交易数据文件，获取从地址到编号的映射关系。

        Returns
        -------
        dict, dict
            返回两个字典，分别是从地址到编号的映射（new_dict_from），
            以及从地址到编号的映射（new_dict_to）
        """
        dict_from, dict_to = self.num_to_addr()
        dict_from = np.array(dict_from)
        dict_to = np.array(dict_to)

        new_dict_from = dict(zip(dict_from[:, 1], dict_from[:, 0]))
        new_dict_to = dict(zip(dict_to[:, 1], dict_to[:, 0]))
        return new_dict_from, new_dict_to

    def cal_time_sus(self, X):
        """计算交易的时间可疑度
        基于交易的时间数据，计算其时间可疑度。

        Parameters
        ----------
        X : array-like
            交易数据数组

        Returns
        -------
        float
            返回计算得到的可疑度
        """
        d = len(X)
        J = range(1, d)
        S = 2 * np.dot(J, X) / (d * sum(X)) - (d + 1) / d
        return S

    def cal_account_sus(self, S):
        """计算账户的可疑度
        基于时间可疑度计算账户的可疑度。

        Parameters
        ----------
        S : float
            时间可疑度

        Returns
        -------
        float
            返回计算得到的账户可疑度
        """
        T = np.mean(S)
        b = 1  # 假设b为1，实际应用中可能根据情况调整
        F = 1 / (1 + np.power(b, T))
        return F

    def cal_tran_sus(self, tran, d=86400):
        """计算交易的可疑度
        基于交易记录，计算每笔交易的可疑度。

        Parameters
        ----------
        tran : pd.DataFrame
            包含交易记录的DataFrame
        d : int, optional
            时间粒度，默认为86400秒（1天）

        Returns
        -------
        pd.DataFrame
            返回包含可疑度分数的新交易数据集
        """
        tol = sum(tran['value'])
        sus = []
        for idx, row in tran.iterrows():
            t = row['timeStamp']
            trand = tran.loc[(tran['timeStamp'] > t - d) & (tran['timeStamp'] < t + d)]
            tol_d = sum(trand['value'])
            if tol != 0:
                sus.append(tol_d / tol)
            else:
                sus.append(0)
        tran['suspicious_score'] = sus
        return tran

    def cal_transaction_suscore(self):
        """计算交易的可疑度分数
        计算整个交易数据集的可疑度分数，并返回带有可疑度分数的交易数据。

        Returns
        -------
        pd.DataFrame
            包含可疑度分数的交易数据
        """
        csv_path = f'./inputData/AML/{self.casename}/all-normal-tx.csv'
        trans = pd.read_csv(csv_path)
        trans[['value']] = trans[['value']].astype(float)

        begintime = min(trans['timeStamp'])
        endtime = max(trans['timeStamp'])
        K = int((endtime - begintime) / self.timeinterval) + 1
        T = [begintime + i * self.timeinterval for i in range(K)]

        columns_name = trans.columns.values.tolist() + ['suspicious_score']
        Tran_sus = pd.DataFrame(columns=columns_name)

        for k in range(K - 1):
            trank = trans.loc[(trans['timeStamp'] > T[k]) & (trans['timeStamp'] < T[k + 1])]
            trank = self.cal_tran_sus(trank)
            Tran_sus = Tran_sus.append(trank)

        return Tran_sus

    def caldataset(self):
        """计算交易数据集的基本信息
        计算交易网络中的from账户数、to账户数及总账户数，并返回处理后的数据。

        Returns
        -------
        pd.DataFrame
            处理后的交易关系数据集
        """
        csv_path = f'./inputData/AML/{self.casename}/all-normal-tx_sus.csv'
        raw_data = pd.read_csv(csv_path)

        dict_from = {}
        dict_to = {}
        count_from = 0
        count_to = 0
        relation = []

        n2afrom, n2ato = self.num_to_addr()
        a2nfrom, a2nto = self.addr_to_num()

        for line in raw_data.itertuples():
            if float(line[4]) < 1.0:
                continue

            getFrom = line[2]
            getTo = line[3]
            getScore = line[12]
            timeStamp = int(line[5])
            dateArray = datetime.datetime.utcfromtimestamp(timeStamp)
            stdTime = dateArray.strftime("%Y-%m-%d")
            getTime = stdTime

            if getFrom not in dict_from:
                dict_from[getFrom] = count_from
                count_from += 1

            if getTo not in dict_to:
                dict_to[getTo] = count_to
                count_to += 1

            relation.append([a2nfrom[getFrom], a2nto[getTo], getTime, int(getScore * 100), 1])

        relationship = pd.DataFrame(relation)
        return relationship

    def output_holo(self):
        """输出Holo数据
        计算并输出交易数据的可疑度分数和交易关系数据。

        """
        print(f'{self.casename} 开始处理...\n')
        source_path = f'./inputData/AML/{self.casename}/'
        suscorefile = source_path + 'all-normal-tx_sus.csv'

        tttt = self.cal_transaction_suscore()
        tttt.to_csv(suscorefile, header=0, index=False)

        dddd = self.caldataset()
        dddd.to_csv(source_path + f'{self.casename}_holo.csv', index=False)

        print(f'{self.casename} 处理完成！\n\n\n')
