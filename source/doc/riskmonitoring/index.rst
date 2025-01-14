风险监测
=================================

1. 模块介绍
----------------------------

本平台中的区块链风险监测算法模块，旨在通过先进的算法技术，对区块链网络中的各类风险行为进行精准监测与识别。

该模块涵盖了钓鱼团伙检测、反洗钱AML以及庞氏骗局检测等多个关键领域，汇集了领域内相关前沿论文呢，为维护区块链生态的安全与稳定提供了多视角的技术参考。

2. 反洗钱AML
----------------------------
- **论文**：*DenseFlow: Spotting Cryptocurrency Money Laundering in Ethereum Transaction Graphs*

- **作者**：Dan Lin, Jiajing Wu, Yunmei Yu, Qishuang Fu, Zibin Zheng, Changlin Yang

- **发表**：Proceedings of the ACM Web Conference 2024 (WWW ’24), May 13–17, 2024, Singapore, Singapore

- **链接**：https://dl.acm.org/doi/10.1145/3589334.3645692

- **源代码**：https://github.com/DenseFlow/DenseFlow_Tool

**论文内容介绍：**

近年来，区块链上的洗钱犯罪行为日益猖獗，尤其是在以太坊上，给金融系统带来了巨大损失。以太坊洗钱活动的去中心化和匿名性等特点，为监管机构识别可疑账户和追踪资金流向带来了新的挑战。本文提出了一个创新的**DenseFlow**框架，通过寻找密集子图并应用最大流思想，有效识别和追踪洗钱活动。

首先分析以太坊洗钱活动的可测量特征，如密集转移、时间激增、金额强度和评级偏差等，然后基于这些特征设计相关可疑性度量指标，并提出了一个贪婪近似算法来寻找最大化可疑性度量的子图。最后，利用最大流算法补充洗钱路径上的相关账户。

通过在四个以太坊真实事件数据集上的实验验证，**DenseFlow**的精确度比现有最佳比较方法平均高出16.34%，在区块链反洗钱领域具有重要的应用价值。

3. 钓鱼团伙检测
----------------------------
- **论文**：*Fishing for Fraudsters: Uncovering Ethereum Phishing Gangs With Blockchain Data*

- **作者**：Jieli Liu, Jinze Chen, Jiajing Wu, Zhiying Wu, Junyuan Fang, Zibin Zheng

- **发表**：IEEE Transactions on Information Forensics and Security, VOL. 19, 2024

- **链接**：https://ieeexplore.ieee.org/document/9767892

- **源代码**：https://github.com/JerryLiu66/PGDetector

**论文内容介绍：**

随着区块链技术的快速发展，以太坊等区块链系统成为了钓鱼诈骗等网络犯罪的新目标。传统的钓鱼检测方法通常只能识别单个钓鱼账户，而无法有效揭露与诈骗相关的交易账户群体（即“团伙”）。文章首次对以太坊钓鱼团伙的交易行为进行了深入研究，从个体、成对以及高阶模式等多个角度进行分析，发现同一团伙内的钓鱼账户之间存在更紧密的交易关系和特定的交易模式。

文章提出了**PGDetector**新型检测模型，该模型以一个已知的高风险钓鱼账户作为种子，通过遗传算法优化，找出与种子账户关系密切的潜在风险账户。

实验结果表明，**PGDetector**在大规模以太坊交易数据上的有效性，能够有效识别出隐藏在区块链网络中的钓鱼团伙，为防范和打击此类网络犯罪提供了有力工具。


4. 庞氏骗局检测
----------------------------
- **论文**：*PonziGuard: Detecting Ponzi Schemes on Ethereum with Contract Runtime Behavior Graph (CRBG)*

- **作者**：Ruichao Liang, Jing Chen, Kun He, Yueming Wu, Gelei Deng, Ruiying Du, Cong Wu

- **发表**：2024 IEEE/ACM 46th International Conference on Software Engineering (ICSE ’24), April 14–20, 2024, Lisbon, Portugal

- **链接**：https://doi.org/10.1145/3597503.3623318

- **源代码**：https://github.com/PonziDetection/PonziGuard

**论文内容介绍：**

庞氏骗局作为一种常见的诈骗形式，在以太坊智能合约中也频繁出现，给投资者带来了巨大的经济损失。传统的基于规则的检测方法依赖于预定义的规则，存在能力有限和领域知识依赖的问题。而使用静态信息如操作码和交易数据的机器学习模型，也无法有效刻画庞氏合约的特征，导致可靠性与可解释性较差。

文章提出**PonziGuard**是一种基于合约运行时行为的高效庞氏骗局检测方法。通过构建一个全面的图表示——合约运行时行为图（CRBG），准确描绘庞氏合约的行为，并将检测过程形式化为图分类任务，显著提高了检测效果。

通过在真实数据集上的比较实验以及在以太坊主网上的应用，结果表明**PonziGuard**优于当前最先进的方法，并且在开放环境中也表现出色。利用**PonziGuard**，研究者在以太坊主网上识别出了805个庞氏合约，估计造成的经济损失高达281,700个以太币，约合5亿美元。

5. 代码模块
----------------------------
.. toctree::
   :maxdepth: 3
   :caption: riskmonitoring

   denseflow/index
   ponziguard/index
   pgdector/index
