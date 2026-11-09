#!/usr/bin/env python3
"""
快速测试脚本 - 验证当前代码生成的资源链接
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database_v3 import IELTSCoachDBV3
from datetime import datetime

def quick_test():
    """快速测试当前代码生成的资源链接"""
    print("🔍 快速测试当前代码资源链接")
    print("=" * 60)
    
    # 创建临时数据库文件
    import tempfile
    import atexit
    
    temp_db = tempfile.NamedTemporaryFile(suffix='.db', delete=False)
    temp_db.close()
    db_path = temp_db.name
    
    def cleanup():
        if os.path.exists(db_path):
            os.unlink(db_path)
    
    atexit.register(cleanup)
    
    db = IELTSCoachDBV3(db_path=db_path)
    
    # 设置测试配置
    print("\n📋 测试配置：")
    interests = ["科技", "美食"]
    print(f"  兴趣领域: {', '.join(interests)}")
    
    db.set_user_config(
        target_score=7.5,
        current_level="四级440+",
        daily_hours=2,
        vocab_tool="墨墨背单词",
        interests=interests
    )
    
    # 生成1天计划测试
    print("\n🚀 生成今日学习计划...")
    db.generate_theme_based_tasks(weeks=1)
    
    # 获取今日任务
    today = datetime.now().strftime('%Y-%m-%d')
    tasks = db.get_daily_tasks(today)
    
    if not tasks:
        print("❌ 没有生成任务")
        return
    
    theme = tasks[0]['theme_name']
    print(f"\n🎯 今日主题: {theme}")
    
    print("\n🔗 生成的资源链接：")
    for task in tasks:
        print(f"\n  {task['task_icon']} {task['task_title']}")
        print(f"    描述: {task['task_description']}")
        print(f"    链接: {task['resource_url']}")
        
        # 分析链接
        url = task['resource_url']
        if 'bilibili.com' in url:
            print(f"    ✅ 平台: B站（国内可访问，双语视频）")
        elif 'xdf.cn' in url:
            print(f"    ✅ 平台: 新东方（国内可访问，权威词汇）")
        elif 'zhihu.com' in url:
            print(f"    ✅ 平台: 知乎（国内可访问，双语文章）")
        elif 'open.163.com' in url:
            print(f"    ✅ 平台: 网易公开课（国内可访问，双语课程）")
        elif 'hjenglish.com' in url:
            print(f"    ✅ 平台: 沪江英语（国内可访问，英语学习）")
        elif 'ielts.org' in url:
            print(f"    ✅ 平台: 雅思官方（国内可访问）")
        elif 'youtube.com' in url or 'youtu.be' in url:
            print(f"    ❌ 平台: YouTube（需要科学上网）")
        elif 'ted.com' in url:
            print(f"    ⚠️ 平台: TED（有时需要科学上网）")
        elif 'englishclub.com' in url:
            print(f"    ❌ 平台: EnglishClub（需要科学上网）")
        elif 'ieltsliz.com' in url:
            print(f"    ❌ 平台: IELTS Liz（需要科学上网）")
        elif 'ieltsadvantage.com' in url:
            print(f"    ❌ 平台: IELTS Advantage（需要科学上网）")
        else:
            print(f"    ❓ 平台: 未知")
    
    # 统计
    print("\n📊 资源平台统计：")
    platforms = {}
    for task in tasks:
        url = task['resource_url']
        if 'bilibili.com' in url:
            platforms['B站'] = platforms.get('B站', 0) + 1
        elif 'xdf.cn' in url:
            platforms['新东方'] = platforms.get('新东方', 0) + 1
        elif 'zhihu.com' in url:
            platforms['知乎'] = platforms.get('知乎', 0) + 1
        elif 'open.163.com' in url:
            platforms['网易公开课'] = platforms.get('网易公开课', 0) + 1
        elif 'hjenglish.com' in url:
            platforms['沪江英语'] = platforms.get('沪江英语', 0) + 1
        elif 'ielts.org' in url:
            platforms['雅思官方'] = platforms.get('雅思官方', 0) + 1
        elif 'youtube.com' in url or 'youtu.be' in url:
            platforms['YouTube'] = platforms.get('YouTube', 0) + 1
        elif 'ted.com' in url:
            platforms['TED'] = platforms.get('TED', 0) + 1
        elif 'englishclub.com' in url:
            platforms['EnglishClub'] = platforms.get('EnglishClub', 0) + 1
    
    for platform, count in platforms.items():
        print(f"  • {platform}: {count}个链接")
    
    # 检查是否有国外资源
    foreign_platforms = ['YouTube', 'TED', 'EnglishClub', 'IELTS Liz', 'IELTS Advantage']
    has_foreign = any(p in platforms for p in foreign_platforms)
    
    print("\n✅ 测试完成！")
    if has_foreign:
        print("⚠️ 警告：检测到国外资源链接，代码可能不是最新版本")
        print("   请确保Streamlit Cloud使用的是最新代码")
    else:
        print("🎉 所有资源都是国内可访问的平台！")

if __name__ == "__main__":
    quick_test()