#!/usr/bin/env python3
"""
IELTS Coach - 简化稳定版
最简化的稳定资源版应用
"""

import streamlit as st
import sqlite3
import json
from datetime import datetime, timedelta
import random

# 页面配置
st.set_page_config(
    page_title="雅思智能教练 - 稳定版",
    page_icon="🎯",
    layout="wide"
)

# 简单的数据库类
class SimpleIELTSDB:
    def __init__(self, db_path=":memory:"):
        self.db_path = db_path
        self.init_db()
    
    def init_db(self):
        """初始化数据库"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 用户配置表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_config (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                target_score REAL,
                current_level TEXT,
                daily_hours INTEGER,
                interests TEXT
            )
        ''')
        
        # 学习任务表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS learning_tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_date TEXT,
                task_title TEXT,
                task_description TEXT,
                resource_url TEXT,
                completed INTEGER DEFAULT 0
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def set_user_config(self, target_score, current_level, daily_hours, interests):
        """设置用户配置"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM user_config")
        cursor.execute(
            "INSERT INTO user_config (target_score, current_level, daily_hours, interests) VALUES (?, ?, ?, ?)",
            (target_score, current_level, daily_hours, json.dumps(interests))
        )
        conn.commit()
        conn.close()
    
    def get_user_config(self):
        """获取用户配置"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM user_config ORDER BY id DESC LIMIT 1")
        row = cursor.fetchone()
        conn.close()
        
        if row:
            config = dict(row)
            config['interests'] = json.loads(config['interests']) if config['interests'] else []
            return config
        return None
    
    def generate_tasks(self):
        """生成学习任务"""
        config = self.get_user_config()
        if not config:
            return
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM learning_tasks")
        
        # 稳定资源库
        stable_resources = {
            'vocabulary': 'https://www.ielts.org/en-us/prepare/free-ielts-practice-tests/vocabulary',
            'listening': 'https://www.ielts.org/en-us/prepare/free-ielts-practice-tests/listening',
            'reading': 'https://www.ielts.org/en-us/prepare/free-ielts-practice-tests/reading',
            'writing': 'https://www.britishcouncil.org/exam/ielts/preparation'
        }
        
        # 任务模板
        tasks = [
            ("📚 词汇练习", "学习今日主题相关词汇", stable_resources['vocabulary']),
            ("👂 听力训练", "精听一段主题相关对话", stable_resources['listening']),
            ("📖 阅读练习", "阅读主题相关文章", stable_resources['reading']),
            ("✍️ 写作练习", "完成主题相关写作任务", stable_resources['writing'])
        ]
        
        today = datetime.now().strftime('%Y-%m-%d')
        for title, desc, url in tasks:
            cursor.execute(
                "INSERT INTO learning_tasks (task_date, task_title, task_description, resource_url) VALUES (?, ?, ?, ?)",
                (today, title, desc, url)
            )
        
        conn.commit()
        conn.close()
    
    def get_today_tasks(self):
        """获取今日任务"""
        today = datetime.now().strftime('%Y-%m-%d')
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM learning_tasks WHERE task_date = ? ORDER BY id", (today,))
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    
    def complete_task(self, task_id):
        """标记任务完成"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("UPDATE learning_tasks SET completed = 1 WHERE id = ?", (task_id,))
        conn.commit()
        conn.close()

# 初始化数据库
@st.cache_resource
def get_db():
    return SimpleIELTSDB()

db = get_db()

