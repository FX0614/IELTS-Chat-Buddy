# 雅思备考智能教练 - 部署指南

## 🚀 快速部署到 Streamlit Cloud（推荐）

### 步骤1：准备GitHub仓库
1. 登录GitHub (https://github.com)
2. 点击右上角 "+" → "New repository"
3. 填写仓库信息：
   - Repository name: `ielts-coach` (或其他名称)
   - Description: 雅思备考智能教练
   - 选择 Public (公开)
   - 不勾选 "Initialize this repository with a README"
4. 点击 "Create repository"

### 步骤2：上传代码到GitHub
```bash
# 如果你有Git环境
git init
git add .
git commit -m "Initial commit: IELTS Coach v1.0"
git branch -M main
git remote add origin https://github.com/你的用户名/ielts-coach.git
git push -u origin main

# 或者使用GitHub Desktop
# 或者直接在GitHub网页上传文件
```

### 步骤3：部署到Streamlit Cloud
1. 访问 https://streamlit.io/cloud
2. 点击 "Get started" → "Sign in with GitHub"
3. 授权Streamlit访问GitHub
4. 点击 "New app"
5. 选择：
   - Repository: 你的 `ielts-coach` 仓库
   - Branch: `main`
   - Main file path: `ielts_coach.py`
6. 点击 "Deploy"

### 步骤4：访问你的应用
部署完成后，你会获得一个永久链接：
```
https://ielts-coach-你的用户名.streamlit.app
```

## 🔧 本地测试（可选）

### 安装依赖
```bash
cd english_learner
pip install -r requirements.txt
```

### 运行应用
```bash
streamlit run ielts_coach.py
```

### 访问本地应用
打开浏览器访问：`http://localhost:8501`

## 📱 使用说明

### 首次使用
1. 打开应用链接
2. 设置目标分数（建议7.5）
3. 选择当前水平（四级440+）
4. 设置每日学习时间（2小时）
5. 点击"开始我的雅思备考之旅"

### 每日学习
1. 查看今日4项任务（听说读写）
2. 点击资源链接学习
3. 返回应用，点击"标记完成"打卡
4. 查看日历，确认今日全绿✅

### 每周回顾
1. 查看本周日历完成情况
2. 更新能力评估（可选）
3. 系统自动调整下周计划难度

## ⚠️ 注意事项

### 数据存储
- 数据存储在本地SQLite数据库 (`ielts_coach.db`)
- Streamlit Cloud上每个会话是独立的
- 建议定期导出数据备份

### 免费额度
- Streamlit Cloud完全免费
- 支持无限应用
- 每月75小时运行时间（足够个人使用）

### 隐私安全
- 不收集任何个人信息
- 所有数据存储在用户本地
- 无需注册登录

## 🔄 更新应用

### 代码更新后重新部署
1. 更新本地代码
2. 推送到GitHub
3. Streamlit Cloud会自动重新部署
4. 等待1-2分钟生效

### 查看部署日志
在Streamlit Cloud控制台可以查看：
- 部署状态
- 运行日志
- 访问统计

## 🆘 常见问题

### Q: 部署失败怎么办？
A: 检查：
1. requirements.txt 是否正确
2. 主文件路径是否正确
3. GitHub仓库是否公开

### Q: 应用无法访问？
A: 检查：
1. Streamlit Cloud状态页面
2. 部署日志中的错误信息
3. 网络连接是否正常

### Q: 数据会丢失吗？
A: Streamlit Cloud上数据是会话级别的，关闭浏览器后数据会重置。建议：
1. 定期导出数据
2. 或使用本地版本长期使用

## 📞 技术支持

如有问题，请联系你的AI助手小牛马。

---

**部署时间**：约15-30分钟  
**成本**：完全免费  
**维护**：无需维护，自动运行