"""
测试完整的确认流程
"""
import sys
sys.path.append('/Applications/MyDocument/7103/backend')

from agent.core import AgentCore
from loguru import logger

# 配置日志
logger.remove()
logger.add(sys.stdout, level="INFO")

def test_confirmation_flow():
    """测试确认流程"""
    agent = AgentCore()
    session_id = "test_confirmation_001"
    
    print("=" * 80)
    print("测试场景: 用户提供完整信息 → 确认 → 生成行程")
    print("=" * 80)
    
    # 第一步：提供完整信息
    user_input_1 = "我想从北京出发去杭州玩5天，我们两个人，预算5000元，喜欢美食"
    print(f"\n👤 用户: {user_input_1}")
    
    response_1 = agent.process_message(session_id, user_input_1)
    print(f"\n🤖 Agent: {response_1['reply']}")
    print(f"📊 当前阶段: {response_1['stage']}")
    
    # 验证是否进入确认阶段
    if response_1['stage'] != 'confirming':
        print(f"❌ 错误：应该进入confirming阶段，实际为{response_1['stage']}")
        return
    
    print("\n" + "-" * 80)
    print("测试不同的确认词")
    print("-" * 80)
    
    # 测试各种确认词
    confirmation_words = ["正确", "是", "是的", "对", "好", "确认", "没错", "ok"]
    
    for word in confirmation_words:
        # 重置会话
        test_session_id = f"test_{word}"
        
        # 重新提供信息
        agent.process_message(test_session_id, user_input_1)
        
        # 测试确认词
        print(f"\n测试确认词: '{word}'")
        response = agent.process_message(test_session_id, word)
        
        if response['stage'] == 'generating':
            print(f"  ✅ 成功识别为确认，进入generating阶段")
            print(f"  回复: {response['reply'][:50]}...")
        else:
            print(f"  ❌ 失败：阶段为{response['stage']}")
            print(f"  回复: {response['reply']}")
    
    print("\n" + "-" * 80)
    print("测试否定词")
    print("-" * 80)
    
    # 测试否定词
    negation_words = ["不对", "修改", "改一下", "错了"]
    
    for word in negation_words:
        # 重置会话
        test_session_id = f"test_neg_{word}"
        
        # 重新提供信息
        agent.process_message(test_session_id, user_input_1)
        
        # 测试否定词
        print(f"\n测试否定词: '{word}'")
        response = agent.process_message(test_session_id, word)
        
        if response['stage'] == 'collecting':
            print(f"  ✅ 成功识别为否定，回到collecting阶段")
            print(f"  回复: {response['reply'][:50]}...")
        else:
            print(f"  ❌ 失败：阶段为{response['stage']}")
            print(f"  回复: {response['reply']}")
    
    print("\n" + "=" * 80)
    print("✅ 测试完成！")
    print("=" * 80)

if __name__ == "__main__":
    test_confirmation_flow()

