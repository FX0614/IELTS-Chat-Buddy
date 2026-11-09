#!/usr/bin/env python3
"""
测试智能学习计划生成器
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database_v2 import IELTSCoachDB
from datetime import datetime, timedelta

def test_smart_plan_generation():
    """测试智能学习计划生成"""
    print("🧪 测试智能学习计划生成器")
    print("=" * 50)
    
    # 创建测试数据库
    test_db_path = "test_ielts_coach.db"
    if os.path.exists(test_db_path):
        os.remove(test_db_path)
    
    db = IELTSCoachDB(db_path=test_db_path)
    
    # 设置测试用户配置（四级440+）
    print("\n📋 设置测试用户配置：")
    print("  - 目标分数: 7.5")
    print("  - 当前水平: 四级440+")
    print("  - 每日时间: 2小时")
    
    db.set_user_config(
        target_score=7.5,
        current_level="四级440+",
        daily_hours=2,
        vocab_tool="墨墨背单词"
    )
    
    # 生成智能学习计划
    print("\n🚀 生成智能学习计划...")
    db.generate_initial_plan(weeks=12)
    
    # 获取第1周的计划
    print("\n📅 第1周学习计划示例：")
    start_date = datetime.now()
    for day in range(7):
        date_str = (start_date + timedelta(days=day)).strftime('%Y-%m-%d')
        daily_plan = db.get_daily_plan(date_str)
        
        print(f"\n  📍 第{day+1}天 ({date_str}):")
        for task in daily_plan:
            print(f"    • {task['task_type']}: {task['task_description']}")
            print(f"      难度: {task['difficulty_level']}/5, 阶段: {task['phase']}")
    
    # 获取第5周的计划（专项提升阶段）
    print("\n📈 第5周学习计划示例（专项提升阶段）：")
    week5_start = start_date + timedelta(days=28)
    date_str = week5_start.strftime('%Y-%m-%d')
    daily_plan = db.get_daily_plan(date_str)
    
    print(f"\n  📍 第5周第1天 ({date_str}):")
    for task in daily_plan:
        print(f"    • {task['task_type']}: {task['task_description']}")
        print(f"      难度: {task['difficulty_level']}/5, 阶段: {task['phase']}")
    
    # 获取第9周的计划（冲刺模考阶段）
    print("\n🏃 第9周学习计划示例（冲刺模考阶段）：")
    week9_start = start_date + timedelta(days=56)
    date_str = week9_start.strftime('%Y-%m-%d')
    daily_plan = db.get_daily_plan(date_str)
    
    print(f"\n  📍 第9周第1天 ({date_str}):")
    for task in daily_plan:
        print(f"    • {task['task_type']}: {task['task_description']}")
        print(f"      难度: {task['difficulty_level']}/5, 阶段: {task['phase']}")
    
    # 统计各阶段任务数量
    print("\n📊 学习计划统计：")
    with db.get_connection() as conn:
        cursor = conn.cursor()
        
        # 统计各阶段任务数
        cursor.execute('''
            SELECT phase, COUNT(*) as task_count 
            FROM study_plans 
            GROUP BY phase
        ''')
        phase_stats = cursor.fetchall()
        
        print("  各阶段任务分布：")
        for stat in phase_stats:
            print(f"    • {stat['phase']}: {stat['task_count']}个任务")
        
        # 统计各技能类型任务数
        cursor.execute('''
            SELECT task_type, COUNT(*) as task_count 
            FROM study_plans 
            GROUP BY task_type
        ''')
        skill_stats = cursor.fetchall()
        
        print("\n  各技能任务分布：")
        for stat in skill_stats:
            skill_name = {
                'listening': '听力',
                'reading': '阅读',
                'writing': '写作',
                'speaking': '口语'
            }.get(stat['task_type'], stat['task_type'])
            print(f"    • {skill_name}: {stat['task_count']}个任务")
    
    # 清理测试数据库
    os.remove(test_db_path)
    
    print("\n✅ 智能学习计划测试完成！")
    print("\n🎯 计划特点总结：")
    print("  1. 分3个阶段：基础巩固 → 专项提升 → 冲刺模考")
    print("  2. 根据四级440+水平定制难度梯度")
    print("  3. 每天重点训练2项技能，避免疲劳")
    print("  4. 周日为复习和模考日")
    print("  5. 资源链接针对每个阶段和技能精心选择")

if __name__ == "__main__":
    test_smart_plan_generation()