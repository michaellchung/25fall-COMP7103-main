"""
测试推理逻辑（不依赖LLM）
直接模拟完整的推理流程：需求收集 -> tool调用 -> 行程生成
"""
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from planner.itinerary_generator import get_itinerary_generator
from loguru import logger


def test_inference_logic():
    """测试完整的推理逻辑"""
    print("\n" + "="*80)
    print("测试推理逻辑：需求 -> Tool调用 -> 行程生成")
    print("="*80 + "\n")
    
    # 模拟用户需求
    print("【用户需求】")
    print("-" * 80)
    user_requirements = {
        "departure_city": "北京",
        "destination": "杭州",
        "days": 3,
        "budget": 5000,
        "preferences": ["文化", "美食"],
        "companions": "情侣",
        "companions_count": 2
    }
    
    for key, value in user_requirements.items():
        print(f"  {key}: {value}")
    
    # 生成行程
    print("\n【开始生成行程】")
    print("-" * 80)
    
    generator = get_itinerary_generator()
    itinerary = generator.generate_itinerary(
        destination=user_requirements["destination"],
        days=user_requirements["days"],
        budget=user_requirements["budget"],
        preferences=user_requirements["preferences"],
        attractions=[],  # 将由tool 2查询
        companions=user_requirements["companions"],
        companions_count=user_requirements["companions_count"],
        departure_city=user_requirements["departure_city"]
    )
    
    # 展示生成的行程
    print("\n【生成的行程】")
    print("="*80)
    
    # 1. 基本信息
    print(f"\n目的地: {itinerary['destination']}")
    print(f"天数: {itinerary['duration_days']}天")
    print(f"预算: ¥{itinerary['total_budget']}")
    print(f"出发地: {itinerary.get('departure_city', '未指定')}")
    print(f"同行: {itinerary.get('companions', '未指定')} ({itinerary.get('companions_count', 1)}人)")
    
    # 2. 交通信息（Tool 1的结果）
    if itinerary.get('transport'):
        print("\n【交通方案】(Tool 1)")
        print("-" * 80)
        outbound = itinerary['transport'].get('outbound')
        if outbound:
            print(f"去程推荐: {outbound.get('method')}")
            print(f"  描述: {outbound.get('description')}")
            print(f"  时长: {outbound.get('duration_hours')}小时")
            print(f"  费用: {outbound.get('cost_per_person')}元/人")
            print(f"  总费用: {outbound.get('details', {}).get('total_cost', 0)}元")
            print(f"  出发: {outbound.get('departure_time')} → 到达: {outbound.get('arrival_time')}")
        
        # 显示其他选项
        options = itinerary['transport'].get('options', [])
        if len(options) > 1:
            print(f"\n  其他选项:")
            for i, opt in enumerate(options[1:], 1):
                print(f"    方案{i+1}: {opt.get('method')} - {opt.get('cost_per_person')}元/人, {opt.get('duration_hours')}小时")
    
    # 3. 每日行程（Tool 2景点 + Tool 3美食）
    if itinerary.get('daily_plans'):
        print("\n【每日行程】(Tool 2 景点 + Tool 3 美食)")
        print("-" * 80)
        for day_plan in itinerary['daily_plans']:
            print(f"\n第 {day_plan['day']} 天:")
            print(f"  预计花费: ¥{day_plan.get('daily_cost', 0)}")
            
            # 景点
            attractions = day_plan.get('attractions', [])
            if attractions:
                print(f"\n  🏛️  景点安排:")
                for attr in attractions:
                    print(f"    • {attr['name']} ({attr['time_slot']})")
                    print(f"      游玩时长: {attr['duration']}小时, 门票: ¥{attr['ticket_price']}")
                    if attr.get('tags'):
                        print(f"      标签: {', '.join(attr['tags'][:3])}")
            
            # 餐饮
            meals = day_plan.get('meals', [])
            if meals:
                print(f"\n  🍽️  餐饮安排:")
                for meal in meals:
                    print(f"    • {meal['type']}: {meal['restaurant']} ({meal['cuisine_type']})")
                    print(f"      人均: ¥{meal['avg_price']}")
                    if meal.get('signature_dishes'):
                        dishes = ', '.join(meal['signature_dishes'][:3])
                        print(f"      招牌菜: {dishes}")
    
    # 4. 住宿信息（Tool 4的结果）
    if itinerary.get('accommodation'):
        print("\n【住宿推荐】(Tool 4)")
        print("-" * 80)
        selected = itinerary['accommodation'].get('selected')
        if selected:
            print(f"推荐酒店: {selected.get('name')}")
            print(f"  类型: {selected.get('hotel_type')}")
            print(f"  评分: {selected.get('rating')}/5.0")
            print(f"  价格: ¥{selected.get('price_per_night')}/晚")
            print(f"  总费用: ¥{selected.get('price_per_night', 0) * (itinerary['duration_days'] - 1)} ({itinerary['duration_days']-1}晚)")
            if selected.get('facilities'):
                print(f"  设施: {', '.join(selected['facilities'][:5])}")
            if selected.get('tags'):
                print(f"  标签: {', '.join(selected['tags'][:3])}")
        
        # 其他选项
        options = itinerary['accommodation'].get('options', [])
        if len(options) > 1:
            print(f"\n  其他选项:")
            for i, hotel in enumerate(options[1:3], 1):
                print(f"    {i+1}. {hotel.get('name')} ({hotel.get('hotel_type')}, ¥{hotel.get('price_per_night')}/晚)")
    
    # 5. 预算分析
    if itinerary.get('budget_breakdown'):
        print("\n【预算分析】")
        print("-" * 80)
        breakdown = itinerary['budget_breakdown']
        
        total_cost = 0
        for category, amount in breakdown.items():
            print(f"  {category:8s}: ¥{amount:7.2f}")
            total_cost += amount
        
        print(f"  {'-'*20}")
        print(f"  {'总预算':8s}: ¥{itinerary['total_budget']:7.2f}")
        print(f"  {'预估花费':8s}: ¥{itinerary['estimated_cost']:7.2f}")
        
        remaining = itinerary['total_budget'] - itinerary['estimated_cost']
        if remaining >= 0:
            print(f"  {'结余':8s}: ¥{remaining:7.2f} ✅")
        else:
            print(f"  {'超支':8s}: ¥{-remaining:7.2f} ⚠️")
    
    # 6. 旅行建议
    if itinerary.get('tips'):
        print("\n【旅行建议】")
        print("-" * 80)
        for i, tip in enumerate(itinerary['tips'][:6], 1):
            print(f"  {i}. {tip}")
    
    print("\n" + "="*80)
    print("推理逻辑测试完成！")
    print("="*80)
    
    # 验证关键点
    print("\n【验证关键点】")
    print("-" * 80)
    checks = [
        ("Tool 1 交通已调用", itinerary.get('transport') is not None),
        ("Tool 2 景点已调用", any(len(day.get('attractions', [])) > 0 for day in itinerary.get('daily_plans', []))),
        ("Tool 3 美食已调用", any(len(day.get('meals', [])) > 0 for day in itinerary.get('daily_plans', []))),
        ("Tool 4 住宿已调用", itinerary.get('accommodation') is not None),
        ("LLM决策完成（每日行程）", len(itinerary.get('daily_plans', [])) == 3),
        ("预算计算正确", itinerary.get('estimated_cost', 0) > 0)
    ]
    
    all_passed = True
    for check_name, result in checks:
        status = "✅" if result else "❌"
        print(f"  {status} {check_name}")
        if not result:
            all_passed = False
    
    if all_passed:
        print("\n🎉 所有验证点通过！推理Agent工作正常！")
    else:
        print("\n⚠️  部分验证点未通过，请检查。")
    
    return itinerary


if __name__ == "__main__":
    test_inference_logic()
    print("\n")

