"""
简单的后端测试 - 验证分步交互流程
"""
import sys
sys.path.insert(0, '/Applications/MyDocument/7103/backend')

from agent.core import get_agent_core
from agent.state import ItineraryStage

def test_simple_flow():
    """测试简化的交互流程"""
    agent = get_agent_core()
    session_id = "test_simple_001"
    
    print("\n" + "=" * 80)
    print("测试分步交互流程（简化版）")
    print("=" * 80)
    
    # 步骤1：初始输入
    print("\n【步骤1】用户输入目的地")
    response = agent.process_message(session_id, "我想去杭州玩3天")
    print(f"✓ Stage: {response['stage']}")
    print(f"✓ Reply: {response['reply'][:100]}...")
    
    # 步骤2：补充信息
    print("\n【步骤2】补充旅行信息")
    response = agent.process_message(
        session_id,
        "预算5000元，喜欢美食，从上海出发，和朋友一起，2人"
    )
    print(f"✓ Stage: {response['stage']}")
    print(f"✓ Reply: {response['reply'][:100]}...")
    
    # 步骤3：确认需求
    print("\n【步骤3】确认需求")
    response = agent.process_message(session_id, "确认")
    print(f"✓ Stage: {response['stage']}")
    print(f"✓ Reply: {response['reply'][:100]}...")
    
    # 检查是否进入交通推荐阶段
    if response['stage'] == ItineraryStage.WAITING_TRANSPORT_SELECTION.value:
        print("✅ 成功进入交通推荐阶段！")
        
        if 'recommendation' in response:
            rec = response['recommendation']
            print(f"✓ 推荐类型: {rec['type']}")
            print(f"✓ 推荐数据keys: {rec['data'].keys()}")
            
            # 步骤4：选择交通
            print("\n【步骤4】选择交通方式")
            response = agent.process_message(session_id, "我选择高铁")
            print(f"✓ Stage: {response['stage']}")
            print(f"✓ Reply: {response['reply'][:100]}...")
            
            # 检查是否进入景点推荐阶段
            if response['stage'] == ItineraryStage.WAITING_ATTRACTIONS_SELECTION.value:
                print("✅ 成功进入景点推荐阶段！")
                
                if 'recommendation' in response:
                    rec = response['recommendation']
                    print(f"✓ 推荐类型: {rec['type']}")
                    
                    # 步骤5：确认景点
                    print("\n【步骤5】确认景点安排")
                    response = agent.process_message(session_id, "确认")
                    print(f"✓ Stage: {response['stage']}")
                    print(f"✓ Reply: {response['reply'][:100]}...")
                    
                    # 检查是否进入美食推荐阶段
                    if response['stage'] == ItineraryStage.WAITING_FOOD_SELECTION.value:
                        print("✅ 成功进入美食推荐阶段！")
                        
                        # 步骤6：确认美食
                        print("\n【步骤6】确认美食安排")
                        response = agent.process_message(session_id, "确认")
                        print(f"✓ Stage: {response['stage']}")
                        print(f"✓ Reply: {response['reply'][:100]}...")
                        
                        # 检查是否进入住宿推荐阶段
                        if response['stage'] == ItineraryStage.WAITING_ACCOMMODATION_SELECTION.value:
                            print("✅ 成功进入住宿推荐阶段！")
                            
                            # 步骤7：选择住宿
                            print("\n【步骤7】选择住宿")
                            response = agent.process_message(session_id, "选择第二个")
                            print(f"✓ Stage: {response['stage']}")
                            print(f"✓ Reply: {response['reply'][:100]}...")
                            
                            # 检查是否完成
                            if response['stage'] == ItineraryStage.COMPLETED.value:
                                print("✅ 成功完成所有阶段！")
                                
                                if 'itinerary' in response:
                                    itinerary = response['itinerary']
                                    print(f"\n【最终行程】")
                                    print(f"✓ 目的地: {itinerary.get('destination')}")
                                    print(f"✓ 天数: {itinerary.get('duration_days')}")
                                    print(f"✓ 预算: {itinerary.get('total_budget')}")
                                    print(f"✓ 交通: {itinerary.get('transport', {}).get('method', 'N/A')}")
                                    if 'daily_plans' in itinerary:
                                        print(f"✓ 每日计划数: {len(itinerary['daily_plans'])}")
                                    if 'hotel' in itinerary and itinerary['hotel']:
                                        print(f"✓ 酒店: {itinerary['hotel'].get('name', 'N/A')}")
    
    print("\n" + "=" * 80)
    print("测试完成！")
    print("=" * 80)


if __name__ == "__main__":
    try:
        test_simple_flow()
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

