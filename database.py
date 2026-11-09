"""
英语学习应用数据库模块
使用SQLite存储学习记录和资料
"""
import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Optional, Tuple
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EnglishLearningDB:
    def __init__(self, db_path: str = "english_learning.db"):
        self.db_path = db_path
        self.init_db()
    
    def get_connection(self):
        """获取数据库连接"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # 返回字典格式
        return conn
    
    def init_db(self):
        """初始化数据库表"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # 学习记录表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS study_records (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date TEXT NOT NULL,
                    duration_minutes INTEGER NOT NULL,
                    content TEXT NOT NULL,
                    resource_url TEXT,
                    tags TEXT,  -- JSON数组格式
                    category TEXT,  -- 听力/阅读/写作/口语/词汇/其他
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # 学习资料表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS learning_resources (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    url TEXT NOT NULL,
                    resource_type TEXT,  -- 文章/视频/PDF/音频/其他
                    tags TEXT,  -- JSON数组格式
                    description TEXT,
                    added_date TEXT NOT NULL,
                    last_reviewed TEXT,
                    review_count INTEGER DEFAULT 0
                )
            ''')
            
            # 学习目标表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS study_goals (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    goal_type TEXT NOT NULL,  -- 每日/每周/每月/雅思目标
                    target_value INTEGER NOT NULL,  -- 目标值（分钟/分数等）
                    start_date TEXT NOT NULL,
                    end_date TEXT,
                    status TEXT DEFAULT 'active',  -- active/completed/failed
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
            logger.info("数据库表初始化完成")
    
    # 学习记录相关方法
    def add_study_record(self, date: str, duration_minutes: int, content: str, 
                        resource_url: str = None, tags: List[str] = None, category: str = None) -> int:
        """添加学习记录"""
        tags_json = json.dumps(tags) if tags else '[]'
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO study_records (date, duration_minutes, content, resource_url, tags, category)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (date, duration_minutes, content, resource_url, tags_json, category))
            conn.commit()
            return cursor.lastrowid
    
    def get_study_records(self, start_date: str = None, end_date: str = None, 
                         category: str = None, limit: int = 100) -> List[Dict]:
        """获取学习记录"""
        query = "SELECT * FROM study_records WHERE 1=1"
        params = []
        
        if start_date:
            query += " AND date >= ?"
            params.append(start_date)
        if end_date:
            query += " AND date <= ?"
            params.append(end_date)
        if category:
            query += " AND category = ?"
            params.append(category)
        
        query += " ORDER BY date DESC LIMIT ?"
        params.append(limit)
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
    
    def get_study_stats(self, start_date: str = None, end_date: str = None) -> Dict:
        """获取学习统计"""
        query = """
            SELECT 
                COUNT(*) as total_sessions,
                SUM(duration_minutes) as total_minutes,
                AVG(duration_minutes) as avg_minutes,
                COUNT(DISTINCT date) as study_days
            FROM study_records
            WHERE 1=1
        """
        params = []
        
        if start_date:
            query += " AND date >= ?"
            params.append(start_date)
        if end_date:
            query += " AND date <= ?"
            params.append(end_date)
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            row = cursor.fetchone()
            return dict(row) if row else {}
    
    # 学习资料相关方法
    def add_learning_resource(self, title: str, url: str, resource_type: str = None,
                             tags: List[str] = None, description: str = None) -> int:
        """添加学习资料"""
        tags_json = json.dumps(tags) if tags else '[]'
        added_date = datetime.now().strftime('%Y-%m-%d')
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO learning_resources (title, url, resource_type, tags, description, added_date)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (title, url, resource_type, tags_json, description, added_date))
            conn.commit()
            return cursor.lastrowid
    
    def get_resources_for_review(self, limit: int = 5) -> List[Dict]:
        """获取需要复习的资料（最近未复习的）"""
        query = """
            SELECT * FROM learning_resources 
            WHERE last_reviewed IS NULL OR last_reviewed < date('now', '-7 days')
            ORDER BY added_date DESC
            LIMIT ?
        """
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (limit,))
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
    
    # 学习目标相关方法
    def add_study_goal(self, goal_type: str, target_value: int, 
                      start_date: str, end_date: str = None) -> int:
        """添加学习目标"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO study_goals (goal_type, target_value, start_date, end_date)
                VALUES (?, ?, ?, ?)
            ''', (goal_type, target_value, start_date, end_date))
            conn.commit()
            return cursor.lastrowid
    
    def get_active_goals(self) -> List[Dict]:
        """获取活跃的学习目标"""
        query = "SELECT * FROM study_goals WHERE status = 'active' ORDER BY created_at DESC"
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query)
            rows = cursor.fetchall()
            return [dict(row) for row in rows]

# 单例实例
db_instance = None

def get_db():
    """获取数据库实例（单例模式）"""
    global db_instance
    if db_instance is None:
        db_instance = EnglishLearningDB()
    return db_instance