"""
测试Agent完整推理流程（集成4个tool）
"""
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from agent.core import get_agent_core
from loguru import logger

# 配置日志
logger.add("test_agent_tools.log", rotation="10 MB")


def test_complete_dialogue_with_杭州():
    """测试完整对话流程 - 去杭州旅游"""
    print("\n" + "="*80)
    print("测试完整对话流程 - 去杭州旅游（集成4个tool）")
    print("="*80 + "\n")
    
    agent = get_agent_core()
    session_id = "test_session_hangzhou"
    
    # 步骤1: 发送初始消息
    print("步骤1: 用户输入需求")
    print("-" * 80)
    user_input = "我想从北京出发去杭州玩3天，我们两个人，预算5000元，喜欢文化和美食"
    print(f"用户: {user_input}\n")
    
    response = agent.process_message(session_id, user_input)
    print(f"Agent: {response['reply']}")
    print(f"当前阶段: {response['stage']}")
    print(f"收集到的需求: {response['requirements']}\n")
    
    # 步骤2: 确认需求（如果需要）
    if response['stage'] == 'confirming':
        print("\n步骤2: 确认需求")
        print("-" * 80)
        user_confirm = "确认"
        print(f"用户: {user_confirm}\n")
        
        response = agent.process_message(session_id, user_confirm)
        print(f"Agent: {response['reply']}")
        print(f"当前阶段: {response['stage']}\n")
    
    # 步骤3: 查看生成的行程
    if response.get('itinerary'):
        print("\n步骤3: 生成的行程详情")
        print("=" * 80)
        itinerary = response['itinerary']
        
        # 交通信息
        if itinerary.get('transport'):
            print("\n【交通信息】")
            print("-" * 80)
            outbound = itinerary['transport'].get('outbound')
            if outbound:
                print(f"去程: {outbound.get('method')} - {outbound.get('description')}")
                print(f"      时长: {outbound.get('duration_hours')}小时")
                print(f"      费用: {outbound.get('cost_per_person')}元/人")
                print(f"      出发: {outbound.get('departure_time')} → 到达: {outbound.get('arrival_time')}")
        
        # 每日行程
        print("\n【每日行程】")
        print("-" * 80)
        for day_plan in itinerary.get('daily_plans', []):
            print(f"\n第{day_plan['day']}天:")
            print(f"  景点:")
            for attr in day_plan.get('attractions', []):
                print(f"    - {attr['name']} ({attr['time_slot']}, {attr['duration']}小时)")
                print(f"      门票: {attr['ticket_price']}元")
                print(f"      {attr['description'][:50]}...")
            
            print(f"  餐饮:")
            for meal in day_plan.get('meals', []):
                print(f"    - {meal['type']}: {meal['restaurant']} ({meal['cuisine_type']})")
                print(f"      人均: {meal['avg_price']}元")
                if meal.get('signature_dishes'):
                    print(f"      招牌菜: {', '.join(meal['signature_dishes'][:3])}")
            
            print(f"  当日花费: {day_plan.get('daily_cost', 0)}元")
        
        # 住宿信息
        if itinerary.get('accommodation'):
            print("\n【住宿信息】")
            print("-" * 80)
            hotel = itinerary['accommodation'].get('selected')
            if hotel:
                print(f"推荐酒店: {hotel.get('name')}")
                print(f"酒店类型: {hotel.get('hotel_type')}")
                print(f"评分: {hotel.get('rating')}/5.0")
                print(f"价格: {hotel.get('price_per_night')}元/晚")
                print(f"设施: {', '.join(hotel.get('facilities', []))}")
        
        # 预算分析
        if itinerary.get('budget_breakdown'):
            print("\n【预算分析】")
            print("-" * 80)
            breakdown = itinerary['budget_breakdown']
            for category, amount in breakdown.items():
                print(f"  {category}: ¥{amount:.2f}")
            print(f"\n  总预算: ¥{itinerary['total_budget']}")
            print(f"  预估花费: ¥{itinerary['estimated_cost']:.2f}")
            
            if itinerary['estimated_cost'] <= itinerary['total_budget']:
                print(f"  ✅ 在预算范围内！")
            else:
                over = itinerary['estimated_cost'] - itinerary['total_budget']
                print(f"  ⚠️  超出预算 ¥{over:.2f}")
        
        # 旅行建议
        if itinerary.get('tips'):
            print("\n【旅行建议】")
            print("-" * 80)
            for tip in itinerary['tips'][:5]:
                print(f"  • {tip}")
    
    print("\n" + "="*80)
    print("测试完成!")
    print("="*80 + "\n")


def test_tools_directly():
    """直接测试4个tool"""
    print("\n" + "="*80)
    print("直接测试4个Tool")
    print("="*80 + "\n")
    
    from tools.transport import get_transport_tool
    from tools.attraction import get_attraction_tool
    from tools.food import get_food_tool
    from tools.accommodation import get_accommodation_tool
    
    # 测试Tool1: 交通
    print("【Tool 1: 交通查询】")
    print("-" * 80)
    transport_tool = get_transport_tool()
    transports = transport_tool.query_transport(
        departure_city="北京",
        destination_city="杭州",
        companions_count=2,
        top_k=2
    )
    for i, t in enumerate(transports):
        print(f"{i+1}. {t['method']} - {t['description']}")
        print(f"   时长: {t['duration_hours']}h, 费用: {t['cost_per_person']}元/人")
    
    # 测试Tool2: 景点
    print("\n【Tool 2: 景点查询】")
    print("-" * 80)
    attraction_tool = get_attraction_tool()
    attractions = attraction_tool.query_attractions(
        city="杭州",
        preferences=["文化", "美食"],
        top_k=5
    )
    for i, attr in enumerate(attractions):
        print(f"{i+1}. {attr['name']} (评分: {attr['rating']}, 门票: {attr['ticket_price']}元)")
    
    # 测试Tool3: 美食
    print("\n【Tool 3: 美食查询】")
    print("-" * 80)
    food_tool = get_food_tool()
    restaurants = food_tool.query_restaurants(
        city="杭州",
        top_k=5
    )
    for i, rest in enumerate(restaurants):
        print(f"{i+1}. {rest['name']} ({rest['cuisine_type']}, 人均: {rest['avg_price']}元)")
    
    # 测试Tool4: 住宿
    print("\n【Tool 4: 住宿查询】")
    print("-" * 80)
    accommodation_tool = get_accommodation_tool()
    hotels = accommodation_tool.query_hotels(
        city="杭州",
        companions_count=2,
        top_k=5
    )
    for i, hotel in enumerate(hotels):
        print(f"{i+1}. {hotel['name']} ({hotel['hotel_type']}, {hotel['price_per_night']}元/晚)")
    
    print("\n" + "="*80)
    print("Tool测试完成!")
    print("="*80 + "\n")


if __name__ == "__main__":
    print("\n开始测试...")
    
    # 测试1: 直接测试4个tool
    test_tools_directly()
    
    # 测试2: 测试完整的agent对话流程
    test_complete_dialogue_with_杭州()
    
    print("\n所有测试完成！✅\n")

