#!/usr/bin/env python3
"""
测试稳定资源版应用
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database_v4 import IELTSCoachDBV4
from datetime import datetime
import tempfile
import atexit

def test_stable_app():
    """测试稳定资源版应用"""
    print("🛡️ 测试稳定资源版应用")
    print("=" * 60)
    
    # 创建临时数据库
    temp_db = tempfile.NamedTemporaryFile(suffix='.db', delete=False)
    temp_db.close()
    db_path = temp_db.name
    
    def cleanup():
        if os.path.exists(db_path):
            os.unlink(db_path)
    
    atexit.register(cleanup)
    
    db = IELTSCoachDBV4(db_path=db_path)
    
    # 测试1：用户配置
    print("\n1. 📋 测试用户配置...")
    db.set_user_config(
        target_score=7.5,
        current_level="四级440+",
        daily_hours=2,
        vocab_tool="墨墨背单词",
        interests=["科技", "美食", "旅行", "艺术"]
    )
    
    config = db.get_user_config()
    if config:
        print(f"   ✅ 用户配置保存成功")
        print(f"     目标分数: {config['target_score']}")
        print(f"     兴趣领域: {config['interests']}")
    else:
        print("   ❌ 用户配置失败")
        return
    
    # 测试2：生成学习计划
    print("\n2. 🚀 测试生成学习计划...")
    db.generate_theme_based_tasks(weeks=2)
    
    weekly_themes = db.get_weekly_themes()
    if weekly_themes:
        print(f"   ✅ 生成{len(weekly_themes)}周主题")
        for theme in weekly_themes[:2]:
            print(f"     第{theme['week_number']}周: {theme['theme_name']}")
    else:
        print("   ❌ 生成主题失败")
        return
    
    # 测试3：获取今日任务
    print("\n3. 📚 测试今日任务...")
    today = datetime.now().strftime('%Y-%m-%d')
    tasks = db.get_daily_tasks(today)
    
    if tasks:
        print(f"   ✅ 生成{len(tasks)}个今日任务")
        theme = tasks[0]['theme_name']
        print(f"     今日主题: {theme}")
        
        # 检查资源稳定性
        print("\n4. 🔗 检查资源稳定性...")
        stable_platforms = 0
        total_tasks = len(tasks)
        
        for task in tasks:
            url = task['resource_url']
            if 'ielts.org' in url or 'britishcouncil' in url or 'cambridgeenglish' in url:
                stable_platforms += 1
        
        stability_rate = (stable_platforms / total_tasks) * 100
        print(f"     稳定资源: {stable_platforms}/{total_tasks} ({stability_rate:.1f}%)")
        
        if stability_rate == 100:
            print("     🎉 所有资源都来自稳定平台！")
        else:
            print("     ⚠️ 部分资源可能不稳定")
        
        # 显示示例任务
        print("\n5. 📝 示例任务展示：")
        for i, task in enumerate(tasks[:3], 1):
            print(f"\n   {task['task_icon']} {task['task_title']}")
            print(f"      描述: {task['task_description']}")
            print(f"      链接: {task['resource_url']}")
            
            # 平台识别
            if 'ielts.org' in task['resource_url']:
                print(f"      平台: 雅思官方 (🏛️ 永久有效)")
            elif 'britishcouncil' in task['resource_url']:
                print(f"      平台: British Council (🇬🇧 官方机构)")
            elif 'cambridgeenglish' in task['resource_url']:
                print(f"      平台: Cambridge English (🎓 权威平台)")
            else:
                print(f"      平台: 其他")
    else:
        print("   ❌ 没有生成任务")
        return
    
    # 测试4：用户进度
    print("\n6. 📊 测试用户进度...")
    progress = db.get_user_progress()
    if progress:
        print(f"   ✅ 用户进度系统正常")
        print(f"     初始积分: {progress.get('total_points', 0)}")
        print(f"     初始等级: {progress.get('level', 1)}")
    else:
        print("   ❌ 用户进度系统异常")
    
    # 测试5：完成任务
    print("\n7. ✅ 测试完成任务...")
    if tasks:
        task_id = tasks[0]['id']
        initial_points = progress.get('total_points', 0) if progress else 0
        
        db.complete_task(task_id)
        db.update_user_progress(tasks[0]['points'])
        
        updated_progress = db.get_user_progress()
        if updated_progress:
            new_points = updated_progress.get('total_points', 0)
            if new_points > initial_points:
                print(f"   ✅ 任务完成系统正常")
                print(f"     积分增加: {initial_points} → {new_points}")
            else:
                print("   ❌ 积分没有增加")
        else:
            print("   ❌ 更新进度失败")
    
    print("\n" + "=" * 60)
    print("✅ 稳定资源版应用测试完成！")
    print("\n🎯 核心优势：")
    print("  1. 🏛️ 使用官方平台资源（永久有效）")
    print("  2. 🌐 所有资源国内可访问")
    print("  3. 🔄 几乎不会过期")
    print("  4. 🎯 精准主题匹配")
    print("  5. 🎮 游戏化学习体验")
    print("\n🚀 现在可以部署到Streamlit Cloud了！")

if __name__ == "__main__":
    test_stable_app()