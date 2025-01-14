class PonziGuard:
    """
    PonziGuard 核心功能类
    提供智能合约加载、特征提取、检测和批量处理的功能。

    Attributes
    ----------
    rpc_url : str
        区块链节点的 RPC URL，用于访问智能合约。
    """

    def __init__(self, rpc_url):
        """
        初始化 PonziGuard 实例。

        Parameters
        ----------
        rpc_url : str
            区块链节点的 RPC URL。
        """
        self.rpc_url = rpc_url

    def load_contract(self, address):
        """
        从区块链加载智能合约字节码。

        Parameters
        ----------
        address : str
            智能合约地址。

        Returns
        -------
        str
            智能合约字节码。

        Raises
        ------
        RuntimeError
            如果合约加载失败或节点不可用。
        """
        from web3 import Web3

        try:
            web3 = Web3(Web3.HTTPProvider(self.rpc_url))
            if not web3.isConnected():
                raise ConnectionError("无法连接到区块链节点")

            bytecode = web3.eth.get_code(Web3.to_checksum_address(address))
            if bytecode == b'':
                raise ValueError(f"未找到合约 {address}")

            return bytecode.hex()
        except Exception as e:
            raise RuntimeError(f"加载合约失败: {str(e)}")

    def extract_features(self, bytecode):
        """
        从智能合约字节码中提取特征。

        Parameters
        ----------
        bytecode : str
            智能合约的字节码。

        Returns
        -------
        dict
            特征字典，包括调用图、资金流动和循环模式。
        """
        features = {}
        features['call_graph'] = self.analyze_call_graph(bytecode)
        features['fund_flow'] = self.analyze_fund_flow(bytecode)
        features['loop_patterns'] = self.detect_loops(bytecode)
        return features

    def analyze_call_graph(self, bytecode):
        """
        分析字节码中的函数调用关系。

        Parameters
        ----------
        bytecode : str
            智能合约的字节码。

        Returns
        -------
        dict
            调用图统计信息。
        """
        import re
        call_pattern = re.compile(r"CALL")
        call_count = len(call_pattern.findall(bytecode))
        return {"total_calls": call_count}

    def analyze_fund_flow(self, bytecode):
        """
        检测资金流动模式，例如是否符合庞氏结构。

        Parameters
        ----------
        bytecode : str
            智能合约的字节码。

        Returns
        -------
        str
            资金流动模式，可能值为 "pyramid_structure" 或 "normal"。
        """
        if "PUSH1" in bytecode and "CALLVALUE" in bytecode:
            return "pyramid_structure"
        return "normal"

    def detect_loops(self, bytecode):
        """
        检测字节码中是否存在循环模式。

        Parameters
        ----------
        bytecode : str
            智能合约的字节码。

        Returns
        -------
        list
            检测到的循环模式列表。
        """
        loop_patterns = []
        if "JUMP" in bytecode and "JUMPDEST" in bytecode:
            loop_patterns.append("simple_loop")
        if "RECURSION" in bytecode:
            loop_patterns.append("recursive_investment")
        return loop_patterns

    def detect_ponzi_scheme(self, features):
        """
        检测智能合约是否为庞氏骗局。

        Parameters
        ----------
        features : dict
            智能合约提取的特征。

        Returns
        -------
        bool
            True 表示检测为庞氏骗局，否则为 False。
        """
        if features['fund_flow'] == "pyramid_structure":
            return True
        if "recursive_investment" in features['loop_patterns']:
            return True
        if features['call_graph']['total_calls'] > 100:  # 示例阈值
            return True
        return False

    def batch_detect(self, addresses):
        """
        批量检测多个智能合约。

        Parameters
        ----------
        addresses : list
            智能合约地址列表。

        Returns
        -------
        dict
            每个地址的检测结果。
        """
        results = {}
        for address in addresses:
            try:
                bytecode = self.load_contract(address)
                features = self.extract_features(bytecode)
                is_ponzi = self.detect_ponzi_scheme(features)
                results[address] = "庞氏骗局" if is_ponzi else "安全"
            except Exception as e:
                results[address] = f"检测失败: {str(e)}"
        return results
