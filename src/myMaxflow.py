


class MaxFlowGraph:
    """
    该类用于构建和处理交易图，使用最大流算法计算源节点与目标节点之间的最大流。
    """

    def mkdir(self, path):
        """
        创建目录，如果目录不存在则创建。

        Parameters:
        path (str): 需要创建的目录路径。

        Returns:
        None
        """
        folder = os.path.exists(path)
        if not folder:  # 判断是否存在文件夹，如果不存在则创建文件夹
            os.makedirs(path)  # 创建文件夹
            print("new folder")
        else:
            print("There is this folder")


    def build_g(self, casename):
        """
        构建交易图，其中每个节点表示一个交易地址，边表示从一个地址到另一个地址的交易。

        Parameters:
        casename (str): 案件名称，用于读取特定文件中的交易数据。

        Returns:
        tuple: start_nodes, end_nodes, capacities, nodenum
            - start_nodes (np.array): 交易起始节点列表
            - end_nodes (np.array): 交易结束节点列表
            - capacities (np.array): 每条边的容量（交易金额）
            - nodenum (dict): 地址与节点编号的映射
        """
        datatu = pd.read_csv(f'./inputData/AML/{casename}/all-normal-tx.csv')
        row = datatu.iloc[:, 0].size
        nodelist = []
        nodenum = {}
        number = 0
        start_nodes = []
        end_nodes = []
        capacities = []
        print('构造图ing')

        for i in range(row):
            # 构建节点列表：
            addf = datatu.iloc[i, 1]  # 交易的起始地址
            addt = datatu.iloc[i, 2]  # 交易的目标地址

            # 如果当前地址未加入图中：
            if addf not in nodelist:
                nodelist.append(addf)
                number += 1
                nodenum[addf] = number

            if addt not in nodelist:
                nodelist.append(addt)
                number += 1
                nodenum[addt] = number

            money = float(datatu.iloc[i, 3]) * 1e-18  # 转换为以太币的金额

            # 筛选部分交易，排除掉无效的交易
            if datatu.loc[i, 'isError'] == 0:  # 只处理有效交易
                if nodenum[addf] != nodenum[addt] and money != 0.0:
                    # 不考虑自己转给自己的交易和金额为0的交易
                    start_nodes.append(nodenum[addf])
                    end_nodes.append(nodenum[addt])
                    capacities.append(money)

        start_nodes = np.array(start_nodes)
        end_nodes = np.array(end_nodes)
        capacities = np.array(capacities)

        nodeadd = {k: v for v, k in nodenum.items()}
        print("完成构建图，节点数：", number, "边数：", len(capacities))

        gpath = './Maxflow_graph/' + casename + '/'
        self.mkdir(gpath)

        # 保存图的数据
        np.save(gpath + 'start_nodes.npy', start_nodes)
        np.save(gpath + 'end_nodes.npy', end_nodes)
        np.save(gpath + 'capacities.npy', capacities)
        np.save(gpath + 'nodenum.npy', nodenum)

        return start_nodes, end_nodes, capacities, nodenum


    def read_g(self, casename):
        """
        读取已保存的交易图数据。

        Parameters:
        casename (str): 案件名称，用于从文件中读取图数据。

        Returns:
        tuple: start_nodes, end_nodes, capacities, nodenum
            - start_nodes (list): 交易起始节点列表
            - end_nodes (list): 交易结束节点列表
            - capacities (list): 每条边的容量（交易金额）
            - nodenum (dict): 地址与节点编号的映射
        """
        print('已完成构建，读取图ing')
        gpath = './Maxflow_graph/' + casename + '/'
        start_nodes = np.load(gpath + 'start_nodes.npy')
        start_nodes = start_nodes.tolist()
        end_nodes = np.load(gpath + 'end_nodes.npy')
        end_nodes = end_nodes.tolist()
        capacities = np.load(gpath + 'capacities.npy')
        capacities = capacities.tolist()
        nodenum = np.load(gpath + 'nodenum.npy', allow_pickle=True).item()
        print('读取完成')
        return start_nodes, end_nodes, capacities, nodenum


    def find_s_t(self, t, s, start_nodes, end_nodes, capacities, p=True):
        """
        使用最大流算法计算从源节点 `s` 到终点节点 `t` 的最大流。

        Parameters:
        t (int): 目标节点编号
        s (int): 源节点编号
        start_nodes (list): 交易起始节点列表
        end_nodes (list): 交易结束节点列表
        capacities (list): 每条边的容量（交易金额）
        p (bool): 是否打印详细信息

        Returns:
        list: [status, max_flow, level]
            - status (int): 计算状态，1表示成功
            - max_flow (float): 最大流的值
            - level (int): 流的层次
        """
        smf = max_flow.SimpleMaxFlow()
        all_arcs = smf.add_arcs_with_capacity(start_nodes, end_nodes, capacities)

        # 求解最大流
        status = smf.solve(s, t)

        if status != smf.OPTIMAL:
            print('There was an issue with the max flow input.')
            print(f'Status: {status}')
            return [1, smf.optimal_flow(), -3]

        if smf.optimal_flow() != 0:
            level = 0  # 可忽略，不再使用
            if p:  # 输出详细信息
                print('Max flow:', smf.optimal_flow())
                print(' Arc    Flow / Capacity')
            solution_flows = smf.flows(all_arcs)
            for arc, flow, capacity in zip(all_arcs, solution_flows, capacities):
                if flow != 0:  # 只输出非零流量的边
                    if p:
                        print(f'{smf.tail(arc)} / {smf.head(arc)}   {flow:3}  / {capacity:3}')
                    level += 1

            return [1, smf.optimal_flow(), level]
        else:
            return [0, 0, 0]


    def find_s_t_address(self, t, s, start_nodes, end_nodes, capacities):
        """
        与 `find_s_t` 类似，但此函数返回流动链路中的地址。

        Parameters:
        t (int): 目标节点编号
        s (int): 源节点编号
        start_nodes (list): 交易起始节点列表
        end_nodes (list): 交易结束节点列表
        capacities (list): 每条边的容量（交易金额）

        Returns:
        list: 包含地址的流动链路列表
        """
        smf = max_flow.SimpleMaxFlow()
        all_arcs = smf.add_arcs_with_capacity(start_nodes, end_nodes, capacities)

        status = smf.solve(s, t)
        flownum = []

        if status != smf.OPTIMAL:
            print('There was an issue with the max flow input.')
            print(f'Status: {status}')
            return flownum

        if smf.optimal_flow() != 0:
            level = 0
            solution_flows = smf.flows(all_arcs)

            for arc, flow, capacity in zip(all_arcs, solution_flows, capacities):
                if flow != 0:
                    if smf.tail(arc) not in flownum:
                        flownum.append(smf.tail(arc))
                    if smf.head(arc) not in flownum:
                        flownum.append(smf.head(arc))

            return flownum
        else:
            return flownum


    def output_flow_add(self, casename, k, level, sourceadd, Show=False, Save=True):
        """
        计算并输出最大流数据，并将结果保存为 Excel 文件。

        Parameters:
        casename (str): 案件名称
        k (int): 当前图的层级
        level (int): 当前处理的层级
        sourceadd (str): 源地址
        Show (bool): 是否打印详细信息
        Save (bool): 是否保存结果

        Returns:
        list: 包含流值的列表
        """
        print('当前正在运行：', casename, 'k=', k, 'level=', level)
        print('读取对应heist地址...')
        heist1 = pd.read_excel(f'./inputData/AML/{casename}/myheist_k_{k}.xlsx', sheet_name='Sheet' + str(level))

        # 输出贼地址
        node_heist1 = []
        if Show:
            print(f"筛选的贼地址：{heist1}")

        for i in range(len(heist1)):
            node_heist1.append(nodenum[heist1[i]])

        flows = []
        for i in range(len(node_heist1)):
            flownum = self.find_s_t_address(node_heist1[i], sourceadd, start_nodes, end_nodes, capacities)
            flows.append(flownum)

        if Save:
            # 保存每层计算结果
            path = f'./Maxflow_graph/{casename}/result_flow_k_{k}_level_{level}.xlsx'
            pd.DataFrame(flows).to_excel(path)

        return flows


