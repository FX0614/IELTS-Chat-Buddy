"""
雅思备考智能教练 - 简化版数据库
只关注：学习计划 + 打卡记录 + 用户配置
"""
import sqlite3
import json
import os
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class IELTSCoachDB:
    def __init__(self, db_path: str = None):
        # 支持环境变量配置数据库路径，便于部署
        if db_path is None:
            db_path = os.getenv("IELTS_DB_PATH", "ielts_coach.db")
        self.db_path = db_path
        self.init_db()
    
    def get_connection(self):
        """获取数据库连接"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def init_db(self):
        """初始化数据库表"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # 用户配置表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_config (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    target_score REAL NOT NULL,  -- 目标分数 7.5
                    current_level TEXT NOT NULL, -- 当前水平 "四级440+"
                    daily_hours INTEGER NOT NULL, -- 每日学习时间 2
                    vocab_tool TEXT,             -- 词汇工具 "墨墨背单词"
                    start_date TEXT NOT NULL,    -- 开始日期
                    exam_date TEXT,              -- 考试日期（可选）
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # 学习计划表（系统生成的每日任务）
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS study_plans (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    plan_date TEXT NOT NULL,      -- 任务日期
                    task_type TEXT NOT NULL,      -- 听力/阅读/写作/口语
                    task_description TEXT NOT NULL, -- 任务描述
                    resource_url TEXT,            -- 资源链接
                    difficulty_level INTEGER,     -- 难度等级 1-5
                    week_number INTEGER,          -- 第几周
                    phase TEXT,                   -- 阶段：基础/专项/冲刺
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(plan_date, task_type)
                )
            ''')
            
            # 打卡记录表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS checkins (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    checkin_date TEXT NOT NULL,   -- 打卡日期
                    task_type TEXT NOT NULL,      -- 听力/阅读/写作/口语
                    completed BOOLEAN DEFAULT 0,  -- 是否完成
                    completed_at TIMESTAMP,       -- 完成时间
                    notes TEXT,                   -- 备注（可选）
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(checkin_date, task_type)
                )
            ''')
            
            # 能力评估表（用于雷达图）
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS skill_assessments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    assessment_date TEXT NOT NULL, -- 评估日期
                    listening_score REAL,          -- 听力分数 1-9
                    reading_score REAL,           -- 阅读分数
                    writing_score REAL,           -- 写作分数  
                    speaking_score REAL,          -- 口语分数
                    overall_score REAL,           -- 总分
                    notes TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
            logger.info("雅思教练数据库初始化完成")
    
    # 用户配置相关
    def set_user_config(self, target_score: float, current_level: str, 
                       daily_hours: int, vocab_tool: str = "墨墨背单词",
                       exam_date: str = None) -> int:
        """设置用户配置"""
        start_date = datetime.now().strftime('%Y-%m-%d')
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            # 清空旧配置（只保留最新）
            cursor.execute("DELETE FROM user_config")
            
            cursor.execute('''
                INSERT INTO user_config 
                (target_score, current_level, daily_hours, vocab_tool, start_date, exam_date)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (target_score, current_level, daily_hours, vocab_tool, start_date, exam_date))
            conn.commit()
            return cursor.lastrowid
    
    def get_user_config(self) -> Optional[Dict]:
        """获取用户配置"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM user_config ORDER BY id DESC LIMIT 1")
            row = cursor.fetchone()
            return dict(row) if row else None
    
    # 学习计划相关
    def clear_existing_plans(self):
        """清除现有的学习计划"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM study_plans")
            cursor.execute("DELETE FROM checkins")
            conn.commit()
            logger.info("已清除现有学习计划和打卡记录")
    
    def generate_initial_plan(self, weeks: int = 12):
        """生成智能学习计划 - 根据四级440+到雅思7.5的科学路径"""
        user_config = self.get_user_config()
        if not user_config:
            raise ValueError("请先设置用户配置")
        
        # 清除旧计划
        self.clear_existing_plans()
        
        start_date = datetime.strptime(user_config['start_date'], '%Y-%m-%d')
        current_level = user_config['current_level']
        
        # 根据当前水平调整计划重点
        level_focus = {
            '四级440+': {
                'phase1_focus': '词汇语法基础',  # 第1-4周
                'phase2_focus': '题型技巧训练',  # 第5-8周
                'phase3_focus': '模考冲刺',      # 第9-12周
                'daily_hours': user_config['daily_hours']
            },
            '四级500+': {
                'phase1_focus': '强化基础',
                'phase2_focus': '技巧提升',
                'phase3_focus': '模考突破',
                'daily_hours': user_config['daily_hours']
            },
            '六级425+': {
                'phase1_focus': '雅思题型适应',
                'phase2_focus': '弱项强化',
                'phase3_focus': '高分冲刺',
                'daily_hours': user_config['daily_hours']
            }
        }
        
        focus = level_focus.get(current_level, level_focus['四级440+'])
        
        # 智能学习资源库 - 根据阶段和技能分类
        smart_resources = {
            # 阶段1：基础巩固（第1-4周）
            'phase1': {
                'listening': [
                    {'desc': '基础听力训练 - 雅思Section 1简单对话', 'url': 'https://www.xdf.cn/ielts/listening/', 'focus': '数字、日期、基础信息'},
                    {'desc': '听力词汇积累 - 常考场景词汇', 'url': 'https://www.ielts.org/en-us/prepare/free-ielts-practice-tests/listening', 'focus': '场景词汇'},
                    {'desc': '精听练习 - 短对话逐句听写', 'url': 'https://www.cambridgeenglish.org/exams-and-tests/ielts/preparation/', 'focus': '精听训练'}
                ],
                'reading': [
                    {'desc': '阅读基础 - 雅思Passage 1简单文章', 'url': 'https://www.xdf.cn/ielts/reading/', 'focus': '事实信息题'},
                    {'desc': '阅读词汇 - 高频同义替换', 'url': 'https://ieltsliz.com/ielts-reading-lessons-information-and-tips/', 'focus': '同义替换'},
                    {'desc': '长难句分析 - 基础语法巩固', 'url': 'https://www.ieltsadvantage.com/reading/', 'focus': '句子结构'}
                ],
                'writing': [
                    {'desc': '写作基础 - Task 1图表描述模板', 'url': 'https://www.xdf.cn/ielts/writing/', 'focus': '图表描述'},
                    {'desc': '基础语法复习 - 时态、语态', 'url': 'https://ieltsliz.com/ielts-writing-task-2-lessons-and-tips/', 'focus': '语法基础'},
                    {'desc': '简单句型练习 - 主谓宾结构', 'url': 'https://www.ieltsadvantage.com/writing-task-2/', 'focus': '句型结构'}
                ],
                'speaking': [
                    {'desc': '口语基础 - Part 1简单问题回答', 'url': 'https://www.xdf.cn/ielts/speaking/', 'focus': '个人信息'},
                    {'desc': '发音练习 - 音标和重音', 'url': 'https://ieltsliz.com/ielts-speaking-free-lessons-essential-tips/', 'focus': '发音'},
                    {'desc': '简单对话练习 - 日常话题', 'url': 'https://www.ieltsadvantage.com/speaking/', 'focus': '流利度'}
                ]
            },
            # 阶段2：专项提升（第5-8周）
            'phase2': {
                'listening': [
                    {'desc': '听力提升 - Section 2&3对话理解', 'url': 'https://www.xdf.cn/ielts/listening/', 'focus': '细节理解'},
                    {'desc': '笔记技巧训练 - 关键信息捕捉', 'url': 'https://www.ielts.org/en-us/prepare/free-ielts-practice-tests/listening', 'focus': '笔记技巧'},
                    {'desc': '多选题训练 - 选项分析', 'url': 'https://www.cambridgeenglish.org/exams-and-tests/ielts/preparation/', 'focus': '多选题'}
                ],
                'reading': [
                    {'desc': '阅读技巧 - Passage 2中等难度', 'url': 'https://www.xdf.cn/ielts/reading/', 'focus': '段落匹配'},
                    {'desc': '快速阅读训练 - 扫读和略读', 'url': 'https://ieltsliz.com/ielts-reading-lessons-information-and-tips/', 'focus': '阅读速度'},
                    {'desc': '判断题训练 - True/False/Not Given', 'url': 'https://www.ieltsadvantage.com/reading/', 'focus': '判断题'}
                ],
                'writing': [
                    {'desc': '写作提升 - Task 2议论文结构', 'url': 'https://www.xdf.cn/ielts/writing/', 'focus': '文章结构'},
                    {'desc': '论证技巧 - 观点支持和反驳', 'url': 'https://ieltsliz.com/ielts-writing-task-2-lessons-and-tips/', 'focus': '论证'},
                    {'desc': '词汇升级 - 学术词汇使用', 'url': 'https://www.ieltsadvantage.com/writing-task-2/', 'focus': '词汇丰富度'}
                ],
                'speaking': [
                    {'desc': '口语提升 - Part 2个人陈述', 'url': 'https://www.xdf.cn/ielts/speaking/', 'focus': '连贯表达'},
                    {'desc': '话题扩展训练 - 2分钟陈述', 'url': 'https://ieltsliz.com/ielts-speaking-free-lessons-essential-tips/', 'focus': '内容扩展'},
                    {'desc': '语法准确性 - 时态和句式', 'url': 'https://www.ieltsadvantage.com/speaking/', 'focus': '语法'}
                ]
            },
            # 阶段3：冲刺模考（第9-12周）
            'phase3': {
                'listening': [
                    {'desc': '听力冲刺 - Section 4学术讲座', 'url': 'https://www.xdf.cn/ielts/listening/', 'focus': '学术听力'},
                    {'desc': '全真模考 - 完整听力测试', 'url': 'https://www.ielts.org/en-us/prepare/free-ielts-practice-tests/listening', 'focus': '模考'},
                    {'desc': '弱点突破 - 错题分析', 'url': 'https://www.cambridgeenglish.org/exams-and-tests/ielts/preparation/', 'focus': '错题分析'}
                ],
                'reading': [
                    {'desc': '阅读冲刺 - Passage 3高难度文章', 'url': 'https://www.xdf.cn/ielts/reading/', 'focus': '深度理解'},
                    {'desc': '时间管理训练 - 60分钟3篇文章', 'url': 'https://ieltsliz.com/ielts-reading-lessons-information-and-tips/', 'focus': '时间管理'},
                    {'desc': '难题突破 - 标题匹配和摘要填空', 'url': 'https://www.ieltsadvantage.com/reading/', 'focus': '难题技巧'}
                ],
                'writing': [
                    {'desc': '写作冲刺 - 高分范文分析', 'url': 'https://www.xdf.cn/ielts/writing/', 'focus': '范文学习'},
                    {'desc': '时间控制训练 - 40分钟完成', 'url': 'https://ieltsliz.com/ielts-writing-task-2-lessons-and-tips/', 'focus': '时间控制'},
                    {'desc': '语言精炼 - 避免重复和啰嗦', 'url': 'https://www.ieltsadvantage.com/writing-task-2/', 'focus': '语言精炼'}
                ],
                'speaking': [
                    {'desc': '口语冲刺 - Part 3深度讨论', 'url': 'https://www.xdf.cn/ielts/speaking/', 'focus': '深度交流'},
                    {'desc': '思维训练 - 快速组织观点', 'url': 'https://ieltsliz.com/ielts-speaking-free-lessons-essential-tips/', 'focus': '思维速度'},
                    {'desc': '发音语调 - 自然流畅表达', 'url': 'https://www.ieltsadvantage.com/speaking/', 'focus': '语音语调'}
                ]
            }
        }
        
        # 智能生成12周计划
        for week in range(weeks):
            # 确定当前阶段
            if week < 4:
                phase = 'phase1'
                phase_name = '基础巩固'
            elif week < 8:
                phase = 'phase2'
                phase_name = '专项提升'
            else:
                phase = 'phase3'
                phase_name = '冲刺模考'
            
            # 每周重点（根据当前水平调整）
            weekly_focus = {
                1: '适应雅思题型，建立学习习惯',
                2: '强化基础词汇和语法',
                3: '掌握基本解题技巧',
                4: '阶段复习和测试',
                5: '专项技巧训练',
                6: '弱项针对性突破',
                7: '模拟考试训练',
                8: '错题分析和改进',
                9: '全真模考开始',
                10: '时间管理训练',
                11: '弱点最后突破',
                12: '考前冲刺和心态调整'
            }
            
            for day in range(7):
                plan_date = (start_date + timedelta(days=week*7 + day)).strftime('%Y-%m-%d')
                
                # 根据星期几安排不同类型的任务
                day_type = day % 7
                
                # 周一、三、五：重点输入（听力+阅读）
                # 周二、四、六：重点输出（写作+口语）
                # 周日：复习和模考
                if day_type in [0, 2, 4]:  # 周一、三、五
                    task_combinations = [
                        ('listening', 'reading'),
                        ('listening', 'writing'),
                        ('reading', 'speaking')
                    ]
                elif day_type in [1, 3, 5]:  # 周二、四、六
                    task_combinations = [
                        ('writing', 'speaking'),
                        ('writing', 'listening'),
                        ('speaking', 'reading')
                    ]
                else:  # 周日
                    task_combinations = [
                        ('listening', 'reading', 'writing', 'speaking')
                    ]
                
                # 选择当天的任务组合
                task_combo = task_combinations[week % len(task_combinations)]
                
                for task_type in task_combo:
                    # 从对应阶段的资源中选择
                    phase_resources = smart_resources[phase][task_type]
                    resource_idx = (week * 7 + day) % len(phase_resources)
                    resource = phase_resources[resource_idx]
                    
                    # 智能调整难度
                    base_difficulty = 1 if phase == 'phase1' else (3 if phase == 'phase2' else 5)
                    day_adjustment = 0.2 * (day % 3)  # 每周内微调难度
                    difficulty = min(base_difficulty + day_adjustment, 5)
                    
                    # 生成任务描述
                    if day_type == 6:  # 周日是复习日
                        task_desc = f"周日复习 - {resource['focus']}"
                    else:
                        task_desc = f"{resource['desc']} - 重点：{resource['focus']}"
                    
                    self.add_study_plan(
                        plan_date=plan_date,
                        task_type=task_type,
                        task_description=task_desc,
                        resource_url=resource['url'],
                        difficulty_level=int(difficulty),
                        week_number=week + 1,
                        phase=phase_name
                    )
    
    def add_study_plan(self, plan_date: str, task_type: str, task_description: str,
                      resource_url: str = None, difficulty_level: int = 1,
                      week_number: int = 1, phase: str = '基础') -> int:
        """添加学习计划"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO study_plans 
                (plan_date, task_type, task_description, resource_url, difficulty_level, week_number, phase)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (plan_date, task_type, task_description, resource_url, difficulty_level, week_number, phase))
            conn.commit()
            return cursor.lastrowid
    
    def get_daily_plan(self, date: str = None) -> List[Dict]:
        """获取某日的学习计划"""
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM study_plans 
                WHERE plan_date = ?
                ORDER BY 
                    CASE task_type
                        WHEN 'listening' THEN 1
                        WHEN 'reading' THEN 2
                        WHEN 'writing' THEN 3
                        WHEN 'speaking' THEN 4
                        ELSE 5
                    END
            ''', (date,))
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
    
    # 打卡相关
    def checkin_task(self, date: str, task_type: str, completed: bool = True, notes: str = None):
        """打卡任务"""
        completed_at = datetime.now().isoformat() if completed else None
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO checkins 
                (checkin_date, task_type, completed, completed_at, notes)
                VALUES (?, ?, ?, ?, ?)
            ''', (date, task_type, 1 if completed else 0, completed_at, notes))
            conn.commit()
    
    def get_daily_checkins(self, date: str = None) -> Dict[str, bool]:
        """获取某日的打卡情况"""
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT task_type, completed FROM checkins 
                WHERE checkin_date = ?
            ''', (date,))
            rows = cursor.fetchall()
            return {row['task_type']: bool(row['completed']) for row in rows}
    
    def get_weekly_completion(self, start_date: str, end_date: str) -> Dict:
        """获取每周完成率"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT 
                    checkin_date,
                    COUNT(*) as total_tasks,
                    SUM(completed) as completed_tasks
                FROM checkins 
                WHERE checkin_date BETWEEN ? AND ?
                GROUP BY checkin_date
                ORDER BY checkin_date
            ''', (start_date, end_date))
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
    
    # 能力评估相关
    def add_skill_assessment(self, listening_score: float, reading_score: float,
                           writing_score: float, speaking_score: float,
                           overall_score: float = None, notes: str = None):
        """添加能力评估"""
        if overall_score is None:
            overall_score = (listening_score + reading_score + writing_score + speaking_score) / 4
        
        assessment_date = datetime.now().strftime('%Y-%m-%d')
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO skill_assessments 
                (assessment_date, listening_score, reading_score, writing_score, speaking_score, overall_score, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (assessment_date, listening_score, reading_score, writing_score, speaking_score, overall_score, notes))
            conn.commit()
    
    def get_latest_assessment(self) -> Optional[Dict]:
        """获取最新的能力评估"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM skill_assessments 
                ORDER BY assessment_date DESC 
                LIMIT 1
            ''')
            row = cursor.fetchone()
            return dict(row) if row else None

# 单例实例
db_instance = None

def get_db():
    """获取数据库实例"""
    global db_instance
    if db_instance is None:
        db_instance = IELTSCoachDB()
    return db_instance