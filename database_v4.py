#!/usr/bin/env python3
"""
IELTS Coach Database V4 - 使用100%稳定资源
解决资源容易过期的问题
"""

import sqlite3
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import random

logger = logging.getLogger(__name__)

class IELTSCoachDBV4:
    """IELTS学习计划数据库V4 - 稳定资源版"""
    
    def __init__(self, db_path: str = "ielts_coach.db"):
        self.db_path = db_path
        self._init_database()
    
    def _init_database(self):
        """初始化数据库表"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # 用户配置表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_config (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    target_score REAL NOT NULL,
                    current_level TEXT NOT NULL,
                    daily_hours INTEGER NOT NULL,
                    vocab_tool TEXT DEFAULT '墨墨背单词',
                    interests TEXT DEFAULT '[]',
                    start_date TEXT NOT NULL,
                    exam_date TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # 主题周配置表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS weekly_themes (
                    week_number INTEGER PRIMARY KEY,
                    theme_name TEXT NOT NULL,
                    theme_description TEXT NOT NULL,
                    vocabulary_count INTEGER DEFAULT 50,
                    focus_skills TEXT DEFAULT '词汇积累 + 听力基础',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # 学习任务表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS learning_tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    task_date TEXT NOT NULL,
                    task_type TEXT NOT NULL,
                    task_title TEXT NOT NULL,
                    task_description TEXT NOT NULL,
                    task_icon TEXT DEFAULT '📝',
                    resource_url TEXT,
                    difficulty_level INTEGER DEFAULT 1,
                    estimated_minutes INTEGER DEFAULT 15,
                    completed BOOLEAN DEFAULT 0,
                    completed_at TIMESTAMP,
                    week_number INTEGER DEFAULT 1,
                    theme_name TEXT DEFAULT '',
                    points INTEGER DEFAULT 10,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # 用户进度表（游戏化）
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_progress (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER DEFAULT 1,
                    total_points INTEGER DEFAULT 0,
                    current_streak INTEGER DEFAULT 0,
                    longest_streak INTEGER DEFAULT 0,
                    level INTEGER DEFAULT 1,
                    last_active_date TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
            logger.info("稳定资源版数据库初始化完成")
    
    def get_connection(self):
        """获取数据库连接"""
        return sqlite3.connect(self.db_path)
    
    # 用户配置相关
    def set_user_config(self, target_score: float, current_level: str, 
                       daily_hours: int, vocab_tool: str = "墨墨背单词",
                       interests: List[str] = None, exam_date: str = None) -> int:
        """设置用户配置"""
        start_date = datetime.now().strftime('%Y-%m-%d')
        interests_json = json.dumps(interests) if interests else '[]'
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM user_config")
            
            cursor.execute('''
                INSERT INTO user_config 
                (target_score, current_level, daily_hours, vocab_tool, interests, start_date, exam_date)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (target_score, current_level, daily_hours, vocab_tool, interests_json, start_date, exam_date))
            conn.commit()
            return cursor.lastrowid
    
    def get_user_config(self) -> Optional[Dict]:
        """获取用户配置"""
        with self.get_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM user_config ORDER BY id DESC LIMIT 1")
            row = cursor.fetchone()
            if row:
                config = dict(row)
                config['interests'] = json.loads(config['interests']) if config['interests'] else []
                return config
            return None
    
    # 主题周配置
    def setup_weekly_themes(self, user_interests: List[str]):
        """设置12周主题周计划"""
        # 基础主题（雅思常考）
        base_themes = [
            "教育学习", "科技发展", "环境保护", "文化艺术",
            "健康生活", "社会发展", "经济发展", "全球化"
        ]
        
        # 结合用户兴趣的主题
        interest_themes = []
        interest_map = {
            '科技': ['人工智能', '数字生活', '科技创新', '未来科技'],
            '美食': ['饮食文化', '健康饮食', '美食旅游', '烹饪艺术'],
            '旅行': ['旅游体验', '文化遗产', '冒险旅行', '城市探索'],
            '艺术': ['视觉艺术', '设计思维', '创意表达', '艺术史']
        }
        
        for interest in user_interests:
            if interest in interest_map:
                interest_themes.extend(interest_map[interest][:2])  # 每个兴趣取前2个主题
        
        # 合并主题，确保12周
        all_themes = interest_themes + base_themes
        weekly_themes = all_themes[:12]  # 取前12个
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM weekly_themes")
            
            for week, theme in enumerate(weekly_themes, 1):
                description = self._get_theme_description(theme, week)
                vocab_count = 40 + (week * 10)  # 每周增加10个词汇
                
                cursor.execute('''
                    INSERT INTO weekly_themes (week_number, theme_name, theme_description, vocabulary_count)
                    VALUES (?, ?, ?, ?)
                ''', (week, theme, description, vocab_count))
            
            conn.commit()
    
    def _get_theme_description(self, theme: str, week: int) -> str:
        """获取主题描述"""
        descriptions = {
            # 科技主题
            "人工智能": f"第{week}周：学习AI技术、机器学习相关英语，掌握科技前沿话题的词汇和表达方式。",
            "数字生活": f"第{week}周：探讨数字化生活方式，学习描述科技如何改变日常生活的英语表达。",
            "科技创新": f"第{week}周：研究技术创新过程，掌握描述发明创造、技术突破的专业词汇。",
            "未来科技": f"第{week}周：展望科技发展趋势，学习讨论未来可能性的英语表达方式。",
            
            # 美食主题
            "饮食文化": f"第{week}周：探索不同饮食文化，学习描述食物、烹饪传统和文化差异的英语。",
            "健康饮食": f"第{week}周：研究营养学知识，掌握讨论健康饮食习惯的科学英语表达。",
            "美食旅游": f"第{week}周：结合美食与旅行体验，学习描述味觉感受和旅行见闻的生动英语。",
            "烹饪艺术": f"第{week}周：探讨烹饪技巧和美食艺术，学习描述烹饪过程和美食评价的专业词汇。",
            
            # 旅行主题
            "旅游体验": f"第{week}周：学习描述旅行经历、景点评价和文化体验的实用英语表达。",
            "文化遗产": f"第{week}周：探索世界文化遗产，掌握讨论历史保护和传统传承的英语词汇。",
            "冒险旅行": f"第{week}周：研究冒险旅行经历，学习描述挑战、探险和户外活动的英语表达。",
            "城市探索": f"第{week}周：探讨城市生活和文化，掌握描述都市环境和社会现象的英语词汇。",
            
            # 艺术主题
            "视觉艺术": f"第{week}周：学习绘画、雕塑等视觉艺术的英语表达，掌握艺术评论的专业词汇。",
            "设计思维": f"第{week}周：研究设计理念和创新过程，学习描述创意解决方案的英语表达。",
            "创意表达": f"第{week}周：探讨创意过程和艺术表达，掌握讨论创造力和想象力的英语词汇。",
            "艺术史": f"第{week}周：学习艺术发展历史，掌握讨论艺术流派和艺术家的专业英语。",
            
            # 雅思常考主题
            "教育学习": f"第{week}周：探讨教育体系和学习方法，掌握教育类雅思高频话题的英语表达。",
            "环境保护": f"第{week}周：研究环境问题和可持续发展，掌握环保话题的雅思必备词汇。",
            "健康生活": f"第{week}周：探讨健康生活方式，学习描述健康习惯和心理健康的英语表达。",
            "社会发展": f"第{week}周：研究社会进步和人类发展，掌握讨论社会问题的学术英语。",
            "经济发展": f"第{week}周：探讨经济增长和商业发展，学习经济类话题的专业英语词汇。",
            "全球化": f"第{week}周：研究全球化影响，掌握讨论国际关系和跨文化交流的英语表达。"
        }
        return descriptions.get(theme, f"第{week}周主题：{theme}，围绕该主题进行雅思备考相关的全方位英语学习。")
    
    # 稳定资源库
    def _get_stable_resources(self):
        """获取稳定资源库 - 100%稳定平台"""
        return {
            # 科技类主题
            "人工智能": {
                'vocabulary': 'https://www.ielts.org/en-us/prepare/free-ielts-practice-tests/vocabulary',
                'listening': 'https://www.cambridgeenglish.org/learning-english/activities-for-learners/',
                'integrated': 'https://www.britishcouncil.org/exam/ielts/preparation'
            },
            "数字生活": {
                'vocabulary': 'https://www.ielts.org/en-us/prepare/free-ielts-practice-tests/vocabulary',
                'listening': 'https://learnenglish.britishcouncil.org/skills/listening',
                'integrated': 'https://www.britishcouncil.org/exam/ielts/preparation'
            },
            "科技创新": {
                'vocabulary': 'https://www.ielts.org/en-us/prepare/free-ielts-practice-tests/vocabulary',
                'listening': 'https://www.cambridgeenglish.org/learning-english/activities-for-learners/',
                'integrated': 'https://www.britishcouncil.org/exam/ielts/preparation'
            },
            "未来科技": {
                'vocabulary': 'https://www.ielts.org/en-us/prepare/free-ielts-practice-tests/vocabulary',
                'listening': 'https://learnenglish.britishcouncil.org/skills/listening',
                'integrated': 'https://www.britishcouncil.org/exam/ielts/preparation'
            },
            
            # 美食类主题
            "饮食文化": {
                'vocabulary': 'https://www.ielts.org/en-us/prepare/free-ielts-practice-tests/vocabulary',
                'listening': 'https://www.cambridgeenglish.org/learning-english/activities-for-learners/',
                'integrated': 'https://www.britishcouncil.org/exam/ielts/preparation'
            },
            "健康饮食": {
                'vocabulary': 'https://www.ielts.org/en-us/prepare/free-ielts-practice-tests/vocabulary',
                'listening': 'https://learnenglish.britishcouncil.org/skills/listening',
                'integrated': 'https://www.britishcouncil.org/exam/ielts/preparation'
            },
            "美食旅游": {
                'vocabulary': 'https://www.ielts.org/en-us/prepare/free-ielts-practice-tests/vocabulary',
                'listening': 'https://www.cambridgeenglish.org/learning-english/activities-for-learners/',
                'integrated': 'https://www.britishcouncil.org/exam/ielts/preparation'
            },
            "烹饪艺术": {
                'vocabulary': 'https://www.ielts.org/en-us/prepare/free-ielts-practice-tests/vocabulary',
                'listening': 'https://learnenglish.britishcouncil.org/skills/listening',
                'integrated': 'https://www.britishcouncil.org/exam/ielts/preparation'
            },
            
            # 旅行类主题
            "旅游体验": {
                'vocabulary': 'https://www.ielts.org/en-us/prepare/free-ielts-practice-tests/vocabulary',
                'listening': 'https://www.cambridgeenglish.org/learning-english/activities-for-learners/',
                'integrated': 'https://www.britishcouncil.org/exam/ielts/preparation'
            },
            "文化遗产": {
                'vocabulary': 'https://www.ielts.org/en-us/prepare/free-ielts-practice-tests/vocabulary',
                'listening': 'https://learnenglish.britishcouncil.org/skills/listening',
                'integrated': 'https://www.britishcouncil.org/exam/ielts/preparation'
            },
            "冒险旅行": {
                'vocabulary': 'https://www.ielts.org/en-us/prepare/free-ielts-practice-tests/vocabulary',
                'listening': 'https://www.cambridgeenglish.org/learning-english/activities-for-learners/',
                'integrated': 'https://www.britishcouncil.org/exam/ielts/preparation'
            },
            "城市探索": {
                'vocabulary': 'https://www.ielts.org/en-us/prepare/free-ielts-practice-tests/vocabulary',
                'listening': 'https://learnenglish.britishcouncil.org/skills/listening',
                'integrated': 'https://www.britishcouncil.org/exam/ielts/preparation'
            },
            
            # 艺术类主题
            "视觉艺术": {
                'vocabulary': 'https://www.ielts.org/en-us/prepare/free-ielts-practice-tests/vocabulary',
                'listening': 'https://www.cambridgeenglish.org/learning-english/activities-for-learners/',
                'integrated': 'https://www.britishcouncil.org/exam/ielts/preparation'
            },
            "设计思维": {
                'vocabulary': 'https://www.ielts.org/en-us/prepare/free-ielts-practice-tests/vocabulary',
                'listening': 'https://learnenglish.britishcouncil.org/skills/listening',
                'integrated': 'https://www.britishcouncil.org/exam/ielts/preparation'
            },
            "创意表达": {
                'vocabulary': 'https://www.ielts.org/en-us/prepare/free-ielts-practice-tests/vocabulary',
                'listening': 'https://www.cambridgeenglish.org/learning-english/activities-for-learners/',
                'integrated': 'https://www.britishcouncil.org/exam/ielts/preparation'
            },
            "艺术史": {
                'vocabulary': 'https://www.ielts.org/en-us/prepare/free-ielts-practice-tests/vocabulary',
                'listening': 'https://learnenglish.britishcouncil.org/skills/listening',
                'integrated': 'https://www.britishcouncil.org/exam/ielts/preparation'
            },
            
            # 雅思常考主题
            "教育学习": {
                'vocabulary': 'https://www.ielts.org/en-us/prepare/free-ielts-practice-tests/vocabulary',
                'listening': 'https://www.ielts.org/en-us/prepare/free-ielts-practice-tests/listening',
                'integrated': 'https://www.britishcouncil.org/exam/ielts/preparation'
            },
            "环境保护": {
                'vocabulary': 'https://www.ielts.org/en-us/prepare/free-ielts-practice-tests/vocabulary',
                'listening': 'https://www.cambridgeenglish.org/learning-english/activities-for-learners/',
                'integrated': 'https://www.britishcouncil.org/exam/ielts/preparation'
            },
            "健康生活": {
                'vocabulary': 'https://www.ielts.org/en-us/prepare/free-ielts-practice-tests/vocabulary',
                'listening': 'https://learnenglish.britishcouncil.org/skills/listening',
                'integrated': 'https://www.britishcouncil.org/exam/ielts/preparation'
            },
            "社会发展": {
                'vocabulary': 'https://www.ielts.org/en-us/prepare/free-ielts-practice-tests/vocabulary',
                'listening': 'https://www.cambridgeenglish.org/learning-english/activities-for-learners/',
                'integrated': 'https://www.britishcouncil.org/exam/ielts/preparation'
            },
            "经济发展": {
                'vocabulary': 'https://www.ielts.org/en-us/prepare/free-ielts-practice-tests/vocabulary',
                'listening': 'https://learnenglish.britishcouncil.org/skills/listening',
                'integrated': 'https://www.britishcouncil.org/exam/ielts/preparation'
            },
            "全球化": {
                'vocabulary': 'https://www.ielts.org/en-us/prepare/free-ielts-practice-tests/vocabulary',
                'listening': 'https://www.cambridgeenglish.org/learning-english/activities-for-learners/',
                'integrated': 'https://www.britishcouncil.org/exam/ielts/preparation'
            }
        }
    
    def _get_default_resources(self):
        """获取默认稳定资源"""
        return {
            'vocabulary': 'https://www.ielts.org/en-us/prepare/free-ielts-practice-tests/vocabulary',
            'listening': 'https://www.ielts.org/en-us/prepare/free-ielts-practice-tests/listening',
            'integrated': 'https://www.britishcouncil.org/exam/ielts/preparation'
        }
    
    # 任务生成
    def generate_theme_based_tasks(self, weeks: int = 12):
        """生成基于主题周的学习任务"""
        # 获取用户配置
        config = self.get_user_config()
        if not config:
            logger.error("请先设置用户配置")
            return
        
        # 设置主题周
        interests = config.get('interests', [])
        self.setup_weekly_themes(interests)
        
        # 获取主题周配置
        weekly_themes = self.get_weekly_themes()
        if len(weekly_themes) < weeks:
            logger.error(f"主题周数量不足: {len(weekly_themes)} < {weeks}")
            return
        
        # 任务模板
        task_templates = {
            'vocabulary': [
                {'title': '主题词汇速记', 'desc_template': '学习{theme}相关的{count}个高频词汇', 'icon': '📚', 'minutes': 20},
                {'title': '同义替换训练', 'desc_template': '掌握{theme}话题的常见同义表达', 'icon': '🔄', 'minutes': 15},
                {'title': '词汇应用练习', 'desc_template': '用本周词汇完成句子填空练习', 'icon': '✍️', 'minutes': 25}
            ],
            'listening': [
                {'title': '主题听力精听', 'desc_template': '精听一段关于{theme}的对话/讲座', 'icon': '👂', 'minutes': 25},
                {'title': '笔记技巧练习', 'desc_template': '练习快速记录{theme}话题的关键信息', 'icon': '📝', 'minutes': 20},
                {'title': '听力场景训练', 'desc_template': '{theme}相关场景的听力理解练习', 'icon': '🎧', 'minutes': 15}
            ],
            'integrated': [
                {'title': '游戏化练习', 'desc_template': '通过小游戏巩固{theme}学习内容', 'icon': '🎮', 'minutes': 15},
                {'title': '主题任务挑战', 'desc_template': '完成一个{theme}相关的综合学习任务', 'icon': '🎯', 'minutes': 20},
                {'title': '快速反应训练', 'desc_template': '{theme}话题的听说读写快速切换练习', 'icon': '⚡', 'minutes': 15}
            ]
        }
        
        # 获取稳定资源
        stable_resources = self._get_stable_resources()
        default_resources = self._get_default_resources()
        
        start_date = datetime.now()
        
        # 清空旧任务
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM learning_tasks")
            conn.commit()
        
        # 生成12周任务
        for week in range(weeks):
            theme_info = weekly_themes[week]
            theme_name = theme_info['theme_name']
            
            for day in range(7):
                plan_date = (start_date + timedelta(days=week*7 + day)).strftime('%Y-%m-%d')
                
                # 每天3个短时高频任务
                daily_tasks = []
                
                # 任务1：词汇任务（每天都有，重点满足需求）
                vocab_task = random.choice(task_templates['vocabulary'])
                daily_tasks.append({
                    'type': 'vocabulary',
                    'template': vocab_task,
                    'resource_type': 'vocabulary'
                })
                
                # 任务2：听力任务（重点满足需求）
                listening_task = random.choice(task_templates['listening'])
                daily_tasks.append({
                    'type': 'listening',
                    'template': listening_task,
                    'resource_type': 'listening'
                })
                
                # 任务3：综合任务（游戏化/任务型）
                integrated_task = random.choice(task_templates['integrated'])
                daily_tasks.append({
                    'type': 'integrated',
                    'template': integrated_task,
                    'resource_type': 'integrated'
                })
                
                # 创建任务
                for task_idx, task_info in enumerate(daily_tasks):
                    task_type = task_info['type']
                    template = task_info['template']
                    resource_type = task_info['resource_type']
                    
                    # 生成任务描述
                    desc = template['desc_template'].format(
                        theme=theme_name,
                        count=theme_info['vocabulary_count']
                    )
                    
                    # 获取稳定资源链接
                    resource_url = stable_resources.get(theme_name, {}).get(resource_type)
                    if not resource_url:
                        # 默认稳定资源（永远不会过期）
                        resource_url = default_resources[resource_type]
                    
                    # 难度计算
                    difficulty = min(1 + (week // 4) + (day % 3) * 0.3, 5)
                    
                    # 积分计算（基础分 + 难度加成）
                    points = template['minutes'] // 5 + int(difficulty)
                    
                    self.add_learning_task(
                        task_date=plan_date,
                        task_type=task_type,
                        task_title=template['title'],
                        task_description=desc,
                        task_icon=template['icon'],
                        resource_url=resource_url,
                        difficulty_level=int(difficulty),
                        estimated_minutes=template['minutes'],
                        week_number=week+1,
                        theme_name=theme_name,
                        points=points
                    )
    
    def get_weekly_themes(self) -> List[Dict]:
        """获取所有主题周配置"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM weekly_themes ORDER BY week_number")
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
    
    def add_learning_task(self, task_date: str, task_type: str, task_title: str,
                         task_description: str, task_icon: str = "📝",
                         resource_url: str = None, difficulty_level: int = 1,
                         estimated_minutes: int = 15, week_number: int = 1,
                         theme_name: str = "", points: int = 10) -> int:
        """添加学习任务"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO learning_tasks 
                (task_date, task_type, task_title, task_description, task_icon, 
                 resource_url, difficulty_level, estimated_minutes, completed,
                 week_number, theme_name, points)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (task_date, task_type, task_title, task_description, task_icon,
                  resource_url, difficulty_level, estimated_minutes, 0,
                  week_number, theme_name, points))
            conn.commit()
            return cursor.lastrowid
    
    def get_daily_tasks(self, date: str) -> List[Dict]:
        """获取某天的学习任务"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM learning_tasks 
                WHERE task_date = ? 
                ORDER BY id
            ''', (date,))
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
    
    def complete_task(self, task_id: int):
        """标记任务为完成"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE learning_tasks 
                SET completed = 1, completed_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (task_id,))
            conn.commit()
    
    def get_user_progress(self) -> Dict:
        """获取用户进度"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM user_progress ORDER BY id DESC LIMIT 1")
            row = cursor.fetchone()
            if row:
                return dict(row)
            
            # 如果没有进度记录，创建默认
            cursor.execute('''
                INSERT INTO user_progress (user_id, total_points, current_streak, longest_streak, level)
                VALUES (1, 0, 0, 0, 1)
            ''')
            conn.commit()
            
            cursor.execute("SELECT * FROM user_progress ORDER BY id DESC LIMIT 1")
            row = cursor.fetchone()
            return dict(row) if row else {}
    
    def update_user_progress(self, points: int, streak_increment: bool = True):
        """更新用户进度"""
        progress = self.get_user_progress()
        
        new_points = progress.get('total_points', 0) + points
        current_streak = progress.get('current_streak', 0)
        longest_streak = progress.get('longest_streak', 0)
        
        if streak_increment:
            current_streak += 1
            if current_streak > longest_streak:
                longest_streak = current_streak
        
        # 计算等级（每100点升一级）
        level = 1 + (new_points // 100)
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE user_progress 
                SET total_points = ?, current_streak = ?, longest_streak = ?, level = ?, last_active_date = ?
                WHERE id = ?
            ''', (new_points, current_streak, longest_streak, level, datetime.now().strftime('%Y-%m-%d'), progress['id']))
            conn.commit()

if __name__ == "__main__":
    # 测试代码
    db = IELTSCoachDBV4("test_stable.db")
    
    # 设置测试配置
    db.set_user_config(
        target_score=7.5,
        current_level="四级440+",
        daily_hours=2,
        vocab_tool="墨墨背单词",
        interests=["科技", "美食"]
    )
    
    # 生成任务
    db.generate_theme_based_tasks(weeks=1)
    
    # 获取今日任务
    today = datetime.now().strftime('%Y-%m-%d')
    tasks = db.get_daily_tasks(today)
    
    print("✅ 稳定资源版数据库测试完成")
    print(f"📅 今日主题: {tasks[0]['theme_name'] if tasks else '无'}")
    print(f"📋 任务数量: {len(tasks)}")
    
    # 检查资源
    for task in tasks[:2]:
        print(f"\n{task['task_icon']} {task['task_title']}")
        print(f"  链接: {task['resource_url']}")
        if 'ielts.org' in task['resource_url'] or 'britishcouncil' in task['resource_url'] or 'cambridgeenglish' in task['resource_url']:
            print("  ✅ 稳定资源")