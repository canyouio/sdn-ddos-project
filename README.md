# SDN-DDoS-Project: 基于软件定义网络（SDN）的DDoS攻击检测与防御系统

这是一个利用机器学习和软件定义网络（SDN）技术来检测和缓解分布式拒绝服务（DDoS）攻击的项目。系统通过实时分析网络流量，能够自动识别恶意流量并采取相应措施，以保护网络服务的可用性。

---

## 目录
- [项目简介](#项目简介)
- [核心功能](#核心功能)
- [技术架构](#技术架构)
- [工作原理](#工作原理)
- [如何运行](#如何运行)
- [项目结构](#项目结构)
- [贡献](#贡献)
- [许可证](#许可证)

---

## 📝 项目简介

随着网络技术的发展，分布式拒绝服务（DDoS）攻击已成为网络安全的主要威胁之一。 传统的网络架构在应对复杂和大规模的DDoS攻击时显得力不从心。软件定义网络（SDN）提供了一种创新的网络架构，它将网络的控制平面与数据平面分离，实现了对网络流量的集中式控制和可编程性，这为防御DDoS攻击提供了新的思路。

本项目旨在构建一个智能、自动化的DDoS防御系统。该系统部署在SDN控制器上，通过收集网络中的流表信息和数据包特征，利用机器学习算法训练模型以区分正常流量和异常攻击流量。 一旦检测到DDoS攻击，系统会迅速响应，通过控制器下发流规则到交换机，从而精确地阻断或限制恶意流量。

---

## ✨ 核心功能

*   **实时流量监控**: 从SDN交换机周期性地收集流统计信息。
*   **智能攻击检测**: 采用多种机器学习算法（如SVM, K-NN, 决策树等）进行流量分类，以高准确率识别DDoS攻击。
*   **自动化防御**: 一旦确认攻击，系统会自动生成并下发流规则至底层交换机，以实现对攻击流量的快速缓解。
*   **集中式管理**: 基于SDN的集中控制特性，提供对整个网络状态的全局视图，简化了安全策略的部署。
*   **可扩展性**: 模块化设计，方便集成新的检测算法或自定义防御策略。

---

## 🚀 技术架构

*   **网络模拟器**: **Mininet** - 用于创建和模拟SDN拓扑，包括交换机、主机和它们之间的链接。
*   **SDN 控制器**: **Ryu / POX** - 作为网络的大脑，负责处理网络事件、收集数据并执行防御逻辑。
*   **机器学习库**: **Scikit-learn** - 用于训练和评估攻击检测模型。
*   **编程语言**: **Python**

---

## ⚙️ 工作原理

系统的运行主要分为以下几个模块：

1.  **流量收集模块 (Flow Collector)**:
    该模块周期性地向网络中的OpenFlow交换机发送请求，收集每个活动流的统计数据，例如数据包数量、字节数、持续时间等。

2.  **特征提取模块 (Feature Extractor)**:
    从收集到的原始流数据中，提取出用于机器学习模型训练和预测的关键特征。这些特征可能包括源IP地址的速度、流条目的增长速度、协议分布等。

3.  **异常检测模块 (Anomaly Detection)**:
    这是系统的核心。它使用预先训练好的机器学习模型对提取出的特征进行分析。模型将实时流量分类为“正常”或“异常（DDoS攻击）”。

4.  **攻击缓解模块 (Anomaly Mitigation)**:
    当检测模块识别出攻击后，该模块被激活。它会确定攻击源，并生成相应的流规则（例如，丢弃来自特定IP地址的数据包），然后通过SDN控制器将这些规则安装到交换机上，从而阻止攻击流量到达目标主机。

---

## ▶️ 如何运行

**环境要求**:
*   Ubuntu 20.04 或更高版本
*   Python 3.x
*   Mininet
*   Ryu SDN Controller
*   Scikit-learn, Pandas, NumPy

**安装与启动步骤**:

1.  **克隆项目仓库**:
    ```bash
    git clone https://github.com/your-username/sdn-ddos-project.git
    cd sdn-ddos-project
    ```

2.  **安装依赖**:
    ```bash
    pip install -r requirements.txt
    ```

3.  **启动SDN控制器**:
    打开一个新的终端，运行检测与防御应用程序。
    ```bash
    ryu-manager your_application.py
    ```

4.  **创建网络拓扑**:
    打开另一个终端，使用Mininet创建虚拟网络拓扑。
    ```bash
    sudo mn --controller=remote,ip=127.0.0.1 --mac -i 10.0.0.0/8 --switch=ovsk,protocols=OpenFlow13 --topo=linear,4
    ```

5.  **生成流量/模拟攻击**:
    使用`hping3`等工具在Mininet主机之间生成正常流量和DDoS攻击流量，以测试系统的检测和防御效果。

---

## 📁 项目结构
```
/sdn-ddos-project
|-- controller_app/
| |-- main_app.py # Ryu 控制器应用主文件
| |-- flow_collector.py # 流量收集模块
| |-- feature_extractor.py# 特征提取模块
| |-- detection_module.py # 攻击检测模块
| |-- mitigation_module.py# 攻击缓解模块
|-- machine_learning/
| |-- model.pkl # 训练好的机器学习模型
| |-- dataset.csv # 训练数据集
| |-- train_model.py # 模型训练脚本
|-- mininet_topology/
| |-- custom_topo.py # 自定义网络拓扑脚本
|-- requirements.txt # Python依赖项
|-- README.md # 项目说明文件
```

---

## 🤝 贡献

欢迎对此项目感兴趣的开发者进行贡献！您可以通过以下方式参与：
*   Fork 本项目
*   创建您的功能分支 (`git checkout -b feature/AmazingFeature`)
*   提交您的更改 (`git commit -m 'Add some AmazingFeature'`)
*   推送到分支 (`git push origin feature/AmazingFeature`)
*   提交一个 Pull Request

---

## 📄 许可证

本项目采用 MIT 许可证。详情请见 `LICENSE` 文件。
