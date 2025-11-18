#!/usr/bin/env python3
"""
Agent功能测试脚本
"""
import sys
import os

# 添加backend目录到Python路径
sys.path.insert(0, os.path.dirname(__file__))

from agent.core import get_agent_core
from config.settings import settings
from loguru import logger

# 配置日志
logger.add("test_agent.log", rotation="10 MB")


def test_dialogue_flow():
    """测试完整对话流程"""
    print("=" * 60)
    print("🧪 测试Agent对话流程")
    print("=" * 60)
    print()
    
    # 检查配置
    print(f"✅ LLM Provider: {settings.LLM_PROVIDER}")
    if settings.LLM_PROVIDER == "sambanova":
        print(f"✅ Model: {settings.SAMBANOVA_MODEL}")
        if not settings.SAMBANOVA_API_KEY:
            print("❌ 错误：SAMBANOVA_API_KEY未设置")
            print("   请在.env文件中配置您的SambaNova API密钥")
            return False
        print(f"✅ API Key: {settings.SAMBANOVA_API_KEY[:20]}...")
    else:
        print(f"✅ Model: {settings.OPENAI_MODEL}")
    
    print()
    
    try:
        # 初始化Agent
        print("📦 初始化Agent...")
        agent = get_agent_core()
        print("✅ Agent初始化成功")
        print()
        
        # 测试会话ID
        session_id = "test_session_001"
        
        # 测试场景
        test_cases = [
            {
                "input": "我想去杭州玩3天",
                "expected_stage": "collecting",
                "description": "测试1: 初始输入（包含目的地和天数）"
            },
            {
                "input": "预算3000元，喜欢文化和美食",
                "expected_stage": "confirming",
                "description": "测试2: 补充预算和偏好"
            },
            {
                "input": "确认",
                "expected_stage": "generating",
                "description": "测试3: 确认需求"
            }
        ]
        
        for i, test in enumerate(test_cases, 1):
            print(f"🔍 {test['description']}")
            print(f"   输入: {test['input']}")
            
            # 处理消息
            result = agent.process_message(session_id, test['input'])
            
            # 显示结果
            print(f"   回复: {result['reply'][:100]}...")
            print(f"   阶段: {result['stage']}")
            
            # 显示需求信息
            req = result['requirements']
            if any(req.values()):
                print(f"   需求:")
                if req.get('destination'):
                    print(f"      - 目的地: {req['destination']}")
                if req.get('days'):
                    print(f"      - 天数: {req['days']}天")
                if req.get('budget'):
                    print(f"      - 预算: {req['budget']}元")
                if req.get('preferences'):
                    print(f"      - 偏好: {', '.join(req['preferences'])}")
            
            # 验证阶段
            if result['stage'] == test['expected_stage']:
                print(f"   ✅ 阶段正确")
            else:
                print(f"   ⚠️  预期阶段: {test['expected_stage']}, 实际: {result['stage']}")
            
            print()
        
        print("=" * 60)
        print("✅ 测试完成！")
        print("=" * 60)
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        logger.exception("测试过程中出错")
        return False


def test_welcome_message():
    """测试欢迎消息"""
    print("\n🧪 测试欢迎消息")
    print("-" * 60)
    
    try:
        agent = get_agent_core()
        welcome = agent.generate_welcome_message()
        print(welcome)
        print("-" * 60)
        print("✅ 欢迎消息生成成功")
        return True
    except Exception as e:
        print(f"❌ 失败: {e}")
        return False


def main():
    """主函数"""
    print("\n🚀 TravelMate AI - Agent测试\n")
    
    # 测试欢迎消息
    test_welcome_message()
    
    print()
    
    # 测试对话流程
    success = test_dialogue_flow()
    
    if success:
        print("\n🎉 所有测试通过！Agent工作正常。")
        print("\n💡 下一步:")
        print("   1. 启动后端: python main.py")
        print("   2. 启动前端: cd ../frontend && npm run dev")
        print("   3. 访问 http://localhost:5173 开始对话")
    else:
        print("\n❌ 测试失败，请检查配置和日志")
        print("\n💡 常见问题:")
        print("   1. 确认.env文件存在且配置正确")
        print("   2. 确认SAMBANOVA_API_KEY已设置")
        print("   3. 检查test_agent.log查看详细错误")


if __name__ == "__main__":
    main()

