#!/usr/bin/env python3
"""
自测学习计划和对应跳转资料是否一致
检查资源链接是否国内可访问
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database_v3 import IELTSCoachDBV3
from datetime import datetime, timedelta
import requests
from urllib.parse import urlparse

def check_resource_accessibility(url, timeout=5):
    """检查资源是否可访问"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.head(url, headers=headers, timeout=timeout, allow_redirects=True)
        return response.status_code == 200
    except requests.exceptions.Timeout:
        return "超时"
    except requests.exceptions.ConnectionError:
        return "连接失败"
    except requests.exceptions.RequestException as e:
        return f"错误: {str(e)}"
    except:
        return "未知错误"

def check_domestic_access(url):
    """检查是否国内可访问（简单判断）"""
    domestic_domains = [
        'xdf.cn', 'xdf.com', 'xdf.com.cn',  # 新东方
        'cambridgeenglish.org',  # 剑桥（通常可访问）
        'ielts.org',  # 雅思官网（通常可访问）
        'bilibili.com', 'youku.com', 'iqiyi.com',  # 国内视频
        'zhihu.com', 'csdn.net', 'jianshu.com',  # 国内社区
        'baidu.com', 'sogou.com'  # 国内搜索
    ]
    
    foreign_domains = [
        'youtube.com', 'youtu.be',  # YouTube（需科学上网）
        'ted.com',  # TED（有时可访问，有时需科学上网）
        'englishclub.com',  # 国外英语学习网站
        'ieltsliz.com',  # 国外雅思网站
        'ieltsadvantage.com'  # 国外雅思网站
    ]
    
    domain = urlparse(url).netloc.lower()
    
    for d in domestic_domains:
        if d in domain:
            return "国内可访问"
    
    for d in foreign_domains:
        if d in domain:
            return "可能需要科学上网"
    
    return "未知"

def self_test():
    """自测函数"""
    print("🧪 学习计划与资源链接自测")
    print("=" * 70)
    
    # 创建测试数据库
    test_db_path = "self_test.db"
    if os.path.exists(test_db_path):
        os.remove(test_db_path)
    
    db = IELTSCoachDBV3(db_path=test_db_path)
    
    # 设置测试配置
    print("\n📋 测试配置：")
    interests = ["科技", "美食", "旅行", "艺术"]
    print(f"  兴趣领域: {', '.join(interests)}")
    
    db.set_user_config(
        target_score=7.5,
        current_level="四级440+",
        daily_hours=2,
        vocab_tool="墨墨背单词",
        interests=interests
    )
    
    # 生成2周计划测试
    print("\n🚀 生成2周学习计划...")
    db.generate_theme_based_tasks(weeks=2)
    
    # 获取主题
    print("\n📅 生成的主题：")
    weekly_themes = db.get_weekly_themes()
    for theme in weekly_themes[:2]:
        print(f"  第{theme['week_number']}周: {theme['theme_name']}")
        print(f"     描述: {theme['theme_description'][:50]}...")
    
    # 检查第1周所有任务
    print("\n🔍 第1周资源链接详细检查：")
    start_date = datetime.now()
    
    all_issues = []
    
    for day in range(7):
        date_str = (start_date + timedelta(days=day)).strftime('%Y-%m-%d')
        tasks = db.get_daily_tasks(date_str)
        
        if tasks:
            theme = tasks[0]['theme_name']
            print(f"\n  📍 第{day+1}天 - 主题: {theme}")
            
            for task in tasks:
                print(f"\n    {task['task_icon']} {task['task_title']}")
                print(f"      描述: {task['task_description']}")
                print(f"      链接: {task['resource_url']}")
                
                # 检查主题与链接一致性
                theme_in_url = False
                url_lower = task['resource_url'].lower()
                theme_lower = theme.lower()
                
                # 简单关键词匹配检查
                theme_keywords = {
                    '人工智能': ['ai', 'artificial', 'intelligence', 'technology'],
                    '数字生活': ['digital', 'life', 'technology'],
                    '饮食文化': ['food', 'culture', 'cooking', 'eating'],
                    '健康饮食': ['health', 'healthy', 'diet', 'eating'],
                    '旅游体验': ['travel', 'tourism', 'journey', 'adventure'],
                    '文化遗产': ['culture', 'heritage', 'history', 'tradition'],
                    '视觉艺术': ['art', 'visual', 'painting', 'design'],
                    '设计思维': ['design', 'thinking', 'creative', 'innovation']
                }
                
                if theme in theme_keywords:
                    for keyword in theme_keywords[theme]:
                        if keyword in url_lower:
                            theme_in_url = True
                            break
                
                if theme_in_url:
                    print(f"      ✅ 主题一致性: 链接包含主题相关关键词")
                else:
                    print(f"      ⚠️ 主题一致性: 链接可能不直接匹配主题")
                    all_issues.append(f"主题'{theme}'的任务链接可能不匹配: {task['resource_url']}")
                
                # 检查国内访问性
                access_status = check_domestic_access(task['resource_url'])
                print(f"      🌐 国内访问: {access_status}")
                
                if "可能需要科学上网" in access_status:
                    all_issues.append(f"可能需要科学上网: {task['resource_url']}")
                
                # 实际访问测试（可选，较慢）
                # print("      测试访问中...", end="")
                # accessibility = check_resource_accessibility(task['resource_url'])
                # print(f" {accessibility}")
    
    # 资源类型分析
    print("\n📊 资源类型分析：")
    
    resource_stats = {}
    for week in range(1, 3):
        for day in range(7):
            date = start_date + timedelta(days=(week-1)*7 + day)
            date_str = date.strftime('%Y-%m-%d')
            tasks = db.get_daily_tasks(date_str)
            
            for task in tasks:
                url = task['resource_url']
                domain = urlparse(url).netloc
                resource_stats[domain] = resource_stats.get(domain, 0) + 1
    
    print("  使用的域名分布：")
    for domain, count in sorted(resource_stats.items(), key=lambda x: x[1], reverse=True):
        print(f"    • {domain}: {count}个链接")
    
    # 问题汇总
    print("\n⚠️ 发现的问题：")
    if all_issues:
        for i, issue in enumerate(all_issues[:10], 1):  # 只显示前10个问题
            print(f"  {i}. {issue}")
        if len(all_issues) > 10:
            print(f"  还有{len(all_issues)-10}个问题...")
    else:
        print("  ✅ 未发现明显问题")
    
    # 清理
    os.remove(test_db_path)
    
    print("\n✅ 自测完成！")
    print("\n🎯 需要改进的地方：")
    print("  1. 部分国外资源可能需要科学上网")
    print("  2. 需要替换为国内可访问的双语资源")
    print("  3. 确保每个链接都直接对应主题内容")
    print("\n🚀 下一步：更新为国内双语资源")

if __name__ == "__main__":
    self_test()