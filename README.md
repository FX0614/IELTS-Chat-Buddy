# 格林 · IELTS Chat Buddy

🟢 格林（Green）是你的雅思口语练习伙伴——一个绿色小球形象的 AI 对话教练。你说一句，它说一句，通过真实对话提升口语水平。

## 核心功能

1. **语音对话**：点击绿色小球开始说话，语音识别自动转文字发送；格林的回答会自动朗读，说完自动继续听你讲，实现真正的"你说一句它说一句"
2. **实时纠错**：每次回答后，格林会指出你的语法和拼写错误，并给出正确说法（`💡 Correction`）
3. **5 种练习模式**：
   - 💬 自由对话 — 日常闲聊，练流利度
   - 🎯 Part 1 — 模拟考试自我介绍与问答
   - 🃏 Part 2 — 话题卡片，准备 1 分钟说 1-2 分钟
   - 💭 Part 3 — 深度讨论，观点/对比/举例
   - 📝 完整模拟考 — Part 1→2→3 全流程
4. **绿色小球形象**：悬浮动画；说话时发出绿色光晕脉冲；聆听时变红跳动

## 技术栈

- Python 3.9+ / Streamlit（Web 界面）
- 浏览器原生 Web Speech API（语音识别 + 朗读，免费，推荐 Chrome / Edge）
- LLM 后端默认 BlockRun（免费、无需 Key）；也可切换 Pollinations / Ollama / 火山方舟 / OpenAI

## 快速开始

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 运行应用
streamlit run ielts_speaking_coach.py

# 3. 浏览器访问 http://localhost:8501
```

首次使用：在侧边栏点「▶ 开始」，等格林打招呼后即可开始对话。浏览器会请求麦克风权限，请允许。

## 文件结构

```
IELTS Chat Buddy/
├── ielts_speaking_coach.py        # 主应用（全部功能在此）
├── requirements.txt               # 依赖（streamlit + requests）
├── .streamlit/config.toml         # 深色主题配置
├── .ielts_speaking_config.json    # 用户配置（自动生成：后端/语音设置）
└── README.md
```

## 使用说明

- **开始对话**：侧边栏选择模式 → 点「开始」，或直接点击绿色小球
- **语音输入**：点绿色小球说话；也可以在输入框打字发送
- **语音设置**：侧边栏可调整识别语言、朗读语言、语速、自动朗读开关
- **切换后端**：侧边栏「高级设置」中选择其他 LLM 后端

## 注意事项

1. 语音识别依赖浏览器能力，请使用 Chrome 或 Edge
2. 免费后端（BlockRun / Pollinations）是公共服务，响应可能有几秒延迟
3. 对话记录仅保存在当前会话，刷新页面后保留，关闭后清空
4. 配置保存在本地 `.ielts_speaking_config.json`，无需注册登录
