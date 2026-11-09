"""
雅思备考智能教练 - 优化版
解决加载速度慢的问题，添加真实学习资源
"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
import calendar
import os
import time
from database_v2 import get_db

# 页面配置 - 优化缓存
st.set_page_config(
    page_title="雅思智能教练",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 初始化数据库 - 支持部署环境
@st.cache_resource
def get_cached_db():
    """缓存数据库连接，避免重复初始化"""
    return get_db()

db = get_cached_db()

# 缓存用户配置
@st.cache_data(ttl=300)  # 5分钟缓存
def get_cached_user_config():
    """缓存用户配置"""
    return db.get_user_config()

# 缓存每日计划
@st.cache_data(ttl=60)  # 1分钟缓存
def get_cached_daily_plan(date_str):
    """缓存每日计划"""
    return db.get_daily_plan(date_str)

# 缓存打卡数据
@st.cache_data(ttl=60)
def get_cached_daily_checkins(date_str):
    """缓存每日打卡数据"""
    return db.get_daily_checkins(date_str)

def init_user_config():
    """初始化用户配置页面"""
    st.title("🎯 雅思备考智能教练")
    st.markdown("---")
    
    with st.form("user_config_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            target_score = st.slider("目标雅思分数", 5.0, 9.0, 7.5, 0.5)
            current_level = st.selectbox(
                "当前英语水平",
                ["四级440+", "四级500+", "六级425+", "六级500+", "其他"]
            )
        
        with col2:
            daily_hours = st.slider("每日学习时间（小时）", 1, 6, 2)
            exam_date = st.date_input("计划考试日期（可选）", value=None)
        
        vocab_tool = st.text_input("背单词工具", value="墨墨背单词")
        
        submitted = st.form_submit_button("开始我的雅思备考之旅")
        
        if submitted:
            exam_date_str = exam_date.strftime('%Y-%m-%d') if exam_date else None
            db.set_user_config(
                target_score=target_score,
                current_level=current_level,
                daily_hours=daily_hours,
                vocab_tool=vocab_tool,
                exam_date=exam_date_str
            )
            
            # 生成初始学习计划
            db.generate_initial_plan(weeks=12)
            
            # 清除缓存
            st.cache_data.clear()
            st.cache_resource.clear()
            
            st.success("✅ 配置已保存！正在生成12周学习计划...")
            st.balloons()
            st.rerun()

def main_dashboard():
    """主仪表板 - 优化版"""
    st.title("📚 今日学习任务")
    st.markdown("---")
    
    # 获取用户配置（使用缓存）
    user_config = get_cached_user_config()
    if not user_config:
        st.warning("请先完成初始配置")
        init_user_config()
        return
    
    # 显示用户信息
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("目标分数", f"{user_config['target_score']}")
    with col2:
        st.metric("当前水平", user_config['current_level'])
    with col3:
        st.metric("每日时间", f"{user_config['daily_hours']}小时")
    with col4:
        st.metric("词汇工具", user_config['vocab_tool'])
    
    st.markdown("---")
    
    # 今日日期
    today = datetime.now().strftime('%Y-%m-%d')
    st.subheader(f"📅 {today} 任务清单")
    
    # 获取今日计划（使用缓存）
    daily_plan = get_cached_daily_plan(today)
    
    if not daily_plan:
        st.info("今天没有安排学习任务，休息一下或自由学习吧！")
        return
    
    # 获取今日打卡情况（使用缓存）
    checkins = get_cached_daily_checkins(today)
    
    # 显示4个任务卡片
    cols = st.columns(4)
    
    task_types = {
        'listening': {'name': '听力', 'emoji': '👂', 'color': '#4CAF50'},
        'reading': {'name': '阅读', 'emoji': '📖', 'color': '#2196F3'},
        'writing': {'name': '写作', 'emoji': '✍️', 'color': '#FF9800'},
        'speaking': {'name': '口语', 'emoji': '🗣️', 'color': '#9C27B0'}
    }
    
    for idx, task in enumerate(daily_plan):
        task_type = task['task_type']
        task_info = task_types.get(task_type, {'name': task_type, 'emoji': '📝', 'color': '#757575'})
        
        with cols[idx]:
            # 任务卡片
            completed = checkins.get(task_type, False)
            
            card_color = task_info['color']
            card_style = f"""
                <div style="
                    background-color: {card_color};
                    padding: 20px;
                    border-radius: 10px;
                    color: white;
                    margin-bottom: 10px;
                ">
                    <h3 style="margin:0;">{task_info['emoji']} {task_info['name']}</h3>
                </div>
            """
            st.markdown(card_style, unsafe_allow_html=True)
            
            # 任务描述
            st.markdown(f"**{task['task_description']}**")
            
            # 资源链接 - 现在有真实的新东方资源
            if task['resource_url']:
                st.markdown(f"🔗 [点击学习]({task['resource_url']})")
            
            # 难度指示
            difficulty = task['difficulty_level']
            st.progress(difficulty / 5, text=f"难度等级: {difficulty}/5")
            
            # 打卡按钮
            if completed:
                st.success("✅ 已完成")
            else:
                if st.button(f"标记{task_info['name']}完成", key=f"checkin_{task_type}"):
                    db.checkin_task(today, task_type, completed=True)
                    # 清除缓存
                    st.cache_data.clear()
                    st.rerun()
    
    # 词汇提醒
    st.markdown("---")
    st.info(f"📝 词汇学习提醒：记得使用 **{user_config['vocab_tool']}** 背单词！")
    
    # 周历视图
    st.markdown("---")
    show_calendar_view()
    
    # 能力雷达图
    st.markdown("---")
    show_radar_chart()

def show_calendar_view():
    """显示日历打卡视图"""
    st.subheader("📅 本周学习日历")
    
    # 获取本周日期范围
    today = datetime.now()
    start_of_week = today - timedelta(days=today.weekday())
    end_of_week = start_of_week + timedelta(days=6)
    
    # 获取本周打卡数据
    weekly_data = db.get_weekly_completion(
        start_of_week.strftime('%Y-%m-%d'),
        end_of_week.strftime('%Y-%m-%d')
    )
    
    # 创建日历数据
    calendar_data = []
    for i in range(7):
        date = start_of_week + timedelta(days=i)
        date_str = date.strftime('%Y-%m-%d')
        
        # 查找当天的打卡数据
        day_data = next((d for d in weekly_data if d['checkin_date'] == date_str), None)
        
        if day_data:
            completion_rate = day_data['completed_tasks'] / day_data['total_tasks'] if day_data['total_tasks'] > 0 else 0
        else:
            completion_rate = 0
        
        calendar_data.append({
            'date': date,
            'day_name': calendar.day_name[date.weekday()][:3],
            'day_num': date.day,
            'completion': completion_rate,
            'is_today': date_str == today.strftime('%Y-%m-%d')
        })
    
    # 显示日历
    cols = st.columns(7)
    for i, day_data in enumerate(calendar_data):
        with cols[i]:
            # 日期框
            bg_color = '#4CAF50' if day_data['is_today'] else '#f0f0f0'
            text_color = 'white' if day_data['is_today'] else 'black'
            
            day_style = f"""
                <div style="
                    background-color: {bg_color};
                    color: {text_color};
                    padding: 10px;
                    border-radius: 5px;
                    text-align: center;
                    margin-bottom: 5px;
                ">
                    <div style="font-size: 12px;">{day_data['day_name']}</div>
                    <div style="font-size: 24px; font-weight: bold;">{day_data['day_num']}</div>
                </div>
            """
            st.markdown(day_style, unsafe_allow_html=True)
            
            # 完成率
            completion = day_data['completion']
            if completion > 0:
                st.progress(completion, text=f"{int(completion*100)}%")
            else:
                st.caption("未开始")

def show_radar_chart():
    """显示能力雷达图"""
    st.subheader("📊 能力评估雷达图")
    
    # 获取最新的能力评估
    with db.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM skill_assessments 
            ORDER BY assessment_date DESC LIMIT 1
        ''')
        row = cursor.fetchone()
    
    if row:
        assessment = dict(row)
        categories = ['听力', '阅读', '写作', '口语']
        values = [
            assessment['listening_score'] or 5,
            assessment['reading_score'] or 5,
            assessment['writing_score'] or 5,
            assessment['speaking_score'] or 5
        ]
    else:
        # 默认值
        categories = ['听力', '阅读', '写作', '口语']
        values = [5, 5, 5, 5]
    
    # 创建雷达图
    fig = go.Figure(data=go.Scatterpolar(
        r=values + [values[0]],  # 闭合图形
        theta=categories + [categories[0]],
        fill='toself',
        line=dict(color='#4CAF50', width=2),
        marker=dict(size=8, color='#4CAF50')
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 9],
                tickfont=dict(size=10)
            ),
            angularaxis=dict(
                tickfont=dict(size=12)
            )
        ),
        showlegend=False,
        height=300,
        margin=dict(l=50, r=50, t=30, b=30)
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # 添加评估按钮
    if st.button("更新能力评估"):
        with st.form("assessment_form"):
            col1, col2 = st.columns(2)
            with col1:
                listening = st.slider("听力", 1.0, 9.0, 5.0, 0.5)
                reading = st.slider("阅读", 1.0, 9.0, 5.0, 0.5)
            with col2:
                writing = st.slider("写作", 1.0, 9.0, 5.0, 0.5)
                speaking = st.slider("口语", 1.0, 9.0, 5.0, 0.5)
            
            if st.form_submit_button("保存评估"):
                overall = (listening + reading + writing + speaking) / 4
                db.add_skill_assessment(
                    listening_score=listening,
                    reading_score=reading,
                    writing_score=writing,
                    speaking_score=speaking,
                    overall_score=overall
                )
                st.success("能力评估已更新！")
                st.rerun()

def main():
    """主函数"""
    # 初始化session_state
    if 'regenerate_plan' not in st.session_state:
        st.session_state.regenerate_plan = False
    
    # 添加侧边栏
    with st.sidebar:
        st.title("⚙️ 设置")
        st.markdown("---")
        
        # 显示当前用户信息
        user_config = get_cached_user_config()
        if user_config:
            st.subheader("当前配置")
            st.write(f"**目标分数**: {user_config['target_score']}")
            st.write(f"**当前水平**: {user_config['current_level']}")
            st.write(f"**每日时间**: {user_config['daily_hours']}小时")
            st.write(f"**词汇工具**: {user_config['vocab_tool']}")
            
            st.markdown("---")
            
            # 重新生成计划按钮
            st.subheader("计划管理")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🔄 重新生成计划", type="secondary", use_container_width=True):
                    st.session_state.regenerate_plan = True
            
            if st.session_state.get('regenerate_plan', False):
                st.warning("⚠️ 重新生成计划将覆盖现有的学习计划和打卡记录！")
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("✅ 确认重新生成", type="primary"):
                        with st.spinner("正在生成智能学习计划..."):
                            db.generate_initial_plan(weeks=12)
                            # 清除缓存
                            st.cache_data.clear()
                            st.cache_resource.clear()
                            st.session_state.regenerate_plan = False
                            st.success("✅ 智能学习计划已重新生成！")
                            st.rerun()
                with col2:
                    if st.button("❌ 取消", type="secondary"):
                        st.session_state.regenerate_plan = False
                        st.rerun()
            
            st.markdown("---")
            
            # 学习策略说明
            st.subheader("📊 你的学习策略")
            if user_config['current_level'] == '四级440+':
                st.info("""
                **四级440+ → 雅思7.5 学习策略**:
                
                1. **基础阶段** (1-4周): 词汇语法巩固
                2. **提升阶段** (5-8周): 题型技巧训练  
                3. **冲刺阶段** (9-12周): 模考和弱点突破
                
                **每日重点**: 听说读写交替训练，避免疲劳
                """)
            elif user_config['current_level'] == '六级425+':
                st.info("""
                **六级425+ → 雅思7.5 学习策略**:
                
                1. **适应阶段**: 熟悉雅思题型特点
                2. **强化阶段**: 提升答题速度和准确性
                3. **冲刺阶段**: 高分技巧和时间管理
                """)
        
        st.markdown("---")
        st.caption("💡 提示：点击上方按钮可重新生成更科学的学习计划")
    
    # 检查是否有用户配置
    if not user_config:
        init_user_config()
    else:
        main_dashboard()

if __name__ == "__main__":
    main()