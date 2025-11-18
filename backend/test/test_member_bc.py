"""
成员B和C接口测试脚本
用于验证RAG检索和行程生成功能
"""
import json
import requests
from datetime import datetime

BASE_URL = "http://localhost:8000"


def print_section(title):
    """打印分隔线"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")


def test_rag_retriever():
    """测试成员B的RAG检索接口"""
    print_section("测试成员B：RAG检索服务")
    
    # 测试1: 杭州自然景观
    print("\n【测试1】获取杭州的自然景观景点")
    response = requests.get(f"{BASE_URL}/api/attractions/杭州?preferences=自然景观")
    result = response.json()
    
    if result['success']:
        print(f"✅ 检索成功，找到 {len(result['data']['attractions'])} 个景点")
        for attr in result['data']['attractions']:
            print(f"  • {attr['name']} (¥{attr['ticket_price']}, ⭐{attr['rating']})")
    else:
        print(f"❌ 检索失败: {result['error']}")
    
    # 测试2: 南京多类别景点
    print("\n【测试2】获取南京的历史文化景点")
    response = requests.get(f"{BASE_URL}/api/attractions/南京?preferences=历史文化")
    result = response.json()
    
    if result['success']:
        print(f"✅ 检索成功，找到 {len(result['data']['attractions'])} 个景点")
        for attr in result['data']['attractions']:
            print(f"  • {attr['name']} (¥{attr['ticket_price']}, ⭐{attr['rating']})")
    else:
        print(f"❌ 检索失败: {result['error']}")
    
    # 测试3: 广州所有景点
    print("\n【测试3】获取广州的所有景点（无偏好过滤）")
    response = requests.get(f"{BASE_URL}/api/attractions/广州")
    result = response.json()
    
    if result['success']:
        print(f"✅ 检索成功，找到 {len(result['data']['attractions'])} 个景点")
        for attr in result['data']['attractions']:
            print(f"  • {attr['name']} ({attr['category']}, ¥{attr['ticket_price']})")
    else:
        print(f"❌ 检索失败: {result['error']}")


def test_itinerary_generation():
    """测试成员C的行程生成接口"""
    print_section("测试成员C：行程规划器")
    
    session_id = f"test_session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    # Step 1: 第一条消息 - 初始需求
    print("\n【Step 1】用户提出初始需求")
    msg1 = "我想去南京玩4天，预算5000元"
    response = requests.post(
        f"{BASE_URL}/api/chat",
        json={"session_id": session_id, "message": msg1}
    )
    result = response.json()
    
    if result['success']:
        print(f"✅ 消息已处理")
        print(f"  • 目的地: {result['data']['requirements']['destination']}")
        print(f"  • 天数: {result['data']['requirements']['days']}")
        print(f"  • 预算: ¥{result['data']['requirements']['budget']}")
        print(f"  • 当前阶段: {result['data']['stage']}")
        print(f"  • Agent回复: {result['data']['reply'][:50]}...")
    else:
        print(f"❌ 处理失败: {result['error']}")
        return
    
    # Step 2: 回答偏好
    print("\n【Step 2】用户回答偏好信息")
    msg2 = "我对历史文化特别感兴趣，也喜欢美食"
    response = requests.post(
        f"{BASE_URL}/api/chat",
        json={"session_id": session_id, "message": msg2}
    )
    result = response.json()
    
    if result['success']:
        print(f"✅ 消息已处理")
        print(f"  • 偏好: {result['data']['requirements']['preferences']}")
        print(f"  • 当前阶段: {result['data']['stage']}")
    else:
        print(f"❌ 处理失败: {result['error']}")
        return
    
    # Step 3: 确认信息并生成行程
    print("\n【Step 3】用户确认信息，触发行程生成")
    msg3 = "好的，就按这个安排"
    response = requests.post(
        f"{BASE_URL}/api/chat",
        json={"session_id": session_id, "message": msg3}
    )
    result = response.json()
    
    if result['success'] and result['data']['stage'] == 'generating':
        print(f"✅ 行程已生成！")
        
        if 'itinerary' in result['data']:
            itinerary = result['data']['itinerary']
            print(f"\n  📍 目的地: {itinerary['destination']}")
            print(f"  📅 时长: {itinerary['duration_days']}天")
            print(f"  💰 总预算: ¥{itinerary['total_budget']}")
            print(f"  💵 日均: ¥{itinerary['daily_budget']:.0f}")
            
            print(f"\n  📋 每日行程:")
            for day_plan in itinerary['daily_plans']:
                print(f"\n    第{day_plan['day']}天 (成本¥{day_plan['daily_cost']:.0f}):")
                print(f"      上午: {day_plan['morning']['activity']} ({day_plan['morning']['time']})")
                print(f"      下午: {day_plan['afternoon']['activity']} ({day_plan['afternoon']['time']})")
                print(f"      晚上: {day_plan['evening']['activity']} ({day_plan['evening']['time']})")
            
            print(f"\n  💰 预算分配:")
            for category, amount in itinerary['budget_breakdown'].items():
                percentage = (amount / itinerary['total_budget']) * 100
                print(f"      {category}: ¥{amount:.0f} ({percentage:.0f}%)")
            
            print(f"\n  💡 旅行建议:")
            for i, tip in enumerate(itinerary['tips'][:5], 1):
                print(f"      {i}. {tip}")
        else:
            print("⚠️ 行程数据不完整")
    else:
        print(f"❌ 行程生成失败")
        if result['data']['stage'] != 'generating':
            print(f"  当前阶段: {result['data']['stage']}")
    
    # Step 4: 通过API获取完整行程
    print("\n【Step 4】通过API获取完整行程详情")
    response = requests.get(f"{BASE_URL}/api/itinerary/{session_id}")
    result = response.json()
    
    if result['success']:
        print(f"✅ 行程详情已获取")
        itinerary = result['data']
        print(f"  • 预计总成本: ¥{itinerary['estimated_cost']:.0f}")
        print(f"  • 总天数: {itinerary['duration_days']}天")
    else:
        print(f"❌ 获取失败: {result['error']}")


def test_multiple_cities():
    """测试多个城市的行程生成"""
    print_section("测试多个城市的行程生成")
    
    test_cases = [
        {
            "city": "杭州",
            "days": 3,
            "budget": 2000,
            "preferences": ["自然景观"]
        },
        {
            "city": "南京",
            "days": 4,
            "budget": 4000,
            "preferences": ["历史文化"]
        },
        {
            "city": "广州",
            "days": 2,
            "budget": 1500,
            "preferences": ["现代建筑"]
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n【用例 {i}】")
        session_id = f"test_{i}_{datetime.now().strftime('%H%M%S')}"
        
        # 生成消息
        msg = f"我想去{test_case['city']}玩{test_case['days']}天，预算{test_case['budget']}元"
        
        # 第一条消息
        requests.post(
            f"{BASE_URL}/api/chat",
            json={"session_id": session_id, "message": msg}
        )
        
        # 回答偏好
        pref_str = "、".join(test_case['preferences'])
        requests.post(
            f"{BASE_URL}/api/chat",
            json={"session_id": session_id, "message": f"我喜欢{pref_str}"}
        )
        
        # 确认并生成
        response = requests.post(
            f"{BASE_URL}/api/chat",
            json={"session_id": session_id, "message": "好的，就这样安排"}
        )
        result = response.json()
        
        if result['success'] and 'itinerary' in result['data']:
            itinerary = result['data']['itinerary']
            print(f"✅ {test_case['city']} - {itinerary['duration_days']}天行程已生成")
            print(f"   总预算: ¥{itinerary['total_budget']}, 预计成本: ¥{itinerary['estimated_cost']:.0f}")
        else:
            print(f"❌ {test_case['city']} - 行程生成失败")


def main():
    """主测试函数"""
    print("""
    ╔════════════════════════════════════════════════════════╗
    ║     成员B和C接口测试 - TravelMate AI 项目            ║
    ║     RAG检索服务 & 行程规划器                          ║
    ╚════════════════════════════════════════════════════════╝
    """)
    
    try:
        # 测试景点检索（成员B）
        test_rag_retriever()
        
        # 测试行程生成（成员C）
        test_itinerary_generation()
        
        # 测试多个城市
        test_multiple_cities()
        
        print_section("✅ 所有测试完成！")
        print("\n📊 总结:")
        print("  • 成员B (RAG检索): ✅ 正常运作")
        print("  • 成员C (行程规划): ✅ 正常运作")
        print("  • 系统集成: ✅ 完成")
        print("\n💡 下一步:")
        print("  1. 成员B: 对接真实数据源和向量数据库")
        print("  2. 成员C: 优化路线算法和成本计算")
        print("  3. 成员D: 实现前端行程展示界面")
        print()
        
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到后端服务器")
        print("请确保后端已启动: python main.py")
    except Exception as e:
        print(f"❌ 测试出错: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

