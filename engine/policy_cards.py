"""
国家宏观金融体系模拟器 - 历史名策卡系统 (Policy Cards)
"""
from dataclasses import dataclass
from typing import Dict, List, Optional, Any

@dataclass
class PolicyCard:
    id: str
    name: str
    tag: str                        # 策略流派标签 (如: 凯恩斯主义 / 供给学派 / 现代货币理论)
    history_intro: str              # 历史背景介绍
    duration_days: int              # 持续天数 (如 720 天 = 8 季度)
    cooldown_days: int              # 到期后冷却天数
    
    # 资金流穿透说明
    money_source: str               # 钱从哪来
    money_target: str               # 钱到哪去
    daily_cost_type: str            # 支出类型 ('treasury', 'central_bank_print', 'tax_cut')
    daily_cost_amount: float        # 每日资金额度 (亿元/天)
    
    # 状态
    is_active: bool = False
    days_active: int = 0
    days_cooldown_left: int = 0

def get_initial_policy_cards() -> Dict[str, PolicyCard]:
    """获取初始提供的3张经典历史名策"""
    return {
        "roosevelt_new_deal": PolicyCard(
            id="roosevelt_new_deal",
            name="【罗斯福新政·以工代赈】",
            tag="凯恩斯主义 / 危机托底",
            history_intro="1933年大萧条时期，美国政府跳过资本中介，以国家信用启动田纳西水利等大规模公共工程，直接向底层失业者购买劳动力。",
            duration_days=720,  # 8 个季度 (2年)
            cooldown_days=360,  # 冷却 4 个季度
            money_source="国库专项赤字拨款 / 特别国债发售",
            money_target="直达底层失业劳工（政府直接雇佣45万人修筑路桥堤坝）",
            daily_cost_type="treasury",
            daily_cost_amount=0.35 # 每天耗费国库0.35亿用于工人工资和材料
        ),
        
        "reagan_tax_cut": PolicyCard(
            id="reagan_tax_cut",
            name="【里根大减税·供给学派革命】",
            tag="供给学派 / 激发活力",
            history_intro="1981年美国里根总统推行供给学派改革，大幅度削减企业所得税与资本利得税，相信降低企业税负能释放强大的民间投资与生产潜能。",
            duration_days=1080, # 12 个季度 (3年)
            cooldown_days=720,
            money_source="国库主动放弃企业税收（企业税率强制定格在超低档 12%）",
            money_target="留存于实体企业营运现金池，全额激励用于扩产与技术升级",
            daily_cost_type="tax_cut",
            daily_cost_amount=0.0  # 自动通过削减税率体现
        ),
        
        "helicopter_money": PolicyCard(
            id="helicopter_money",
            name="【直升机撒钱·普惠现金补贴】",
            tag="现代货币理论 / 消费刺激",
            history_intro="弗里德曼构想、2020年全球抗疫期间多国实践。央行越过银行信贷传导阻塞，直接印钞并无差别向全民发放生存消费支票。",
            duration_days=360,  # 4 个季度 (1年)
            cooldown_days=720,
            money_source="央行特殊资产负债表扩张（无负债直接印发基础货币）",
            money_target="直达全社会居民存款账户（重点补贴底层基本口粮与民生）",
            daily_cost_type="central_bank_print",
            daily_cost_amount=0.40 # 每天由央行凭空印出0.40亿直接打入居民账户
        ),
        
        "austerity_reform": PolicyCard(
            id="austerity_reform",
            name="【铁腕财政整顿·阳光采购与机构精简】",
            tag="财政紧缩 / 标本兼治",
            history_intro="阿根廷与希腊债务危机整顿方案。针对行政开支严重臃肿、公款吃喝与采购回扣，推行铁腕行政重组与公开电子透明集中采购，裁撤冗员，从制度源头压降财政黑洞。",
            duration_days=540,  # 6 个季度 (1.5年)
            cooldown_days=360,
            money_source="财政部预算硬约束命令",
            money_target="全面削减公车、差旅、豪华修缮与政府采购溢价",
            daily_cost_type="treasury",
            daily_cost_amount=0.0  # 自动大幅扣减日常行政公用开支G (压降40%)
        ),
        
        "digital_tax_reform": PolicyCard(
            id="digital_tax_reform",
            name="【金税工程·数字税控与穿透征管】",
            tag="制度经济学 / 拓宽税基",
            history_intro="借鉴金税工程与现代GST增值税电子发票改革。推行全社会商户发票联单与银行流水数字穿透，严厉打击地下经济与假账偷税，在不提高名义税率的前提下做大实际税基。",
            duration_days=720,  # 8 个季度 (2年)
            cooldown_days=360,
            money_source="国库数字稽查与IT系统维护专款",
            money_target="国家税务总局全国发票与税控服务器集群",
            daily_cost_type="treasury",
            daily_cost_amount=0.04 # 每日划拨0.04亿系统运维与稽查队伍津贴
        )
    }

class PolicyCardManager:
    """政策卡槽位与生命周期管理器"""
    def __init__(self, max_active_slots: int = 2):
        self.max_active_slots = max_active_slots
        self.cards: Dict[str, PolicyCard] = get_initial_policy_cards()
        self.active_card_ids: List[str] = []
        
    def activate_card(self, card_id: str) -> tuple[bool, str]:
        if card_id not in self.cards:
            return False, "未找到该政策卡。"
            
        card = self.cards[card_id]
        if card.is_active:
            return False, "该政策卡正在生效中。"
            
        if card.days_cooldown_left > 0:
            return False, f"该政策卡正处于冷却中，还剩 {card.days_cooldown_left} 天。"
            
        if len(self.active_card_ids) >= self.max_active_slots:
            return False, f"政策槽位已满（最多同时激活 {self.max_active_slots} 张战略政策卡）。"
            
        card.is_active = True
        card.days_active = 0
        self.active_card_ids.append(card_id)
        return True, f"成功签署并推行了 {card.name}！"
        
    def cancel_card_early(self, card_id: str) -> tuple[bool, str]:
        """提前废除正在生效的政策卡（朝令夕改重罚）"""
        if card_id not in self.cards or card_id not in self.active_card_ids:
            return False, "该政策卡并未激活。"
            
        card = self.cards[card_id]
        card.is_active = False
        card.days_cooldown_left = card.cooldown_days
        self.active_card_ids.remove(card_id)
        return True, f"强行废除了 {card.name}！政策公信力受到严厉惩罚！"
        
    def tick_daily(self) -> List[str]:
        """每日更新政策卡计时，返回到期事件信息"""
        expired_events = []
        for card_id, card in self.cards.items():
            if card.is_active:
                card.days_active += 1
                if card.days_active >= card.duration_days:
                    card.is_active = False
                    card.days_cooldown_left = card.cooldown_days
                    if card_id in self.active_card_ids:
                        self.active_card_ids.remove(card_id)
                    expired_events.append(f"【政策到期】{card.name} 预定期限已满，正式平稳结束。进入冷却期。")
            else:
                if card.days_cooldown_left > 0:
                    card.days_cooldown_left -= 1
        return expired_events
