# 基于 RAG+LangGraph-Agent 企业知识库智能问答系统

> 🔥 企业级轻量化知识库问答解决方案 | 多层级权限管控 | 增强型混合检索 RAG | 多工具智能 Agent | 全链路日志监控 | Docker 容器化部署





------

## 📌 项目简介



本项目是一套**集权限管理、私有化知识库、混合增强 RAG、多功能智能 Agent、会话持久化、全局异常治理**于一体的综合性大模型应用系统。

依托 LangGraph 构建智能 Agent 核心能力，结合 Milvus 向量数据库、MySQL 关系型数据库、Redis 缓存中间件，打造**高精准、高可控、可扩展**的私有文档问答平台。

系统支持**管理员 / 普通用户双层权限体系**，搭载自研「父子切块存储 + 问题改写 + 向量 & 关键词混合检索 + 重排过滤」全链路 RAG 优化策略；

Agent 集成联网搜索、时间获取等拓展工具，打破大模型知识时效性限制；

全站实现身份鉴权、分段流式输出、会话分层存储、分类日志管理、全局异常捕获，整体架构标准化、工程化程度高，满足中小型企业私有化部署、内部知识库问答、智能客服等业务场景。





------

## 📂 项目目录结构解析

text

```
NEW_RAG/
├── admin/                       # 管理员后台模块
│   └── user_manage_main.py      # 用户管理核心代码（增删改查）
├── agent/                       # LangGraph 智能 Agent 模块
│   ├── agent.py                 # Agent 核心逻辑
│   ├── agent_prompt.txt         # Agent 系统提示词配置
│   ├── middleware.py            # 会话中间件（鉴权、日志、异常处理）
│   └── tool.py                  # Agent 工具注册与调用（rag、联网搜索、时间工具）
├── ai_search_online/            # 联网搜索工具模块
│   └── search_online.py         # 全网实时搜索能力核心代码
├── config/                      # 项目配置文件
│   ├── agent.yaml               # Agent 运行参数配置
│   └── rag.yaml                 # RAG 检索参数配置
├── knowledge_base/              # 知识库管理模块
│   ├── file_handler.py          # 文件上传、解析、分块处理
│   └── vector_store.py          # Milvus 向量库操作核心代码
├── logs/                        # 分级日志目录
│   ├── admin_logs/              # 管理员操作日志
│   ├── agent_logs/              # Agent 运行日志
│   └── knowledge_base_logs/     # 知识库操作日志以及rag检索日志
├── mysql_handler/               # MySQL 持久化模块
│   ├── user_chat_history.py     # 用户全量聊天记录存储
│   ├── user_handler.py          # 用户信息数据库管理操作
│   ├── user_login.py            # 用户登录鉴权
│   ├── user_stored_file.py      # 知识库文件台账管理
│   └── user_stored_parent_chunk.py # 父级文本块持久化
├── rag/                         # 增强型 RAG 检索模块
│   ├── rag.py                   # RAG 主流程核心代码
│   └── vector_retrieve.py       # 片段检索以及优化核心代码
├── redis_handler/               # Redis 缓存模块
│   ├── user_cache_history.py    # 最近5轮会话缓存
│   └── user_often_query.py      # 高频问题缓存加速
├── utils/                       # 通用工具模块
│   ├── config_handler.py        # 加载配置项工具
│   ├── load_prompt              # 加载提示词工具
│   ├── logger_handler           # 配置日志的工具
│   └── path_tool.py             # 获取路径的工具
│── admin_handler_app.py         # 管理员后台接口
│── agent_chat_app.py            # Agent 对话接口
│── upload_fie_app.py            # 文件上传接口
└── README.md                    # 项目说明文档
└── requirements.txt             # 核心依赖
```

------





## 🧩 整体核心模块

1. **管理员权限后台模块**
2. **用户登录与身份鉴权模块**
3. **增强型 RAG 知识库检索模块**
4. **多工具协同智能 Agent 问答模块**
5. **分层数据存储中间件模块**
6. **全局异常处理 & 分级日志运维模块**





------

## ✨ 核心功能详细介绍



### 🔐 一、双层权限管理体系

严格划分角色权限，做到功能隔离、安全可控：

- **管理员专属后台**

  仅指定超级管理员账号可登录访问，提供完整用户管理能力：

  新增用户、删除用户、修改信息、全员查询

  ，所有用户操作数据统一持久化至 MySQL。

- **普通用户登录校验**

  向量知识库管理页面、Agent 智能对话页面

  全部强制登录鉴权

  ，仅合法账号密码可进入系统，杜绝匿名访问。

- **独立知识库台账管理**

  单独设计 MySQL 数据表，统一管理用户上传的知识库文件清单，方便管理员统一维护、溯源文档资源。

  

------

### 📚 二、增强型 RAG 知识库（项目核心亮点）

针对传统 RAG 上下文断裂、检索精准度低、召回片面等痛点，全链路优化切块、存储、检索全流程：

