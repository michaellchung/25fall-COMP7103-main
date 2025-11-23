#!/usr/bin/env python3
"""
测试RAG景点检索服务
"""
import sys
import os

# 添加backend到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from tools.attraction import get_attraction_service

def test_basic_retrieval():
    """测试基本检索功能"""
    print("="*60)
    print("测试1: 基本检索 - 杭州景点")
    print("="*60)
    
    service = get_attraction_service()
    
    results = service.retrieve_attractions(
        city="杭州",
        preferences=[],
        top_k=5
    )
    
    print(f"\n✅ 检索到 {len(results)} 个景点：")
    for i, att in enumerate(results, 1):
        print(f"{i}. {att.name}")
        print(f"   分类: {att.category}")
        print(f"   评分: {att.rating}")
        print(f"   门票: ¥{att.ticket_price}")
        print(f"   位置: {att.location}")
        print()

def test_preference_filter():
    """测试偏好过滤"""
    print("="*60)
    print("测试2: 偏好过滤 - 自然风光")
    print("="*60)
    
    service = get_attraction_service()
    
    results = service.retrieve_attractions(
        city="杭州",
        preferences=["自然风光", "文化"],
        top_k=5
    )
    
    print(f"\n✅ 检索到 {len(results)} 个景点：")
    for i, att in enumerate(results, 1):
        print(f"{i}. {att.name} - {att.category}")

def test_budget_filter():
    """测试预算过滤"""
    print("\n" + "="*60)
    print("测试3: 预算过滤 - 免费景点")
    print("="*60)
    
    service = get_attraction_service()
    
    results = service.retrieve_attractions(
        city="杭州",
        preferences=[],
        top_k=10,
        budget_max=0
    )
    
    print(f"\n✅ 检索到 {len(results)} 个免费景点：")
    for i, att in enumerate(results, 1):
        print(f"{i}. {att.name} - ¥{att.ticket_price}")

def test_agent_integration():
    """测试Agent集成"""
    print("\n" + "="*60)
    print("测试4: Agent集成测试")
    print("="*60)
    
    # 模拟Agent调用
    service = get_attraction_service()
    
    # 场景：用户想去杭州，偏好自然风光，预算500元内
    req = {
        "city": "杭州",
        "preferences": ["自然风光"],
        "budget": 500
    }
    
    print(f"\n用户需求: {req}")
    
    results = service.retrieve_attractions(
        city=req["city"],
        preferences=req["preferences"],
        top_k=5,
        budget_max=req["budget"]
    )
    
    print(f"\n✅ 为用户推荐 {len(results)} 个景点：")
    for i, att in enumerate(results, 1):
        print(f"\n{i}. 【{att.name}】")
        print(f"   📍 {att.address}")
        print(f"   💰 门票: ¥{att.ticket_price}")
        print(f"   ⏱️  建议游玩: {att.duration_hours}小时")
        print(f"   ⭐ 评分: {att.rating}")
        print(f"   💡 建议: {att.tips}")

if __name__ == "__main__":
    try:
        test_basic_retrieval()
        test_preference_filter()
        test_budget_filter()
        test_agent_integration()
        
        print("\n" + "="*60)
        print("✅ 所有测试通过！")
        print("="*60)
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

