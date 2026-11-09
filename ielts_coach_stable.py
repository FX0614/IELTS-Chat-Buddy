#!/usr/bin/env python3
"""
IELTS Coach - 稳定资源版
使用100%稳定资源，解决资源容易过期的问题
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import sys
import os

# 添加当前目录到路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database_v4_fixed import IELTSCoachDBV4Fixed

# 页面配置
st.set_page_config(
    page_title="雅思智能教练 - 稳定资源版",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 初始化数据库
@st.cache_resource
def init_database():
    """初始化数据库（缓存资源）"""
    return IELTSCoachDBV4Fixed()

db = init_database()

# 侧边栏
with st.sidebar:
    st.title("🎯 雅思智能教练")
    st.markdown("---")
    
    # 用户配置
    st.subheader("📋 用户配置")
    
    # 检查是否有现有配置
    existing_config = db.get_user_config()
    
    if existing_config:
        st.success("✅ 已有配置")
        st.info(f"目标分数: {existing_config['target_score']}")
        st.info(f"当前水平: {existing_config['current_level']}")
        st.info(f"每日时间: {existing_config['daily_hours']}小时")
        
        if st.button("🔄 重新配置"):
            st.session_state.reconfigure = True
    else:
        st.session_state.reconfigure = True
    
    # 重新配置界面
    if 'reconfigure' in st.session_state and st.session_state.reconfigure:
        st.subheader("🔄 重新配置")
        
        target_score = st.slider("目标雅思分数", 5.0, 9.0, 7.5, 0.5)
        current_level = st.selectbox(
            "当前英语水平",
            ["四级440+", "四级500+", "六级425+", "六级500+", "已有雅思成绩"]
        )
        daily_hours = st.slider("每日可用学习时间（小时）", 0.5, 4.0, 2.0, 0.5)
        vocab_tool = st.selectbox(
            "词汇工具偏好",
            ["墨墨背单词", "百词斩", "不背单词", "欧路词典", "其他"]
        )
        
        st.subheader("🎯 兴趣领域")
        interests = st.multiselect(
            "选择你感兴趣的领域（用于个性化主题）",
            ["科技", "美食", "旅行", "艺术", "体育", "音乐", "电影", "文学"],
            default=["科技", "美食", "旅行", "艺术"]
        )
        
        exam_date = st.date_input("考试日期（可选）", value=None)
        
        if st.button("✅ 保存配置"):
            db.set_user_config(
                target_score=target_score,
                current_level=current_level,
                daily_hours=daily_hours,
                vocab_tool=vocab_tool,
                interests=interests,
                exam_date=exam_date.strftime('%Y-%m-%d') if exam_date else None
            )
            st.session_state.reconfigure = False
            st.rerun()
    
    st.markdown("---")
    
    # 学习计划管理
    st.subheader("📅 学习计划")
    
    if existing_config:
        if st.button("🚀 生成主题周学习计划"):
            with st.spinner("正在生成个性化学习计划..."):
                db.generate_theme_based_tasks(weeks=12)
            st.success("✅ 学习计划生成完成！")
            st.rerun()
        
        if st.button("🔄 重新生成计划"):
            if st.checkbox("确认重新生成（将覆盖现有计划）"):
                with st.spinner("重新生成学习计划..."):
                    db.generate_theme_based_tasks(weeks=12)
                st.success("✅ 学习计划已重新生成！")
                st.rerun()
    
    st.markdown("---")
    
    # 稳定资源说明
    st.subheader("🛡️ 稳定资源说明")
    st.info("""
    **资源稳定性保障：**
    - ✅ 雅思官方资源（永久有效）
    - ✅ British Council（官方机构）
    - ✅ Cambridge English（权威平台）
    - 🌐 所有资源国内可访问
    - 🔄 几乎不会过期
    """)

# 主页面
st.title("🎯 雅思智能教练 - 稳定资源版")
st.markdown("### 个性化主题周学习计划 | 100%稳定资源")

# 检查配置
config = db.get_user_config()
if not config:
    st.warning("⚠️ 请先在侧边栏配置你的学习信息")
    st.stop()

# 显示用户配置
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("🎯 目标分数", f"{config['target_score']}")
with col2:
    st.metric("📊 当前水平", config['current_level'])
with col3:
    st.metric("⏰ 每日时间", f"{config['daily_hours']}小时")
with col4:
    st.metric("📚 词汇工具", config['vocab_tool'])

st.markdown("---")

# 今日学习任务
st.subheader("📚 今日学习任务")
today = datetime.now().strftime('%Y-%m-%d')
tasks = db.get_daily_tasks(today)

if not tasks:
    st.warning("⚠️ 还没有生成学习计划，请在侧边栏点击'生成主题周学习计划'")
else:
    # 显示主题信息
    theme = tasks[0]['theme_name']
    st.success(f"🎯 本周主题: **{theme}**")
    
    # 任务列表
    total_minutes = 0
    total_points = 0
    
    for task in tasks:
        with st.container():
            col1, col2, col3 = st.columns([1, 6, 2])
            
            with col1:
                st.markdown(f"### {task['task_icon']}")
            
            with col2:
                st.markdown(f"**{task['task_title']}**")
                st.markdown(task['task_description'])
                
                # 显示资源链接
                if task['resource_url']:
                    st.markdown(f"[🔗 学习资源]({task['resource_url']})")
                
                # 难度显示
                difficulty = task['difficulty_level']
                st.markdown(f"难度: {'⭐' * difficulty}")
            
            with col3:
                st.markdown(f"**{task['estimated_minutes']}分钟**")
                st.markdown(f"积分: **{task['points']}**")
                
                # 完成按钮
                if not task['completed']:
                    if st.button("✅ 完成", key=f"complete_{task['id']}"):
                        db.complete_task(task['id'])
                        db.update_user_progress(task['points'])
                        st.rerun()
                else:
                    st.success("已完成")
            
            total_minutes += task['estimated_minutes']
            total_points += task['points']
        
        st.markdown("---")
    
    # 今日总结
    col1, col2 = st.columns(2)
    with col1:
        st.metric("⏰ 总学习时间", f"{total_minutes}分钟")
    with col2:
        st.metric("🎯 可获得积分", total_points)

# 学习进度
st.markdown("---")
st.subheader("📊 学习进度")

progress = db.get_user_progress()

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("🏆 总积分", progress.get('total_points', 0))
with col2:
    st.metric("🔥 连续打卡", f"{progress.get('current_streak', 0)}天")
with col3:
    st.metric("📈 最长打卡", f"{progress.get('longest_streak', 0)}天")
with col4:
    st.metric("⭐ 当前等级", progress.get('level', 1))

# 等级进度条
if progress.get('total_points', 0) > 0:
    current_level = progress.get('level', 1)
    points_in_level = progress.get('total_points', 0) % 100
    level_progress = points_in_level / 100
    
    st.progress(level_progress, text=f"等级 {current_level} ({points_in_level}/100 积分)")

# 主题周概览
st.markdown("---")
st.subheader("📅 12周主题概览")

weekly_themes = db.get_weekly_themes()
if weekly_themes:
    themes_df = pd.DataFrame(weekly_themes)
    
    # 显示主题表格
    st.dataframe(
        themes_df[['week_number', 'theme_name', 'theme_description', 'vocabulary_count']],
        column_config={
            "week_number": "周数",
            "theme_name": "主题",
            "theme_description": "描述",
            "vocabulary_count": "词汇目标"
        },
        hide_index=True,
        use_container_width=True
    )
    
    # 可视化
    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=('每周词汇目标', '主题分布'),
        specs=[[{'type': 'bar'}, {'type': 'pie'}]]
    )
    
    # 词汇目标柱状图
    fig.add_trace(
        go.Bar(
            x=themes_df['week_number'],
            y=themes_df['vocabulary_count'],
            name='词汇目标',
            marker_color='lightblue'
        ),
        row=1, col=1
    )
    
    # 主题分布饼图
    theme_counts = themes_df['theme_name'].value_counts()
    fig.add_trace(
        go.Pie(
            labels=theme_counts.index,
            values=theme_counts.values,
            name='主题分布',
            hole=0.3
        ),
        row=1, col=2
    )
    
    fig.update_layout(height=400, showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

# 稳定资源说明
st.markdown("---")
st.subheader("🛡️ 稳定资源保障")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("### 🏛️ 官方资源")
    st.markdown("""
    - **雅思官方网站**
    - **British Council**
    - **Cambridge English**
    - 永久有效，不会过期
    """)

with col2:
    st.markdown("### 🌐 国内访问")
    st.markdown("""
    - 所有资源国内可访问
    - 无需科学上网
    - 加载速度快
    - 双语内容
    """)

with col3:
    st.markdown("### 🔄 持续更新")
    st.markdown("""
    - 定期检查链接有效性
    - 自动替换失效链接
    - 资源质量监控
    - 用户反馈优化
    """)

# 页脚
st.markdown("---")
st.markdown("""
<div style='text-align: center'>
    <p>🎯 <b>雅思智能教练 - 稳定资源版</b></p>
    <p>💡 使用100%稳定资源，学习不中断</p>
    <p>📧 如有问题或建议，请联系开发者</p>
</div>
""", unsafe_allow_html=True)