


class myHoloscope:
    """myHoloscope 类用于处理AML数据，计算和输出Heist相关信息

    该类提供了数据预处理、可疑交易计算、图数据处理、以及结果输出功能。
    """

    def __init__(self, casename):
        """初始化myHoloscope类
        Parameters
        ----------
        casename : str
            数据集名称
        """
        self.casename = casename

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

    def Search_full_tranrecord(self, fromnumheist, tonumheist):
        """搜索完整的交易记录
        输入地址序号列表，返回与这些地址相关的完整交易记录。

        Parameters
        ----------
        fromnumheist : list
            从地址的序号列表
        tonumheist : list
            到地址的序号列表

        Returns
        -------
        pd.DataFrame
            包含相关交易记录的DataFrame
        """
        TR = pd.read_csv(f'./inputData/AML/{self.casename}/all-normal-tx_holo.csv')
        tr = pd.DataFrame(columns=TR.columns)
        d_f, d_t = holo.num_to_addr(self.casename)
        addr_f = [list(d_f[f])[1] for f in fromnumheist]
        addr_t = [list(d_t[t])[1] for t in tonumheist]

        for af in addr_f:
            af_tran = TR.loc[TR['0'] == af]
            tr = tr.append(af_tran)

        for at in addr_t:
            at_tran = TR.loc[TR['1'] == at]
            tr = tr.append(at_tran)

        return tr

    def outputheist(self, res, from_n2a, to_n2a):
        """输出Heist相关地址
        根据计算结果和映射关系返回Heist相关地址。

        Parameters
        ----------
        res : list
            计算结果
        from_n2a : dict
            地址到编号的映射字典
        to_n2a : dict
            编号到地址的映射字典

        Returns
        -------
        list
            Heist相关地址列表
        """
        R, C = [], []
        for r in res:
            rows, cols = r[0]
            R.extend(rows)
            C.extend(cols)

        add_h = []
        for rr, cc in zip(R, C):
            addtemp = list(from_n2a[rr])[1]
            if addtemp not in add_h:
                add_h.append(addtemp)
            addtemp = list(to_n2a[cc])[1]
            if addtemp not in add_h:
                add_h.append(addtemp)

        return add_h

    def build_hs(self, numSing=10):
        """构建HoloScope模型
        处理数据并返回构建的HoloScope实例。

        Parameters
        ----------
        numSing : int, optional
            单一事件的数量，默认值为10

        Returns
        -------
        hs : HoloScope
            构建好的HoloScope实例
        """
        print(f'现在正在进行案件 {self.casename} 的数据预处理...\n')
        print('读取数据')
        address = pd.read_csv(f'./inputData/AML/{self.casename}/all-normal-address.csv')
        heist = address.loc[address['label'] == 'heist']
        heist_address = heist['address'].tolist()
        from_a2n, to_a2n = holo.addr_to_num(self.casename)
        from_n2a, to_n2a = holo.num_to_addr(self.casename)

        print('处理数据')
        filePath = f'./inputData/AML/{self.casename}/all-normal-tx_holo.csv'
        tensor_data = st.loadTensor(path=filePath, header=None)
        tensor_data.data = tensor_data.data.drop(columns=[0]).drop([0])
        tensor_data.data.columns = [0, 1, 2, 3, 4]
        tensor_data.data[2] = tensor_data.data[2].str.replace('/', '-')

        stensor = tensor_data.toSTensor(hasvalue=True, mappers={2: st.TimeMapper(timeformat='%Y-%m-%d')})
        graph = st.Graph(stensor, bipartite=True, weighted=True, modet=2)
        hs = st.HoloScope(graph, numSing=numSing)

        print(f'{self.casename} 数据构造完毕')
        return hs

    def output_holo(self, k, hs):
        """输出HoloScope计算结果
        运行HoloScope并输出Heist相关地址和计算结果。

        Parameters
        ----------
        k : int
            输出级别
        hs : HoloScope
            已构建的HoloScope实例
        """
        t = time.time()
        res = hs.run(level=0, k=k)
        res1 = hs.run(level=1, k=k)
        res2 = hs.run(level=2, k=k)
        res3 = hs.run(level=3, k=k)
        res4 = hs.run(level=4, k=k)
        res5 = hs.run(level=5, k=k)
        res6 = hs.run(level=6, k=k)

        print(f'{self.casename} k={k} 7种运行总耗时：')
        print(f'cost: {time.time() - t:.8f}s namely: {((time.time() - t) / 60):.8f}min')

        from_a2n, to_a2n = holo.addr_to_num(self.casename)
        from_n2a, to_n2a = holo.num_to_addr(self.casename)
        add_h = self.outputheist(res, from_n2a, to_n2a)
        add_h1 = self.outputheist(res1, from_n2a, to_n2a)
        add_h2 = self.outputheist(res2, from_n2a, to_n2a)
        add_h3 = self.outputheist(res3, from_n2a, to_n2a)
        add_h4 = self.outputheist(res4, from_n2a, to_n2a)
        add_h5 = self.outputheist(res5, from_n2a, to_n2a)
        add_h6 = self.outputheist(res6, from_n2a, to_n2a)

        print('heist数量计算结果：', len(add_h), len(add_h1), len(add_h2), len(add_h3), len(add_h4), len(add_h5),
              len(add_h6))
        print('结果存储中')

        # 保存结果到Excel
        a = pd.DataFrame(add_h, columns=['heist0'])
        a1 = pd.DataFrame(add_h1, columns=['heist1'])
        a2 = pd.DataFrame(add_h2, columns=['heist2'])
        a3 = pd.DataFrame(add_h3, columns=['heist3'])
        a4 = pd.DataFrame(add_h4, columns=['heist4'])
        a5 = pd.DataFrame(add_h5, columns=['heist5'])
        a6 = pd.DataFrame(add_h6, columns=['heist6'])

        writer = pd.ExcelWriter(f'./inputData/AML/{self.casename}/myheist_k_{k}.xlsx')
        a.to_excel(writer, 'Sheet0')
        a1.to_excel(writer, 'Sheet1')
        a2.to_excel(writer, 'Sheet2')
        a3.to_excel(writer, 'Sheet3')
        a4.to_excel(writer, 'Sheet4')
        a5.to_excel(writer, 'Sheet5')
        a6.to_excel(writer, 'Sheet6')
        writer.close()
