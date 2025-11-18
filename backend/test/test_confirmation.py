"""
测试确认逻辑
"""
import sys
sys.path.append('/Applications/MyDocument/7103/backend')

from agent.dialogue import DialogueManager

def test_confirmation_logic():
    """测试确认词识别"""
    dm = DialogueManager()
    
    test_cases = [
        # (输入, 预期结果)
        ("正确", True),
        ("是", True),
        ("是的", True),
        ("对", True),
        ("对的", True),
        ("好", True),
        ("好的", True),
        ("可以", True),
        ("确认", True),
        ("没错", True),
        ("没问题", True),
        ("行", True),
        ("嗯", True),
        ("ok", True),
        ("OK", True),
        ("yes", True),
        ("YES", True),
        ("开始", True),
        ("生成", True),
        ("继续", True),
        ("👌", True),
        ("✅", True),
        # 否定词
        ("不对", False),
        ("错了", False),
        ("修改", False),
        ("改一下", False),
        ("我要改", False),
    ]
    
    print("=" * 80)
    print("确认词识别测试")
    print("=" * 80)
    
    passed = 0
    failed = 0
    
    for user_input, expected in test_cases:
        result = dm._is_confirmation(user_input)
        status = "✅ PASS" if result == expected else "❌ FAIL"
        
        if result == expected:
            passed += 1
        else:
            failed += 1
        
        print(f"{status} | 输入: '{user_input}' | 预期: {expected} | 实际: {result}")
    
    print("\n" + "=" * 80)
    print(f"测试结果: {passed} passed, {failed} failed")
    print("=" * 80)
    
    if failed == 0:
        print("✅ 所有测试通过！")
    else:
        print(f"❌ 有 {failed} 个测试失败")

if __name__ == "__main__":
    test_confirmation_logic()

