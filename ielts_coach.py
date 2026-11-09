"""
雅思备考智能教练 - 主应用
Streamlit Web界面
部署优化版：支持Streamlit Cloud部署
"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
import calendar
import os
from database_v2 import get_db

# 页面配置
st.set_page_config(
    page_title="雅思智能教练",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 初始化数据库 - 支持部署环境
db = get_db()

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
            
            st.success("✅ 配置已保存！正在生成12周学习计划...")
            st.balloons()
            st.rerun()

def main_dashboard():
    """主仪表板"""
    st.title("📚 今日学习任务")
    st.markdown("---")
    
    # 获取用户配置
    user_config = db.get_user_config()
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
    
    # 获取今日计划
    daily_plan = db.get_daily_plan(today)
    
    if not daily_plan:
        st.info("今天没有安排学习任务，休息一下或自由学习吧！")
        return
    
    # 获取今日打卡情况
    checkins = db.get_daily_checkins(today)
    
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
            
            # 资源链接
            if task['resource_url'] and task['resource_url'] != 'https://example.com/listening':
                st.markdown(f"[学习资源链接]({task['resource_url']})")
            
            # 难度指示
            difficulty = task['difficulty_level']
            st.progress(difficulty / 5, text=f"难度等级: {difficulty}/5")
            
            # 打卡按钮
            if completed:
                st.success("✅ 已完成")
            else:
                if st.button(f"标记{task_info['name']}完成", key=f"checkin_{task_type}"):
                    db.checkin_task(today, task_type, completed=True)
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
            'is_today': date.date() == today.date()
        })
    
    # 显示日历
    cols = st.columns(7)
    for idx, day in enumerate(calendar_data):
        with cols[idx]:
            # 日期框
            bg_color = "#4CAF50" if day['completion'] == 1 else "#FF9800" if day['completion'] > 0 else "#E0E0E0"
            if day['is_today']:
                bg_color = "#2196F3"  # 今天特殊颜色
            
            day_style = f"""
                <div style="
                    background-color: {bg_color};
                    padding: 15px;
                    border-radius: 10px;
                    text-align: center;
                    color: white;
                    margin-bottom: 5px;
                ">
                    <div style="font-size: 12px;">{day['day_name']}</div>
                    <div style="font-size: 24px; font-weight: bold;">{day['day_num']}</div>
                </div>
            """
            st.markdown(day_style, unsafe_allow_html=True)
            
            # 完成率
            if day['completion'] > 0:
                st.markdown(f"**{int(day['completion'] * 100)}%**")
            else:
                st.markdown("--")

def show_radar_chart():
    """显示能力雷达图"""
    st.subheader("📊 能力评估雷达图")
    
    # 获取最新评估数据
    assessment = db.get_latest_assessment()
    
    if assessment:
        categories = ['听力', '阅读', '写作', '口语']
        scores = [
            assessment['listening_score'],
            assessment['reading_score'], 
            assessment['writing_score'],
            assessment['speaking_score']
        ]
        
        # 创建雷达图
        fig = go.Figure(data=go.Scatterpolar(
            r=scores + [scores[0]],  # 闭合图形
            theta=categories + [categories[0]],
            fill='toself',
            name='当前能力',
            line_color='blue'
        ))
        
        # 添加目标线（假设目标都是7.5）
        target_score = 7.5
        fig.add_trace(go.Scatterpolar(
            r=[target_score] * 5,
            theta=categories + [categories[0]],
            name='目标能力',
            line_color='red',
            line_dash='dash'
        ))
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 9]
                )),
            showlegend=True,
            title="雅思能力评估"
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # 添加评估按钮
        if st.button("更新能力评估"):
            show_assessment_form()
    else:
        st.info("暂无能力评估数据")
        if st.button("进行首次能力评估"):
            show_assessment_form()

def show_assessment_form():
    """显示能力评估表单"""
    with st.form("assessment_form"):
        st.write("### 能力自我评估")
        
        col1, col2 = st.columns(2)
        
        with col1:
            listening_score = st.slider("听力", 1.0, 9.0, 5.0, 0.5)
            reading_score = st.slider("阅读", 1.0, 9.0, 5.0, 0.5)
        
        with col2:
            writing_score = st.slider("写作", 1.0, 9.0, 5.0, 0.5)
            speaking_score = st.slider("口语", 1.0, 9.0, 5.0, 0.5)
        
        notes = st.text_area("备注（可选）")
        
        submitted = st.form_submit_button("保存评估")
        
        if submitted:
            db.add_skill_assessment(
                listening_score=listening_score,
                reading_score=reading_score,
                writing_score=writing_score,
                speaking_score=speaking_score,
                notes=notes
            )
            st.success("✅ 能力评估已保存！")
            st.rerun()

def sidebar_navigation():
    """侧边栏导航"""
    with st.sidebar:
        st.image("https://img.icons8.com/color/96/000000/english.png", width=80)
        st.title("雅思智能教练")
        
        st.markdown("---")
        
        # 导航选项
        page = st.radio(
            "导航",
            ["今日任务", "学习计划", "数据统计", "系统设置"],
            index=0
        )
        
        st.markdown("---")
        
        # 用户信息
        user_config = db.get_user_config()
        if user_config:
            st.markdown("### 用户信息")
            st.markdown(f"**目标**: 雅思 {user_config['target_score']}")
            st.markdown(f"**水平**: {user_config['current_level']}")
            st.markdown(f"**每日**: {user_config['daily_hours']}小时")
            
            if user_config['exam_date']:
                exam_date = datetime.strptime(user_config['exam_date'], '%Y-%m-%d')
                days_left = (exam_date - datetime.now()).days
                if days_left > 0:
                    st.markdown(f"**考试倒计时**: {days_left}天")
        
        st.markdown("---")
        st.markdown("### 使用说明")
        st.markdown("""
        1. 每天完成4项任务（听说读写）
        2. 点击"标记完成"打卡
        3. 每周日系统自动调整下周计划
        4. 定期更新能力评估
        """)

# 主程序
def main():
    sidebar_navigation()
    
    # 根据导航显示不同页面
    # 这里先只实现今日任务页面，其他页面后续扩展
    main_dashboard()

if __name__ == "__main__":
    main()