#### 1. 文档切分策略

- 采用 **递归字符切分** 作为基础分割规则，保障文本语义完整性；
- 自研**父子双块存储架构**：
  - 子块：细粒度文本片段，存入 `Milvus` 向量数据库，用于高密度语义检索；
  - 父块：完整上下文大段文本，统一存入 `MySQL` 关系库，检索后补充全局上下文，解决碎片化回答问题。

#### 2. 多路混合召回策略

摒弃单一向量检索，采用**双引擎融合检索**：

- `Milvus 原生向量语义检索`：基于向量相似度，捕捉语义关联内容；
- `BM25 关键词检索`：弥补向量检索关键词漏召回问题，兼顾语义 + 字面匹配。

#### 3. 问题增强 & 重排优化

1. 接入轻量级改写小模型，将用户原始问题**智能衍生 3 条子问题**，多维度拆解检索需求；

2. 基于多条改写问题分别执行混合检索，合并全部召回片段；

3. 引入**重排模型**对合并后的候选片段进行相关性打分筛选，过滤无效、低关联内容；

4. 最终输出高质量上下文给大模型，极大提升问答准确率与逻辑性。

   

------

### 🤖 三、LangGraph 智能 Agent 能力

- **多功能工具调用**：内置全网联网搜索、实时日期获取工具，弥补模型知识截止短板（弱化实用性较低的天气功能，精简架构）；

- **分层会话记忆**

  - MySQL：**全量历史会话永久持久化存储**，长期保存用户对话记录；
  - Redis：缓存最近 5 轮短期会话，减少数据库查询压力，提升对话响应速度；

- **分段式流式输出**

  基于 LangGraph 节点级流式能力，实现 Agent 思考、工具调用、结果生成

  分段分步输出

  ，交互体验更流畅；

- **标准化提示词编排**：统一系统指令，约束 Agent 输出格式与行为逻辑。

  

------

### 🛠️ 四、工程化 & 运维能力

1. **全局异常统一处理**

   全接口、全模块捕获异常错误，避免服务崩溃，保障系统稳定运行；

2. **分类分级日志管理**

   按业务维度拆分日志：

   ```
   管理员操作日志
   ```

   ```
   RAG知识库日志
   ```

   ```
   Agent对话运行日志
   ```

   分类落地存储，便于问题排查、运维审计；

3. **容器化快速部署**

   采用 

   ```
   Docker
   ```

    一键部署 Milvus 向量数据库、Redis 缓存数据库，环境搭建简单、跨平台兼容性强；

4. **可视化数据管理**

   MySQL 采用 DBeaver 可视化工具管理，数据表结构清晰、数据操作直观，降低维护成本。





------

## 🏗️ 系统架构 & 数据存储分层



```
前端页面 → FastAPI 后端服务
↓
权限层：登录鉴权 + 管理员角色隔离
↓
业务层：RAG检索服务 + LangGraph-Agent智能对话
↓
存储层
├─ MySQL ：用户信息、父级文档块、全量聊天记录、知识库文件台账
├─ Milvus：文档子块向量数据、高密度语义检索
└─ Redis ：短期会话缓存、高频数据加速、性能优化
```

------





## 🧰 技术栈



- **后端框架**：FastAPI、LangChain、LangGraph
- **大模型服务**：阿里千问系列模型（兼容 OpenAI 标准接口）
- **检索框架**：Milvus 向量库、BM25 检索引擎、文本重排模型
- **数据库 & 缓存**：MySQL、Redis
- **容器部署**：Docker
- **数据管理**：DBeaver
- **日志 & 异常**：自定义日志收集、全局异常捕获
- **前端交互**：Streamlit



------





## 🖼️ 项目页面展示



1. **管理员登录页**

   ![]()

   ![721357cb1c4ba32ff8ca98bedb6fdb86](C:\Users\李增旭\xwechat_files\wxid_wlnvuxv6puqp22_a437\temp\RWTemp\2026-04\ea91f4c679cdba9d018ae3133c744dc6\721357cb1c4ba32ff8ca98bedb6fdb86.png)

2. **管理员后台 - 用户管理界面**

![](C:\Users\李增旭\xwechat_files\wxid_wlnvuxv6puqp22_a437\temp\RWTemp\2026-04\ea91f4c679cdba9d018ae3133c744dc6\23f5450833920464f7d2467511a8a2a2.jpg)

3.**知识库文件上传与向量入库页面**

![](C:\Users\李增旭\xwechat_files\wxid_wlnvuxv6puqp22_a437\temp\RWTemp\2026-04\ea91f4c679cdba9d018ae3133c744dc6\20d13e97a0411bc5f9ba44704908729e.jpg)



4.**Agent 智能对话首页（登录后）**

![img](C:\Users\李增旭\xwechat_files\wxid_wlnvuxv6puqp22_a437\temp\RWTemp\2026-04\ea91f4c679cdba9d018ae3133c744dc6\3bd1aa1d84f1ed7a2741270d84cd71b0.jpg)



