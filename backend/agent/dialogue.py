"""
对话管理器
"""
from typing import Dict, Optional
from loguru import logger

from agent.state import ConversationState, UserRequirements
from utils.llm import get_llm_client
from config import prompts


class DialogueManager:
    """对话管理器"""
    
    def __init__(self):
        self.llm = get_llm_client()
        logger.info("对话管理器初始化完成")
    
    def process_user_input(
        self,
        state: ConversationState,
        user_input: str
    ) -> str:
        """
        处理用户输入并返回回复
        
        Args:
            state: 对话状态
            user_input: 用户输入
        
        Returns:
            Agent的回复
        """
        # 添加用户消息到历史
        state.add_message("user", user_input)
        
        # 根据当前阶段决定处理方式
        if state.current_stage == "greeting":
            response = self._handle_initial_input(state, user_input)
            state.current_stage = "collecting"
            
        elif state.current_stage == "collecting":
            # 提取需求信息
            self._extract_requirements(state, user_input)
            
            # 检查是否完整
            if state.user_requirements.is_complete():
                response = self._confirm_requirements(state)
                state.current_stage = "confirming"
            else:
                response = self._ask_missing_info(state)
                
        elif state.current_stage == "confirming":
            if self._is_confirmation(user_input):
                state.current_stage = "generating"
                response = "好的！正在为您生成行程，请稍候...⏳"
            else:
                # 用户想修改，回到收集阶段
                state.current_stage = "collecting"
                response = "好的，请告诉我需要修改哪些内容～"
                
        else:
            response = "抱歉，我不太理解。您可以说得更具体一些吗？"
        
        # 添加Agent回复到历史
        state.add_message("assistant", response)
        
        return response
    
    def _handle_initial_input(
        self,
        state: ConversationState,
        user_input: str
    ) -> str:
        """处理首次输入"""
        # 尝试提取初步信息
        self._extract_requirements(state, user_input)
        
        req = state.user_requirements
        
        # 构建回复 - 主动询问所有必要信息
        if req.destination:
            return (
                f"好的！{req.destination}是个不错的选择！✨\n\n"
                f"为了给您制定更合适的行程，我需要了解以下信息：\n\n"
                f"1. 🚄 您从哪个城市出发？\n"
                f"2. 📅 计划玩几天？\n"
                f"3. 💰 大概的预算范围是多少？\n"
                f"4. 🎯 您对哪些方面比较感兴趣？（美食/文化/自然/休闲）\n"
                f"5. 👥 您是独行还是和谁一起出行？（独行/情侣/家庭/朋友）\n"
                f"6. 🔢 一共几个人出行？（包括您自己）\n\n"
                f"💡 您可以一次性告诉我，也可以分开回答～"
            )
        else:
            return (
                "好的！请问您想去哪个城市旅游呢？🌍\n\n"
                "我可以帮您规划：\n"
                "• 广东省：广州、深圳、珠海、佛山\n"
                "• 江苏省：南京、苏州、无锡、扬州\n"
                "• 浙江省：杭州、宁波、绍兴、温州\n\n"
                "💡 您也可以直接告诉我完整需求，比如：\n"
                "\"我想从上海出发去杭州玩3天，我们两个人，预算3000元，喜欢文化和美食\""
            )
    
    def _extract_requirements(
        self,
        state: ConversationState,
        user_input: str
    ):
        """使用LLM提取用户需求"""
        try:
            # 获取对话历史
            history = state.get_recent_history(5)
            context = "\n".join([
                f"{msg['role']}: {msg['content']}" 
                for msg in history
            ])
            
            # 构建提示词
            prompt = prompts.EXTRACTION_PROMPT.format(
                context=context,
                user_input=user_input
            )
            
            # 调用LLM提取
            extracted = self.llm.extract_json(prompt, user_input)
            
            logger.debug(f"提取的需求: {extracted}")
            
            # 更新用户需求（只更新非空字段）
            if extracted.get("destination"):
                state.user_requirements.destination = extracted["destination"]
                state.user_requirements.province = self._get_province(
                    extracted["destination"]
                )
            
            if extracted.get("days"):
                try:
                    state.user_requirements.days = int(extracted["days"])
                except (ValueError, TypeError):
                    pass
            
            if extracted.get("budget"):
                try:
                    state.user_requirements.budget = int(extracted["budget"])
                except (ValueError, TypeError):
                    pass
            
            if extracted.get("preferences"):
                # 合并偏好，去重
                current = set(state.user_requirements.preferences)
                new_prefs = set(extracted["preferences"])
                state.user_requirements.preferences = list(current | new_prefs)
            
            if extracted.get("travel_dates"):
                state.user_requirements.travel_dates = extracted["travel_dates"]
            
            if extracted.get("companions"):
                state.user_requirements.companions = extracted["companions"]
            
            if extracted.get("companions_count"):
                try:
                    state.user_requirements.companions_count = int(extracted["companions_count"])
                except (ValueError, TypeError):
                    pass
            
            if extracted.get("departure_city"):
                state.user_requirements.departure_city = extracted["departure_city"]
                
        except Exception as e:
            logger.error(f"提取需求失败: {e}")
            # 失败不影响流程，继续进行
    
    def _confirm_requirements(self, state: ConversationState) -> str:
        """生成需求确认信息"""
        req = state.user_requirements
        
        prefs_str = "、".join(req.preferences)
        
        confirmation = f"""
            太好了！让我为您总结一下收集到的信息：

            📍 目的地：{req.destination}
            📅 天数：{req.days}天
            💰 预算：{req.budget}元
            🎯 偏好：{prefs_str}
            """
        
        if req.departure_city:
            confirmation += f"🚄 出发地：{req.departure_city}\n"
        if req.travel_dates:
            confirmation += f"🗓️  出行时间：{req.travel_dates}\n"
        if req.companions:
            confirmation += f"👥 同行人员：{req.companions}\n"
        if req.companions_count:
            confirmation += f"🔢 出行人数：{req.companions_count}人\n"
        
        confirmation += "\n✅ 请确认以上信息是否正确？\n如需修改，请直接告诉我。确认无误的话，我就开始为您生成行程啦～"
        
        return confirmation
    
    def _ask_missing_info(self, state: ConversationState) -> str:
        """询问缺失的信息"""
        missing = state.user_requirements.missing_fields()
        
        if not missing:
            return self._confirm_requirements(state)
        
        req = state.user_requirements
        
        # 构建提问
        questions = []
        
        if "目的地" in missing:
            questions.append("📍 您想去哪个城市？（广东/江苏/浙江）")
        if "旅行天数" in missing:
            questions.append("📅 计划玩几天？")
        if "预算" in missing:
            questions.append("💰 大概预算是多少？")
        if "旅行偏好" in missing:
            questions.append("🎯 您对哪些方面比较感兴趣？\n   （美食🍜 / 文化🏛️ / 自然🏞️ / 休闲🛋️）")
        if not req.departure_city:
            questions.append("🚄 您从哪个城市出发？")
        if not req.companions:
            questions.append("👥 您是独行还是和谁一起出行？\n   （独行 / 情侣 / 家庭 / 朋友）")
        if not req.companions_count:
            questions.append("🔢 一共几个人出行？（包括您自己）")
        
        # 显示已收集的信息
        collected_info = []
        if req.destination:
            collected_info.append(f"目的地：{req.destination}")
        if req.departure_city:
            collected_info.append(f"出发地：{req.departure_city}")
        if req.days:
            collected_info.append(f"天数：{req.days}天")
        if req.budget:
            collected_info.append(f"预算：{req.budget}元")
        if req.preferences:
            collected_info.append(f"偏好：{'、'.join(req.preferences)}")
        if req.companions:
            collected_info.append(f"同行：{req.companions}")
        if req.companions_count:
            collected_info.append(f"人数：{req.companions_count}人")
        
        response = "好的！"
        if collected_info:
            response += "我已经了解到：" + "、".join(collected_info) + "。\n\n"
        
        response += "为了给您更好的推荐，我还需要了解：\n" + "\n".join(questions)
        
        return response
    
    def _is_confirmation(self, user_input: str) -> bool:
        """使用LLM智能判断是否为确认回复"""
        try:
            prompt = f"""你是一个意图识别专家。判断用户的回复是"确认"还是"否定/修改"。

            用户回复: "{user_input}"

            场景: 系统刚刚向用户展示了收集到的旅行需求信息，并询问"请确认以上信息是否正确？"

            判断规则:
            1. 如果用户表示确认、同意、正确，返回: YES
            2. 如果用户表示否定、要修改、有错误，返回: NO
            3. 如果不确定，倾向于返回: YES

            只返回YES或NO，不要其他内容。"""

            response = self.llm.chat(prompt, user_input)
            result = response.strip().upper()
            
            logger.debug(f"确认判断 - 用户输入: '{user_input}' | LLM返回: '{result}'")
            
            return result == "YES"
            
        except Exception as e:
            logger.error(f"LLM确认判断失败: {e}，使用关键词fallback")
            # Fallback到关键词匹配
            return self._is_confirmation_fallback(user_input)
    
    def _is_confirmation_fallback(self, user_input: str) -> bool:
        """关键词匹配fallback方法"""
        user_input_lower = user_input.lower().strip()
        
        # 完全匹配列表
        exact_confirmations = ["是", "对", "好", "行", "嗯", "yes", "ok", "y"]
        if user_input_lower in exact_confirmations:
            return True
        
        # 肯定短语
        positive_phrases = [
            "确认", "正确", "可以", "好的", "是的", "没错", "对的", "没问题",
            "correct", "okay", "👌", "✅", "开始", "生成", "继续"
        ]
        if any(phrase in user_input_lower for phrase in positive_phrases):
            return True
        
        # 否定词
        negations = ["不", "别", "修改", "改", "no", "不是", "不对", "不行", "错了"]
        if any(neg in user_input_lower for neg in negations):
            return False
        
        return False
    
    def _get_province(self, city: str) -> Optional[str]:
        """根据城市名获取省份"""
        city_province_map = {
            # 广东
            "广州": "广东省", "深圳": "广东省", "珠海": "广东省", "佛山": "广东省",
            # 江苏
            "南京": "江苏省", "苏州": "江苏省", "无锡": "江苏省", "扬州": "江苏省",
            # 浙江
            "杭州": "浙江省", "宁波": "浙江省", "绍兴": "浙江省", "温州": "浙江省",
        }
        return city_province_map.get(city)

