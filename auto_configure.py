#!/usr/bin/env python3
"""
自动化配置Streamlit Cloud主文件路径
"""

import webbrowser
import time
import pyautogui
import sys
import os

def print_instructions():
    """打印操作指南"""
    print("=" * 70)
    print("🎯 Streamlit Cloud主文件路径自动化配置")
    print("=" * 70)
    print("\n🚀 这个脚本将指导你完成Streamlit Cloud配置修改")
    print("   只需要跟着步骤操作，3分钟完成！")
    print("\n📋 需要修改的内容：")
    print("   Main file path: [当前内容] → ielts_coach_stable.py")
    print("\n⚠️  注意：请确保你已经登录Streamlit Cloud")
    print("=" * 70)

def step1_open_streamlit_cloud():
    """步骤1：打开Streamlit Cloud"""
    print("\n1️⃣ 第一步：打开Streamlit Cloud")
    print("   • 正在打开浏览器...")
    
    url = "https://streamlit.io/cloud"
    webbrowser.open(url)
    
    print("   ✅ 浏览器已打开")
    print("   🔍 请确保你已经用GitHub登录")
    input("   ⏸️  登录后按回车继续...")

def step2_find_application():
    """步骤2：找到应用"""
    print("\n2️⃣ 第二步：找到你的应用")
    print("   📍 在Streamlit Cloud页面，你应该能看到：")
    print("   • 左侧：应用列表")
    print("   • 右侧：'New app'按钮")
    print("\n   🔍 找到 'ielts-coach' 应用")
    print("   👆 点击进入应用详情页")
    input("   ⏸️  进入应用详情页后按回车继续...")

def step3_open_settings():
    """步骤3：打开设置"""
    print("\n3️⃣ 第三步：打开设置")
    print("   📍 在应用详情页，寻找：")
    print("   • 右上角的 'Settings' 或 'Edit app' 按钮")
    print("   • 或者三个点菜单 '⋮' → 'Settings'")
    print("\n   👆 点击进入设置页面")
    input("   ⏸️  进入设置页面后按回车继续...")

def step4_modify_main_file():
    """步骤4：修改主文件路径"""
    print("\n4️⃣ 第四步：修改主文件路径")
    print("   📍 在设置页面，找到：")
    print("   • 'Main file path' 输入框")
    print("   • 当前可能是: ielts_coach_theme.py")
    print("\n   ✏️  修改为: ielts_coach_stable.py")
    print("   📋 复制这个内容: ielts_coach_stable.py")
    print("\n   👆 点击输入框，粘贴新内容")
    input("   ⏸️  修改后按回车继续...")

def step5_save_changes():
    """步骤5：保存更改"""
    print("\n5️⃣ 第五步：保存更改")
    print("   📍 找到保存按钮：")
    print("   • 'Save' 或 'Deploy' 或 'Update' 按钮")
    print("   • 通常是蓝色按钮")
    print("\n   👆 点击保存按钮")
    print("   ⏳ 等待部署完成（约1-2分钟）")
    input("   ⏸️  保存后按回车继续...")

def step6_verify_changes():
    """步骤6：验证更改"""
    print("\n6️⃣ 第六步：验证更改")
    print("   🔍 检查是否成功：")
    print("   1. 返回应用详情页")
    print("   2. 查看 'Main file' 显示")
    print("   3. 应该显示: ielts_coach_stable.py")
    print("\n   🌐 打开应用链接测试：")
    print("   https://ielts-coach-robinszabeeba-maker.streamlit.app")
    print("\n   ✅ 如果成功，重新生成学习计划")
    print("   🔄 在侧边栏点击'重新生成主题周学习计划'")

def create_quick_guide():
    """创建快速操作指南"""
    print("\n" + "=" * 70)
    print("📋 快速操作指南（保存备用）")
    print("=" * 70)
    print("\n1. 登录 https://streamlit.io/cloud")
    print("2. 找到 ielts-coach 应用，点击进入")
    print("3. 点击右上角 'Settings' 或 'Edit app'")
    print("4. 找到 'Main file path' 输入框")
    print("5. 修改为: ielts_coach_stable.py")
    print("6. 点击 'Save' 或 'Deploy'")
    print("7. 等待部署完成")
    print("8. 重新生成学习计划")
    print("=" * 70)

def main():
    """主函数"""
    print_instructions()
    
    # 询问用户是否准备好
    ready = input("\n🎯 你准备好开始了吗？(y/n): ").lower()
    if ready != 'y':
        print("❌ 取消操作")
        return
    
    # 执行步骤
    try:
        step1_open_streamlit_cloud()
        step2_find_application()
        step3_open_settings()
        step4_modify_main_file()
        step5_save_changes()
        step6_verify_changes()
        create_quick_guide()
        
        print("\n" + "=" * 70)
        print("🎉 配置完成！")
        print("=" * 70)
        print("\n✅ 稳定资源版应用已配置完成")
        print("🎯 现在所有学习资源都来自稳定平台，不会过期！")
        print("\n📱 立即体验：")
        print("   https://ielts-coach-robinszabeeba-maker.streamlit.app")
        
    except KeyboardInterrupt:
        print("\n❌ 用户中断操作")
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        print("💡 请按照快速操作指南手动操作")

if __name__ == "__main__":
    # 检查依赖
    try:
        import webbrowser
        import pyautogui
    except ImportError:
        print("❌ 缺少依赖，请安装：")
        print("   pip install pyautogui")
        sys.exit(1)
    
    main()