def find_whole_flow(t, s, start_nodes, end_nodes, capacities, p=True):
    """
    计算从源节点s到目标节点t的最大流，并合并所有的流结果。

    参数:
    t (int): 目标节点的编号
    s (int): 源节点的编号
    start_nodes (list[int]): 所有起始节点的编号列表
    end_nodes (list[int]): 所有终止节点的编号列表
    capacities (list[float]): 每条边的容量
    p (bool): 控制是否打印详细的最大流信息，默认为True

    返回:
    wholeflow (dict): 一个字典，键为（起始节点，目标节点），值为流量。表示从源节点到目标节点的流量总和。
    """

    # 创建SimpleMaxFlow对象，初始化最大流计算器
    smf = max_flow.SimpleMaxFlow()

    # 将起始节点、目标节点和容量批量添加到最大流计算器中
    all_arcs = smf.add_arcs_with_capacity(start_nodes, end_nodes, capacities)

    # 计算从源节点s到目标节点t的最大流
    status = smf.solve(s, t)

    # 如果计算失败，输出错误信息并返回空字典
    if status != smf.OPTIMAL:
        print('There was an issue with the max flow input.')
        print(f'Status: {status}')
        return {}

    # 存储每条边的最终流量结果
    wholeflow = {}

    # 如果最大流不为零，进行结果的收集和输出
    if smf.optimal_flow() != 0:
        level = 0  # 记录源节点到当前节点的流量数目

        # 打印最大流信息（如果p为True）
        if p:
            print('Max flow:', smf.optimal_flow())
            print('')
            print(' Arc    Flow / Capacity')

        # 获取所有边的流量
        solution_flows = smf.flows(all_arcs)

        # 遍历每一条边，记录非零流量
        for arc, flow, capacity in zip(all_arcs, solution_flows, capacities):
            if flow != 0:  # 只考虑非零流量的边
                if p:
                    print(f'{smf.tail(arc)} / {smf.head(arc)}   {flow:3}  / {capacity:3}')

                # 如果该边已经在字典中，累加流量；否则新建键值对
                if (smf.tail(arc), smf.head(arc)) in wholeflow:
                    wholeflow[(smf.tail(arc), smf.head(arc))] += flow
                else:
                    wholeflow[(smf.tail(arc), smf.head(arc))] = flow

                level += 1  # 记录流量数量（可选）

    # 返回合并后的最大流结果
    return wholeflow
