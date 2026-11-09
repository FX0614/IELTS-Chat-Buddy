"""
雅思备考智能教练 - 增强防丢失版
解决跳转后丢失资源的问题
添加学习流程引导和状态保存
"""
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import json
import random
import time
from typing import List, Dict, Optional

# ==================== 增强内存数据库 ====================
class EnhancedMemoryDatabase:
    """增强版内存数据库，支持状态保存和防丢失"""
    
    def __init__(self):
        self.user_config = None
        self.tasks = {}
        self.progress = {}
        self.themes = {}
        self.learning_sessions = {}  # 跟踪学习会话
        self.init_data()
    
    def init_data(self):
        """初始化基础数据"""
        # 主题数据
        self.themes = {
            "科技": {
                "name": "人工智能与未来科技",
                "description": "探索AI、机器学习、未来科技趋势",
                "color": "#4A90E2"
            },
            "美食": {
                "name": "世界美食文化",
                "description": "了解不同国家的饮食文化、烹饪技巧",
                "color": "#F5A623"
            },
            "旅行": {
                "name": "环球旅行与文化",
                "description": "探索世界各地的文化、风景、旅行体验",
                "color": "#7ED321"
            },
            "艺术": {
                "name": "现代艺术与设计",
                "description": "欣赏现代艺术、设计理念、创意表达",
                "color": "#BD10E0"
            }
        }
        
        # 增强资源库 - 添加学习时长建议
        self.resources = {
            "词汇积累": [
                {
                    "name": "雅思官方词汇练习",
                    "url": "https://www.ielts.org/en-us/prepare/free-ielts-practice-tests/vocabulary",
                    "platform": "🏛️ 雅思官方",
                    "description": "雅思官方免费词汇练习测试",
                    "suggested_time": 20,  # 建议学习时间（分钟）
                    "learning_tips": "重点学习高频词汇和搭配用法"
                },
                {
                    "name": "British Council词汇资源",
                    "url": "https://learnenglish.britishcouncil.org/vocabulary",
                    "platform": "🇬🇧 British Council",
                    "description": "英国文化协会官方词汇学习资源",
                    "suggested_time": 25,
                    "learning_tips": "按主题分类学习，注意发音和例句"
                }
            ],
            "听力训练": [
                {
                    "name": "雅思官方听力练习",
                    "url": "https://www.ielts.org/en-us/prepare/free-ielts-practice-tests/listening",
                    "platform": "🏛️ 雅思官方",
                    "description": "雅思官方免费听力练习测试",
                    "suggested_time": 30,
                    "learning_tips": "第一遍听大意，第二遍听细节，第三遍跟读"
                },
                {
                    "name": "BBC Learning English",
                    "url": "https://www.bbc.co.uk/learningenglish/english/features/6-minute-english",
                    "platform": "🇬🇧 BBC英语",
                    "description": "BBC 6分钟英语，适合听力训练",
                    "suggested_time": 25,
                    "learning_tips": "利用6分钟短音频，反复听直到完全理解"
                }
            ],
            "阅读练习": [
                {
                    "name": "雅思官方阅读练习",
                    "url": "https://www.ielts.org/en-us/prepare/free-ielts-practice-tests/reading",
                    "platform": "🏛️ 雅思官方",
                    "description": "雅思官方免费阅读练习测试",
                    "suggested_time": 40,
                    "learning_tips": "先快速浏览问题，再带着问题阅读"
                },
                {
                    "name": "British Council阅读资源",
                    "url": "https://learnenglish.britishcouncil.org/skills/reading",
                    "platform": "🇬🇧 British Council",
                    "description": "英国文化协会官方阅读练习",
                    "suggested_time": 35,
                    "learning_tips": "注意文章结构和逻辑连接词"
                }
            ],
            "写作练习": [
                {
                    "name": "雅思官方写作指南",
                    "url": "https://www.ielts.org/en-us/prepare/free-ielts-practice-tests/writing",
                    "platform": "🏛️ 雅思官方",
                    "description": "雅思官方写作练习和评分标准",
                    "suggested_time": 45,
                    "learning_tips": "学习范文结构，注意语法和词汇多样性"
                },
                {
                    "name": "IELTS Liz写作技巧",
                    "url": "https://ieltsliz.com/ielts-writing-task-2/",
                    "platform": "✍️ IELTS Liz",
                    "description": "IELTS Liz的写作技巧和范文",
                    "suggested_time": 30,
                    "learning_tips": "重点学习不同题型的写作思路"
                }
            ]
        }
    
    def set_user_config(self, target_score, current_level, daily_hours, vocab_tool, interests, exam_date=None):
        """保存用户配置"""
        self.user_config = {
            "target_score": target_score,
            "current_level": current_level,
            "daily_hours": daily_hours,
            "vocab_tool": vocab_tool,
            "interests": interests,
            "exam_date": exam_date,
            "start_date": datetime.now().strftime("%Y-%m-%d")
        }
        return True
    
    def get_user_config(self):
        """获取用户配置"""
        return self.user_config
    
    def start_learning_session(self, task_id):
        """开始学习会话"""
        self.learning_sessions[task_id] = {
            "start_time": datetime.now(),
            "status": "in_progress"
        }
        return True
    
    def end_learning_session(self, task_id):
        """结束学习会话"""
        if task_id in self.learning_sessions:
            self.learning_sessions[task_id]["end_time"] = datetime.now()
            self.learning_sessions[task_id]["status"] = "completed"
        return True
    
    def get_learning_session(self, task_id):
        """获取学习会话状态"""
        return self.learning_sessions.get(task_id)
    
    def generate_daily_tasks(self, date_str=None):
        """生成每日任务"""
        if date_str is None:
            date_str = datetime.now().strftime("%Y-%m-%d")
        
        if date_str in self.tasks:
            return self.tasks[date_str]
        
        # 随机选择一个主题
        if self.user_config and "interests" in self.user_config:
            interests = self.user_config["interests"]
            if interests:
                theme = random.choice(interests)
            else:
                theme = random.choice(list(self.themes.keys()))
        else:
            theme = random.choice(list(self.themes.keys()))
        
        # 生成4个任务
        task_types = ["词汇积累", "听力训练", "阅读练习", "写作练习"]
        tasks = []
        
        for i, task_type in enumerate(task_types):
            # 从资源库中选择一个资源
            resources = self.resources.get(task_type, [])
            if resources:
                resource = random.choice(resources)
            else:
                resource = {
                    "name": f"{task_type}练习",
                    "url": "https://www.ielts.org",
                    "platform": "🏛️ 雅思官方",
                    "description": f"{task_type}基础练习",
                    "suggested_time": 20,
                    "learning_tips": "按建议时间完成学习"
                }
            
            task = {
                "id": f"{date_str}_{i}",
                "date": date_str,
                "type": task_type,
                "theme": theme,
                "title": f"{task_type} - {self.themes[theme]['name']}",
                "description": f"{self.themes[theme]['description']}。{resource['description']}",
                "duration": resource.get("suggested_time", 20),
                "resource_url": resource["url"],
                "resource_name": resource["name"],
                "platform": resource["platform"],
                "learning_tips": resource.get("learning_tips", "按建议时间完成学习"),
                "completed": False,
                "points": 10,
                "session_started": False
            }
            tasks.append(task)
        
        self.tasks[date_str] = tasks
        return tasks
    
    def get_daily_tasks(self, date_str=None):
        """获取每日任务"""
        if date_str is None:
            date_str = datetime.now().strftime("%Y-%m-%d")
        
        if date_str not in self.tasks:
            return self.generate_daily_tasks(date_str)
        
        return self.tasks[date_str]
    
    def complete_task(self, task_id):
        """完成任务"""
        for date_str, tasks in self.tasks.items():
            for task in tasks:
                if task["id"] == task_id:
                    task["completed"] = True
                    
                    # 更新进度
                    if date_str not in self.progress:
                        self.progress[date_str] = {"completed": 0, "total": 0, "points": 0}
                    
                    self.progress[date_str]["completed"] += 1
                    self.progress[date_str]["total"] = len(tasks)
                    self.progress[date_str]["points"] += task["points"]
                    
                    # 结束学习会话
                    self.end_learning_session(task_id)
                    
                    return True
        return False
    
    def get_user_progress(self):
        """获取用户进度"""
        total_completed = 0
        total_tasks = 0
        total_points = 0
        streak = 0
        
        # 计算连续打卡
        dates = sorted(self.progress.keys(), reverse=True)
        current_date = datetime.now().strftime("%Y-%m-%d")
        
        for i, date_str in enumerate(dates):
            progress = self.progress[date_str]
            total_completed += progress["completed"]
            total_tasks += progress["total"]
            total_points += progress["points"]
            
            # 检查连续打卡
            if i == 0 and date_str == current_date:
                streak += 1
            elif i > 0:
                prev_date = dates[i-1]
                date1 = datetime.strptime(date_str, "%Y-%m-%d")
                date2 = datetime.strptime(prev_date, "%Y-%m-%d")
                if (date2 - date1).days == 1:
                    streak += 1
                else:
                    break
        
        return {
            "total_completed": total_completed,
            "total_tasks": total_tasks,
            "total_points": total_points,
            "streak": streak,
            "completion_rate": (total_completed / total_tasks * 100) if total_tasks > 0 else 0
        }
    
    def get_weekly_themes(self):
        """获取本周主题"""
        return self.themes

