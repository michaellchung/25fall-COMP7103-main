"""
测试分步决策Agent
"""
import sys
sys.path.append('/Applications/MyDocument/7103/backend')

from agent.core import AgentCore
from loguru import logger

# 配置日志
logger.remove()
logger.add(sys.stdout, level="INFO")

def test_complete_flow():
    """测试完整对话流程"""
    agent = AgentCore()
    session_id = "test_step_by_step_001"
    
    print("\n" + "=" * 80)
    print("🧪 测试分步决策Agent - 完整流程")
    print("=" * 80)
    
    # Step 1: 用户输入
    user_input = "我想从北京出发去杭州玩3天，我们两个人，预算5000元，喜欢文化和美食"
    print(f"\n👤 用户: {user_input}")
    
    response1 = agent.process_message(session_id, user_input)
    print(f"\n🤖 Agent: {response1['reply'][:200]}...")
    print(f"📊 当前阶段: {response1['stage']}")
    
    # Step 2: 确认
    if response1['stage'] == 'confirming':
        print("\n" + "-" * 80)
        print("用户确认")
        print("-" * 80)
        
        user_input2 = "是的，正确"
        print(f"\n👤 用户: {user_input2}")
        
        response2 = agent.process_message(session_id, user_input2)
        print(f"\n🤖 Agent: {response2['reply']}")
        
        if response2.get('itinerary'):
            print("\n" + "=" * 80)
            print("✅ 生成的行程")
            print("=" * 80)
            
            itinerary = response2['itinerary']
            
            # 打印基本信息
            print(f"\n📍 目的地: {itinerary.get('destination')}")
            print(f"🚄 出发地: {itinerary.get('departure_city')}")
            print(f"📅 天数: {itinerary.get('duration_days')}天")
            print(f"💰 预算: {itinerary.get('total_budget')}元")
            print(f"👥 同行: {itinerary.get('companions')} ({itinerary.get('companions_count')}人)")
            
            # 打印交通方案
            if itinerary.get('transport'):
                print("\n🚗 交通方案:")
                transport = itinerary['transport']
                print(f"  去程: {transport.get('outbound', {}).get('method')} - {transport.get('outbound', {}).get('cost')}元")
                print(f"  返程: {transport.get('return', {}).get('method')} - {transport.get('return', {}).get('cost')}元")
            
            # 打印酒店
            if itinerary.get('hotel'):
                hotel = itinerary['hotel']
                print(f"\n🏨 酒店: {hotel.get('name')}")
                print(f"  住宿: {hotel.get('nights')}晚")
                print(f"  费用: {hotel.get('total_cost')}元")
            
            # 打印每日行程
            if itinerary.get('daily_plans'):
                print("\n📅 每日行程:")
                for plan in itinerary['daily_plans']:
                    print(f"\n  Day {plan.get('day')}: {plan.get('theme', '')}")
                    print(f"  日期: {plan.get('date', '待定')}")
                    print(f"  当日费用: {plan.get('daily_cost', 0)}元")
                    
                    if plan.get('schedule'):
                        for item in plan['schedule']:
                            print(f"    {item.get('time', '')} - {item.get('type', '')}: {item.get('name', '')} ({item.get('cost', 0)}元)")
            
            # 打印预算明细
            if itinerary.get('budget_breakdown'):
                print("\n💰 预算明细:")
                breakdown = itinerary['budget_breakdown']
                print(f"  交通: {breakdown.get('transport', 0)}元")
                print(f"  景点: {breakdown.get('attractions', 0)}元")
                print(f"  餐饮: {breakdown.get('food', 0)}元")
                print(f"  住宿: {breakdown.get('accommodation', 0)}元")
                print(f"  其他: {breakdown.get('misc', 0)}元")
                print(f"  总计: {breakdown.get('total', 0)}元")
            
            # 打印旅行建议
            if itinerary.get('tips'):
                print("\n💡 旅行建议:")
                for tip in itinerary['tips']:
                    print(f"  • {tip}")
    
    print("\n" + "=" * 80)
    print("✅ 测试完成！")
    print("=" * 80)

if __name__ == "__main__":
    test_complete_flow()

