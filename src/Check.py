# -*- coding: utf-8 -*-

"""
数据分析与指标计算工具类
该类封装了几个方法用于分析不同的案件文件，计算精度、召回率、资金覆盖率等指标。
"""

class Check:
    """
    Check 类用于分析案件文件的结果，并计算各种指标。

    Attributes
    ----------
    casename : str
        案件的名称，用于指定案件文件的路径。
    k : int
        参数k，指定分析的级别。
    level : int
        级别，用于指定处理的级别。
    """

    def __init__(self, casename, k):
        """
        初始化 MetricsAnalyzer 对象。

        Parameters
        ----------
        casename : str
            案件名称
        k : int
            参数k，用于设置级别和文件名
        """
        self.casename = casename
        self.k = k

    def case_analysis(self, casename, k):
        """
        分析案件数据，计算每个级别的精度和召回率。

        Parameters
        ----------
        casename : str
            案件的名称。
        k : int
            级别k，影响文件名的命名

        Returns
        -------
        dict
            案件的精度和召回率字典。
        """
        out_path = f'C:/Users/eyzy/Desktop/DenseFlow_Tool-main/{casename}_out/'
        P = []
        R = []
        for level in range(4):
            file_path = out_path + f'{casename}_k_{k}_level_{level}.xlsx'
            if not os.path.exists(file_path):
                print(f"缺少结果文件 {casename}_k_{k}_level_{level}")
                pre = rec = -1
            else:
                result = pd.read_excel(file_path, sheet_name='Sheet3')
                result = result['all_heist'].tolist()
                address_path = f'./inputData/AML/{casename}/accounts-hacker.csv'
                if not os.path.exists(address_path):
                    print("Error: 缺少标签文件")
                    continue
                address = pd.read_csv(address_path)
                heist = address.loc[address['label'] == 'heist']
                heist_address = heist['address'].tolist()
                correct = [fh for fh in result if fh in heist_address]

                pre = len(correct) / len(result) if len(result) != 0 else -2
                rec = len(correct) / len(heist_address)

                print(
                    f"{casename}:\n holo+maxflow (level={level}, k={k}) 总共找出：{len(result)} 找出正确的：(heist) {len(correct)}")
                print(f"正确率(Precision): {pre}, 召回率（Recall）：{rec}\n\n")

            P.append(pre)
            R.append(rec)

        return {'precision': P, 'recall': R}

    def aggregate_results(self, cases):
        """
        聚合所有案件的结果，并返回一个包含所有案件的精度和召回率的 DataFrame。

        Parameters
        ----------
        cases : list of str
            案件名称列表

        Returns
        -------
        pd.DataFrame
            包含各案件精度和召回率的 DataFrame。
        """
        RESULT = {}
        for casename in cases:
            caseresult = self.case_analysis(casename, self.k)
            RESULT[casename] = caseresult

        res_df = pd.DataFrame.from_dict(RESULT, orient='index')
        pre_df = res_df['precision'].apply(lambda x: pd.Series(x))
        pre_df.columns = [f'precision_level_{i}' for i in range(4)]
        res_df = pd.concat([res_df, pre_df], axis=1)
        rec_df = res_df['recall'].apply(lambda x: pd.Series(x))
        rec_df.columns = [f'recall_level_{i}' for i in range(4)]
        res_df = pd.concat([res_df, rec_df], axis=1)
        res_df = res_df.drop(columns=['precision', 'recall'])

        return res_df

    def check_metrics(self, casename, level=1, k=10):
        """
        检查并计算具体案件的指标，包括精度、召回率、资金覆盖率等。

        Parameters
        ----------
        casename : str
            案件名称
        level : int, optional
            级别，默认为1
        k : int, optional
            参数k，默认为10

        Returns
        -------
        dict
            包含计算结果的字典，包括精度、资金覆盖率等。
        """
        PRE = {}
        MC = {}
        nodenum = {}
        METRICS = {}

        address_path = f'./inputData/AML/{casename}/accounts-hacker.csv'
        if not os.path.exists(address_path):
            print(f"{casename} 错误：缺少标签文件")
            return METRICS

        address = pd.read_csv(address_path)
        heist = address.loc[address['label'] == 'heist']
        heist_address = heist['address'].tolist()

        out_path = f'./Result/{casename}_out/'
        myfile = f'{casename}_k_{k}_level_{level}.xlsx'
        file_path = os.path.join(out_path, myfile)

        result = pd.read_excel(file_path, sheet_name='Sheet3')
        result = result['all_heist'].tolist()

        correct = [fh for fh in result if fh in heist_address]
        pre = len(correct) / len(result) if len(result) != 0 else -2
        rec = len(correct) / len(heist_address)

        print(f"{casename}:")
        print(f"总共找出：{len(result)}, 找出正确的：{len(correct)}, 正确率(Precision): {pre}, 召回率（Recall）：{rec}\n\n")

        # 计算资金覆盖率
        csv_path = f'./inputData/AML/{casename}/all-normal-tx.csv'
        raw_data = pd.read_csv(csv_path)
        raw_data[['value']] = raw_data[['value']].astype(float)
        raw_data[['timeStamp']] = raw_data[['timeStamp']].astype(int)

        account = list(set(raw_data['from'].tolist() + raw_data['to'].tolist()))
        fromisheist = raw_data[raw_data['from'].isin(result)]
        fromisheisttrue = raw_data[raw_data['from'].isin(heist_address)]

        m1 = fromisheist['value'].sum() * 1e-18  # 发起方主动
        m2 = fromisheisttrue['value'].sum() * 1e-18

        mrc = min(m1 / m2, 1)
        print(f'追踪金额：{m1}, 涉案金额：{m2}, 资金覆盖率：{mrc}')

        PRE['HOLO+MAXFLOW'] = pre
        MC['HOLO+MAXFLOW'] = m1 / m2 if m1 / m2 <= 1 else 1
        nodenum['HOLO+MAXFLOW'] = len(result)

        METRICS['HOLO+MAXFLOW'] = [pre, m1 / m2, len(result)]

        return METRICS
