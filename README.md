# 沉浸式多角色互动小说引擎 v2.0

AI驱动的沉浸式文字冒险游戏，支持跨平台访问和桌面应用打包。

## 功能特性

- **精致UI**：全新设计的界面，支持动画效果和响应式布局
- **跨平台访问**：部署到Streamlit Cloud后，手机、平板、电脑均可访问
- **桌面应用**：可通过PyInstaller打包为独立exe应用
- **多世界选择**：支持「暗影纪元」（西方奇幻）和「仙途」（东方仙侠）两种世界观
- **AI游戏大师**：由LLM驱动的动态剧情生成，每次游戏体验独一无二
- **长短期记忆结合**：使用对话历史记录近期交互，向量数据库存储世界观和线索
- **自主工具调用**：AI根据剧情需要自动调用探索、战斗、查看线索等工具
- **角色成长系统**：HP、攻击、防御等属性，物品收集系统

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

复制 `.env.example` 为 `.env`，填入你的API Key：

```
DASHSCOPE_API_KEY=your-api-key-here
DASHSCOPE_API_BASE=https://dashscope.aliyuncs.com/compatible-mode/v1
MODEL_NAME=qwen-turbo
```

### 3. 启动应用

```bash
streamlit run app.py
```

## 部署到Streamlit Cloud

### 方法一：GitHub部署（推荐）

1. 在GitHub上创建新仓库
2. 推送代码到仓库：
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin https://github.com/yourusername/your-repo.git
   git push -u origin main
   ```
3. 访问 [Streamlit Cloud](https://share.streamlit.io/)
4. 点击 "New app"，选择仓库和 `app.py`
5. 在 "Advanced settings" → "Secrets" 中添加：
   ```
   DASHSCOPE_API_KEY = "your-api-key"
   DASHSCOPE_API_BASE = "https://dashscope.aliyuncs.com/compatible-mode/v1"
   MODEL_NAME = "qwen-turbo"
   ```
6. 点击 Deploy

### 方法二：直接上传

1. 打包项目文件（不含 `data/chroma_db/` 目录）
2. 在Streamlit Cloud中直接上传

## 构建桌面应用

```bash
python build_desktop.py
```

构建完成后，可执行文件在 `dist/` 目录下。

**注意**：
- 首次构建需要安装PyInstaller，脚本会自动安装
- 构建时间较长，请耐心等待
- 构建后的exe文件较大（约200-500MB），因为包含Python运行时和所有依赖

## 项目结构

```
final_project_v2/
├── app.py                 # Streamlit 主程序入口
├── requirements.txt       # 依赖包列表
├── .env                   # 环境变量配置
├── .streamlit/
│   └── config.toml        # Streamlit配置
├── build_desktop.py       # 桌面应用构建脚本
├── .gitignore             # Git忽略文件
├── data/                  # 数据目录（数据库、向量库）
├── utils/
│   ├── core_logic.py      # 核心业务逻辑（LCEL编排、RAG、Agent）
│   ├── tools.py           # 自定义工具函数（探索、战斗、线索等）
│   └── db_manager.py      # SQLite 数据库管理
└── README.md              # 项目说明
```

## 技术栈

- **LangChain**：AI应用开发框架，使用LCEL编排工作流
- **ChromaDB**：向量数据库，存储世界观和剧情线索
- **SQLite**：关系型数据库，存储用户数据和游戏状态
- **Streamlit**：Web交互界面
- **OpenAI API / DashScope**：大语言模型接口
- **PyInstaller**：桌面应用打包

## 更新日志

### v2.0 (2026-06-13)
- 全新UI设计，更精致的界面
- 响应式布局，支持手机和平板访问
- 添加Streamlit Cloud部署配置
- 添加桌面应用构建脚本
- 优化动画效果和交互体验

### v1.0 (2026-06-12)
- 初始版本
- 支持暗影纪元和仙途两个世界
- AI驱动的互动小说系统
