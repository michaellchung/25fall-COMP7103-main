"""
测试LLM版本的确认识别
"""
import sys
sys.path.append('/Applications/MyDocument/7103/backend')

from agent.dialogue import DialogueManager
from loguru import logger

# 配置日志
logger.remove()
logger.add(sys.stdout, level="DEBUG")

def test_llm_confirmation():
    """测试LLM确认识别"""
    dm = DialogueManager()
    
    test_cases = [
        # (输入, 预期结果, 描述)
        ("正确", True, "直接确认"),
        ("是", True, "简短确认"),
        ("是的", True, "礼貌确认"),
        ("对", True, "口语确认"),
        ("对的", True, "口语确认+语气词"),
        ("好", True, "同意"),
        ("好的", True, "礼貌同意"),
        ("可以", True, "表示可以"),
        ("确认", True, "明确确认"),
        ("没错", True, "肯定无误"),
        ("没问题", True, "表示没问题"),
        ("ok", True, "英文确认"),
        ("yes", True, "英文确认"),
        ("对的，没问题", True, "复合确认"),
        ("是的，正确", True, "复合确认"),
        ("嗯，可以", True, "口语+确认"),
        
        # 否定/修改
        ("不对", False, "明确否定"),
        ("错了", False, "指出错误"),
        ("修改", False, "要求修改"),
        ("改一下", False, "要求修改"),
        ("我要改", False, "要求修改"),
        ("不是", False, "否定"),
        ("不对，预算应该是3000", False, "否定+修改"),
        ("天数改成4天", False, "直接修改"),
        ("预算不对", False, "指出错误"),
        
        # 边界情况
        ("嗯嗯", True, "口语确认"),
        ("👌", True, "emoji确认"),
        ("✅", True, "emoji确认"),
        ("好的，开始吧", True, "确认+行动"),
        ("对，就这样", True, "确认+肯定"),
    ]
    
    print("=" * 80)
    print("LLM确认识别测试")
    print("=" * 80)
    
    passed = 0
    failed = 0
    failed_cases = []
    
    for user_input, expected, description in test_cases:
        result = dm._is_confirmation(user_input)
        status = "✅ PASS" if result == expected else "❌ FAIL"
        
        if result == expected:
            passed += 1
        else:
            failed += 1
            failed_cases.append((user_input, expected, result, description))
        
        print(f"{status} | '{user_input}' ({description}) | 预期: {expected} | 实际: {result}")
    
    print("\n" + "=" * 80)
    print(f"测试结果: {passed} passed, {failed} failed")
    print("=" * 80)
    
    if failed > 0:
        print("\n失败的测试用例:")
        for user_input, expected, result, description in failed_cases:
            print(f"  ❌ '{user_input}' ({description})")
            print(f"     预期: {expected}, 实际: {result}")
    else:
        print("\n✅ 所有测试通过！")

if __name__ == "__main__":
    test_llm_confirmation()

