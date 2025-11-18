"""
测试完整的对话流程 - 包含出发地和同行人数
"""
import sys
sys.path.append('/Applications/MyDocument/7103/backend')

from agent.core import AgentCore
from loguru import logger

# 配置日志
logger.remove()
logger.add(sys.stdout, level="INFO")

def test_dialogue_flow():
    """测试完整对话流程"""
    agent = AgentCore()
    session_id = "test_session_001"
    
    print("=" * 80)
    print("测试场景1: 完整信息一次性提供")
    print("=" * 80)
    
    # 测试1: 完整信息
    user_input_1 = "我想从上海出发去杭州玩3天，我们两个人，预算3000元，喜欢文化和美食"
    print(f"\n👤 用户: {user_input_1}")
    
    response_1 = agent.process_message(session_id, user_input_1)
    print(f"\n🤖 Agent: {response_1['reply']}")
    print(f"\n📊 当前阶段: {response_1['stage']}")
    print(f"\n📋 收集到的需求:")
    for key, value in response_1['requirements'].items():
        if value:
            print(f"  - {key}: {value}")
    
    # 如果需要确认，发送确认
    if response_1['stage'] == 'confirming':
        print("\n" + "=" * 80)
        print("用户确认信息")
        print("=" * 80)
        
        user_input_2 = "确认"
        print(f"\n👤 用户: {user_input_2}")
        
        response_2 = agent.process_message(session_id, user_input_2)
        print(f"\n🤖 Agent: {response_2['reply']}")
        
        if response_2.get('itinerary'):
            print("\n📋 生成的行程:")
            itinerary = response_2['itinerary']
            print(f"  目的地: {itinerary.get('destination')}")
            print(f"  出发地: {itinerary.get('departure_city')}")
            print(f"  天数: {itinerary.get('duration_days')}")
            print(f"  预算: {itinerary.get('total_budget')}")
            print(f"  同行: {itinerary.get('companions')}")
            print(f"  人数: {itinerary.get('companions_count')}")
            print(f"  预估费用: {itinerary.get('estimated_cost')}")
    
    print("\n" + "=" * 80)
    print("测试场景2: 分步提供信息")
    print("=" * 80)
    
    # 新会话
    session_id_2 = "test_session_002"
    
    # 第一步：只说目的地
    user_input_3 = "我想去苏州玩"
    print(f"\n👤 用户: {user_input_3}")
    
    response_3 = agent.process_message(session_id_2, user_input_3)
    print(f"\n🤖 Agent: {response_3['reply']}")
    
    # 第二步：提供其他信息
    user_input_4 = "从北京出发，一家三口，预算5000，喜欢自然风光"
    print(f"\n👤 用户: {user_input_4}")
    
    response_4 = agent.process_message(session_id_2, user_input_4)
    print(f"\n🤖 Agent: {response_4['reply']}")
    print(f"\n📊 当前阶段: {response_4['stage']}")
    print(f"\n📋 收集到的需求:")
    for key, value in response_4['requirements'].items():
        if value:
            print(f"  - {key}: {value}")
    
    print("\n" + "=" * 80)
    print("测试场景3: 家庭4人出游（预算调整测试）")
    print("=" * 80)
    
    session_id_3 = "test_session_003"
    
    user_input_5 = "我们一家四口从深圳去广州玩2天，预算4000元，喜欢美食和文化"
    print(f"\n👤 用户: {user_input_5}")
    
    response_5 = agent.process_message(session_id_3, user_input_5)
    print(f"\n🤖 Agent: {response_5['reply']}")
    print(f"\n📋 收集到的需求:")
    for key, value in response_5['requirements'].items():
        if value:
            print(f"  - {key}: {value}")
    
    print("\n" + "=" * 80)
    print("测试场景4: 朋友团5人（团体优惠测试）")
    print("=" * 80)
    
    session_id_4 = "test_session_004"
    
    user_input_6 = "我和4个朋友从上海去杭州玩3天，一共5个人，预算6000，喜欢休闲"
    print(f"\n👤 用户: {user_input_6}")
    
    response_6 = agent.process_message(session_id_4, user_input_6)
    print(f"\n🤖 Agent: {response_6['reply']}")
    print(f"\n📋 收集到的需求:")
    for key, value in response_6['requirements'].items():
        if value:
            print(f"  - {key}: {value}")
    
    print("\n" + "=" * 80)
    print("✅ 测试完成！")
    print("=" * 80)

if __name__ == "__main__":
    test_dialogue_flow()