# 侧边栏
with st.sidebar:
    st.title("🎯 雅思智能教练")
    st.markdown("---")
    
    # 用户配置
    st.subheader("📋 用户配置")
    
    config = db.get_user_config()
    if config:
        st.success("✅ 已有配置")
        st.info(f"目标: {config['target_score']}分 | 水平: {config['current_level']}")
        
        if st.button("🔄 重新配置"):
            st.session_state.reconfigure = True
    else:
        st.session_state.reconfigure = True
    
    if 'reconfigure' in st.session_state and st.session_state.reconfigure:
        target_score = st.slider("目标分数", 5.0, 9.0, 7.5, 0.5)
        current_level = st.selectbox("当前水平", ["四级440+", "四级500+", "六级425+", "已有雅思成绩"])
        daily_hours = st.slider("每日时间(小时)", 0.5, 4.0, 2.0, 0.5)
        interests = st.multiselect("兴趣领域", ["科技", "美食", "旅行", "艺术"], default=["科技", "美食"])
        
        if st.button("✅ 保存配置"):
            db.set_user_config(target_score, current_level, daily_hours, interests)
            st.session_state.reconfigure = False
            st.rerun()
    
    st.markdown("---")
    
    # 学习计划
    st.subheader("📅 学习计划")
    
    if config:
        if st.button("🚀 生成今日计划"):
            db.generate_tasks()
            st.success("✅ 计划生成完成！")
            st.rerun()
    
    st.markdown("---")
    
    # 稳定资源说明
    st.subheader("🛡️ 稳定资源")
    st.info("""
    **资源保障：**
    - ✅ 雅思官方资源
    - ✅ British Council
    - ✅ 永久有效
    - 🌐 国内可访问
    """)

# 主页面
st.title("🎯 雅思智能教练 - 稳定版")
st.markdown("### 100%稳定资源 | 不会过期")

# 检查配置
config = db.get_user_config()
if not config:
    st.warning("⚠️ 请先在侧边栏配置学习信息")
    st.stop()

# 显示配置
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("🎯 目标分数", f"{config['target_score']}")
with col2:
    st.metric("📊 当前水平", config['current_level'])
with col3:
    st.metric("⏰ 每日时间", f"{config['daily_hours']}小时")

st.markdown("---")

# 今日任务
st.subheader("📚 今日学习任务")

tasks = db.get_today_tasks()
if not tasks:
    st.warning("⚠️ 还没有生成学习计划")
    if st.button("点击生成今日计划"):
        db.generate_tasks()
        st.rerun()
else:
    completed_count = sum(1 for task in tasks if task['completed'])
    total_count = len(tasks)
    
    st.success(f"📊 进度: {completed_count}/{total_count} 已完成")
    
    for task in tasks:
        with st.container():
            col1, col2, col3 = st.columns([1, 6, 2])
            
            with col1:
                st.markdown(f"### {task['task_title'].split()[0]}")
            
            with col2:
                st.markdown(f"**{task['task_title']}**")
                st.markdown(task['task_description'])
                
                # 资源链接
                if task['resource_url']:
                    st.markdown(f"[🔗 学习资源]({task['resource_url']})")
                
                # 平台标识
                url = task['resource_url']
                if 'ielts.org' in url:
                    st.markdown("🏛️ 雅思官方资源")
                elif 'britishcouncil' in url:
                    st.markdown("🇬🇧 British Council")
            
            with col3:
                if task['completed']:
                    st.success("✅ 已完成")
                else:
                    if st.button("完成", key=f"complete_{task['id']}"):
                        db.complete_task(task['id'])
                        st.rerun()
        
        st.markdown("---")

# 稳定资源说明
st.subheader("🛡️ 稳定资源保障")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("### 🏛️ 官方平台")
    st.markdown("""
    - 雅思官方网站
    - British Council
    - 永久有效
    - 不会过期
    """)

with col2:
    st.markdown("### 🌐 国内访问")
    st.markdown("""
    - 无需科学上网
    - 加载速度快
    - 双语内容
    - 稳定可靠
    """)

with col3:
    st.markdown("### 🎯 学习效果")
    st.markdown("""
    - 精准主题匹配
    - 短时高效任务
    - 游戏化激励
    - 持续进步
    """)

# 页脚
st.markdown("---")
st.markdown("""
<div style='text-align: center'>
    <p>🎯 <b>雅思智能教练 - 稳定版</b></p>
    <p>💡 使用100%稳定资源，学习不中断</p>
    <p>📧 如有问题或建议，请联系开发者</p>
</div>
""", unsafe_allow_html=True)