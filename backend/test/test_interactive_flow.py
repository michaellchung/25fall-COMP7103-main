"""
测试分步交互式推荐流程
"""
import sys
sys.path.insert(0, '/Applications/MyDocument/7103/backend')

from agent.core import get_agent_core

def test_interactive_flow():
    """测试完整的交互式推荐流程"""
    agent = get_agent_core()
    session_id = "test_session_001"
    
    print("=" * 80)
    print("测试分步交互式推荐流程")
    print("=" * 80)
    
    # 步骤1：初始输入
    print("\n【步骤1】用户输入目的地")
    response = agent.process_message(session_id, "我想去杭州玩3天")
    print(f"Stage: {response['stage']}")
    print(f"Reply: {response['reply']}")
    
    # 步骤2：补充信息
    print("\n【步骤2】补充旅行信息")
    response = agent.process_message(
        session_id,
        "预算5000元，喜欢美食，从上海出发，和朋友一起，2人"
    )
    print(f"Stage: {response['stage']}")
    print(f"Reply: {response['reply']}")
    
    # 步骤3：确认需求
    print("\n【步骤3】确认需求")
    response = agent.process_message(session_id, "确认")
    print(f"Stage: {response['stage']}")
    print(f"Reply: {response['reply']}")
    
    # 检查是否有推荐数据
    if 'recommendation' in response:
        print(f"\n推荐类型: {response['recommendation']['type']}")
        print(f"推荐数据: {response['recommendation']['data'].keys()}")
    
    # 步骤4：选择交通
    print("\n【步骤4】选择交通方式")
    response = agent.process_message(session_id, "我选择高铁")
    print(f"Stage: {response['stage']}")
    print(f"Reply: {response['reply']}")
    
    # 检查是否有推荐数据
    if 'recommendation' in response:
        print(f"\n推荐类型: {response['recommendation']['type']}")
    
    # 步骤5：确认景点
    print("\n【步骤5】确认景点安排")
    response = agent.process_message(session_id, "确认")
    print(f"Stage: {response['stage']}")
    print(f"Reply: {response['reply']}")
    
    # 步骤6：确认美食
    print("\n【步骤6】确认美食安排")
    response = agent.process_message(session_id, "确认")
    print(f"Stage: {response['stage']}")
    print(f"Reply: {response['reply']}")
    
    # 步骤7：选择住宿
    print("\n【步骤7】选择住宿")
    response = agent.process_message(session_id, "选择第二个")
    print(f"Stage: {response['stage']}")
    print(f"Reply: {response['reply']}")
    
    # 检查最终行程
    if 'itinerary' in response:
        print("\n【最终行程生成成功】")
        itinerary = response['itinerary']
        print(f"目的地: {itinerary.get('destination')}")
        print(f"天数: {itinerary.get('duration_days')}")
        print(f"预算: {itinerary.get('total_budget')}")
        if 'daily_plans' in itinerary:
            print(f"每日计划数: {len(itinerary['daily_plans'])}")
    
    print("\n" + "=" * 80)
    print("测试完成")
    print("=" * 80)


if __name__ == "__main__":
    test_interactive_flow()