# ==================== Streamlit应用 ====================
# 页面配置
st.set_page_config(
    page_title="雅思防丢失版",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 初始化session_state
if "db" not in st.session_state:
    st.session_state.db = EnhancedMemoryDatabase()

if "current_learning_task" not in st.session_state:
    st.session_state.current_learning_task = None

if "show_learning_guide" not in st.session_state:
    st.session_state.show_learning_guide = False

db = st.session_state.db

def show_learning_guide(task):
    """显示学习引导"""
    st.session_state.show_learning_guide = True
    st.session_state.current_learning_task = task
    
    st.success("🎯 学习引导已启动！")
    
    with st.expander("📖 详细学习步骤", expanded=True):
        st.markdown(f"""
        ### 第1步：准备学习
        - **任务类型**: {task['type']}
        - **主题**: {task['theme']}
        - **建议时间**: {task['duration']}分钟
        - **学习提示**: {task['learning_tips']}
        
        ### 第2步：开始学习
        1. **点击下方链接**（建议右键 → "在新标签页打开"）
        2. **专注学习** {task['duration']} 分钟
        3. **完成学习后返回此页面**
        
        ### 第3步：标记完成
        1. 返回此页面
        2. 点击"我已学完"按钮
        3. 获得 {task['points']} 积分
        4. 继续下一个任务
        
        ### ⏰ 学习计时器
        开始时间: {datetime.now().strftime('%H:%M:%S')}
        预计结束: {(datetime.now() + timedelta(minutes=task['duration'])).strftime('%H:%M:%S')}
        """)
        
        # 资源链接（大按钮样式）
        st.markdown(f"""
        <div style="text-align: center; margin: 20px 0;">
            <a href="{task['resource_url']}" target="_blank" style="
                display: inline-block;
                padding: 15px 30px;
                background-color: #4A90E2;
                color: white;
                text-decoration: none;
                border-radius: 8px;
                font-size: 18px;
                font-weight: bold;
                margin: 10px;
            ">
            🚀 点击开始学习：{task['resource_name']}
            </a>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("✅ 我已学完，标记完成", type="primary", use_container_width=True):
                db.complete_task(task["id"])
                st.session_state.show_learning_guide = False
                st.session_state.current_learning_task = None
                st.rerun()
        
        with col2:
            if st.button("↩️ 返回任务列表", use_container_width=True):
                st.session_state.show_learning_guide = False
                st.rerun()

def init_user_config():
    """初始化用户配置页面"""
    st.title("🛡️ 雅思备考防丢失版")
    st.markdown("---")
    
    st.success("""
    🎯 **防丢失功能**：
    - ✅ 学习流程引导 - 明确每一步操作
    - ✅ 学习会话跟踪 - 记录学习状态
    - ✅ 返回提醒机制 - 防止跳转后迷失
    - ✅ 学习计时器 - 掌握学习进度
    - ✅ 状态保存 - 刷新不丢失进度
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
            default=["科技", "美食", "旅行"],
            max_selections=4
        )
        
        submitted = st.form_submit_button("开始防丢失学习之旅")
        
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
            
            st.success("✅ 配置保存成功！页面将自动刷新...")
            st.rerun()

def main_dashboard():
    """主仪表板"""
    # 检查是否在学习引导中
    if st.session_state.show_learning_guide and st.session_state.current_learning_task:
        show_learning_guide(st.session_state.current_learning_task)
        return
    
    user_config = db.get_user_config()
    if not user_config:
        init_user_config()
        return
    
    # 侧边栏
    with st.sidebar:
        st.title("📊 学习统计")
        
        progress = db.get_user_progress()
        
        st.metric("总积分", f"{progress['total_points']}分")
        st.metric("连续打卡", f"{progress['streak']}天")
        st.metric("完成率", f"{progress['completion_rate']:.1f}%")
        
        st.markdown("---")
        st.subheader("🎯 你的配置")
        st.write(f"目标分数: {user_config['target_score']}")
        st.write(f"当前水平: {user_config['current_level']}")
        st.write(f"每日时间: {user_config['daily_hours']}小时")
        st.write(f"背单词工具: {user_config['vocab_tool']}")
        st.write(f"兴趣领域: {', '.join(user_config['interests'])}")
        
        if st.button("🔄 重新生成今日任务"):
            today = datetime.now().strftime("%Y-%m-%d")
            if today