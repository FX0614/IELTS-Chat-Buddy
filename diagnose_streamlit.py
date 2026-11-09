#!/usr/bin/env python3
"""
诊断Streamlit Cloud应用状态
"""

import requests
import json
import time
from datetime import datetime

def check_streamlit_app(app_url):
    """检查Streamlit应用状态"""
    print(f"🔍 检查Streamlit应用: {app_url}")
    print("=" * 60)
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    try:
        # 尝试访问应用
        print("1. 尝试访问应用...")
        response = requests.get(app_url, headers=headers, timeout=10, allow_redirects=True)
        
        print(f"   状态码: {response.status_code}")
        print(f"   最终URL: {response.url}")
        
        if response.status_code == 200:
            # 检查页面内容
            content = response.text
            if "Streamlit" in content:
                print("   ✅ 检测到Streamlit应用")
                
                # 检查可能的错误信息
                if "not found" in content.lower() or "error" in content.lower():
                    print("   ⚠️ 页面可能包含错误信息")
                
                # 检查应用版本
                if "ielts_coach_optimized" in content:
                    print("   📄 检测到: ielts_coach_optimized.py (旧版本)")
                elif "ielts_coach_theme" in content:
                    print("   📄 检测到: ielts_coach_theme.py (主题周版本)")
                elif "ielts_coach" in content:
                    print("   📄 检测到: ielts_coach.py (原始版本)")
                else:
                    print("   ❓ 无法确定应用版本")
                
                # 检查资源链接
                if "englishclub.com" in content:
                    print("   🌐 检测到国外资源: englishclub.com")
                if "ted.com" in content:
                    print("   🌐 检测到国外资源: ted.com")
                if "ieltsliz.com" in content:
                    print("   🌐 检测到国外资源: ieltsliz.com")
                if "xdf.cn" in content:
                    print("   🇨🇳 检测到国内资源: xdf.cn (新东方)")
                if "bilibili.com" in content:
                    print("   🇨🇳 检测到国内资源: bilibili.com (B站)")
                if "zhihu.com" in content:
                    print("   🇨🇳 检测到国内资源: zhihu.com (知乎)")
                    
            else:
                print("   ❌ 不是Streamlit应用或页面异常")
                
        elif response.status_code == 404:
            print("   ❌ 应用不存在 (404)")
            print("   可能原因:")
            print("   • 应用已被删除")
            print("   • 应用名称错误")
            print("   • Streamlit Cloud配置问题")
            
        elif response.status_code == 502 or response.status_code == 503:
            print("   ⚠️ 服务器错误，应用可能正在部署或重启")
            
        else:
            print(f"   ❓ 未知状态码: {response.status_code}")
            
    except requests.exceptions.Timeout:
        print("   ⏱️ 连接超时，应用可能正在启动")
    except requests.exceptions.ConnectionError:
        print("   🔌 连接失败，应用可能不存在或网络问题")
    except Exception as e:
        print(f"   ❌ 检查失败: {str(e)}")

def check_github_repo():
    """检查GitHub仓库状态"""
    print("\n2. 检查GitHub仓库状态...")
    
    repo_url = "https://github.com/robinszabeeba-maker/ielts-coach"
    
    try:
        # 检查仓库是否存在
        api_url = "https://api.github.com/repos/robinszabeeba-maker/ielts-coach"
        response = requests.get(api_url, timeout=5)
        
        if response.status_code == 200:
            repo_info = response.json()
            print(f"   ✅ 仓库存在: {repo_info['full_name']}")
            print(f"   最后更新: {repo_info['updated_at']}")
            print(f"   默认分支: {repo_info['default_branch']}")
            print(f"   星标数: {repo_info['stargazers_count']}")
            print(f"   Fork数: {repo_info['forks_count']}")
            
            # 检查文件
            files_url = "https://api.github.com/repos/robinszabeeba-maker/ielts-coach/contents"
            files_response = requests.get(files_url, timeout=5)
            
            if files_response.status_code == 200:
                files = files_response.json()
                print(f"   文件数量: {len(files)}")
                
                # 检查关键文件
                key_files = ['ielts_coach_theme.py', 'database_v3.py', 'ielts_coach_optimized.py']
                for file in key_files:
                    found = any(f['name'] == file for f in files)
                    status = "✅" if found else "❌"
                    print(f"   {status} {file}")
                    
        elif response.status_code == 404:
            print("   ❌ GitHub仓库不存在 (404)")
        else:
            print(f"   ❓ GitHub API返回: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ 检查GitHub失败: {str(e)}")

def check_streamlit_cloud_pattern():
    """检查Streamlit Cloud常见问题模式"""
    print("\n3. 分析可能的问题模式...")
    
    print("   📋 常见问题及解决方案:")
    print("   A. 应用不存在 (404)")
    print("      • 原因: 应用被删除或名称错误")
    print("      • 解决: 重新创建应用")
    print("")
    print("   B. 应用使用旧代码")
    print("      • 原因: Streamlit Cloud缓存或配置错误")
    print("      • 解决: 重新部署或更新配置")
    print("")
    print("   C. 部署失败")
    print("      • 原因: 代码错误或依赖问题")
    print("      • 解决: 检查错误日志，修复代码")
    print("")
    print("   D. 网络问题")
    print("      • 原因: 网络限制或DNS问题")
    print("      • 解决: 检查网络，尝试不同网络")

def main():
    """主函数"""
    print("🚀 Streamlit Cloud应用诊断工具")
    print("=" * 60)
    
    # 应用URL
    app_url = "https://ielts-coach-robinszabeeba-maker.streamlit.app"
    
    # 执行检查
    check_streamlit_app(app_url)
    check_github_repo()
    check_streamlit_cloud_pattern()
    
    print("\n" + "=" * 60)
    print("🎯 诊断完成")
    print("\n📋 建议操作:")
    print("1. 登录Streamlit Cloud检查应用状态")
    print("2. 确认Main file path是ielts_coach_theme.py")
    print("3. 如果应用不存在，创建新应用")
    print("4. 如果应用存在但代码旧，重新部署")
    print("\n💡 提示: Streamlit Cloud有时需要几分钟同步GitHub更新")

if __name__ == "__main__":
    main()