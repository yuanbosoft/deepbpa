# -*- coding: utf-8 -*-




class DataTran:
    '''数据处理与转换类
    该类包含一系列数据转换、映射和存储的操作，主要处理CSV文件中的地址与编号之间的映射。

    Attributes
    ----------
    casename : str
        数据集的名称，用于指定文件路径
    '''

    def __init__(self, casename):
        '''初始化DataTran类
        Parameters
        ----------
        casename : str
            数据集的名称，用于指定文件路径
        '''
        self.casename = casename

    def mkdir(self, path):
        '''创建目录
        判断路径是否存在，如果不存在则创建。

        Parameters
        ----------
        path : str
            需要创建的目录路径
        '''
        folder = os.path.exists(path)
        if not folder:
            os.makedirs(path)
            print("new folder")
        else:
            print("There is this folder")

    def csvtodata(self):
        '''将CSV文件中的地址转化为编号，并存储映射关系

        该方法读取原始交易数据，生成`from`和`to`地址的编号映射，并保存为文件。

        Returns
        -------
        dict_from : dict
            从地址到编号的映射字典
        dict_to : dict
            到地址到编号的映射字典
        '''
        csv_path = f'./inputData/AML/{self.casename}/all-normal-tx.csv'
        raw_data = pd.read_csv(csv_path)

        dict_from = {}
        dict_to = {}
        relation = []
        count_from = 0
        count_to = 0

        print('读取交易完成\n')
        self.datasetoverview()
        print('构建序号地址映射')

        for idx, data in raw_data.iterrows():
            if data['value'] == 0.0:  # 过滤交易金额为0的记录
                continue
            getFrom = data['from']
            getTo = data['to']

            # 构建from和序号的映射
            if getFrom not in dict_from:
                dict_from[getFrom] = count_from
                count_from += 1
            # 构建to和序号的映射
            if getTo not in dict_to:
                dict_to[getTo] = count_to
                count_to += 1
            relation.append([dict_from[getFrom], dict_to[getTo]])

        print('完成构建序号地址映射')

        # 排序和去重
        relation.sort()
        relation_new = []
        relation_new.append(relation[0])
        new_count = 1

        for i in relation:
            if i != relation_new[new_count - 1]:
                relation_new.append(i)
                new_count += 1

        # 保存映射文件
        print('存储numadd关系文件...\n')
        new_dict_from = dict(zip(dict_from.values(), dict_from.keys()))
        new_dict_to = dict(zip(dict_to.values(), dict_to.keys()))

        self.mkdir(f'data/{self.casename}/')

        dict_from_path = f'./inputData/AML/data/{self.casename}/all-normal-tx_from.txt'
        dict_to_path = f'./inputData/AML/data/{self.casename}/all-normal-tx_to.txt'

        with open(dict_from_path, 'w') as f:
            f.write(str(sorted(new_dict_from.items())))
        with open(dict_to_path, 'w') as f:
            f.write(str(sorted(new_dict_to.items())))

        # 输出关系文件
        relation_count = pd.value_counts(relation)
        edgef, edget, edgenum = [], [], []

        for d, v in relation_count.items():
            edgef.append(d[0])
            edget.append(d[1])
            edgenum.append(v)

        relationship = {'edgef': edgef, 'edget': edget}
        relationship_df = pd.DataFrame.from_dict(relationship)
        relationship_df.to_csv(f'./inputData/AML/{self.casename}/all-normal-tx_fraudar.csv', header=0, index=False)

        txtname = f'./inputData/AML/data/{self.casename}/all-normal-tx_count.txt'
        with open(txtname, 'w') as f:
            for i in relation:
                f.write(f'{i[0]} {i[1]}\n')

    def myReadData(self, path):
        '''读取映射关系文件

        Parameters
        ----------
        path : str
            映射文件路径

        Returns
        -------
        dict
            映射关系字典
        '''
        with open(path, 'r') as f:
            data = eval(f.read())
        return data

    def num_to_addr(self):
        '''获取从编号到地址的映射

        Returns
        -------
        dict_from : dict
            从编号到地址的映射字典
        dict_to : dict
            到编号到地址的映射字典
        '''
        dict_from_path = f'./inputData/AML/data/{self.casename}/all-normal-tx_from.txt'
        dict_to_path = f'./inputData/AML/data/{self.casename}/all-normal-tx_to.txt'
        dict_from = self.myReadData(dict_from_path)
        dict_to = self.myReadData(dict_to_path)
        return dict_from, dict_to

    def addr_to_num(self):
        '''获取从地址到编号的映射

        Returns
        -------
        new_dict_from : dict
            从地址到编号的映射字典
        new_dict_to : dict
            到地址到编号的映射字典
        '''
        dict_from, dict_to = self.num_to_addr()
        dict_from = np.array(list(dict_from.items()))
        dict_to = np.array(list(dict_to.items()))

        new_dict_from = dict(zip(dict_from[:, 1], dict_from[:, 0]))
        new_dict_to = dict(zip(dict_to[:, 1], dict_to[:, 0]))
        return new_dict_from, new_dict_to

    def saveaddr(self, ifrows, data):
        '''保存运算结果的实际地址

        Parameters
        ----------
        ifrows : bool
            如果为True，保存为行数据
        data : list
            要保存的数据列表
        '''
        dict_from, dict_to = self.num_to_addr()
        path = f'out/{self.casename}_result'

        if ifrows:
            path += '_rows.txt'
            with open(path, 'w') as f:
                for i in data:
                    f.write(f'{dict_from[i]}\n')
        else:
            path += '_cols.txt'
            with open(path, 'w') as f:
                for i in data:
                    f.write(f'{dict_to[i]}\n')

    def fraud_tran(self):
        '''根据标签设置点的权重，并保存运算结果

        获取与诈骗相关的交易，并将结果保存为Excel文件。
        '''
        from_n2a, to_n2a = self.num_to_addr()

        out_path = "./Fraudar_output/"
        file_name = f'{self.casename}_out/'

        frow = open(out_path + file_name + '_0.rows', "r")
        fcol = open(out_path + file_name + '_0.cols', "r")
        linecols = fcol.readlines()
        linerows = frow.readlines()

        numcol, numrow = [], []
        for line in linecols:
            numcol.append(int(line))
        for line in linerows:
            numrow.append(int(line))

        addcol, addrow = [], []
        for col, row in zip(numcol, numrow):
            rowadd = from_n2a[row]
            coladd = to_n2a[col]
            addcol.append(list(coladd)[1])
            addrow.append(list(rowadd)[1])

        a2 = pd.DataFrame(addcol, columns=['to_heist'])
        a1 = pd.DataFrame(addrow, columns=['from_heist'])
        a3 = pd.DataFrame(addcol + addrow, columns=['all_heist'])

        a3.drop_duplicates(inplace=True)

        writer = pd.ExcelWriter(out_path + file_name + 'fraudar_heist.xlsx')
        a1.to_excel(writer, 'Sheet1')
        a2.to_excel(writer, 'Sheet2')
        a3.to_excel(writer, 'Sheet3')
        writer.save()
        writer.close()

    def datasetoverview(self):
        '''输出数据集的基本概况

        显示交易数据集的账户数、交易金额、时间跨度等基本信息。
        '''
        csv_path = f'./inputData/AML/{self.casename}/all-normal-tx.csv'
        raw_data = pd.read_csv(csv_path)
        raw_data[['value']] = raw_data[['value']].astype(float)
        raw_data[['timeStamp']] = raw_data[['timeStamp']].astype(float)

        print("数据集概况:")
        print('账户数', len(set(raw_data['from'])))
        print('交易笔数', len(raw_data))
        print('金额总数', raw_data['value'].sum())
        print('时间跨度', int(time.time()) - int(raw_data['timeStamp'].min()))
