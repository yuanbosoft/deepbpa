# -*- coding: utf-8 -*-




class CompareMethod:
    '''用于比较不同AML案件的数据处理方法
    本类封装了多种数据处理与模型运行方法，包括Fraudar、CubeFlow和Holoscope
    每个方法都有特定的处理逻辑和输出结果存储。

    Attributes
    ----------
    casename : str
        当前处理的案件名称
    '''

    def __init__(self, casename):
        '''初始化方法，接收案件名称'''
        self.casename = casename

    def mkdir(self, path):
        '''创建文件夹方法
        如果路径不存在，则创建该路径

        Parameters
        ----------
        path : str
            需要创建的文件夹路径
        '''
        folder = os.path.exists(path)
        if not folder:  # 判断是否存在文件夹
            os.makedirs(path)  # 创建文件夹
            print("new folder")
        else:
            print("There is this folder")

    def fraudar(self):
        '''Fraudar方法
        该方法用于运行Fraudar模型并保存结果。

        Parameters
        ----------
        casename : str
            当前处理的案件名称
        '''
        filePath = f'./inputData/AML/{self.casename}/all-normal-tx_fraudar.csv'

        # 加载图数据
        tensor = st.loadTensor(path=filePath)
        stensor = tensor.toSTensor(hasvalue=False)
        fd = st.Fraudar(stensor)

        # 运行模型
        out_path = "./Fraudar_output/"
        file_name = self.casename + "_out/"
        self.mkdir(out_path + file_name)

        res = fd.run(k=10, out_path=out_path, file_name=file_name, maxsize=[100, 100])
        dt.fraud_tran(self.casename)
        print('完成fraudar结果转换与存储')

    def cubeflow(self):
        '''CubeFlow方法
        该方法用于运行CubeFlow模型并保存结果。

        Parameters
        ----------
        casename : str
            当前处理的案件名称
        '''
        print("案件", self.casename, '\n')

        xy_path = f'./inputData/AML/{self.casename}/all-normal-tx-cube_xy.csv'
        zy_path = f'./inputData/AML/{self.casename}/all-normal-tx-cube_zy.csv'

        out_path = f"./CubeFlow_output/{self.casename}_out/"
        file_name = self.casename + "_cubeflow.txt"

        self.mkdir(out_path)

        amt_tensor = st.loadTensor(path=xy_path, header=None)
        cmt_tensor = st.loadTensor(path=zy_path, header=None)

        amt_stensor = amt_tensor.toSTensor(hasvalue=True)
        cmt_stensor = cmt_tensor.toSTensor(hasvalue=True)

        cf = st.CubeFlow([amt_stensor, cmt_stensor], alpha=0.2, k=10, dim=3, outpath=out_path)

        res = cf.run(del_type=1, maxsize=-1)
        print("案件", self.casename, '完成cubeflow\n')

        n2aA, n2aH, n2aB = cube.num_to_addr(self.casename)
        print(len(n2aA), len(n2aH), len(n2aB))

        cube_heist = []
        for num in res[0][0][0]:
            cube_heist.append(n2aA[num][1])
        for num in res[0][0][1]:
            cube_heist.append(n2aH[num][1])
        for num in res[0][0][2]:
            cube_heist.append(n2aB[num][1])

        a1 = pd.DataFrame(cube_heist, columns=['heist'])
        file_name = self.casename + "_cubehseit.csv"
        outpath = out_path + file_name
        self.mkdir(out_path)

        a1.to_csv(outpath, index=False)
        print("案件", self.casename, '完成cubeflow存储\n')

    def holoscope(self, k, level):
        '''Holoscope方法
        该方法用于运行Holoscope模型并保存结果。

        Parameters
        ----------
        casename : str
            当前处理的案件名称
        k : int
            用于Holoscope模型的参数k
        level : int
            模型的层级
        '''
        print(self.casename)
        filePath = f'./inputData/AML/{self.casename}/all-normal-tx_holo.csv'
        tensor_data = st.loadTensor(path=filePath, header=None)

        # 格式化数据
        tensor_data.data = tensor_data.data.drop(columns=[0])
        tensor_data.data = tensor_data.data.drop([0])
        tensor_data.data.columns = [0, 1, 2, 3, 4]
        tensor_data.data[2] = tensor_data.data[2].str.replace('/', '-')

        stensor = tensor_data.toSTensor(hasvalue=True, mappers={2: st.TimeMapper(timeformat='%Y-%m-%d')})
        graph = st.Graph(stensor, bipartite=True, weighted=True, modet=2)
        hs = st.HoloScope(graph, numSing=10)

        res = hs.run(level=level, k=k)
        from_n2a, to_n2a = holo.num_to_addr(self.casename)

        add_h_1 = []
        R1 = []
        C1 = []
        for r in res:
            rows, cols = r[0]
            print(rows, cols)

            # 转换子图
            for rr in rows:
                R1.append(rr)
                addtemp = list(from_n2a[rr])[1]
                if addtemp not in add_h_1:
                    add_h_1.append(addtemp)
            for cc in cols:
                C1.append(cc)
                addtemp = list(to_n2a[cc])[1]
                if addtemp not in add_h_1:
                    add_h_1.append(addtemp)

        a1 = pd.DataFrame(add_h_1, columns=['heist1'])
        out_path = f'./Holoscope_output/{self.casename}_out/'
        file_name = f'{self.casename}_hs_level_{level}.csv'
        outpath = out_path + file_name
        self.mkdir(out_path)

        a1.to_csv(outpath, index=False)
        print('Holoscope完成')