5.**数据库台账 & 数据可视化管理截图（DBeaver）**

![img](C:\Users\李增旭\xwechat_files\wxid_wlnvuxv6puqp22_a437\temp\RWTemp\2026-04\ea91f4c679cdba9d018ae3133c744dc6\ed062c61de3aca16d538d58acd2825cd.png)![image](C:\Users\李增旭\xwechat_files\wxid_wlnvuxv6puqp22_a437\temp\RWTemp\2026-04\ea91f4c679cdba9d018ae3133c744dc6\edbfb279a90131317572f8ddf4136c59.png)







------







## 📌环境准备

本项目基于以下环境开发与测试，推荐使用相近版本以保证兼容性：



### 💻开发环境

- Python：3.12.8

- IDE：PyCharm 2024.1.4（专业版）

- 数据库管理工具：DBeaver 26.0.2（社区版）

  

### 🚀依赖服务（需提前部署）

- MySQL：8.0.45
- Redis：8.6.2（Docker 部署）
- Milvus：2.6.14（Docker 部署，需依赖 etcd）
- etcd：3.5.5（Milvus 依赖组件，Docker 部署）
- MinIO：（Docker 部署，对象存储）
- Docker：20.10.8





## 🚀 部署方式



1. 通过 `Docker` 快速拉取并启动 **Milvus、Redis** 容器服务，无需复杂环境配置；

   

2. 使用 DBeaver 连接本地 MySQL，导入项目数据表结构，以下是MYSQL建表的语句:

   - -- 创建数据库
     CREATE DATABASE `my_rag_db` 
     DEFAULT CHARACTER SET utf8mb4 
     COLLATE utf8mb4_0900_ai_ci;

     USE `my_rag_db`;

     - -- 用户表
       CREATE TABLE `user` (
         `id` int NOT NULL AUTO_INCREMENT COMMENT '用户ID，主键自增',
         `username` varchar(50) NOT NULL COMMENT '登录账号，唯一',
         `password` varchar(100) NOT NULL COMMENT '登录密码',
         `nickname` varchar(50) DEFAULT NULL COMMENT '用户昵称',
         `role` varchar(20) DEFAULT 'user' COMMENT '角色：admin管理员 / user普通用户',
         `create_time` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '账号创建时间',
         PRIMARY KEY (`id`),
         UNIQUE KEY `username` (`username`)
       ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='RAG系统用户表';

     - -- 文件表
       CREATE TABLE `user_file` (
         `file_id` int unsigned NOT NULL AUTO_INCREMENT,
         `filename` varchar(255) NOT NULL,
         `md5` varchar(32) DEFAULT NULL COMMENT '文件MD5值',
         PRIMARY KEY (`file_id`)
       ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

     - -- 文件父块表
       CREATE TABLE `file_parent_chunks` (
         `id` bigint NOT NULL AUTO_INCREMENT COMMENT '自增主键',
         `file_id` varchar(64) NOT NULL COMMENT '关联 user_file 中的 file_id',
         `parent_idx` int NOT NULL COMMENT '父块序号',
         `parent_content` longtext NOT NULL COMMENT '父块原文内容',
         PRIMARY KEY (`id`),
         UNIQUE KEY `uk_fileid_parentidx` (`file_id`,`parent_idx`),
         KEY `idx_file_id` (`file_id`)
       ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='RAG父块内容存储表';

     - -- 用户聊天历史表
       CREATE TABLE `user_chat_history` (
         `id` int NOT NULL AUTO_INCREMENT COMMENT '自增ID',
         `nickname` varchar(50) NOT NULL COMMENT '用户昵称',
         `query` text NOT NULL COMMENT '用户问题',
         `agent_answer` text NOT NULL COMMENT 'Agent回复',
         `created_at` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
         PRIMARY KEY (`id`)
       ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

     

3. 配置大模型 Key、向量库连接地址、数据库配置文件；

   

4. 启动 FastAPI 后端服务，运行 Streamlit 前端页面，即可完整使用全部功能。





------

## 💡 项目亮点总结

1. ✅ **RAG 优化方案**：父子切块 + 问题改写 + 混合检索 + 重排，工业级检索优化；
2. ✅ **完整权限控制系统**：角色隔离、登录鉴权、用户全生命周期管理；
3. ✅ **Agent 工程化落地**：多工具调用、分层会话存储、分段流式输出；
4. ✅ **多层存储架构**：MySQL+Milvus+Redis 各司其职，性能与持久化兼顾；
5. ✅ **完善工程规范**：全局异常、分类日志、容器化部署，代码结构清晰；
6. ✅ **高拓展性**：支持新增工具、接入多厂商大模型、拓展更多知识库功能。





## 📝 项目总结

本项目从实际业务场景出发，完整实现**权限管控、私有知识库问答、智能体对话、运维监控**一体化能力。

全程遵循模块化、分层化、工程化开发思想，针对传统 RAG 与 Agent 的痛点完成多项优化。

