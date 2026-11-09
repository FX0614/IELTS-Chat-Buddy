"""
雅思备考智能教练 - 主题周版本
根据Leon需求定制：主题周 + 任务型学习 + 游戏化元素
"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
import calendar
import os
import time
from database_v3 import get_db_v3

# 页面配置
st.set_page_config(
    page_title="雅思主题周教练",
    page_icon="🎨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 初始化数据库
@st.cache_resource
def get_cached_db():
    return get_db_v3()

db = get_cached_db()

# 缓存
@st.cache_data(ttl=300)
def get_cached_user_config():
    return db.get_user_config()

@st.cache_data(ttl=60)
def get_cached_daily_tasks(date_str):
    return db.get_daily_tasks(date_str)

@st.cache_data(ttl=60)
def get_cached_user_progress():
    return db.get_user_progress()

@st.cache_data(ttl=300)
def get_cached_weekly_themes():
    return db.get_weekly_themes()

def init_user_config():
    """初始化用户配置页面"""
    st.title("🎨 雅思主题周智能教练")
    st.markdown("---")
    
    st.info("""
    🎯 **全新主题周学习模式**：
    - 每周一个有趣主题（科技、美食、旅行、艺术等）
    - 每天3个短时高频任务（15-25分钟/个）
    - 游戏化元素：积分、徽章、连续打卡
    - 重点满足：词汇量 + 听力提升需求
    """)
    
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
        
        # 兴趣选择
        st.subheader("🎯 选择你的兴趣（用于个性化主题）")
        interests = st.multiselect(
            "选择2-4个兴趣领域：",
            ["科技", "美食", "旅行", "艺术", "体育", "音乐", "电影", "阅读", "游戏", "设计"],
            default=["科技", "美食", "旅行", "艺术"],
            max_selections=4
        )
        
        submitted = st.form_submit_button("开始主题周学习之旅")
        
        if submitted:
            if len(interests) < 2:
                st.error("请至少选择2个兴趣领域")
                return
                
            exam_date_str = exam_date.strftime('%Y-%m-%d') if exam_date else None
            db.set_user_config(
                target_score=target_score,
                current_level=current_level,
                daily_hours=daily_hours,
                vocab_tool=vocab_tool,
                interests=interests,
                exam_date=exam_date_str
            )
            
            # 生成主题周学习计划
            with st.spinner("正在生成个性化主题周学习计划..."):
                db.generate_theme_based_tasks(weeks=12)
            
            # 清除缓存
            st.cache_data.clear()
            st.cache_resource.clear()
            
            st.success("✅ 个性化主题周学习计划已生成！")
            st.balloons()
            st.rerun()

def main_dashboard():
    """主仪表板 - 主题周版本"""
    # 获取用户配置
    user_config = get_cached_user_config()
    if not user_config:
        st.warning("请先完成初始配置")
        init_user_config()
        return
    
    # 获取用户进度
    user_progress = get_cached_user_progress()
    
    # 顶部进度条
    st.title(f"🎨 第{get_current_week()}周学习中心")
    st.markdown("---")
    
    # 进度显示
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("🏆 总积分", f"{user_progress['total_points']}")
    with col2:
        st.metric("🔥 连续打卡", f"{user_progress['current_streak']}天")
    with col3:
        st.metric("📈 当前等级", f"Lv.{user_progress['level']}")
    with col4:
        st.metric("📚 掌握词汇", f"{user_progress['vocabulary_mastered']}")
    
    st.markdown("---")
    
    # 本周主题
    weekly_themes = get_cached_weekly_themes()
    current_week = get_current_week()
    current_theme = next((t for t in weekly_themes if t['week_number'] == current_week), None)
    
    if current_theme:
        st.subheader(f"📌 本周主题：{current_theme['theme_name']}")
        st.info(current_theme['theme_description'])
        st.caption(f"🎯 重点技能：{current_theme['focus_skills']} | 📚 词汇目标：{current_theme['vocabulary_count']}个")
    
    st.markdown("---")
    
    # 今日任务
    today = datetime.now().strftime('%Y-%m-%d')
    st.subheader(f"📅 今日学习任务 ({today})")
    
    daily_tasks = get_cached_daily_tasks(today)
    
    if not daily_tasks:
        st.info("🎉 今天没有安排学习任务，休息一下或自由探索吧！")
        return
    
    # 显示任务卡片
    for task in daily_tasks:
        show_task_card(task)
    
    # 本周主题预览
    st.markdown("---")
    show_weekly_themes_preview()
    
    # 学习统计
    st.markdown("---")
    show_learning_stats()

def get_current_week():
    """获取当前是第几周"""
    user_config = get_cached_user_config()
    if not user_config:
        return 1
    
    start_date = datetime.strptime(user_config['start_date'], '%Y-%m-%d')
    today = datetime.now()
    days_diff = (today - start_date).days
    return min(days_diff // 7 + 1, 12)

def show_task_card(task):
    """显示任务卡片"""
    with st.container():
        col1, col2, col3 = st.columns([1, 3, 1])
        
        with col1:
            st.markdown(f"<h1 style='text-align: center;'>{task['task_icon']}</h1>", unsafe_allow_html=True)
        
        with col2:
            st.subheader(task['task_title'])
            st.write(task['task_description'])
            
            # 任务信息
            col_info1, col_info2, col_info3 = st.columns(3)
            with col_info1:
                st.caption(f"⏱️ {task['estimated_minutes']}分钟")
            with col_info2:
                st.caption(f"📊 难度: {task['difficulty_level']}/5")
            with col_info3:
                st.caption(f"🎯 积分: {task['points']}")
            
            # 资源链接
            if task['resource_url']:
                st.markdown(f"[🔗 学习资源]({task['resource_url']})")
        
        with col3:
            if task['completed']:
                st.success("✅ 已完成")
                st.caption(f"+{task['points']}积分")
            else:
                if st.button("完成", key=f"complete_{task['id']}"):
                    db.complete_task(task['id'])
                    db.add_points(task['points'])
                    db.update_streak()
                    st.cache_data.clear()
                    st.rerun()
        
        st.markdown("---")

def show_weekly_themes_preview():
    """显示本周主题预览"""
    st.subheader("📅 12周主题预览")
    
    weekly_themes = get_cached_weekly_themes()
    current_week = get_current_week()
    
    # 显示4周为一个区块
    cols = st.columns(3)
    for i in range(0, min(12, len(weekly_themes)), 4):
        col_idx = i // 4
        if col_idx < len(cols):
            with cols[col_idx]:
                for j in range(4):
                    if i + j < len(weekly_themes):
                        theme = weekly_themes[i + j]
                        week_num = theme['week_number']
                        
                        # 卡片样式
                        is_current = week_num == current_week
                        bg_color = "#4CAF50" if is_current else "#f0f0f0"
                        text_color = "white" if is_current else "black"
                        
                        card_html = f"""
                        <div style="
                            background-color: {bg_color};
                            color: {text_color};
                            padding: 12px;
                            border-radius: 8px;
                            margin-bottom: 8px;
                        ">
                            <div style="font-weight: bold;">第{week_num}周</div>
                            <div>{theme['theme_name']}</div>
                            {'<div style="font-size: 12px;">🎯 进行中</div>' if is_current else ''}
                        </div>
                        """
                        st.markdown(card_html, unsafe_allow_html=True)

def show_learning_stats():
    """显示学习统计"""
    st.subheader("📊 学习统计")
    
    # 获取最近7天的任务完成情况
    today = datetime.now()
    last_7_days = [(today - timedelta(days=i)).strftime('%Y-%m-%d') for i in range(6, -1, -1)]
    
    completion_data = []
    for date in last_7_days:
        tasks = db.get_daily_tasks(date)
        if tasks:
            completed = sum(1 for t in tasks if t['completed'])
            total = len(tasks)
            completion_rate = completed / total if total > 0 else 0
        else:
            completion_rate = 0
        
        completion_data.append({
            'date': date,
            'rate': completion_rate
        })
    
    # 创建柱状图
    if completion_data:
        df = pd.DataFrame(completion_data)
        df['date_short'] = df['date'].apply(lambda x: x[5:])  # MM-DD格式
        
        fig = go.Figure(data=[
            go.Bar(
                x=df['date_short'],
                y=df['rate'],
                marker_color=['#4CAF50' if rate > 0.5 else '#FF9800' for rate in df['rate']],
                text=[f"{rate*100:.0f}%" for rate in df['rate']],
                textposition='auto'
            )
        ])
        
        fig.update_layout(
            title="最近7天任务完成率",
            yaxis=dict(range=[0, 1], tickformat=".0%"),
            height=300,
            margin=dict(l=20, r=20, t=40, b=20)
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    # 技能分布
    st.subheader("🎯 技能训练分布")
    
    # 模拟数据（实际应从数据库统计）
    skills_data = {
        '词汇': 35,  # 重点满足词汇需求
        '听力': 30,  # 重点满足听力需求
        '综合': 20,
        '阅读': 10,
        '写作': 5
    }
    
    fig2 = go.Figure(data=[
        go.Pie(
            labels=list(skills_data.keys()),
            values=list(skills_data.values()),
            hole=0.3,
            marker_colors=['#4CAF50', '#2196F3', '#FF9800', '#9C27B0', '#607D8B']
        )
    ])
    
    fig2.update_layout(
        height=300,
        margin=dict(l=20, r=20, t=20, b=20)
    )
    
    st.plotly_chart(fig2, use_container_width=True)

def main():
    """主函数"""
    # 初始化session_state
    if 'regenerate_plan' not in st.session_state:
        st.session_state.regenerate_plan = False
    
    # 侧边栏
    with st.sidebar:
        st.title("⚙️ 主题周设置")
        st.markdown("---")
        
        # 显示当前用户信息
        user_config = get_cached_user_config()
        if user_config:
            st.subheader("👤 我的配置")
            st.write(f"**目标分数**: {user_config['target_score']}")
            st.write(f"**当前水平**: {user_config['current_level']}")
            st.write(f"**每日时间**: {user_config['daily_hours']}小时")
            st.write(f"**兴趣领域**: {', '.join(user_config['interests'])}")
            
            st.markdown("---")
            
            # 重新生成计划
            st.subheader("🔄 计划管理")
            if st.button("重新生成主题周计划", type="secondary", use_container_width=True):
                st.session_state.regenerate_plan = True
            
            if st.session_state.get('regenerate_plan', False):
                st.warning("⚠️ 重新生成将覆盖现有学习计划！")
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("确认重新生成", type="primary"):
                        with st.spinner("正在重新生成主题周计划..."):
                            db.clear_existing_data()
                            db.generate_theme_based_tasks(weeks=12)
                            st.cache_data.clear()
                            st.cache_resource.clear()
                            st.session_state.regenerate_plan = False
                            st.success("✅ 主题周计划已重新生成！")
                            st.rerun()
                with col2:
                    if st.button("取消", type="secondary"):
                        st.session_state.regenerate_plan = False
                        st.rerun()
            
            st.markdown("---")
            
            # 学习模式说明
            st.subheader("🎨 学习模式说明")
            st.info("""
            **主题周学习特点**：
            1. 每周一个有趣主题
            2. 每天3个短任务（15-25分钟）
            3. 重点训练词汇和听力
            4. 游戏化激励系统
            5. 个性化兴趣匹配
            """)
        
        st.markdown("---")
        st.caption("💡 提示：点击上方按钮可重新生成个性化主题周计划")

    # 主内容
    if not user_config:
        init_user_config()
    else:
        main_dashboard()

if __name__ == "__main__":
    main()