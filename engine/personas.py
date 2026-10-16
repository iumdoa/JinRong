"""
国家宏观金融体系模拟器 - 全景微观真实账本与画像引擎 (personas.py)
涵盖：
1. 全产业 15 大微观雇主与资本经营账本 (跨行业实体与资本视角，映射全国 98,300 家各类企业实体)
2. 全社会 22 大工种与民生阶层真实家庭账本 (严格映射全国 10,000,000 人口大盘与 6 大阶层)

核心数学与经济学原则：
- 严格社会普查基准 (Census)：全国人口总数严格恒等于 10,000,000 人 (1000万人)。
- 22 位代表性国民的代表人口之和严格等于 1000 万，与 6 大社会阶层人口严格闭合。
- 15 位微观产业雇主的实体数量 (entity_count) 真实反映全社会商业与工业实体密度 (共 98,300 家企业)。
- 微观 ➔ 宏观聚合：微观每人/每店收支 × 全国同类人数/实体数 = 全社会宏观经济总流量 (亿元)。
- 宏观 ➔ 微观均摊：全社会特定产业消费总额 / 全国在册实体总数 = 单一代表商户/工厂的真实营业额。
- 收支比 (R) 与活动能力分层：游戏初期大部分底层群众收支比低 (R < 1.3)，主要用于生存温饱；
  高净值科研专家、IT白领及各行业雇主收支比高 (R >= 2.2)，率先启动文旅度假、大众餐饮和成衣轻工消费！
"""
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional

@dataclass
class MicroReceiptLine:
    """微观真实凭证流水行"""
    subject: str           # 会计科目 (如: "高压合成氨采购", "个人住房按揭扣息")
    from_acc: str          # 资金来源账户
    to_acc: str            # 资金去向账户
    amount_yuan: float     # 金额 (元/天)
    direction: str         # "income" (流入) | "expense" (流出)
    note: str              # 业务说明

@dataclass
class MicroLedgerCard:
    """微观人物账本实体"""
    id: str
    name: str
    title: str
    category: str          # "agriculture", "mining", "manufacturing", "logistics", "service", "middle_class", "welfare"
    category_name: str
    avatar: str
    scale_label: str       # 代表规模 (如: "代表全国80万井下采掘重工 · 收支比 1.39x")
    
    # 宏观普查与代表规模 (人数或实体数)
    representative_count: int = 1         # 公民为全国同类代表人口数 / 雇主为全国同类实体企业数
    income_expense_ratio: float = 1.0     # 收支比 R = 日总收入 / 日生存刚性支出
    savings_cushion_months: float = 1.0   # 储蓄抗风险安全垫 (可支撑生存月数)
    discretionary_propensity: float = 0.0 # 改善型可选消费意向活跃度 (0~1)
    
    # 核心财务指标 (元/天)
    daily_revenue: float = 0.0     # 雇主为日营收入 / 个人为日总收入
    daily_expense: float = 0.0     # 雇主为营运总支出 / 个人为生活总支出
    daily_net: float = 0.0         # 雇主为净留存利润 / 个人为日净储蓄结余
    accumulated_funds: float = 0.0 # 雇主为企业银行存款(万元) / 个人为家庭总储蓄(元)
    
    # 财务与生活抗风险状态
    financial_status: str = "normal"  # "thriving" (充沛景气) | "normal" (平稳运行) | "warning" (压力紧张) | "crisis" (入不敷出/濒临断炊)
    status_desc: str = ""
    
    # 核心开销科目占比拆解 (用于UI条形图展示)
    breakdown: Dict[str, float] = field(default_factory=dict)
    
    # 实时动态心声
    voice: str = ""
    
    # 仿真纸质对账凭单
    voucher_title: str = ""
    voucher_number: str = ""
    receipt_lines: List[Dict[str, Any]] = field(default_factory=list)


# ==============================================================================
# 📊 全国人口与实体经济严格普查映射表 (Strict Census Mapping, 闭环 1000 万人)
# ==============================================================================

CITIZEN_CENSUS: Dict[str, Dict[str, Any]] = {
    # 1. 采矿与重体力劳工阶层 (miner_heavy: 2,200,000人)
    "zhang_miner": {
        "name": "老张", "tier_id": "miner_heavy", "population": 800_000,
        "role_desc": "煤矿大型井下机电综采掘进工",
        "base_budget": {"tour": 0.0, "eat": 3.0, "apparel": 2.5}
    },
    "zhao_builder": {
        "name": "老赵", "tier_id": "miner_heavy", "population": 900_000,
        "role_desc": "基建重大工程泥瓦钢筋散工",
        "base_budget": {"tour": 2.0, "eat": 4.0, "apparel": 3.0}
    },
    "zhao_cleaner": {
        "name": "赵阿姨", "tier_id": "miner_heavy", "population": 500_000,
        "role_desc": "市政环境卫生道路清扫与绿化保洁员",
        "base_budget": {"tour": 0.0, "eat": 1.0, "apparel": 2.0}
    },
    
    # 2. 农耕自耕农与种植散工阶层 (farmer: 2,400,000人)
    "tian_farmer": {
        "name": "老田", "tier_id": "farmer", "population": 1_600_000,
        "role_desc": "农村粮食种植自耕农",
        "base_budget": {"tour": 0.0, "eat": 1.5, "apparel": 2.0}
    },
    "xu_farm_driver": {
        "name": "徐师傅", "tier_id": "farmer", "population": 400_000,
        "role_desc": "大型现代农场联合收割机农机手",
        "base_budget": {"tour": 4.0, "eat": 6.0, "apparel": 4.0}
    },
    "zhang_elder": {
        "name": "张大爷", "tier_id": "farmer", "population": 400_000,
        "role_desc": "农村高龄留守丧失劳动能力老农",
        "base_budget": {"tour": 0.0, "eat": 0.0, "apparel": 1.0}
    },
    
    # 3. 轻工制造流水线操作工阶层 (operator_light: 2,000,000人)
    "liu_textile": {
        "name": "小刘", "tier_id": "operator_light", "population": 700_000,
        "role_desc": "现代外贸服装流水线平缝车位工",
        "base_budget": {"tour": 2.0, "eat": 4.0, "apparel": 5.0}
    },
    "guan_food_pack": {
        "name": "关师傅", "tier_id": "operator_light", "population": 500_000,
        "role_desc": "粮油精炼与食品包装车间操作手",
        "base_budget": {"tour": 3.0, "eat": 5.0, "apparel": 4.0}
    },
    "yang_cashier": {
        "name": "小杨", "tier_id": "operator_light", "population": 400_000,
        "role_desc": "商超收银员与便利零售理货员",
        "base_budget": {"tour": 1.0, "eat": 3.0, "apparel": 3.0}
    },
    "he_kitchen": {
        "name": "小何", "tier_id": "operator_light", "population": 400_000,
        "role_desc": "大众快餐连锁后厨配菜打荷工",
        "base_budget": {"tour": 2.0, "eat": 3.0, "apparel": 3.0}
    },
    
    # 4. 熟练数控车铣与特种技工阶层 (technician_skilled: 1,400,000人)
    "sun_machinist": {
        "name": "孙师傅", "tier_id": "technician_skilled", "population": 400_000,
        "role_desc": "高级八级数控车铣与精密模具技师",
        "base_budget": {"tour": 10.0, "eat": 12.0, "apparel": 10.0}
    },
    "liu_truck_driver": {
        "name": "刘师傅", "tier_id": "technician_skilled", "population": 350_000,
        "role_desc": "跨省大宗干线重型卡车长途驾驶员",
        "base_budget": {"tour": 5.0, "eat": 8.0, "apparel": 6.0}
    },
    "jiang_taxi_driver": {
        "name": "蒋师傅", "tier_id": "technician_skilled", "population": 350_000,
        "role_desc": "城市出租车与纯电网约车全职驾驶员",
        "base_budget": {"tour": 5.0, "eat": 8.0, "apparel": 6.0}
    },
    "xie_electrician": {
        "name": "老谢", "tier_id": "technician_skilled", "population": 300_000,
        "role_desc": "大型社区综合物业工程维保特种水电工",
        "base_budget": {"tour": 4.0, "eat": 6.0, "apparel": 5.0}
    },
    
    # 5. 白领财务、管理与公共事业阶层 (white_collar: 1,500,000人)
    "li_accountant": {
        "name": "李会计", "tier_id": "white_collar", "population": 500_000,
        "role_desc": "民营企业与商贸物流总账会计",
        "base_budget": {"tour": 15.0, "eat": 18.0, "apparel": 12.0}
    },
    "lin_it_engineer": {
        "name": "小林", "tier_id": "white_collar", "population": 300_000,
        "role_desc": "工业物联网与MES系统软件实施工程师",
        "base_budget": {"tour": 25.0, "eat": 25.0, "apparel": 18.0}
    },
    "zhou_nurse": {
        "name": "周护士", "tier_id": "white_collar", "population": 350_000,
        "role_desc": "社区卫生服务站与平价门诊部骨干护士",
        "base_budget": {"tour": 8.0, "eat": 10.0, "apparel": 8.0}
    },
    "chen_teacher": {
        "name": "陈老师", "tier_id": "white_collar", "population": 350_000,
        "role_desc": "扎根乡村义务教育特岗骨干教师",
        "base_budget": {"tour": 6.0, "eat": 8.0, "apparel": 7.0}
    },
    
    # 6. 工业专家、顶尖科研与灵活服务阶层 (engineer_expert: 500,000人)
    "lin_expert": {
        "name": "林博士", "tier_id": "engineer_expert", "population": 150_000,
        "role_desc": "国家电网与半导体芯片首席科学家",
        "base_budget": {"tour": 45.0, "eat": 35.0, "apparel": 28.0}
    },
    "zheng_tour_guide": {
        "name": "小郑", "tier_id": "engineer_expert", "population": 100_000,
        "role_desc": "文旅精品度假与研学持证地接导游",
        "base_budget": {"tour": 3.0, "eat": 5.0, "apparel": 5.0}
    },
    "zhou_rider": {
        "name": "小周", "tier_id": "engineer_expert", "population": 150_000,
        "role_desc": "同城即时配送外卖跑腿骑手",
        "base_budget": {"tour": 2.0, "eat": 4.0, "apparel": 4.0}
    },
    "aqiang_unemployed": {
        "name": "阿强", "tier_id": "engineer_expert", "population": 100_000,
        "role_desc": "城镇流动待业青年与失业求职者",
        "base_budget": {"tour": 0.0, "eat": 1.0, "apparel": 1.0}
    }
}

EMPLOYER_CENSUS: Dict[str, Dict[str, Any]] = {
    "qian_farm": {"entity_count": 1_200, "unit_name": "个万亩现代粮油家庭农场", "employees_per_entity": 15},
    "sun_coal": {"entity_count": 300, "unit_name": "座现代化综合综采煤矿井", "employees_per_entity": 120},
    "chen_machinery": {"entity_count": 2_500, "unit_name": "家精密机械五金加工厂", "employees_per_entity": 24},
    "zhu_textile": {"entity_count": 1_800, "unit_name": "家出口轻工服装制衣厂", "employees_per_entity": 180},
    "wu_construction": {"entity_count": 1_500, "unit_name": "个市政路桥与建工承包标段", "employees_per_entity": 40},
    "wei_logistics": {"entity_count": 3_000, "unit_name": "个跨省大宗干线物流车队", "employees_per_entity": 30},
    "wang_retail": {"entity_count": 20_000, "unit_name": "家社区便民连锁超市门市", "employees_per_entity": 8},
    "zhang_tech": {"entity_count": 800, "unit_name": "家工业软件与企业财税科技公司", "employees_per_entity": 40},
    "gao_bank": {"entity_count": 600, "unit_name": "家国家商业银行重点城市分行/网点", "employees_per_entity": 50},
    "zhang_catering": {"entity_count": 45_000, "unit_name": "家社区大众便民快餐连锁店", "employees_per_entity": 4},
    "su_tourism": {"entity_count": 12_000, "unit_name": "家文旅近郊精品度假民宿客栈", "employees_per_entity": 3},
    "he_clinic": {"entity_count": 4_000, "unit_name": "家社区平价综合门诊部/卫生所", "employees_per_entity": 6},
    "liang_training": {"entity_count": 600, "unit_name": "家现代职业技能技术实训中心", "employees_per_entity": 5},
    "lu_taxi_fleet": {"entity_count": 1_500, "unit_name": "个城市客运出租与网约车队", "employees_per_entity": 40},
    "luo_property": {"entity_count": 3_500, "unit_name": "个社区综合物业租售服务处", "employees_per_entity": 12}
}


def calculate_discretionary_propensity(ratio: float, cushion_months: float, sentiment_index: float) -> float:
    """
    根据微观个体收支比 (R) 与储蓄缓冲度 (C) 计算其改善型消费活跃度 (A: 0~1)
    - R < 1.25: 严格生存兜底线，可选改善型消费 = 0 (优先满足口粮与房租)
    - 1.25 <= R < 1.70: 弱改善期 (A: 0.00 ~ 0.35)
    - 1.70 <= R < 2.20: 稳步中产期 (A: 0.20 ~ 0.75)
    - R >= 2.20: 高度充裕消费期 (A: 0.60 ~ 1.00，林博士、IT白领及各行业雇主率先消费)
    """
    s_mult = max(0.2, min(2.0, (sentiment_index / 100.0) * 1.5))
    if ratio < 1.25:
        return 0.0
    elif ratio < 1.70:
        base = ((ratio - 1.25) / 0.45) * 0.35
        cushion_factor = min(1.0, cushion_months / 2.0)
        return max(0.0, min(0.35, round(base * cushion_factor * s_mult, 3)))
    elif ratio < 2.20:
        base = 0.35 + ((ratio - 1.70) / 0.50) * 0.40
        cushion_factor = min(1.0, cushion_months / 3.0)
        return max(0.20, min(0.75, round(base * cushion_factor * s_mult, 3)))
    else:
        base = min(1.0, 0.75 + (ratio - 2.20) * 0.15)
        cushion_factor = min(1.0, cushion_months / 4.0)
        return max(0.60, min(1.0, round(base * cushion_factor * s_mult, 3)))


def calculate_micro_ledgers(
    state: Any,
    accounting_bus: Any,
    factory_manager: Any,
    commodity_hub: Any,
    labor_manager: Any,
    infra_manager: Any
) -> Dict[str, Any]:
    """
    全景计算并生成 15 大微观雇主经营账本与 22 大工种民生家庭账本
    全部数据严格基于 1000 万人口普查矩阵与 98,300 家企业实体普查闭环联动
    """
    # 宏观环境变量提取
    gdp_runrate = getattr(state, "gdp_annual_runrate", 2300.0)
    baseline_gdp = 3800.0 if getattr(state, "difficulty_mode", "frugal") == "standard" else 1900.0
    macro_rev_factor = max(0.6, min(2.5, gdp_runrate / baseline_gdp))
    
    food_price = getattr(state, "food_basket_price", 15.0)
    cpi = getattr(state, "cpi_index", 100.0)
    loan_rate = getattr(state, "loan_interest_rate", 0.065)
    deposit_rate = getattr(state, "deposit_interest_rate", 0.02)
    loan_cost_10k_month = getattr(state, "loan_cost_per_10k_month", 54.2)
    min_wage = getattr(state, "min_wage_daily", 36.0)
    corp_tax_rate = getattr(state, "corp_tax_rate", 0.18)
    vat_tax_rate = getattr(state, "vat_tax_rate", 0.08)
    income_tax_rate = getattr(state, "income_tax_rate", 0.05)
    social_contrib_rate = getattr(state, "social_contrib_rate", 0.12)
    medicare_rate = getattr(state, "medicare_reimburse_rate", 0.65)
    sentiment_index = getattr(state, "consumer_sentiment", 30.0)
    sentiment = sentiment_index / 100.0
    unemployment_rate = getattr(state, "unemployment_rate", 0.18)
    
    infra_daily = getattr(state, "infra_daily_spending", 0.0)
    infra_maint = getattr(state, "infra_maintenance_spending", 0.0)
    welfare_daily = getattr(state, "welfare_spending", 0.15)
    res_grant = getattr(state, "active_research_grant", {})
    
    # 政策卡生效检查与基础设施增益
    buffs = getattr(infra_manager, "accumulated_buffs", {}) if infra_manager else {}
    energy_discount = buffs.get("corp_cost_discount", 0.0) * 1.8
    profit_mult = buffs.get("firm_profit_multiplier", 1.0)
    mobility_factor = 1.0 + buffs.get("transport_mobility", 0.0) # 跨省骨干铁路公路带来的旅游出游流动性倍率
    
    # 大宗物资即期价格
    comms = getattr(commodity_hub, "commodities", {}) if commodity_hub else {}
    p_coal = comms.get("coal").domestic_price if "coal" in comms else 480.0
    p_steel = comms.get("steel").domestic_price if "steel" in comms else 3200.0
    p_cement = comms.get("cement").domestic_price if "cement" in comms else 350.0
    p_fertilizer = comms.get("fertilizer").domestic_price if "fertilizer" in comms else 2100.0
    p_oil = comms.get("crude_oil").domestic_price if "crude_oil" in comms else 520.0
    p_grain = comms.get("raw_grain").domestic_price if "raw_grain" in comms else 2200.0
    p_textile = comms.get("textile").domestic_price if "textile" in comms else 45.0
    p_hardware = comms.get("hardware").domestic_price if "hardware" in comms else 180.0
    p_machinery = comms.get("heavy_machinery").domestic_price if "heavy_machinery" in comms else 480000.0
    
    # 工厂经营状态
    facts = getattr(factory_manager, "factories", {}) if factory_manager else {}
    f_hardware = facts.get("hardware_machinery")
    f_textile = facts.get("textile_light")
    f_coal = facts.get("coal_mine")
    
    tier_map = {h.id: h for h in state.households}
    h_miner = tier_map.get("miner_heavy", state.households[0])
    h_farmer = tier_map.get("farmer", state.households[1] if len(state.households) > 1 else state.households[0])
    h_light = tier_map.get("operator_light", state.households[2] if len(state.households) > 2 else state.households[0])
    h_skilled = tier_map.get("technician_skilled", state.households[3] if len(state.households) > 3 else state.households[0])
    h_white = tier_map.get("white_collar", state.households[4] if len(state.households) > 4 else state.households[0])
    h_expert = tier_map.get("engineer_expert", state.households[5] if len(state.households) > 5 else state.households[0])

    c_pool = getattr(state, "citizen_savings_pool", {})
    e_pool = getattr(state, "employer_capital_pool", {})
    
    # Phase 1: 跟踪在册企业实体数与破产重组出清数
    active_entities = getattr(state, "employer_active_entities", {})
    bankrupt_counts = getattr(state, "employer_bankrupt_counts", {})
    if not active_entities:
        active_entities = {eid: cfg["entity_count"] for eid, cfg in EMPLOYER_CENSUS.items()}
        state.employer_active_entities = active_entities
    if not bankrupt_counts:
        bankrupt_counts = {eid: 0 for eid in EMPLOYER_CENSUS}
        state.employer_bankrupt_counts = bankrupt_counts

    # =========================================================================
    # 🔍 第一阶段：预计算 22 大国民个体的收支比 R、储蓄安全垫 C 与可选消费活跃度 A
    # =========================================================================
    cit_metrics: Dict[str, Dict[str, float]] = {}
    
    # 预计算老张收入
    if h_miner.daily_income > 0.001 and h_miner.employed > 0:
        zm_inc = round((h_miner.daily_income * 100_000_000) / h_miner.employed, 1)
    else:
        zm_inc = round(h_miner.base_wage, 1)
        
    # 预计算老赵工钱
    zhao_inc_rate = max(min_wage * 1.25, 45.0 + (infra_daily / 0.15) * 12.0)
    
    # 预计算小刘工钱 (现代外贸流水线缝纫女工：保障底薪 + 计件绩效与赶工津贴)
    zhu_util = getattr(f_textile, "utilization_rate", 85.0) if f_textile else 85.0
    liu_base_wage = max(min_wage * 1.20, 48.0)  # 法定兜底保障底薪
    liu_piece_bonus = round(16.0 * (zhu_util / 85.0), 1) # 出口外贸成衣计件提成与加班奖励
    liu_inc_rate = round(liu_base_wage + liu_piece_bonus, 1) # 正常达产为 48 + 16 = 64 元/天
    zhu_wage_per_worker = liu_inc_rate

    # 预计算李会计收入
    if h_white.daily_income > 0.001 and h_white.employed > 0:
        li_inc_rate = round((h_white.daily_income * 100_000_000) / h_white.employed, 1)
    else:
        li_inc_rate = round(h_white.base_wage, 1)

    # 预计算林博士日薪
    grant_boost = res_grant.get("boost", 0.0) if res_grant.get("is_active") else 0.0
    dr_inc_rate = round(280.0 + (grant_boost * 12.0), 1)

    # 预估各公民的基准收入与生存刚性支出
    pre_data = {
        "zhang_miner": {"inc": zm_inc, "ess": round(food_price * 1.5 + 3.5 + max(1.0, 4.0 * (1.0 - medicare_rate)), 1)},
        "zhao_builder": {"inc": zhao_inc_rate, "ess": round(food_price * 1.3 + 6.0, 1)},
        "zhao_cleaner": {"inc": round(max(min_wage * 1.05, 38.0) + 4.0, 1), "ess": round(food_price * 0.75 + 10.0 + max(1.0, 6.0 * (1.0 - medicare_rate)), 1)},
        "tian_farmer": {"inc": round(30.0 * (p_grain / 2200.0) + (welfare_daily * 4.0), 1), "ess": round(8.5 * (p_fertilizer / 2100.0) + food_price * 0.7 + 4.5, 1)},
        "xu_farm_driver": {"inc": 65.0, "ess": round(food_price * 1.2 + 6.0 * (p_oil / 520.0) + 20.0, 1)},
        "zhang_elder": {"inc": round(12.0 * (state.social_fund_pool / 450.0 * 0.2 + 0.8), 1), "ess": round(food_price * 0.6 + max(0.5, 4.0 * (1.0 - medicare_rate)), 1)},
        "liu_textile": {"inc": liu_inc_rate, "ess": round(food_price * 1.0 + 5.0 + liu_inc_rate * (social_contrib_rate * 0.4) + 16.0, 1)},
        "guan_food_pack": {"inc": round(max(min_wage * 1.12, 50.0), 1), "ess": round(food_price * 1.1 + 12.0 + 6.0, 1)},
        "yang_cashier": {"inc": round(min_wage, 1), "ess": round(food_price * 1.0 + 10.0, 1)},
        "he_kitchen": {"inc": round(max(min_wage * 1.15, 45.0) + (sentiment * 6.0), 1), "ess": round(food_price * 0.45 + 12.0 + 18.0, 1)},
        "sun_machinist": {"inc": round(135.0 * (1.0 + buffs.get("capacity_bonus", 0.0) / 3000.0), 1), "ess": round(food_price * 1.8 + 18.0 + max(0.0, 135.0 * (1.0 + buffs.get("capacity_bonus", 0.0) / 3000.0) - 80.0) * (0.08 * max(0.2, income_tax_rate / 0.05)) + 22.0, 1)},
        "liu_truck_driver": {"inc": round(95.0 * (p_oil / 520.0 * 0.2 + 0.8), 1), "ess": round(food_price * 2.2 + 12.0 + 8.0, 1)},
        "jiang_taxi_driver": {"inc": round(120.0 * (0.6 + 0.4 * sentiment) * macro_rev_factor, 1), "ess": round(32.0 + 22.0 * (p_oil / 520.0 * 0.7 + 0.3 * max(0.65, 1.0 - energy_discount)) + food_price * 1.1, 1)},
        "xie_electrician": {"inc": round(max(min_wage * 1.35, 50.0) + 12.0 * macro_rev_factor, 1), "ess": round(food_price * 1.05 + 16.0 + 6.0, 1)},
        "li_accountant": {"inc": li_inc_rate, "ess": round((loan_cost_10k_month * 10.0) / 30.0 + (food_price * 2.2 + 20.0) + max(0.0, li_inc_rate - 80.0) * (0.08 * max(0.2, income_tax_rate / 0.05)), 1)},
        "lin_it_engineer": {"inc": 140.0, "ess": round(food_price * 2.0 + 32.0 + max(0.0, 140.0 - 80.0) * (0.08 * max(0.2, income_tax_rate / 0.05)), 1)},
        "zhou_nurse": {"inc": round(max(min_wage * 1.5, 60.0) + (medicare_rate * 28.0), 1), "ess": round(food_price * 1.1 + 8.0 + 22.0, 1)},
        "chen_teacher": {"inc": round(max(min_wage * 1.4, 55.0) + 15.0 * (welfare_daily / 0.15) + (res_grant.get("boost", 0.0) * 8.0), 1), "ess": round(food_price * 0.85 + 7.0 + 15.0, 1)},
        "lin_expert": {"inc": dr_inc_rate, "ess": round((100.0 * 0.12 + 150.0 * 0.22 + max(0.0, dr_inc_rate - 80.0 - 250.0) * 0.32) * max(0.2, income_tax_rate / 0.05) + (food_price * 2.8 + 45.0), 1)},
        "zheng_tour_guide": {"inc": round(max(min_wage * 0.9, 32.0) + (35.0 * (sentiment ** 1.2)), 1), "ess": round(food_price * 1.15 + 9.0 * (p_oil / 520.0) + 8.0, 1)},
        "zhou_rider": {"inc": round(65.0 * (0.5 + 0.5 * sentiment), 1), "ess": round(food_price * 1.3 + 10.0 + 5.0, 1)},
        "aqiang_unemployed": {"inc": round(getattr(state, "unemployment_relief_standard", 28.0) + 15.0 * (welfare_daily / 0.15), 1), "ess": round(food_price * 0.9, 1)}
    }

    macro_cit_tour_yuan = 0.0
    macro_cit_eat_yuan = 0.0
    macro_cit_apparel_yuan = 0.0

    for cid, census in CITIZEN_CENSUS.items():
        pop = census["population"]
        p_inc = pre_data[cid]["inc"]
        p_ess = pre_data[cid]["ess"]
        p_funds = c_pool.get(cid, 5000.0)
        
        ratio = round(p_inc / max(1.0, p_ess), 2)
        cushion = round(p_funds / max(10.0, p_ess * 30.0), 1)
        propensity = calculate_discretionary_propensity(ratio, cushion, sentiment_index)
        
        b_tour = round(census["base_budget"]["tour"] * propensity, 2)
        b_eat = round(census["base_budget"]["eat"] * propensity, 2)
        b_app = round(census["base_budget"]["apparel"] * propensity, 2)
        
        macro_cit_tour_yuan += pop * b_tour
        macro_cit_eat_yuan += pop * b_eat
        macro_cit_apparel_yuan += pop * b_app
        
        cit_metrics[cid] = {
            "inc": p_inc, "ess": p_ess, "ratio": ratio, "cushion": cushion,
            "propensity": propensity, "tour": b_tour, "eat": b_eat, "apparel": b_app
        }

    # =========================================================================
    # 🔍 第二阶段：企业主个人家庭消费与全社会宏观服务/轻工总需求聚合
    # =========================================================================
    # 全国约 98,300 位企业主/个体经营者在扣除营运成本后，留存利润派发分红拉动消费
    emp_owner_propensity = max(0.40, min(1.0, 0.60 + 0.40 * (sentiment_index / 100.0)))
    macro_emp_tour_yuan = 15_000 * 75.0 * emp_owner_propensity # 重点企业主周末度假
    macro_emp_eat_yuan = 35_000 * 40.0 * emp_owner_propensity  # 商务与家庭堂食聚餐
    macro_emp_apparel_yuan = 35_000 * 30.0 * emp_owner_propensity # 品质成衣轻工采购

    # 全社会下游客流与商业零售总盘子
    macro_tourism_total_yuan = (macro_cit_tour_yuan + macro_emp_tour_yuan) * mobility_factor
    macro_catering_total_yuan = macro_cit_eat_yuan + macro_emp_eat_yuan + 20_000_000.0 # 叠加全社会每日刚性在岗午间盒饭快餐
    mci_factor = max(0.20, min(2.0, getattr(state, "manufacturing_competitiveness_index", 100.0) / 100.0))
    export_apparel_yuan = round(0.16 * 100_000_000 * (p_textile / 45.0) * macro_rev_factor * mci_factor, 1) # 外贸口岸海关结汇出口 (联动MCI制造业竞争力)
    macro_apparel_total_yuan = macro_cit_apparel_yuan + macro_emp_apparel_yuan + export_apparel_yuan

    # =========================================================================
    # 🏢 第三阶段：全产业 15 大微观雇主经营账本计算 (由全社会宏观总量严格均摊)
    # =========================================================================
    employers: Dict[str, Any] = {}

    # (1) 万亩现代家庭农场 · 钱场长 (现代农业)
    qian_count = EMPLOYER_CENSUS["qian_farm"]["entity_count"]
    qian_rev = round((1600.0 * (p_grain / 2200.0) * macro_rev_factor) + (infra_maint * 120.0), 1)
    qian_fert = round(180.0 * (p_fertilizer / 2100.0), 1)
    qian_diesel = round(110.0 * (p_oil / 520.0), 1)
    qian_wages = round(15 * 65.0, 1) # 15名农机手日薪 (小徐等)
    qian_loan_int = round(35.0 * (loan_rate / 0.065), 1)
    qian_tax = round(max(0.0, qian_rev - qian_fert - qian_diesel - qian_wages - qian_loan_int) * (corp_tax_rate * 0.5), 1)
    qian_profit = round(qian_rev - qian_fert - qian_diesel - qian_wages - qian_loan_int - qian_tax, 1)
    qian_r = round(qian_rev / max(1.0, qian_fert + qian_diesel + qian_wages + qian_loan_int + qian_tax), 2)
    qian_funds = e_pool.get("qian_farm", 180.0)
    qian_c = round((qian_funds * 10000.0) / max(10.0, (qian_fert + qian_diesel + qian_wages + qian_loan_int + qian_tax) * 30.0), 1)

    if p_fertilizer > 2300.0:
        qian_status = "warning"
        qian_s_desc = "化肥成本高企侵蚀收益"
        qian_voice = f"化肥涨到 {p_fertilizer:.0f} 元/吨，每天光买化肥就吃掉 {qian_fert:.0f} 块！全国{qian_count}个家庭农场要是粮价不托底，今年全得亏本！"
    elif qian_profit > 240.0:
        qian_status = "thriving"
        qian_s_desc = "丰产丰收 · 利润充沛"
        qian_voice = f"粮食统购顺畅，日营收达 {qian_rev:.0f} 块，每天净赚 {qian_profit:.0f} 块！准备向重机厂再添购一台大型联合收割机！"
    else:
        qian_status = "normal"
        qian_s_desc = "稳态经营 · 农忙排产"
        qian_voice = f"作为全国{qian_count}个大农场之一，日营收 {qian_rev:.0f} 块，付农机员工钱 {qian_wages:.0f} 块，化肥柴油 {qian_fert+qian_diesel:.0f} 块，净利 {qian_profit:.0f} 块。"

    employers["qian_farm"] = {
        "id": "qian_farm",
        "name": "钱场长",
        "title": "万亩现代粮油家庭农场主",
        "category": "agriculture",
        "category_name": "🌾 现代农业",
        "avatar": "🌾",
        "scale_label": f"全国 {qian_count:,} 个万亩家庭农场之一 · 承包万亩农田·雇佣15名农机手",
        "representative_count": qian_count,
        "income_expense_ratio": qian_r,
        "savings_cushion_months": qian_c,
        "discretionary_propensity": emp_owner_propensity,
        "daily_revenue": qian_rev,
        "daily_expense": round(qian_fert + qian_diesel + qian_wages + qian_loan_int + qian_tax, 1),
        "daily_net": qian_profit,
        "accumulated_funds": qian_funds,
        "financial_status": qian_status,
        "status_desc": qian_s_desc,
        "breakdown": {"农机手工资": qian_wages, "高压化肥": qian_fert, "农用柴油": qian_diesel, "农贷利息": qian_loan_int, "农业税金": qian_tax},
        "voice": qian_voice,
        "voucher_title": "万亩家庭农场·每日农业产销核算流水单",
        "voucher_number": f"AGRI-{state.day:04d}-082",
        "receipt_lines": [
            {"subject": "原粮统购交割款进项", "from_acc": "国家粮油收储与精炼专户", "to_acc": "现代家庭农场营运户", "amount_yuan": qian_rev, "direction": "income", "note": "交付1.8吨标准杂交水稻与专用小麦原粮"},
            {"subject": "优质化肥采购支取", "from_acc": "现代家庭农场营运户", "to_acc": "合成化肥石化集团 (专户)", "amount_yuan": qian_fert, "direction": "expense", "note": f"按现货价 {p_fertilizer:.0f} 元/吨采购基肥"},
            {"subject": "大型农机柴油加油", "from_acc": "现代家庭农场营运户", "to_acc": "国家油气田与石化销售公司", "amount_yuan": qian_diesel, "direction": "expense", "note": "大型拖拉机与联合收割机保供柴油"},
            {"subject": "农机手小徐等人日薪直发", "from_acc": "现代家庭农场营运户", "to_acc": "农机手小徐等人银行卡", "amount_yuan": qian_wages, "direction": "expense", "note": "15名在册农机手与灌溉工日薪结算"},
            {"subject": "农田水利信贷按日还息", "from_acc": "现代家庭农场营运户", "to_acc": "商业银行信贷营运专户", "amount_yuan": qian_loan_int, "direction": "expense", "note": "高标准农田土地平整中长期低息贷款付息"}
        ]
    }

    # (2) 现代化中型煤井承包商 · 孙总 (能源矿产)
    sun_count_base = EMPLOYER_CENSUS["sun_coal"]["entity_count"]
    sun_active = active_entities.get("sun_coal", sun_count_base)
    if f_coal and f_coal.status in ["downsizing", "suspended", "bankrupt"]:
        if sun_active > int(sun_count_base * 0.60):
            bankrupt_today = min(2, sun_active - int(sun_count_base * 0.60))
            sun_active -= bankrupt_today
            active_entities["sun_coal"] = sun_active
            bankrupt_counts["sun_coal"] = bankrupt_counts.get("sun_coal", 0) + bankrupt_today
    elif f_coal and f_coal.status == "operating" and f_coal.daily_profit > 0.08:
        if sun_active < sun_count_base:
            sun_active = min(sun_count_base, sun_active + 1)
            active_entities["sun_coal"] = sun_active
    sun_count = max(100, sun_active)

    sun_util = getattr(f_coal, "utilization_rate", 85.0) if f_coal else 85.0
    sun_rev = round(6800.0 * (p_coal / 480.0) * (0.4 + 0.6 * (sun_util / 85.0)) * macro_rev_factor, 1)
    sun_miner_wage = max(min_wage * 1.10, 38.0)
    sun_wages = round(120 * sun_miner_wage * (0.5 + 0.5 * (sun_util / 85.0)), 1) # 120名综采工日薪 (老张等)
    sun_power = round(240.0 * max(0.5, 1.0 - energy_discount), 1)
    sun_safety = round(180.0, 1)
    sun_loan_int = round(120.0 * (loan_rate / 0.065), 1)
    sun_tax = round(max(0.0, sun_rev - sun_wages - sun_power - sun_safety - sun_loan_int) * corp_tax_rate, 1)
    sun_profit = round(sun_rev - sun_wages - sun_power - sun_safety - sun_loan_int - sun_tax, 1)
    sun_r = round(sun_rev / max(1.0, sun_wages + sun_power + sun_safety + sun_loan_int + sun_tax), 2)
    sun_funds = e_pool.get("sun_coal", 450.0)
    sun_c = round((sun_funds * 10000.0) / max(10.0, (sun_wages + sun_power + sun_safety + sun_loan_int + sun_tax) * 30.0), 1)

    bankrupt_total_sun = bankrupt_counts.get("sun_coal", 0)
    dutch_active = getattr(state, "dutch_disease_active", False)
    if dutch_active:
        sun_status = "thriving"
        sun_s_desc = "大宗出口井喷 · 享资源繁荣溢价"
        sun_voice = f"国际能源大宗出口全面爆发，海关结汇外汇滚滚而来！虽然听说汇率升值把沿海轻工搞得很惨，但我们能源矿企现在可是实打实的暴利黄金期！"
    elif bankrupt_total_sun > 0 and f_coal and f_coal.status in ["downsizing", "suspended", "bankrupt"]:
        sun_status = "warning" if sun_profit >= 0 else "crisis"
        sun_s_desc = f"煤矿产能淘汰出清 · 倒闭 {bankrupt_total_sun} 矿"
        sun_voice = f"行业限产整顿，全国已有 {bankrupt_total_sun} 座老旧煤井关停出清！我们矿抓紧安全排查，在册煤井仅剩 {sun_count} 座！"
    elif sun_power > 260.0:
        sun_status = "warning"
        sun_s_desc = "矿井重载电费负担沉重"
        sun_voice = f"矿井大功率抽水与强通风耗电极大，每天电费支出 {sun_power:.0f} 块！紧盯国家特高压电网并网，早日把动力电费降下来！"
    elif sun_profit > 450.0:
        sun_status = "thriving"
        sun_s_desc = "电煤畅销 · 开工饱满"
        sun_voice = f"主力电厂和钢厂采购电煤订单拉满，日营业额冲到 {sun_rev:.0f} 块，每天净赚 {sun_profit:.0f} 块！全国{sun_count}座煤矿都在加班加点！"
    else:
        sun_status = "normal"
        sun_s_desc = "常态化连续综采"
        sun_voice = f"日出煤营收 {sun_rev:.0f} 块，给采煤工老张他们发工资 {sun_wages:.0f} 块，动力电费 {sun_power:.0f} 块，付机电设备利息 {sun_loan_int:.0f} 块，净利润 {sun_profit:.0f} 块。"

    employers["sun_coal"] = {
        "id": "sun_coal",
        "name": "孙总",
        "title": "综合煤炭开采承包公司老总",
        "category": "mining",
        "category_name": "⛏️ 能源采掘",
        "avatar": "⛏️",
        "scale_label": f"全国 {sun_count:,} 座现代化综采煤井之一 · 雇佣120名综采机电矿工",
        "representative_count": sun_count,
        "income_expense_ratio": sun_r,
        "savings_cushion_months": sun_c,
        "discretionary_propensity": emp_owner_propensity,
        "daily_revenue": sun_rev,
        "daily_expense": round(sun_wages + sun_power + sun_safety + sun_loan_int + sun_tax, 1),
        "daily_net": sun_profit,
        "accumulated_funds": sun_funds,
        "financial_status": sun_status,
        "status_desc": sun_s_desc,
        "breakdown": {"矿工薪酬": sun_wages, "提升动力电费": sun_power, "井下防爆劳保": sun_safety, "采掘重贷利息": sun_loan_int, "企业所得税": sun_tax},
        "voice": sun_voice,
        "voucher_title": "现代化煤矿开采承包综合日结算单",
        "voucher_number": f"COAL-{state.day:04d}-119",
        "receipt_lines": [
            {"subject": "电厂长协电煤结算款进项", "from_acc": "国家骨干电网公司 (专户)", "to_acc": "现代化煤矿集团 (专户)", "amount_yuan": sun_rev, "direction": "income", "note": "供应骨干火电厂高热值原煤"},
            {"subject": "综采普工与机电掘进日薪直发", "from_acc": "现代化煤矿集团 (专户)", "to_acc": "采煤工老张等矿工个人储蓄户", "amount_yuan": sun_wages, "direction": "expense", "note": "120名在册井下综采司机、掘进机手日薪"},
            {"subject": "矿井大功率强排水风机工业电费", "from_acc": "现代化煤矿集团 (专户)", "to_acc": "国家骨干电网公司 (专户)", "amount_yuan": sun_power, "direction": "expense", "note": "井下强力通风与抽水泵动力电费"},
            {"subject": "瓦斯监测传感器与液压耗材采购", "from_acc": "现代化煤矿集团 (专户)", "to_acc": "国家实体企业综合清算总专户", "amount_yuan": sun_safety, "direction": "expense", "note": "安全防护网、防爆传感器耗材"},
            {"subject": "综采成套设备融资租赁还息", "from_acc": "现代化煤矿集团 (专户)", "to_acc": "商业银行信贷营运专户", "amount_yuan": sun_loan_int, "direction": "expense", "note": "抵押综采机组银行贷款利息偿付"}
        ]
    }

    # (3) 精密机械五金制造厂 · 陈厂长 (实体制造)
    chen_count_base = EMPLOYER_CENSUS["chen_machinery"]["entity_count"]
    chen_active = active_entities.get("chen_machinery", chen_count_base)
    if f_hardware and f_hardware.status in ["downsizing", "suspended", "bankrupt"]:
        if chen_active > int(chen_count_base * 0.60):
            bankrupt_today = min(4, chen_active - int(chen_count_base * 0.60))
            chen_active -= bankrupt_today
            active_entities["chen_machinery"] = chen_active
            bankrupt_counts["chen_machinery"] = bankrupt_counts.get("chen_machinery", 0) + bankrupt_today
    elif f_hardware and f_hardware.status == "operating" and f_hardware.daily_profit > 0.08:
        if chen_active < chen_count_base:
            chen_active = min(chen_count_base, chen_active + 2)
            active_entities["chen_machinery"] = chen_active
    chen_count = max(800, chen_active)

    chen_base_rev = 1450.0 * macro_rev_factor * (1.0 + buffs.get("capacity_bonus", 0.0) / 2500.0)
    infra_orders = (infra_daily / 0.15) * 85.0 + (infra_maint / 0.10) * 45.0
    chen_rev = round(chen_base_rev + infra_orders, 1)
    chen_wages = 720.0 # 24名技工日薪 (含孙师傅)
    chen_steel = round(190.0 * (p_steel / 3200.0), 1)
    chen_energy = round(160.0 * max(0.50, 1.0 - energy_discount), 1)
    chen_loan_int = round(100.0 * (loan_rate / 0.065), 1)
    chen_tax = round(max(0.0, chen_rev - chen_wages - chen_steel - chen_energy - chen_loan_int) * corp_tax_rate, 1)
    chen_profit = round((chen_rev - chen_wages - chen_steel - chen_energy - chen_loan_int - chen_tax) * profit_mult, 1)
    chen_r = round(chen_rev / max(1.0, chen_wages + chen_steel + chen_energy + chen_loan_int + chen_tax), 2)
    chen_funds = e_pool.get("chen_machinery", 320.0)
    chen_c = round((chen_funds * 10000.0) / max(10.0, (chen_wages + chen_steel + chen_energy + chen_loan_int + chen_tax) * 30.0), 1)

    bankrupt_total_chen = bankrupt_counts.get("chen_machinery", 0)
    if bankrupt_total_chen > 0 and f_hardware and f_hardware.status in ["downsizing", "suspended", "bankrupt"]:
        chen_status = "warning" if chen_profit >= 0 else "crisis"
        chen_s_desc = f"机械配套洗牌 · 淘汰倒闭 {bankrupt_total_chen} 家"
        chen_voice = f"五金下游订单偏冷，全国已有 {bankrupt_total_chen} 家机加厂关门拍卖设备！好在活下来的 {chen_count} 家加工厂接到了技改配件翻新订单！"
    elif energy_discount > 0.05:
        chen_status = "thriving"
        chen_s_desc = "特高压电网并网 · 动力成本大降"
        chen_voice = f"特高压大电网建好后，工厂动力电费每天省下 {160.0 - chen_energy:.0f} 块！工人们三班倒赶工，每天净利润突破 {chen_profit:.0f} 块！"
    elif getattr(state, "daily_durable_spending", 0.0) > 0.15:
        chen_status = "thriving"
        chen_s_desc = "汽车家电耐用品配件热销"
        chen_voice = f"民间耐用品消费火爆！车间接满了汽车冲压件与家电模具配件订单，全国{chen_count}家加工厂三班倒，日营收冲到 {chen_rev:.0f} 块，净利润 {chen_profit:.0f} 块！"
    elif infra_daily > 0.05:
        chen_status = "thriving"
        chen_s_desc = "重大工程配套五金热销"
        chen_voice = f"接到重大工程配套五金配件订单，车间机器轰鸣，全国{chen_count}家加工厂开足马力，日营收冲到 {chen_rev:.0f} 块！"
    elif loan_rate > 0.08:
        chen_status = "warning"
        chen_s_desc = "信贷成本高企压制微利"
        chen_voice = f"商业贷款利率高达 {loan_rate*100:.1f}%！每天光给银行利息就吃掉 {chen_loan_int:.0f} 块，开厂微薄利润被严重压榨..."
    else:
        chen_status = "normal"
        chen_s_desc = "平稳有序组织排产"
        chen_voice = f"日营业额 {chen_rev:.0f} 块，付技工师傅工资 {chen_wages:.0f} 块，购合金钢 {chen_steel:.0f} 块，动力电费 {chen_energy:.0f} 块，净利润 {chen_profit:.0f} 块。"

    employers["chen_machinery"] = {
        "id": "chen_machinery",
        "name": "陈厂长",
        "title": "精密机械五金加工厂总经理",
        "category": "manufacturing",
        "category_name": "⚙️ 高端装备",
        "avatar": "🏭",
        "scale_label": f"全国 {chen_count:,} 家精密五金制造工场之一 · 雇佣24名车铣模具技工",
        "representative_count": chen_count,
        "income_expense_ratio": chen_r,
        "savings_cushion_months": chen_c,
        "discretionary_propensity": emp_owner_propensity,
        "daily_revenue": chen_rev,
        "daily_expense": round(chen_wages + chen_steel + chen_energy + chen_loan_int + chen_tax, 1),
        "daily_net": chen_profit,
        "accumulated_funds": chen_funds,
        "financial_status": chen_status,
        "status_desc": chen_s_desc,
        "breakdown": {"技工薪酬": chen_wages, "特种合金钢": chen_steel, "车间动力电费": chen_energy, "机床经营贷利息": chen_loan_int, "企业所得税": chen_tax},
        "voice": chen_voice,
        "voucher_title": "陈厂长精密机械五金制造车间日清结算单",
        "voucher_number": f"MACH-{state.day:04d}-024",
        "receipt_lines": [
            {
                "subject": "耐用消费品核心五金与机械配件交割货款" if getattr(state, "daily_durable_spending", 0.0) > 0.15 else "机械装备与重大工程配件货款进项",
                "from_acc": "重型机械装备制造厂与民用耐用消费品结算专户",
                "to_acc": "陈厂长五金机械集群 (专户)",
                "amount_yuan": chen_rev,
                "direction": "income",
                "note": "交付500套汽车冲压件、家电精密模具与工程紧固件" if getattr(state, "daily_durable_spending", 0.0) > 0.15 else "交付500套数控加工紧固件"
            },
            {"subject": "数控车铣工人工资直发", "from_acc": "陈厂长五金机械集群 (专户)", "to_acc": "数控技工孙师傅等在册员工账户", "amount_yuan": chen_wages, "direction": "expense", "note": "车间24名技工模具师傅全职日薪"},
            {"subject": "优质合金冷拔型钢采购款", "from_acc": "陈厂长五金机械集群 (专户)", "to_acc": "特大型钢铁联合体 (专户)", "amount_yuan": chen_steel, "direction": "expense", "note": f"按指导价 {p_steel:.0f} 元/吨采购标准机械合金型钢"},
            {"subject": "数控机床动力电费划拨", "from_acc": "陈厂长五金机械集群 (专户)", "to_acc": "国家骨干电网公司 (专户)", "amount_yuan": chen_energy, "direction": "expense", "note": "加工中心与大型冲压设备动力电费"},
            {"subject": "高精密母机抵押贷款利息", "from_acc": "陈厂长五金机械集群 (专户)", "to_acc": "商业银行信贷营运专户", "amount_yuan": chen_loan_int, "direction": "expense", "note": "数控母机银行贷款利息偿付"}
        ]
    }

    # (4) 沿海出口服装制衣厂 · 朱老板 (外贸轻工 - 严格基于全社会成衣总需求均摊)
    zhu_base_count = EMPLOYER_CENSUS["zhu_textile"]["entity_count"] # 1800
    zhu_active = active_entities.get("zhu_textile", zhu_base_count)
    if f_textile and f_textile.status in ["downsizing", "suspended", "bankrupt"]:
        if zhu_active > int(zhu_base_count * 0.50):
            bankrupt_today = min(3, zhu_active - int(zhu_base_count * 0.50))
            zhu_active -= bankrupt_today
            active_entities["zhu_textile"] = zhu_active
            bankrupt_counts["zhu_textile"] = bankrupt_counts.get("zhu_textile", 0) + bankrupt_today
    elif f_textile and f_textile.status == "operating" and f_textile.daily_profit > 0.08:
        if zhu_active < zhu_base_count:
            zhu_active = min(zhu_base_count, zhu_active + 2)
            active_entities["zhu_textile"] = zhu_active
    zhu_count = max(500, zhu_active)

    # 单厂营收 = 全社会成衣总需求(内销+外贸出口) / 在册制衣厂数
    zhu_rev = round(macro_apparel_total_yuan / zhu_count, 1)
    zhu_wages = round(180 * zhu_wage_per_worker, 1) # 180名流水线女工日薪 (联动小刘)
    zhu_fabric = round(450.0 * (p_textile / 45.0), 1)
    zhu_social = round(zhu_wages * (social_contrib_rate * 0.6), 1)
    zhu_power_rent = round(160.0 * max(0.6, 1.0 - energy_discount) + 80.0, 1)

    # 银行信用评级与信贷息差联动 (Phase 3)
    textile_rating = getattr(f_textile, "credit_rating", "BBB") if f_textile else "BBB"
    textile_rate = getattr(f_textile, "borrowing_rate", loan_rate) if f_textile else loan_rate
    textile_debt_p = getattr(f_textile, "debt_principal", 80.0) if f_textile else 80.0
    recalled_textile = getattr(f_textile, "recalled_loans_today", 0.0) if f_textile else 0.0
    zhu_loan_int = round((textile_debt_p * textile_rate * 1e8 / 360.0) / zhu_count, 1)
    zhu_recalled_yuan = round((recalled_textile * 1e8) / zhu_count, 1)

    zhu_tax = round(max(0.0, zhu_rev - zhu_wages - zhu_fabric - zhu_social - zhu_power_rent - zhu_loan_int) * corp_tax_rate, 1)
    zhu_profit = round(zhu_rev - zhu_wages - zhu_fabric - zhu_social - zhu_power_rent - zhu_loan_int - zhu_tax, 1)
    zhu_r = round(zhu_rev / max(1.0, zhu_wages + zhu_fabric + zhu_social + zhu_power_rent + zhu_loan_int + zhu_tax), 2)
    zhu_funds = e_pool.get("zhu_textile", 260.0)
    zhu_c = round((zhu_funds * 10000.0) / max(10.0, (zhu_wages + zhu_fabric + zhu_social + zhu_power_rent + zhu_loan_int + zhu_tax) * 30.0), 1)

    bankrupt_total_zhu = bankrupt_counts.get("zhu_textile", 0)
    dutch_active_zhu = getattr(state, "dutch_disease_active", False)
    mci_val_zhu = getattr(state, "manufacturing_competitiveness_index", 100.0)
    fx_rate_val = getattr(state, "exchange_rate", 7.20)

    if zhu_recalled_yuan > 0:
        zhu_status = "crisis"
        zhu_s_desc = f"银行强制抽贷 · 扣划 {zhu_recalled_yuan:.0f} 元"
        zhu_voice = f"轻纺评级降至 {textile_rating} 级！高行长直接启动风控强制抽贷，单厂被强行扣收 {zhu_recalled_yuan:.0f} 块周转金去平账，全国{zhu_count}家制衣厂账面现金快见底了！"
    elif dutch_active_zhu or mci_val_zhu < 75.0:
        zhu_status = "crisis" if zhu_profit < 0 else "warning"
        zhu_s_desc = f"遭遇荷兰病冲击 · 汇率升至 {fx_rate_val:.2f} 削弱外贸"
        zhu_voice = f"本币汇率飙升至 {fx_rate_val:.2f}！MCI竞争力指数跌至 {mci_val_zhu:.1f}，海外客商嫌我们报价太贵大批退单！大宗资源出口过热正引发严重的荷兰病反噬！"
    elif textile_rating in ["CCC", "D"]:
        zhu_status = "crisis"
        zhu_s_desc = f"信用评级跌入 {textile_rating} 级 · 授信冻结"
        zhu_voice = f"由于连续亏损和资负比攀升，商业银行把我们评级打到 {textile_rating} 级！新增流动资金借款全部被叫停，适用利率高达 {textile_rate*100:.1f}%，只能紧缩度日！"
    elif bankrupt_total_zhu > 0 and f_textile and f_textile.status in ["downsizing", "suspended"]:
        zhu_status = "warning" if zhu_profit >= 0 else "crisis"
        zhu_s_desc = f"行业残酷洗牌 · 累计倒闭 {bankrupt_total_zhu} 家"
        zhu_voice = f"衣服严重供大于求，全国已有 {bankrupt_total_zhu} 家制衣厂资金断裂倒闭清盘！好在落后产能出清后，活下来的 {zhu_count} 家工厂订单稍有回暖！"
    elif f_textile and f_textile.status == "bankrupt":
        zhu_status = "crisis"
        zhu_s_desc = "严重资不抵债 · 司法破产重组"
        zhu_voice = f"轻纺大厂严重资不抵债进入司法破产重组，裁员出清落后产能，全行业正在经历残酷的阵痛出清！"
    elif social_contrib_rate > 0.16:
        zhu_status = "warning"
        zhu_s_desc = "雇主社保统筹费率偏重"
        zhu_voice = f"社保统筹费率调到 {social_contrib_rate*100:.0f}%，每天替180个女工交社保就要 {zhu_social:.0f} 块！外贸订单本来就薄利，全国{zhu_count}家制衣厂都在咬牙硬抗！"
    elif zhu_profit > 500.0:
        zhu_status = "thriving"
        zhu_s_desc = "内销与海关出口畅旺 · 订单排满"
        zhu_voice = f"全国内销成衣消费大爆发，海外退税极快！全国服装日流水达 {macro_apparel_total_yuan/1e8:.2f} 亿，分摊到本厂日营收 {zhu_rev:.0f} 块，每天净赚 {zhu_profit:.0f} 块！"
    else:
        zhu_status = "normal"
        zhu_s_desc = "两班倒稳定出货"
        zhu_voice = f"全国{zhu_count}家服装厂之一。日成衣营收 {zhu_rev:.0f} 块，发女工小刘等人日薪 {zhu_wages:.0f} 块，购面料 {zhu_fabric:.0f} 块，银行周转利息 {zhu_loan_int:.0f} 块 (评级 {textile_rating})，净利 {zhu_profit:.0f} 块。"

    zhu_receipt_lines = [
        {"subject": "全国成衣内销订购与出口结汇进项", "from_acc": "国内消费零售户与外贸口岸专户", "to_acc": "轻纺织造日用轻工厂 (专户)", "amount_yuan": zhu_rev, "direction": "income", "note": f"全国日总额 {macro_apparel_total_yuan/1e8:.3f} 亿元按 {zhu_count} 家工厂均摊"},
        {"subject": "缝纫女工小刘等人日薪直发", "from_acc": "轻纺织造日用轻工厂 (专户)", "to_acc": "缝纫女工小刘等银行卡", "amount_yuan": zhu_wages, "direction": "expense", "note": "180名在册平缝车位工两班倒日薪"},
        {"subject": "合成聚酯纤维与棉纱针织面料采购", "from_acc": "轻纺织造日用轻工厂 (专户)", "to_acc": "合成化肥石化集团 (专户)", "amount_yuan": zhu_fabric, "direction": "expense", "note": "采购高支棉纱与石化制衣面料"},
        {"subject": "商业银行流动周转信贷利息结算", "from_acc": "轻纺织造日用轻工厂 (专户)", "to_acc": "商业银行信贷营运专户", "amount_yuan": zhu_loan_int, "direction": "expense", "note": f"按现行企业风险评级 {textile_rating} 级浮动利率 {textile_rate*100:.2f}% 执行付息"},
        {"subject": "企业统筹职工养老失业社保金", "from_acc": "轻纺织造日用轻工厂 (专户)", "to_acc": "国家社会保障与医保统筹专户", "amount_yuan": zhu_social, "direction": "expense", "note": f"按法定费率 {social_contrib_rate*100:.0f}% 缴纳雇主承担部分"},
        {"subject": "喷气织机与电脑平缝机动力电费租金", "from_acc": "轻纺织造日用轻工厂 (专户)", "to_acc": "国家骨干电网公司 (专户)", "amount_yuan": zhu_power_rent, "direction": "expense", "note": "工业缝纫电机动力电费与厂房摊销"}
    ]
    if zhu_recalled_yuan > 0:
        zhu_receipt_lines.append({
            "subject": "商业银行高风险主动风控抽贷还本",
            "from_acc": "轻纺织造日用轻工厂 (专户)",
            "to_acc": "商业银行信贷营运专户",
            "amount_yuan": zhu_recalled_yuan,
            "direction": "expense",
            "note": f"评级打入高危预警档，银行风控系统强制划扣企业流动资金用于压降信贷敞口"
        })

    employers["zhu_textile"] = {
        "id": "zhu_textile",
        "name": "朱老板",
        "title": "外贸制衣轻工联合代工厂厂长",
        "category": "manufacturing",
        "category_name": "🧵 外贸轻工",
        "avatar": "🧵",
        "scale_label": f"全国 {zhu_count:,} 家出口制衣轻工厂之一 · 雇佣180名缝纫轻工女工 (信用评级 {textile_rating})",
        "representative_count": zhu_count,
        "income_expense_ratio": zhu_r,
        "savings_cushion_months": zhu_c,
        "discretionary_propensity": emp_owner_propensity,
        "daily_revenue": zhu_rev,
        "daily_expense": round(zhu_wages + zhu_fabric + zhu_social + zhu_power_rent + zhu_loan_int + zhu_tax, 1),
        "daily_net": zhu_profit,
        "accumulated_funds": zhu_funds,
        "financial_status": zhu_status,
        "status_desc": zhu_s_desc,
        "breakdown": {"缝纫女工工资": zhu_wages, "面料辅料采购": zhu_fabric, "周转贷款利息": zhu_loan_int, "雇主统筹社保": zhu_social, "动力电费与租金": zhu_power_rent, "企业所得税": zhu_tax},
        "voice": zhu_voice,
        "voucher_title": "外贸服装出口与内销代工每日产销台账",
        "voucher_number": f"TEXT-{state.day:04d}-451",
        "receipt_lines": zhu_receipt_lines
    }

    # (5) 基建工程项目包工头 · 吴总 (建筑市政)
    wu_count = EMPLOYER_CENSUS["wu_construction"]["entity_count"]
    wu_workers = round(20 + min(60, (infra_daily / 0.15) * 60))
    wu_rev = round(max(1150.0, (infra_daily / 0.15) * 3400.0 + 1150.0), 1)
    wu_wages = round(wu_workers * zhao_inc_rate, 1)
    wu_cement = round((60.0 + (infra_daily / 0.15) * 100.0) * (p_cement / 350.0), 1)
    wu_steel = round((60.0 + (infra_daily / 0.15) * 120.0) * (p_steel / 3200.0), 1)
    wu_machines = round((45.0 + (infra_daily / 0.15) * 50.0) * (loan_rate / 0.065), 1)
    wu_tax = round(max(0.0, wu_rev - wu_wages - wu_cement - wu_steel - wu_machines) * 0.12, 1)
    wu_profit = round(wu_rev - wu_wages - wu_cement - wu_steel - wu_machines - wu_tax, 1)
    wu_r = round(wu_rev / max(1.0, wu_wages + wu_cement + wu_steel + wu_machines + wu_tax), 2)
    wu_funds = e_pool.get("wu_construction", 280.0)
    wu_c = round((wu_funds * 10000.0) / max(10.0, (wu_wages + wu_cement + wu_steel + wu_machines + wu_tax) * 30.0), 1)

    if infra_daily > 0.08:
        wu_status = "thriving"
        wu_s_desc = "国家重大工程全线开工"
        wu_voice = f"财政部直拨工程款非常充裕！项目部拉满80人抢工期，全国{wu_count}个标段同时大干，日入账 {wu_rev:.0f} 块，每天净赚 {wu_profit:.0f} 块！"
    elif infra_daily < 0.01:
        wu_status = "normal"
        wu_s_desc = "市政标段正常施工"
        wu_voice = f"承接零星市政路面维保，带 {wu_workers} 名在册散工，日进账 {wu_rev:.0f} 块，发工钱 {wu_wages:.0f} 块，净结余 {wu_profit:.0f} 块。"
    else:
        wu_status = "normal"
        wu_s_desc = "市政标段正常施工"
        wu_voice = f"工程款每日拨付 {wu_rev:.0f} 块，给钢筋工老赵发工钱 {wu_wages:.0f} 块，购水泥型钢 {wu_cement+wu_steel:.0f} 块，结余 {wu_profit:.0f} 块。"

    employers["wu_construction"] = {
        "id": "wu_construction",
        "name": "吴总",
        "title": "市政路桥与水利建工项目承包商",
        "category": "service",
        "category_name": "🏗️ 建筑市政",
        "avatar": "🏗️",
        "scale_label": f"全国 {wu_count:,} 个基建承包标段之一 · 带队{wu_workers}名基建钢筋泥瓦工",
        "representative_count": wu_count,
        "income_expense_ratio": wu_r,
        "savings_cushion_months": wu_c,
        "discretionary_propensity": emp_owner_propensity,
        "daily_revenue": wu_rev,
        "daily_expense": round(wu_wages + wu_cement + wu_steel + wu_machines + wu_tax, 1),
        "daily_net": wu_profit,
        "accumulated_funds": wu_funds,
        "financial_status": wu_status,
        "status_desc": wu_s_desc,
        "breakdown": {"建筑工人日薪": wu_wages, "高标号水泥": wu_cement, "结构螺纹钢": wu_steel, "大型挖掘机租赁": wu_machines, "工程建安税": wu_tax},
        "voice": wu_voice,
        "voucher_title": "建工集团市政工程标段每日工程决算单",
        "voucher_number": f"CONS-{state.day:04d}-703",
        "receipt_lines": [
            {"subject": "重大工程与市政项目进度款拨付", "from_acc": "中央政府国库单一账户 (TSA)", "to_acc": "建工集团项目结算专户", "amount_yuan": wu_rev, "direction": "income", "note": "特高压变电站地基与桥梁标段施工节点拨款"},
            {"subject": "散工老赵等人钢筋泥瓦工钱日结", "from_acc": "建工集团项目结算专户", "to_acc": "建筑工老赵等在册工人银行卡", "amount_yuan": wu_wages, "direction": "expense", "note": f"{wu_workers}名在册混凝土浇筑工、钢筋手日结报酬"},
            {"subject": "干法高标号水泥采购划拨", "from_acc": "建工集团项目结算专户", "to_acc": "新型干法水泥建材厂 (专户)", "amount_yuan": wu_cement, "direction": "expense", "note": f"按现货指导价 {p_cement:.0f} 元/吨采购水泥"},
            {"subject": "特种高强螺纹型钢采购款", "from_acc": "建工集团项目结算专户", "to_acc": "特大型钢铁联合体 (专户)", "amount_yuan": wu_steel, "direction": "expense", "note": "结构抗震螺纹钢筋"},
            {"subject": "大型挖掘机吊车租赁台班费", "from_acc": "建工集团项目结算专户", "to_acc": "重型机械装备制造厂 (专户)", "amount_yuan": wu_machines, "direction": "expense", "note": "大型旋挖钻机与履带吊每日台班租赁费"}
        ]
    }

    # (6) 跨省干线大宗货运车队 · 魏老板 (交通物流)
    wei_count = EMPLOYER_CENSUS["wei_logistics"]["entity_count"]
    wei_rev = round(4600.0 * (p_oil / 520.0 * 0.3 + 0.7) * macro_rev_factor, 1)
    wei_wages = round(30 * 95.0, 1) # 30名干线货车司机日薪 (大刘等)
    wei_diesel = round(680.0 * (p_oil / 520.0), 1)
    wei_toll = round(210.0, 1)
    wei_truck_int = round(140.0 * (loan_rate / 0.065), 1)
    wei_tax = round(max(0.0, wei_rev - wei_wages - wei_diesel - wei_toll - wei_truck_int) * 0.08, 1)
    wei_profit = round(wei_rev - wei_wages - wei_diesel - wei_toll - wei_truck_int - wei_tax, 1)
    wei_r = round(wei_rev / max(1.0, wei_wages + wei_diesel + wei_toll + wei_truck_int + wei_tax), 2)
    wei_funds = e_pool.get("wei_logistics", 350.0)
    wei_c = round((wei_funds * 10000.0) / max(10.0, (wei_wages + wei_diesel + wei_toll + wei_truck_int + wei_tax) * 30.0), 1)

    if p_oil > 620.0:
        wei_status = "warning"
        wei_s_desc = "柴油暴涨 · 运费被严重侵蚀"
        wei_voice = f"原油涨到 {p_oil:.0f} 元/桶，加油站柴油水涨船高！25辆重卡每天加油扣走 {wei_diesel:.0f} 块，给大刘他们结完运费，车队几乎是在给油站打工！"
    elif wei_profit > 350.0:
        wei_status = "thriving"
        wei_s_desc = "大宗调拨繁荣 · 车队满载"
        wei_voice = f"全国工矿大宗煤炭和钢材调拨极其频繁，全国{wei_count}个车队一趟都不放空！日运费入账 {wei_rev:.0f} 块，每天净利 {wei_profit:.0f} 块！"
    else:
        wei_status = "normal"
        wei_s_desc = "跨省干线常态化运输"
        wei_voice = f"全国{wei_count}个车队之一。日运费营收 {wei_rev:.0f} 块，给大刘等司机发提成 {wei_wages:.0f} 块，柴油加油 {wei_diesel:.0f} 块，还车贷利息 {wei_truck_int:.0f} 块，净利 {wei_profit:.0f} 块。"

    employers["wei_logistics"] = {
        "id": "wei_logistics",
        "name": "魏老板",
        "title": "跨省大宗干线物流车队总经理",
        "category": "logistics",
        "category_name": "🚚 现代物流",
        "avatar": "🚚",
        "scale_label": f"全国 {wei_count:,} 个跨省干线货运车队之一 · 拥有25台重卡·30名长途司机",
        "representative_count": wei_count,
        "income_expense_ratio": wei_r,
        "savings_cushion_months": wei_c,
        "discretionary_propensity": emp_owner_propensity,
        "daily_revenue": wei_rev,
        "daily_expense": round(wei_wages + wei_diesel + wei_toll + wei_truck_int + wei_tax, 1),
        "daily_net": wei_profit,
        "accumulated_funds": wei_funds,
        "financial_status": wei_status,
        "status_desc": wei_s_desc,
        "breakdown": {"货运司机提成": wei_wages, "车用柴油加油": wei_diesel, "高速路桥通行": wei_toll, "重卡车贷利息": wei_truck_int, "物流运输增值税": wei_tax},
        "voice": wei_voice,
        "voucher_title": "干线物流车队每日运单与油料财务结算单",
        "voucher_number": f"LOGI-{state.day:04d}-338",
        "receipt_lines": [
            {"subject": "工矿大宗原料运费统筹结算进项", "from_acc": "特大型钢铁联合体 (专户)", "to_acc": "干线货运车队结算专户", "amount_yuan": wei_rev, "direction": "income", "note": "承运铁矿石与精焦煤跨省干线重载公路转运"},
            {"subject": "长途卡车司机大刘等人运单提成", "from_acc": "干线货运车队结算专户", "to_acc": "卡车司机大刘等司机银行卡", "amount_yuan": wei_wages, "direction": "expense", "note": "30名长途重卡驾驶员、押运员安全里程提成"},
            {"subject": "重载柴油批量加注集中划款", "from_acc": "干线货运车队结算专户", "to_acc": "国家油气田开采公司 (专户)", "amount_yuan": wei_diesel, "direction": "expense", "note": "车用重柴油批发加油款"},
            {"subject": "高等级公路收费站通行费", "from_acc": "干线货运车队结算专户", "to_acc": "中央政府国库单一账户 (TSA)", "amount_yuan": wei_toll, "direction": "expense", "note": "跨省高速ETC电子清算缴费"},
            {"subject": "商用重卡分期车贷利息还款", "from_acc": "干线货运车队结算专户", "to_acc": "商业银行信贷营运专户", "amount_yuan": wei_truck_int, "direction": "expense", "note": "25台重型牵引车按揭付息"}
        ]
    }

    # (7) 社区平价连锁超市 · 王掌柜 (商贸零售)
    wang_count = EMPLOYER_CENSUS["wang_retail"]["entity_count"]
    wang_rev = round(1750.0 * (food_price / 15.0) * (0.6 + 0.4 * sentiment) * macro_rev_factor, 1)
    wang_wholesale = round(wang_rev * 0.60, 1)
    wang_wage_per_worker = max(min_wage, 38.0)
    wang_wages = round(8 * wang_wage_per_worker, 1) # 8名收银理货员 (小杨等)
    wang_rent_power = round(130.0, 1)
    wang_vat = round(wang_rev * vat_tax_rate, 1)
    wang_profit = round(wang_rev - wang_wholesale - wang_wages - wang_rent_power - wang_vat, 1)
    wang_r = round(wang_rev / max(1.0, wang_wholesale + wang_wages + wang_rent_power + wang_vat), 2)
    wang_funds = e_pool.get("wang_retail", 120.0)
    wang_c = round((wang_funds * 10000.0) / max(10.0, (wang_wholesale + wang_wages + wang_rent_power + wang_vat) * 30.0), 1)

    if sentiment_index < 25.0:
        wang_status = "warning"
        wang_s_desc = "居民消费信心低迷 · 门庭冷落"
        wang_voice = f"全社会消费信心只有 {sentiment_index:.0f} 点，老百姓捂紧钱包不敢花钱！全国{wang_count}家便民店日均营业额缩到 {wang_rev:.0f} 块，快交不起房租了！"
    elif wang_profit > 180.0:
        wang_status = "thriving"
        wang_s_desc = "人潮涌动 · 客流与消费意向爆发"
        wang_voice = f"收银台排长队！消费意向冲上去了，居民敢于买米买肉，日销售额冲破 {wang_rev:.0f} 块，扣完进货与税费每天净赚 {wang_profit:.0f} 块！"
    else:
        wang_status = "normal"
        wang_s_desc = "平价生鲜常态流转"
        wang_voice = f"全国{wang_count}家便民超市之一。日零售流水 {wang_rev:.0f} 块，批发进货 {wang_wholesale:.0f} 块，发收银员小杨工资 {wang_wages:.0f} 块，净赚 {wang_profit:.0f} 块。"

    employers["wang_retail"] = {
        "id": "wang_retail",
        "name": "王掌柜",
        "title": "社区便民连锁超市总经理",
        "category": "service",
        "category_name": "🛒 商贸零售",
        "avatar": "🛒",
        "scale_label": f"全国 {wang_count:,} 家社区便民超市之一 · 拥有3家门市·8名收银理货员",
        "representative_count": wang_count,
        "income_expense_ratio": wang_r,
        "savings_cushion_months": wang_c,
        "discretionary_propensity": emp_owner_propensity,
        "daily_revenue": wang_rev,
        "daily_expense": round(wang_wholesale + wang_wages + wang_rent_power + wang_vat, 1),
        "daily_net": wang_profit,
        "accumulated_funds": wang_funds,
        "financial_status": wang_status,
        "status_desc": wang_s_desc,
        "breakdown": {"粮油日化进货批发": wang_wholesale, "理货收银员基本薪资": wang_wages, "生鲜冷柜电费与租金": wang_rent_power, "终端商品增值流转税": wang_vat},
        "voice": wang_voice,
        "voucher_title": "社区便民平价超市每日收银对账结存单",
        "voucher_number": f"RET-{state.day:04d}-905",
        "receipt_lines": [
            {"subject": "市民日常扫码与现金消费进项", "from_acc": "千家万户市民个人账户", "to_acc": "国家商贸流通与综合商业 (专户)", "amount_yuan": wang_rev, "direction": "income", "note": "采购大米面粉、蔬菜日化消费款"},
            {"subject": "上游保供面粉粮油与副食品批发进货", "from_acc": "国家商贸流通与综合商业 (专户)", "to_acc": "粮油食品精炼联合企业 (专户)", "amount_yuan": wang_wholesale, "direction": "expense", "note": "大众米面食用油批量进货"},
            {"subject": "门店收银员小杨等人日薪结算", "from_acc": "国家商贸流通与综合商业 (专户)", "to_acc": "收银员小杨等在册员工账户", "amount_yuan": wang_wages, "direction": "expense", "note": "8名门店理货收银员报酬"},
            {"subject": "生鲜风幕柜冷藏电费与门面租金", "from_acc": "国家商贸流通与综合商业 (专户)", "to_acc": "国家骨干电网公司 (专户)", "amount_yuan": wang_rent_power, "direction": "expense", "note": "商用冷链用电与临街商铺租金"},
            {"subject": "终端零售商品流转增值税", "from_acc": "国家商贸流通与综合商业 (专户)", "to_acc": "中央政府国库单一账户 (TSA)", "amount_yuan": wang_vat, "direction": "expense", "note": f"按现行税率 {vat_tax_rate*100:.0f}% 代扣流转增值税"}
        ]
    }

    # (8) 数字化工业软件与财税科技服务公司 · 张总 (科技信息)
    zhang_tech_count = EMPLOYER_CENSUS["zhang_tech"]["entity_count"]
    zhang_rev = round(6800.0 * macro_rev_factor * (0.8 + 0.2 * (getattr(f_hardware, "utilization_rate", 85.0) / 85.0)), 1)
    zhang_wages = round(40 * 125.0, 1) # 40名白领工程师与财务日薪 (含李会计、小林)
    zhang_cloud = round(280.0, 1)
    zhang_social = round(zhang_wages * (social_contrib_rate * 0.6), 1)
    zhang_tax = round(max(0.0, zhang_rev - zhang_wages - zhang_cloud - zhang_social) * corp_tax_rate, 1)
    zhang_profit = round(zhang_rev - zhang_wages - zhang_cloud - zhang_social - zhang_tax, 1)
    zhang_tech_r = round(zhang_rev / max(1.0, zhang_wages + zhang_cloud + zhang_social + zhang_tax), 2)
    zhang_tech_funds = e_pool.get("zhang_tech", 580.0)
    zhang_tech_c = round((zhang_tech_funds * 10000.0) / max(10.0, (zhang_wages + zhang_cloud + zhang_social + zhang_tax) * 30.0), 1)

    if zhang_profit > 450.0:
        zhang_status = "thriving"
        zhang_s_desc = "制造业技改活跃 · 数字化需求强劲"
        zhang_voice = f"陈厂长等实体企业今年利润好，纷纷采购工业 MES 排产软件！日合同款到账 {zhang_rev:.0f} 块，全国{zhang_tech_count}家软件商净赚充沛，小林他们奖金稳了！"
    elif gdp_runrate < 2000.0:
        zhang_status = "warning"
        zhang_s_desc = "实体紧缩 · 数字化预算被削"
        zhang_voice = f"实体经济不景气，很多下游工厂取消了数字化改造。每天进账萎缩到 {zhang_rev:.0f} 块，40多个工程师与会计工资就要 {zhang_wages:.0f} 块，现金流很紧张..."
    else:
        zhang_status = "normal"
        zhang_s_desc = "合同软件开发稳健履约"
        zhang_voice = f"全国{zhang_tech_count}家科技公司之一。日软件营收 {zhang_rev:.0f} 块，付李会计与IT工程师小林薪水 {zhang_wages:.0f} 块，服务器租金 {zhang_cloud:.0f} 块，净利润 {zhang_profit:.0f} 块。"

    employers["zhang_tech"] = {
        "id": "zhang_tech",
        "name": "张总",
        "title": "工业软件与企业财税科技公司创始人",
        "category": "service",
        "category_name": "💻 科技服务",
        "avatar": "💻",
        "scale_label": f"全国 {zhang_tech_count:,} 家工业软件商之一 · 团队40人·雇佣小林与李会计等白领",
        "representative_count": zhang_tech_count,
        "income_expense_ratio": zhang_tech_r,
        "savings_cushion_months": zhang_tech_c,
        "discretionary_propensity": emp_owner_propensity,
        "daily_revenue": zhang_rev,
        "daily_expense": round(zhang_wages + zhang_cloud + zhang_social + zhang_tax, 1),
        "daily_net": zhang_profit,
        "accumulated_funds": zhang_tech_funds,
        "financial_status": zhang_status,
        "status_desc": zhang_s_desc,
        "breakdown": {"白领工程师与会计薪酬": zhang_wages, "云服务器算力租金": zhang_cloud, "研发人员五险一金": zhang_social, "企业所得税": zhang_tax},
        "voice": zhang_voice,
        "voucher_title": "工业软件与企业数字化专业服务日清凭单",
        "voucher_number": f"TECH-{state.day:04d}-612",
        "receipt_lines": [
            {"subject": "制造工厂MES软件与财税实施合同进项", "from_acc": "陈厂长五金机械集群 (专户)", "to_acc": "电子芯片与变电设备集团 (专户)", "amount_yuan": zhang_rev, "direction": "income", "note": "车间数控机床联网MES与李会计总账云服务"},
            {"subject": "软件工程师与专业会计薪酬直发", "from_acc": "电子芯片与变电设备集团 (专户)", "to_acc": "李会计、小林等白领储蓄账户", "amount_yuan": zhang_wages, "direction": "expense", "note": "40名IT工程师、产品经理与财务顾问日薪"},
            {"subject": "云计算算力集群与科技园区租金", "from_acc": "电子芯片与变电设备集团 (专户)", "to_acc": "国家实体企业综合清算总专户", "amount_yuan": zhang_cloud, "direction": "expense", "note": "工业物联网私有云服务器托管费用"},
            {"subject": "高新研发人员五险一金单位统筹", "from_acc": "电子芯片与变电设备集团 (专户)", "to_acc": "国家社会保障与医保统筹专户", "amount_yuan": zhang_social, "direction": "expense", "note": "依法为软件研发人员代缴综合社保"},
            {"subject": "企业所得税完税申报", "from_acc": "电子芯片与变电设备集团 (专户)", "to_acc": "中央政府国库单一账户 (TSA)", "amount_yuan": zhang_tax, "direction": "expense", "note": "按软件服务净收益向国税申报企业所得税"}
        ]
    }

    # (9) 国家商业银行城市分行 · 高行长 (金融中介 - 映射全国600家重点分行)
    gao_count = EMPLOYER_CENSUS["gao_bank"]["entity_count"]
    # 全国信贷日息收缴 / 600 家重点分行
    daily_loan_rev_total = getattr(state, "daily_bank_loan_interest_rev", 0.0)
    if daily_loan_rev_total <= 0.001:
        bank_loans_all = getattr(state, "bank_loans", 3000.0) # 亿元
        daily_loan_rev_total = (bank_loans_all * loan_rate) / 360.0
    gao_int_in_display = round((daily_loan_rev_total * 100_000_000 / gao_count) / 10000.0, 1) # 万元/天
    
    daily_dep_cost_total = getattr(state, "daily_bank_deposit_interest_cost", 0.0)
    if daily_dep_cost_total <= 0.001:
        daily_dep_cost_total = (getattr(state, "bank_deposits", 4000.0) * deposit_rate) / 360.0
    gao_int_out_display = round((daily_dep_cost_total * 100_000_000 / gao_count) / 10000.0, 1)
    
    daily_prov_total = getattr(state, "daily_bank_provision_deduction", 0.0)
    if daily_prov_total <= 0.001:
        daily_prov_total = (daily_loan_rev_total * getattr(state, "bad_debt_rate", 0.045) * 1.5)
    gao_bad_debt_loss = round((daily_prov_total * 100_000_000 / gao_count) / 10000.0, 1)
    
    gao_ops_cost = round(1.8, 1) # 网点50人日薪、机房与柜面运维 (1.8万元/天)
    gao_net_spread = round(gao_int_in_display - gao_int_out_display - gao_bad_debt_loss - gao_ops_cost, 1)
    gao_r = round(gao_int_in_display / max(0.1, gao_int_out_display + gao_bad_debt_loss + gao_ops_cost), 2)
    gao_funds = e_pool.get("gao_bank", 1200.0)
    gao_c = round(gao_funds / max(1.0, (gao_int_out_display + gao_bad_debt_loss + gao_ops_cost) * 30.0), 1)

    car_val = getattr(state, "capital_adequacy_ratio", 10.0)
    recalled_total = getattr(state, "daily_loans_recalled", 0.0)
    npl_rate = getattr(state, "bad_debt_rate", 0.045) * 100.0

    if getattr(state, "credit_crunch_active", False) or car_val < 8.0:
        gao_status = "crisis"
        gao_s_desc = f"资本充足率告警 ({car_val:.1f}%) · 启动信贷紧缩"
        gao_voice = f"巴塞尔监管红线告急！总行资本充足率跌破8.0%警戒线（仅 {car_val:.1f}%），我们已全面收回高风险贷款，暂停新增普通企业授信，严防系统性金融风险！"
    elif recalled_total > 0.05:
        gao_status = "warning"
        gao_s_desc = f"风控抽贷压降敞口 ({recalled_total:.2f}亿) · 资产保全"
        gao_voice = f"全行业不良贷款率达 {npl_rate:.1f}%！针对评级恶化至CCC级的高危亏损实体，本行今日已启动强制抽贷 {recalled_total:.2f} 亿元，优先扣划存款保全国家信贷资产！"
    elif npl_rate > 5.5:
        gao_status = "warning"
        gao_s_desc = f"不良贷款率攀升至 {npl_rate:.1f}% · 加大拨备"
        gao_voice = f"实体企业不良贷款率升至 {npl_rate:.1f}%！全国{gao_count}家分行每日计提拨备准备金承压，正对高杠杆弱质企业加强贷后风控！"
    elif gao_net_spread > 2.0:
        gao_status = "thriving"
        gao_s_desc = f"净息差稳健 · CAR {car_val:.1f}% 坚挺"
        gao_voice = f"商业贷款利率 {loan_rate*100:.1f}%，资本充足率 {car_val:.1f}%！全国信贷基本盘稳固，优质AAA级实体扩产授信通畅，日息差结余稳健！"
    else:
        gao_status = "normal"
        gao_s_desc = "存贷利差平稳排产"
        gao_voice = f"作为全国{gao_count}家骨干分行之一，每日收缴贷款利息 {gao_int_in_display:.1f} 万元，划付储户利息 {gao_int_out_display:.1f} 万元，计提不良拨备 {gao_bad_debt_loss:.1f} 万元，营运结余 {gao_net_spread:.1f} 万元。"

    employers["gao_bank"] = {
        "id": "gao_bank",
        "name": "高行长",
        "title": "国家商业银行城市分行行长",
        "category": "service",
        "category_name": "🏦 商业银行",
        "avatar": "🏦",
        "scale_label": f"全国 {gao_count:,} 家商业银行重点分行之一 · 管理50亿元信贷盘子 (CAR {car_val:.1f}%)",
        "representative_count": gao_count,
        "income_expense_ratio": gao_r,
        "savings_cushion_months": gao_c,
        "discretionary_propensity": emp_owner_propensity,
        "daily_revenue": gao_int_in_display * 10000.0, # 换算为元以保持数据量纲一致
        "daily_expense": round((gao_int_out_display + gao_bad_debt_loss + gao_ops_cost) * 10000.0, 1),
        "daily_net": gao_net_spread * 10000.0,
        "accumulated_funds": gao_funds,
        "financial_status": gao_status,
        "status_desc": gao_s_desc,
        "breakdown": {"储户存款付息": gao_int_out_display * 10000.0, "不良坏账拨备": gao_bad_debt_loss * 10000.0, "网点营运科技支出": gao_ops_cost * 10000.0},
        "voice": gao_voice,
        "voucher_title": "国家商业银行城市分行信贷与利差结算日报",
        "voucher_number": f"BANK-{state.day:04d}-001",
        "receipt_lines": [
            {"subject": "持有国家主权记账式国债票息进项", "from_acc": "中央政府国库单一账户 (TSA)", "to_acc": "商业银行系统营运准备金与利差头寸", "amount_yuan": round((getattr(state, "national_debt", 800.0) * getattr(state, "national_debt_rate", 0.035) * 0.85 * 1e8 / 360.0) / gao_count, 1), "direction": "income", "note": f"商业银行资产负债表中持有国债 (0%风险权重，Basel CAR RWA=0)，主权评级 {getattr(state, 'sovereign_credit_rating', 'AAA')}，日票息无风险兑付"},
            {"subject": "企业经营贷与个人按揭利息归集", "from_acc": "企业专户与李会计等个人账户", "to_acc": "商业银行系统营运准备金与利差头寸", "amount_yuan": gao_int_in_display * 10000.0, "direction": "income", "note": f"按现行商业贷款利率 {loan_rate*100:.2f}% 执行每日利息结算"},
            {"subject": "储蓄存款法定利息给付划出", "from_acc": "商业银行系统营运准备金与利差头寸", "to_acc": "全体居民与实体企业储蓄账户", "amount_yuan": gao_int_out_display * 10000.0, "direction": "expense", "note": f"按指导存款利率 {deposit_rate*100:.2f}% 向全社会存款人付息"},
            {"subject": "实体不良贷款核销与风险拨备", "from_acc": "商业银行系统营运准备金与利差头寸", "to_acc": "商业银行信贷风险准备金专户", "amount_yuan": gao_bad_debt_loss * 10000.0, "direction": "expense", "note": f"依据全社会不良率 {npl_rate:.2f}% 计提风险准备 (拨备覆盖率 {getattr(state, 'bank_provision_coverage', 148.0):.1f}%)"},
            {"subject": "银行柜面运营、科技清算与员工开支", "from_acc": "商业银行系统营运准备金与利差头寸", "to_acc": "商业银行内部综合费用支出户", "amount_yuan": gao_ops_cost * 10000.0, "direction": "expense", "note": "营业网点柜员薪酬、核心交易主机运维费用"}
        ] + ([{
            "subject": "海外主权财富基金每日海外股息代收结汇",
            "from_acc": "境外离岸清算与主权投资基金专户",
            "to_acc": "中央政府国库单一账户 (TSA)",
            "amount_yuan": round(getattr(state, "swf_daily_yield_usd", 0.0) * getattr(state, "exchange_rate", 7.20) * 1e8 / gao_count, 1),
            "direction": "income",
            "note": f"主权基金资产规模 ${getattr(state, 'sovereign_wealth_fund_usd', 0.0):.2f} 亿，平准外汇同时赚取海外无风险资产息差"
        }] if getattr(state, "sovereign_wealth_fund_usd", 0.0) > 0.01 else [])
    }

    # (10) 大众便民快餐连锁 · 张老板 (大众餐饮 - 严格基于全社会餐饮总需求均摊)
    zhang_eat_count = EMPLOYER_CENSUS["zhang_catering"]["entity_count"]
    # 单店营业额 = 全社会大众餐饮消费总额 / 45,000 家快餐门市
    zhang_eat_rev = round(macro_catering_total_yuan / zhang_eat_count, 1)
    zhang_eat_food = round(zhang_eat_rev * 0.42 * (food_price / 15.0), 1)
    zhang_eat_wages = round(4 * max(min_wage * 1.15, 45.0), 1) # 4名后厨打荷配菜工 (小何等)
    zhang_eat_gas_power = round(160.0 * max(0.6, 1.0 - energy_discount) + 30.0, 1)
    zhang_eat_rent = round(110.0, 1)
    zhang_eat_tax = round(max(0.0, zhang_eat_rev - zhang_eat_food - zhang_eat_wages - zhang_eat_gas_power - zhang_eat_rent) * vat_tax_rate, 1)
    zhang_eat_profit = round(zhang_eat_rev - zhang_eat_food - zhang_eat_wages - zhang_eat_gas_power - zhang_eat_rent - zhang_eat_tax, 1)
    zhang_eat_r = round(zhang_eat_rev / max(1.0, zhang_eat_food + zhang_eat_wages + zhang_eat_gas_power + zhang_eat_rent + zhang_eat_tax), 2)
    zhang_eat_funds = e_pool.get("zhang_catering", 150.0)
    zhang_eat_c = round((zhang_eat_funds * 10000.0) / max(10.0, (zhang_eat_food + zhang_eat_wages + zhang_eat_gas_power + zhang_eat_rent + zhang_eat_tax) * 30.0), 1)

    if sentiment_index < 25.0:
        zhang_eat_status = "warning"
        zhang_eat_s_desc = "市民紧缩少下馆子 · 堂食冷落"
        zhang_eat_voice = f"市民消费信心仅 {sentiment_index:.0f} 点，老百姓中午只敢吃白馒头，全国{zhang_eat_count}家便民快餐店日均流水缩到 {zhang_eat_rev:.0f} 块，交完房租水电几乎没得赚！"
    elif food_price > 18.0:
        zhang_eat_status = "warning"
        zhang_eat_s_desc = "肉蛋菜原料高企 · 利薄难熬"
        zhang_eat_voice = f"菜篮子涨到 {food_price:.1f} 块，每天买肉进菜就要吃掉 {zhang_eat_food:.0f} 块！快餐不敢轻易涨价，利润薄得像刀片一样！"
    elif zhang_eat_profit > 240.0:
        zhang_eat_status = "thriving"
        zhang_eat_s_desc = "座无虚席 · 翻台爆满"
        zhang_eat_voice = f"老百姓消费意愿上来了！全国大众餐饮日消费冲上 {macro_catering_total_yuan/1e8:.2f} 亿，分摊到小店日流水突破 {zhang_eat_rev:.0f} 块，每天净赚 {zhang_eat_profit:.0f} 块！"
    else:
        zhang_eat_status = "normal"
        zhang_eat_s_desc = "社区平价常态供餐"
        zhang_eat_voice = f"全国{zhang_eat_count}家便民小吃店之一。日均快餐流水 {zhang_eat_rev:.0f} 块，采购肉菜米面 {zhang_eat_food:.0f} 块，发后厨小何工资 {zhang_eat_wages:.0f} 块，租金燃气 {zhang_eat_gas_power+zhang_eat_rent:.0f} 块，净赚 {zhang_eat_profit:.0f} 块。"

    employers["zhang_catering"] = {
        "id": "zhang_catering",
        "name": "张老板",
        "title": "社区大众便民快餐连锁掌勺主理人",
        "category": "catering",
        "category_name": "🍜 大众餐饮",
        "avatar": "🍲",
        "scale_label": f"全国 {zhang_eat_count:,} 家社区便民小吃店之一 · 雇佣4名后厨配菜打荷工",
        "representative_count": zhang_eat_count,
        "income_expense_ratio": zhang_eat_r,
        "savings_cushion_months": zhang_eat_c,
        "discretionary_propensity": emp_owner_propensity,
        "daily_revenue": zhang_eat_rev,
        "daily_expense": round(zhang_eat_food + zhang_eat_wages + zhang_eat_gas_power + zhang_eat_rent + zhang_eat_tax, 1),
        "daily_net": zhang_eat_profit,
        "accumulated_funds": zhang_eat_funds,
        "financial_status": zhang_eat_status,
        "status_desc": zhang_eat_s_desc,
        "breakdown": {"肉禽蛋菜进货": zhang_eat_food, "后厨员工工资": zhang_eat_wages, "厨房燃气动力电费": zhang_eat_gas_power, "门面房租开销": zhang_eat_rent, "餐饮流转增值税": zhang_eat_tax},
        "voice": zhang_eat_voice,
        "voucher_title": "社区大众便民快餐连锁每日出餐结算单",
        "voucher_number": f"FOOD-{state.day:04d}-782",
        "receipt_lines": [
            {"subject": "大众堂食快餐与外卖扫码流水进项", "from_acc": "周边白领、散工与市民个人账户", "to_acc": "大众便民快餐连锁营运户", "amount_yuan": zhang_eat_rev, "direction": "income", "note": f"全国餐饮日总额 {macro_catering_total_yuan/1e8:.3f} 亿元按 {zhang_eat_count} 家门店均摊"},
            {"subject": "菜市场生鲜肉禽蔬菜与大米采购", "from_acc": "大众便民快餐连锁营运户", "to_acc": "国家商贸流通与综合商业 (专户)", "amount_yuan": zhang_eat_food, "direction": "expense", "note": "采购精制大米、食用油与生鲜肉禽"},
            {"subject": "后厨配菜打荷与掌勺员工工资", "from_acc": "大众便民快餐连锁营运户", "to_acc": "后厨配菜工小何等在册员工账户", "amount_yuan": zhang_eat_wages, "direction": "expense", "note": "4名后厨打荷工、炒锅师傅在岗日薪"},
            {"subject": "商用爆炒猛火燃气与冷藏展示柜动力电", "from_acc": "大众便民快餐连锁营运户", "to_acc": "国家骨干电网公司 (专户)", "amount_yuan": zhang_eat_gas_power, "direction": "expense", "note": "管道燃气与展示柜动力电费"},
            {"subject": "临街商铺房租按日分摊", "from_acc": "大众便民快餐连锁营运户", "to_acc": "临街房东个人储蓄账户", "amount_yuan": zhang_eat_rent, "direction": "expense", "note": "城市生活区临街商铺租赁日分摊"}
        ]
    }

    # (11) 文旅精品客栈民宿 · 苏老板 (文化旅游 - 严格基于全社会文旅总需求均摊)
    su_count = EMPLOYER_CENSUS["su_tourism"]["entity_count"]
    # 单店日客房流水 = 全社会文旅消费总额 / 12,000 家客栈民宿
    su_tour_rev = round(macro_tourism_total_yuan / su_count, 1)
    su_tour_rent = round(280.0, 1)
    su_tour_loan = round(90.0 * (loan_rate / 0.065), 1)
    su_tour_power = round(130.0 * max(0.65, 1.0 - energy_discount), 1)
    su_tour_wages = round(3 * max(min_wage * 1.2, 50.0), 1)
    su_tour_tax = round(max(0.0, su_tour_rev - su_tour_rent - su_tour_loan - su_tour_power - su_tour_wages) * 0.08, 1)
    su_tour_profit = round(su_tour_rev - su_tour_rent - su_tour_loan - su_tour_power - su_tour_wages - su_tour_tax, 1)
    su_tour_r = round(su_tour_rev / max(1.0, su_tour_rent + su_tour_loan + su_tour_power + su_tour_wages + su_tour_tax), 2)
    su_tour_funds = e_pool.get("su_tourism", 180.0)
    su_tour_c = round((su_tour_funds * 10000.0) / max(10.0, (su_tour_rent + su_tour_loan + su_tour_power + su_tour_wages + su_tour_tax) * 30.0), 1)

    if sentiment_index < 25.0:
        su_tour_status = "warning"
        su_tour_s_desc = "大众紧缩 · 依靠高净值客群托底"
        su_tour_voice = f"市民消费信心仅 {sentiment_index:.0f} 点，普通打工人不敢旅游，幸好全国15万林博士、30万小林工程师还有高行长、张总这些高收支比老板们撑着，客栈日营收仍有 {su_tour_rev:.0f} 块！"
    elif loan_rate > 0.08:
        su_tour_status = "warning"
        su_tour_s_desc = "翻新贷款利息沉重"
        su_tour_voice = f"商业贷款利率高达 {loan_rate*100:.1f}%，每天一睁眼先给银行还 {su_tour_loan:.0f} 块利息！文旅微利全被金融利息吞噬了！"
    elif su_tour_profit > 300.0:
        su_tour_status = "thriving"
        su_tour_s_desc = "周末满房 · 露营下午茶爆满"
        su_tour_voice = f"交通便利且工薪阶层收支比提升，市民旅游意愿彻底爆发！全社会文旅日总额达 {macro_tourism_total_yuan/1e8:.2f} 亿，单店日流水冲破 {su_tour_rev:.0f} 块，每天净赚 {su_tour_profit:.0f} 块！"
    else:
        su_tour_status = "normal"
        su_tour_s_desc = "近郊休闲常态接待"
        su_tour_voice = f"全国{su_count}家特色客栈之一。全社会文旅日均 {macro_tourism_total_yuan/1e8:.2f} 亿，均摊到本店日营收 {su_tour_rev:.0f} 块，付老宅租金 {su_tour_rent:.0f} 块，还利息 {su_tour_loan:.0f} 块，空调电费 {su_tour_power:.0f} 块，结余 {su_tour_profit:.0f} 块。"

    employers["su_tourism"] = {
        "id": "su_tourism",
        "name": "苏老板",
        "title": "近郊文旅精品度假民宿客栈主理人",
        "category": "tourism",
        "category_name": "🏖️ 文旅住宿",
        "avatar": "🏖️",
        "scale_label": f"全国 {su_count:,} 家精品民宿客栈之一 · 18间特色客房·雇佣3名布草管家",
        "representative_count": su_count,
        "income_expense_ratio": su_tour_r,
        "savings_cushion_months": su_tour_c,
        "discretionary_propensity": emp_owner_propensity,
        "daily_revenue": su_tour_rev,
        "daily_expense": round(su_tour_rent + su_tour_loan + su_tour_power + su_tour_wages + su_tour_tax, 1),
        "daily_net": su_tour_profit,
        "accumulated_funds": su_tour_funds,
        "financial_status": su_tour_status,
        "status_desc": su_tour_s_desc,
        "breakdown": {"景区老宅长租金": su_tour_rent, "精品装修银行利息": su_tour_loan, "中央空调全天电费": su_tour_power, "客栈管家日薪": su_tour_wages, "文旅综合服务税": su_tour_tax},
        "voice": su_tour_voice,
        "voucher_title": "文旅精品度假客栈每日宿务对账单",
        "voucher_number": f"TOUR-{state.day:04d}-205",
        "receipt_lines": [
            {"subject": "全国度假游客客房预订与露营消费", "from_acc": "林博士、小林及高净值企业主储蓄户", "to_acc": "精品文旅民宿营运专户", "amount_yuan": su_tour_rev, "direction": "income", "note": f"全国文旅日总额 {macro_tourism_total_yuan/1e8:.3f} 亿元按 {su_count} 家客栈均摊"},
            {"subject": "景区传统民居院落长租金", "from_acc": "精品文旅民宿营运专户", "to_acc": "乡村集体经济合作社账户", "amount_yuan": su_tour_rent, "direction": "expense", "note": "文旅示范村传统民居保护性租赁费按日摊销"},
            {"subject": "客栈绿色升级改造信贷还息", "from_acc": "精品文旅民宿营运专户", "to_acc": "商业银行信贷营运专户", "amount_yuan": su_tour_loan, "direction": "expense", "note": "中长期文旅微利抵押信贷每日偿付利息"},
            {"subject": "中央空调冷暖与恒温地暖电费", "from_acc": "精品文旅民宿营运专户", "to_acc": "国家骨干电网公司 (专户)", "amount_yuan": su_tour_power, "direction": "expense", "note": "舒适温控商业动力电费"},
            {"subject": "客房管家与布草保洁团队工资", "from_acc": "精品文旅民宿营运专户", "to_acc": "民宿管家前台等在册员工账户", "amount_yuan": su_tour_wages, "direction": "expense", "note": "3名在册客房管家、专业布草清洁阿姨日薪"}
        ]
    }

    # (12) 社区平价综合门诊部 · 何院长 (医疗卫生)
    he_count = EMPLOYER_CENSUS["he_clinic"]["entity_count"]
    he_med_rev = round(3200.0 * (0.7 + 0.3 * medicare_rate) * (0.8 + 0.2 * (state.social_fund_pool / 450.0)), 1)
    he_med_drugs = round(he_med_rev * 0.45, 1)
    he_med_wages = round(6 * max(min_wage * 1.8, 80.0), 1) # 6名执业医护 (含周护士)
    he_med_equip_loan = round(70.0 * (loan_rate / 0.065), 1)
    he_med_waste = round(40.0, 1)
    he_med_tax = round(max(0.0, he_med_rev - he_med_drugs - he_med_wages - he_med_equip_loan - he_med_waste) * 0.05, 1)
    he_med_profit = round(he_med_rev - he_med_drugs - he_med_wages - he_med_equip_loan - he_med_waste - he_med_tax, 1)
    he_med_r = round(he_med_rev / max(1.0, he_med_drugs + he_med_wages + he_med_equip_loan + he_med_waste + he_med_tax), 2)
    he_med_funds = e_pool.get("he_clinic", 320.0)
    he_med_c = round((he_med_funds * 10000.0) / max(10.0, (he_med_drugs + he_med_wages + he_med_equip_loan + he_med_waste + he_med_tax) * 30.0), 1)

    if medicare_rate < 0.50:
        he_med_status = "warning"
        he_med_s_desc = "医保报销率下降 · 居民就医迟疑"
        he_med_voice = f"国家医保报销比例降到 {medicare_rate*100:.0f}%，许多慢病老乡因个人自负过高放弃常态开药，门诊统筹结算额明显缩水！"
    elif he_med_profit > 260.0:
        he_med_status = "thriving"
        he_med_s_desc = "医保直报顺畅 · 基层防线坚固"
        he_med_voice = f"国家医保基金池保障有力，全国{he_count}家门诊即时结算！日就诊与药品周转达 {he_med_rev:.0f} 块，医护津贴全额兑现！"
    else:
        he_med_status = "normal"
        he_med_s_desc = "基层诊疗常态接诊"
        he_med_voice = f"全国{he_count}家平价诊所之一。日诊疗与药房流水 {he_med_rev:.0f} 块，采购基本集采药物 {he_med_drugs:.0f} 块，发周护士等医护工资 {he_med_wages:.0f} 块，结余 {he_med_profit:.0f} 块。"

    employers["he_clinic"] = {
        "id": "he_clinic",
        "name": "何院长",
        "title": "基层社区平价综合门诊部院长",
        "category": "medical",
        "category_name": "🏥 社区医疗",
        "avatar": "🏥",
        "scale_label": f"全国 {he_count:,} 家社区平价门诊之一 · 医护团队6人·辐射2万居民",
        "representative_count": he_count,
        "income_expense_ratio": he_med_r,
        "savings_cushion_months": he_med_c,
        "discretionary_propensity": emp_owner_propensity,
        "daily_revenue": he_med_rev,
        "daily_expense": round(he_med_drugs + he_med_wages + he_med_equip_loan + he_med_waste + he_med_tax, 1),
        "daily_net": he_med_profit,
        "accumulated_funds": he_med_funds,
        "financial_status": he_med_status,
        "status_desc": he_med_s_desc,
        "breakdown": {"国家基本药物采购": he_med_drugs, "执业医护人员薪酬": he_med_wages, "检验诊断仪器按揭": he_med_equip_loan, "医疗危废处置耗材": he_med_waste, "普惠医疗服务税": he_med_tax},
        "voice": he_med_voice,
        "voucher_title": "社区综合门诊部每日诊疗与医保结算报表",
        "voucher_number": f"MEDI-{state.day:04d}-112",
        "receipt_lines": [
            {"subject": "居民慢病与常见病统筹报销进项", "from_acc": "国家社会保障与医保统筹专户", "to_acc": "基层平价门诊部营运账户", "amount_yuan": round(he_med_rev * 0.75, 1), "direction": "income", "note": f"按现行医保报销率 {medicare_rate*100:.0f}% 自动清算"},
            {"subject": "门诊就医患者自负现金缴费", "from_acc": "张大娘、老田等就诊居民个人账户", "to_acc": "基层平价门诊部营运账户", "amount_yuan": round(he_med_rev * 0.25, 1), "direction": "income", "note": "患者个人支付自费部分"},
            {"subject": "国家集采基本药物与输液耗材采购", "from_acc": "基层平价门诊部营运账户", "to_acc": "国家实体企业综合清算总专户", "amount_yuan": he_med_drugs, "direction": "expense", "note": "常用抗生素、降压降糖药采购"},
            {"subject": "在册全科医生与护士岗位日薪直发", "from_acc": "基层平价门诊部营运账户", "to_acc": "在册执业医生、护士周护士等储蓄卡", "amount_yuan": he_med_wages, "direction": "expense", "note": "6名全科执业医生、输液护士在岗日薪"},
            {"subject": "检验诊断仪器融资租赁贷款付息", "from_acc": "基层平价门诊部营运账户", "to_acc": "商业银行信贷营运专户", "amount_yuan": he_med_equip_loan, "direction": "expense", "note": "基层生化分析设备贷款利息偿付"}
        ]
    }

    # (13) 现代职业技能技术培训中心 · 梁校长 (职业教育)
    liang_count = EMPLOYER_CENSUS["liang_training"]["entity_count"]
    liang_gov_sub = round(infra_daily * 40.0 + welfare_daily * 30.0 + (unemployment_rate * 320.0), 1)
    liang_self_fee = round(750.0 * macro_rev_factor, 1)
    liang_rev = round(liang_gov_sub + liang_self_fee, 1)
    liang_mach_maint = round(160.0 * (p_steel / 3200.0), 1)
    liang_power = round(140.0 * max(0.65, 1.0 - energy_discount), 1)
    liang_wages = round(5 * max(min_wage * 2.0, 90.0), 1)
    liang_tax = round(max(0.0, liang_rev - liang_mach_maint - liang_power - liang_wages) * 0.05, 1)
    liang_profit = round(liang_rev - liang_mach_maint - liang_power - liang_wages - liang_tax, 1)
    liang_r = round(liang_rev / max(1.0, liang_mach_maint + liang_power + liang_wages + liang_tax), 2)
    liang_funds = e_pool.get("liang_training", 160.0)
    liang_c = round((liang_funds * 10000.0) / max(10.0, (liang_mach_maint + liang_power + liang_wages + liang_tax) * 30.0), 1)

    if liang_profit > 240.0:
        liang_status = "thriving"
        liang_s_desc = "技能转岗培训饱满 · 财政直达"
        liang_voice = f"以工代赈与职业技能扶持专款足额直达！机加和焊工实训台全部满员，全国{liang_count}家中心每天净赚 {liang_profit:.0f} 块，输送大批合格技工！"
    elif liang_rev < 1200.0:
        liang_status = "warning"
        liang_s_desc = "再就业培训补贴紧缩 · 设备闲置"
        liang_voice = f"财政技能培训补贴收紧，学员囊中羞涩，数控实训车间机器开机率不足一半，折旧开销巨大！"
    else:
        liang_status = "normal"
        liang_s_desc = "工匠学徒常态化轮训"
        liang_voice = f"全国{liang_count}家培训中心之一。日收入 {liang_rev:.0f} 块，付实训耗材 {liang_mach_maint:.0f} 块，实训高压电 {liang_power:.0f} 块，发教练技师工资 {liang_wages:.0f} 块，结余 {liang_profit:.0f} 块。"

    employers["liang_training"] = {
        "id": "liang_training",
        "name": "梁校长",
        "title": "现代职业技能技术实训中心校长",
        "category": "education",
        "category_name": "🎓 职业培训",
        "avatar": "🎓",
        "scale_label": f"全国 {liang_count:,} 家现代实训中心之一 · 4大实训车间·年实训1500人",
        "representative_count": liang_count,
        "income_expense_ratio": liang_r,
        "savings_cushion_months": liang_c,
        "discretionary_propensity": emp_owner_propensity,
        "daily_revenue": liang_rev,
        "daily_expense": round(liang_mach_maint + liang_power + liang_wages + liang_tax, 1),
        "daily_net": liang_profit,
        "accumulated_funds": liang_funds,
        "financial_status": liang_status,
        "status_desc": liang_s_desc,
        "breakdown": {"实训钢件刀具损耗": liang_mach_maint, "实训工场工业动力电": liang_power, "双师型技术教练工资": liang_wages, "职业技术教育税费": liang_tax},
        "voice": liang_voice,
        "voucher_title": "职业技能技术培训中心每日教务收支决算单",
        "voucher_number": f"EDUC-{state.day:04d}-402",
        "receipt_lines": [
            {"subject": "再就业与技能培训专款直拨", "from_acc": "中央政府国库单一账户 (TSA)", "to_acc": "现代职业技能培训中心专户", "amount_yuan": liang_gov_sub, "direction": "income", "note": "国家以工代赈转岗技能培训人头补贴"},
            {"subject": "社会学徒自费培训考证学费", "from_acc": "青年技工等学员银行卡", "to_acc": "现代职业技能培训中心专户", "amount_yuan": liang_self_fee, "direction": "income", "note": "数控车工、高级焊工考培费"},
            {"subject": "机加实训钢件与硬质合金刀具损耗", "from_acc": "现代职业技能培训中心专户", "to_acc": "陈厂长五金机械集群 (专户)", "amount_yuan": liang_mach_maint, "direction": "expense", "note": "实训工件及刀具采购"},
            {"subject": "实训机房与大功率焊机工业电费", "from_acc": "现代职业技能培训中心专户", "to_acc": "国家骨干电网公司 (专户)", "amount_yuan": liang_power, "direction": "expense", "note": "数控机床全天候实操动力电"},
            {"subject": "高级技师实操教练日薪薪资", "from_acc": "现代职业技能培训中心专户", "to_acc": "在册实训带教骨干教练银行卡", "amount_yuan": liang_wages, "direction": "expense", "note": "5名骨干技术教练日薪"}
        ]
    }

    # (14) 城市客运出租车与网约车队 · 陆队长 (客运出行)
    lu_count = EMPLOYER_CENSUS["lu_taxi_fleet"]["entity_count"]
    lu_rev = round(4200.0 * (0.6 + 0.4 * sentiment) * macro_rev_factor, 1)
    lu_payout = round(lu_rev * 0.65, 1) # 直发司机劳务 (蒋师傅等)
    lu_fuel_charge = round(320.0 * (p_oil / 520.0 * 0.6 + 0.4 * max(0.65, 1.0 - energy_discount)), 1)
    lu_car_loan = round(120.0 * (loan_rate / 0.065), 1)
    lu_insurance_maint = round(160.0, 1)
    lu_tax = round(max(0.0, lu_rev - lu_payout - lu_fuel_charge - lu_car_loan - lu_insurance_maint) * 0.08, 1)
    lu_profit = round(lu_rev - lu_payout - lu_fuel_charge - lu_car_loan - lu_insurance_maint - lu_tax, 1)
    lu_r = round(lu_rev / max(1.0, lu_payout + lu_fuel_charge + lu_car_loan + lu_insurance_maint + lu_tax), 2)
    lu_funds = e_pool.get("lu_taxi_fleet", 220.0)
    lu_c = round((lu_funds * 10000.0) / max(10.0, (lu_payout + lu_fuel_charge + lu_car_loan + lu_insurance_maint + lu_tax) * 30.0), 1)

    if p_oil > 620.0:
        lu_status = "warning"
        lu_s_desc = "油价与补能高企 · 车队利润收缩"
        lu_voice = f"车用燃油和气价持续飙升，40台营运车每天光补能就要扣走 {lu_fuel_charge:.0f} 块！司机们喊交不起份子钱，车队微利几乎见底！"
    elif lu_profit > 280.0:
        lu_status = "thriving"
        lu_s_desc = "城市客流活跃 · 调度周转高效"
        lu_voice = f"市民出行打车需求极度旺盛，全国{lu_count}个车队早晚高峰满负荷接单！车队日流水突破 {lu_rev:.0f} 块，每天净赚 {lu_profit:.0f} 块！"
    else:
        lu_status = "normal"
        lu_s_desc = "城市道路全天候平稳客运"
        lu_voice = f"全国{lu_count}个出租车队之一。日客运流水 {lu_rev:.0f} 块，发蒋师傅等司机劳务 {lu_payout:.0f} 块，充气充电动力费 {lu_fuel_charge:.0f} 块，净结余 {lu_profit:.0f} 块。"

    employers["lu_taxi_fleet"] = {
        "id": "lu_taxi_fleet",
        "name": "陆队长",
        "title": "城市客运出租与网约出行车队队长",
        "category": "transport",
        "category_name": "🚖 客运出行",
        "avatar": "🚖",
        "scale_label": f"全国 {lu_count:,} 个城市客运车队之一 · 40台双燃料车·50名职业司机",
        "representative_count": lu_count,
        "income_expense_ratio": lu_r,
        "savings_cushion_months": lu_c,
        "discretionary_propensity": emp_owner_propensity,
        "daily_revenue": lu_rev,
        "daily_expense": round(lu_payout + lu_fuel_charge + lu_car_loan + lu_insurance_maint + lu_tax, 1),
        "daily_net": lu_profit,
        "accumulated_funds": lu_funds,
        "financial_status": lu_status,
        "status_desc": lu_s_desc,
        "breakdown": {"营运司机日结劳务": lu_payout, "车队充气充电动力": lu_fuel_charge, "纯电车辆租赁分期": lu_car_loan, "营运保险与日常维保": lu_insurance_maint, "客运综合营业税": lu_tax},
        "voice": lu_voice,
        "voucher_title": "城市公共交通客运出租车队营运结算单",
        "voucher_number": f"TAXI-{state.day:04d}-631",
        "receipt_lines": [
            {"subject": "市民出行扫码车费进项", "from_acc": "市民大众出行支付扫码专户", "to_acc": "城市出租网约客运车队专户", "amount_yuan": lu_rev, "direction": "income", "note": "40辆在册营运车辆接单线上流水汇总"},
            {"subject": "出租驾驶员蒋师傅营运劳务返付", "from_acc": "城市出租网约客运车队专户", "to_acc": "蒋师傅等职业驾驶员个人银行卡", "amount_yuan": lu_payout, "direction": "expense", "note": "扣除平台服务费后直发驾驶员里程劳务"},
            {"subject": "车用压缩天然气加注与快充电费", "from_acc": "城市出租网约客运车队专户", "to_acc": "国家油气田开采公司 (专户)", "amount_yuan": lu_fuel_charge, "direction": "expense", "note": "全天车辆CNG与充电桩电费"},
            {"subject": "新能源车辆融资租赁分期利息", "from_acc": "城市出租网约客运车队专户", "to_acc": "商业银行信贷营运专户", "amount_yuan": lu_car_loan, "direction": "expense", "note": "购置纯电车辆信贷利息偿付"},
            {"subject": "营运高保额交强险与例行机修", "from_acc": "城市出租网约客运车队专户", "to_acc": "国家实体企业综合清算总专户", "amount_yuan": lu_insurance_maint, "direction": "expense", "note": "营运车辆商业险与日常保养"}
        ]
    }

    # (15) 房产租售与社区物业服务 · 罗经理 (居住物业)
    luo_count = EMPLOYER_CENSUS["luo_property"]["entity_count"]
    luo_prop_fee = round(2100.0 * macro_rev_factor, 1)
    luo_agency_fee = round(900.0 * max(0.3, 1.2 - (loan_rate / 0.065)), 1)
    luo_rev = round(luo_prop_fee + luo_agency_fee, 1)
    luo_wages = round(12 * max(min_wage * 1.25, 48.0), 1) # 12名安保维修 (含老谢)
    luo_parts = round(150.0 * (p_hardware / 180.0), 1)
    luo_elevator_power = round(180.0 * max(0.65, 1.0 - energy_discount), 1)
    luo_tax = round(max(0.0, luo_rev - luo_wages - luo_parts - luo_elevator_power) * 0.10, 1)
    luo_profit = round(luo_rev - luo_wages - luo_parts - luo_elevator_power - luo_tax, 1)
    luo_r = round(luo_rev / max(1.0, luo_wages + luo_parts + luo_elevator_power + luo_tax), 2)
    luo_funds = e_pool.get("luo_property", 550.0)
    luo_c = round((luo_funds * 10000.0) / max(10.0, (luo_wages + luo_parts + luo_elevator_power + luo_tax) * 30.0), 1)

    if loan_rate > 0.08:
        luo_status = "warning"
        luo_s_desc = "房贷利率高企 · 房屋租售佣金冰封"
        luo_voice = f"商业房贷利率高达 {loan_rate*100:.1f}%，刚需买房全在观望，二手房交易中介费跌到谷底！全靠微薄的刚性物业费维持日常电梯与安保运作！"
    elif luo_profit > 320.0:
        luo_status = "thriving"
        luo_s_desc = "楼市租售活跃 · 物业费收缴齐整"
        luo_voice = f"央行降息有效激活二手房交易，买房带看爆满，全国{luo_count}家服务处营收大增！本店日总营收达 {luo_rev:.0f} 块，每天净赚 {luo_profit:.0f} 块！"
    else:
        luo_status = "normal"
        luo_s_desc = "社区物业常态服务"
        luo_voice = f"全国{luo_count}家物业服务处之一。日流水 {luo_rev:.0f} 块，发维修工老谢等人薪资 {luo_wages:.0f} 块，购水暖备件 {luo_parts:.0f} 块，公摊电费 {luo_elevator_power:.0f} 块，净余 {luo_profit:.0f} 块。"

    employers["luo_property"] = {
        "id": "luo_property",
        "name": "罗经理",
        "title": "社区物业服务与房屋租售置业公司总经理",
        "category": "property",
        "category_name": "🏢 居住物业",
        "avatar": "🏢",
        "scale_label": f"全国 {luo_count:,} 个物业服务处之一 · 托管3个小区·员工12人",
        "representative_count": luo_count,
        "income_expense_ratio": luo_r,
        "savings_cushion_months": luo_c,
        "discretionary_propensity": emp_owner_propensity,
        "daily_revenue": luo_rev,
        "daily_expense": round(luo_wages + luo_parts + luo_elevator_power + luo_tax, 1),
        "daily_net": luo_profit,
        "accumulated_funds": luo_funds,
        "financial_status": luo_status,
        "status_desc": luo_s_desc,
        "breakdown": {"工程安保保洁薪资": luo_wages, "水暖电路备件耗材": luo_parts, "电梯与公摊动力电费": luo_elevator_power, "社区综合服务税费": luo_tax},
        "voice": luo_voice,
        "voucher_title": "社区物业管理与置业服务每日收支结算单",
        "voucher_number": f"PROP-{state.day:04d}-515",
        "receipt_lines": [
            {"subject": "业主住宅物业管理服务费集中托收", "from_acc": "社区业主与商户日常银行账户", "to_acc": "社区物业管理服务营运账户", "amount_yuan": luo_prop_fee, "direction": "income", "note": "2800户业主日常保洁、绿化与安保物管费"},
            {"subject": "社区二手房租售与租房中介佣金进项", "from_acc": "房屋买卖双方银行监管账户", "to_acc": "社区物业管理服务营运账户", "amount_yuan": luo_agency_fee, "direction": "income", "note": "刚需房屋流转居间服务佣金"},
            {"subject": "水电维修师傅老谢与安保保洁工资", "from_acc": "社区物业管理服务营运账户", "to_acc": "维修工老谢等在册员工账户", "amount_yuan": luo_wages, "direction": "expense", "note": "12名在册工程维保电工、消控值班员日薪"},
            {"subject": "水暖阀门PVC管道与断路器备件", "from_acc": "社区物业管理服务营运账户", "to_acc": "特大型钢铁联合体 (专户)", "amount_yuan": luo_parts, "direction": "expense", "note": "常备水暖配件与公共区域维修五金"},
            {"subject": "住宅电梯运行与楼道公共照明动力电", "from_acc": "社区物业管理服务营运账户", "to_acc": "国家骨干电网公司 (专户)", "amount_yuan": luo_elevator_power, "direction": "expense", "note": "电梯动力电与小区二次供水水泵用电"}
        ]
    }


    # =========================================================================
    # 👥 第四阶段：全社会 22 大工种真实家庭账本计算 (严格映射全国 1000 万人口)
    # =========================================================================
    citizens: Dict[str, Any] = {}

    for cid, census in CITIZEN_CENSUS.items():
        pop = census["population"]
        m = cit_metrics[cid]
        c_funds = c_pool.get(cid, 5000.0)
        
        inc = m["inc"]
        ess = m["ess"]
        r = m["ratio"]
        c = m["cushion"]
        prop = m["propensity"]
        t_tour = m["tour"]
        t_eat = m["eat"]
        t_app = m["apparel"]
        
        total_exp = round(ess + t_tour + t_eat + t_app, 1)
        net_saved = round(inc - total_exp, 1)

        # 针对每个公民的具体会计凭单行、心声与分类
        if cid == "zhang_miner":
            title, cat, c_name, ava = "煤矿大型井下机电综采掘进工", "mining", "⛏️ 采掘重工", "👷"
            food_item = round(food_price * 1.5, 1)
            b_down = {"高热量口粮": food_item, "井下防尘劳保": 3.5, "自费医药": round(max(1.0, 4.0 * (1.0 - medicare_rate)), 1)}
            if t_eat > 0: b_down["工友加餐堂食"] = t_eat
            if t_app > 0: b_down["耐磨工服成衣"] = t_app
            status = "warning" if food_price > 18.0 else ("thriving" if inc >= 45.0 else "normal")
            s_desc = "菜价肉价高企 · 生活被压榨" if food_price > 18.0 else ("煤矿订单充足 · 收入提升" if inc >= 45.0 else "受雇正常 · 重体力维持")
            voice = f"全国80万采煤工都在指望着电煤销路。今天日薪 {inc:.0f} 块(依法享受80元起征点免征)，收支比 {r:.2f}x，光吃饱饭就吃掉 {food_item:.1f} 块，结存 {net_saved:.1f} 块，必须省吃俭用！"
            v_title = "大型煤矿综采工作面工人日薪发放凭条"
            v_no = f"MINE-{state.day:04d}-012"
            lines = [
                {"subject": "现代化煤矿集团机电采掘日薪进项", "from_acc": "现代化煤矿集团 (专户)", "to_acc": "采矿普工老张储蓄存折", "amount_yuan": inc, "direction": "income", "note": "井下综采割煤机操作在岗日薪"},
                {"subject": "矿区食堂高热量伙食扣除", "from_acc": "采矿普工老张储蓄存折", "to_acc": "粮油食品精炼联合企业 (专户)", "amount_yuan": food_item, "direction": "expense", "note": "矿工三餐高热量面食与肉类"},
                {"subject": "法定个税免征确认 (日薪<80元免税)", "from_acc": "采矿普工老张储蓄存折", "to_acc": "中央政府国库单一账户 (TSA)", "amount_yuan": 0.0, "direction": "expense", "note": "普工日收入低于法定80元/天起征点，个税全免"},
                {"subject": "防尘口罩与劳保靴耗材自负", "from_acc": "采矿普工老张储蓄存折", "to_acc": "轻纺织造日用轻工厂 (专户)", "amount_yuan": 3.5, "direction": "expense", "note": "特种工矿防护服与呼吸耗材"},
                {"subject": "跌打风湿公立医保自费部分", "from_acc": "采矿普工老张储蓄存折", "to_acc": "国家实体企业综合清算总专户", "amount_yuan": round(max(1.0, 4.0 * (1.0 - medicare_rate)), 1), "direction": "expense", "note": f"公立医保报销 {medicare_rate*100:.0f}% 后个人自负"}
            ]

        elif cid == "zhao_builder":
            title, cat, c_name, ava = "基建重大工程泥瓦钢筋散工", "service", "🧱 基建散工", "🧱"
            food_item = round(food_price * 1.3, 1)
            b_down = {"工地大份盒饭": food_item, "彩钢板房床位": 6.0}
            if t_eat > 0: b_down["沿街小吃堂食"] = t_eat
            if t_app > 0: b_down["劳保工装鞋服"] = t_app
            status = "thriving" if infra_daily > 0.08 else ("warning" if infra_daily < 0.01 else "normal")
            s_desc = "重大工程大干快上 · 日结工钱高" if infra_daily > 0.08 else ("工程停滞待料 · 零工不稳定" if infra_daily < 0.01 else "市政标段正常施工")
            voice = f"在吴总工地绑钢筋，代表全国90万基建工人。今天日薪 {inc:.0f} 块，收支比 {r:.2f}x，盒饭扣 {food_item:.1f} 块，工棚 {6.0} 块，每天净存 {net_saved:.1f} 块！"
            v_title = "建工集团施工标段散工日工钱收据条"
            v_no = f"BLD-{state.day:04d}-773"
            lines = [
                {"subject": "市政大桥与水利标段钢筋日工钱", "from_acc": "建工集团项目结算专户", "to_acc": "建筑散工老赵银行存折", "amount_yuan": inc, "direction": "income", "note": "桥梁承台钢筋绑扎施工作业"},
                {"subject": "施工现场流动送餐车大盒饭", "from_acc": "建筑散工老赵银行存折", "to_acc": "国家商贸流通与综合商业 (专户)", "amount_yuan": food_item, "direction": "expense", "note": "两荤一素大米快餐"},
                {"subject": "临时生活区工棚床位费分摊", "from_acc": "建筑散工老赵银行存折", "to_acc": "建工集团项目结算专户", "amount_yuan": 6.0, "direction": "expense", "note": "彩钢板房宿舍床位与热水供应"}
            ]

        elif cid == "zhao_cleaner":
            title, cat, c_name, ava = "市政环境卫生道路清扫与绿化保洁员", "welfare", "🧹 城市环卫", "🧹"
            food_item = round(food_price * 0.75, 1)
            b_down = {"自备清淡口粮": food_item, "环卫公租床位": 10.0, "风湿膏药自费": round(max(1.0, 6.0 * (1.0 - medicare_rate)), 1)}
            status = "warning" if medicare_rate < 0.50 else ("thriving" if min_wage >= 40.0 else "normal")
            s_desc = "医保自费上涨 · 膏药负担重" if medicare_rate < 0.50 else "晨曦扫街保洁常态出勤"
            voice = f"代表全国50万环卫工人，清晨四点半上街扫马路，日薪加津贴 {inc:.1f} 块，收支比 {r:.2f}x。买干粮花 {food_item:.1f} 块，净存 {net_saved:.1f} 块钱给孙子。"
            v_title = "市政环卫作业处道路清扫保洁考勤发薪条"
            v_no = f"SANI-{state.day:04d}-618"
            lines = [
                {"subject": "市政道路清扫法定日薪与晨班津贴", "from_acc": "中央政府国库单一账户 (TSA)", "to_acc": "环卫工赵阿姨薪金储蓄存折", "amount_yuan": inc, "direction": "income", "note": "责任路段清扫保洁劳动报酬"},
                {"subject": "环卫工人爱心驿站集体宿舍床位", "from_acc": "环卫工赵阿姨薪金储蓄存折", "to_acc": "社区物业管理服务营运账户", "amount_yuan": 10.0, "direction": "expense", "note": "公租房廉租床位分摊"},
                {"subject": "平价大米挂面与生活副食采购", "from_acc": "环卫工赵阿姨薪金储蓄存折", "to_acc": "国家商贸流通与综合商业 (专户)", "amount_yuan": food_item, "direction": "expense", "note": "基础温饱干粮采购"}
            ]

        elif cid == "tian_farmer":
            title, cat, c_name, ava = "农村粮食种植自耕农", "agriculture", "🌾 粮田小农", "🌾"
            food_item = round(food_price * 0.7, 1)
            fert_item = round(8.5 * (p_fertilizer / 2100.0), 1)
            b_down = {"化肥农药支出": fert_item, "生活副食品": food_item, "农田灌溉水电": 4.5}
            status = "warning" if p_fertilizer > 2300.0 else ("thriving" if net_saved > 12.0 else "normal")
            s_desc = "化肥涨价 · 种粮利润微薄" if p_fertilizer > 2300.0 else "农家自给自足 · 勤劳耕作"
            voice = f"代表全国160万自耕农家庭。每天交粮折合赚 {inc:.1f} 块，收支比 {r:.2f}x，买化肥花 {fert_item:.1f} 块，口粮副食 {food_item:.1f} 块，净存 {net_saved:.1f} 块。"
            v_title = "供销社原粮售粮交割与农资采购凭条"
            v_no = f"FARM-{state.day:04d}-991"
            lines = [
                {"subject": "粮站原粮交售收购结算款", "from_acc": "国家粮油食品加工联合企业 (专户)", "to_acc": "自耕农老田家庭存款折", "amount_yuan": inc, "direction": "income", "note": "向国家粮库交售水稻原粮结款"},
                {"subject": "高压尿素与复合肥化肥采购款", "from_acc": "自耕农老田家庭存款折", "to_acc": "合成化肥石化集团 (专户)", "amount_yuan": fert_item, "direction": "expense", "note": f"现货价 {p_fertilizer:.0f} 元/吨采购农资"},
                {"subject": "生活副食品采购", "from_acc": "自耕农老田家庭存款折", "to_acc": "国家商贸流通与综合商业 (专户)", "amount_yuan": food_item, "direction": "expense", "note": "采购食盐油料副食品"}
            ]

        elif cid == "xu_farm_driver":
            title, cat, c_name, ava = "大型现代农场联合收割机农机手", "agriculture", "🚜 现代农机", "🚜"
            food_item = round(food_price * 1.2, 1)
            fuel_item = round(6.0 * (p_oil / 520.0), 1)
            b_down = {"农场集体伙食": food_item, "摩托车通勤燃油": fuel_item, "寄老家生活费": 20.0}
            if t_eat > 0: b_down["集镇快餐加餐"] = t_eat
            status = "thriving" if net_saved > 18.0 else "normal"
            s_desc = "规模农业 · 手艺赚钱" if net_saved > 18.0 else "在册农机手稳定受雇"
            voice = f"在钱场长大农场开现代化收割机，代表全国40万专业农机手！每天实打实拿 {inc:.0f} 块日薪，收支比 {r:.2f}x，净存 {net_saved:.1f} 块！"
            v_title = "万亩现代农场农机手劳动薪酬发薪条"
            v_no = f"DRIV-{state.day:04d}-104"
            lines = [
                {"subject": "现代家庭农场收割机驾驶日薪", "from_acc": "现代家庭农场营运户", "to_acc": "农机手小徐银行储蓄卡", "amount_yuan": inc, "direction": "income", "note": "联合收割机在岗操作日薪"},
                {"subject": "农场员工大食堂伙食费扣款", "from_acc": "农机手小徐银行储蓄卡", "to_acc": "现代家庭农场营运户", "amount_yuan": food_item, "direction": "expense", "note": "农忙一日三餐伙食"},
                {"subject": "寄回老家赡养父母汇款", "from_acc": "农机手小徐银行储蓄卡", "to_acc": "农村老家父母养老存折", "amount_yuan": 20.0, "direction": "expense", "note": "邮政储蓄按日划转孝心款"}
            ]

        elif cid == "zhang_elder":
            title, cat, c_name, ava = "农村丧失劳动能力高龄留守老农", "welfare", "👵 养老兜底", "👵"
            food_item = round(food_price * 0.6, 1)
            med_item = round(max(0.5, 4.0 * (1.0 - medicare_rate)), 1)
            b_down = {"日常清淡白粥": food_item, "慢病常备药自费": med_item}
            status = "crisis" if state.social_fund_pool < 120.0 else ("thriving" if net_saved > 3.0 else "normal")
            s_desc = "社保基金枯竭风险" if state.social_fund_pool < 120.0 else "国家社保医保兜底保障"
            voice = f"代表全国40万高龄留守特困老农。一天领基础养老金 {inc:.1f} 块，收支比 {r:.2f}x，吃咸菜稀饭花 {food_item:.1f} 块，药费自费 {med_item:.1f} 块，剩两块防身。"
            v_title = "国家社会保障与公立医保报销发放单"
            v_no = f"PENS-{state.day:04d}-003"
            lines = [
                {"subject": "社保统筹发放农村基础养老金", "from_acc": "国家社会保障与医保统筹专户", "to_acc": "孤寡老人张大娘社保折", "amount_yuan": inc, "direction": "income", "note": "城乡居民基础养老保险金直发"},
                {"subject": "乡村小卖部大米面粉采购", "from_acc": "孤寡老人张大娘社保折", "to_acc": "国家商贸流通与综合商业 (专户)", "amount_yuan": food_item, "direction": "expense", "note": "清淡主食日常开销"},
                {"subject": "卫生院慢病降压药医保自费", "from_acc": "孤寡老人张大娘社保折", "to_acc": "国家实体企业综合清算总专户", "amount_yuan": med_item, "direction": "expense", "note": f"医保报销 {medicare_rate*100:.0f}% 后个人自负"}
            ]

        elif cid == "liu_textile":
            title, cat, c_name, ava = "现代外贸服装流水线平缝车位工", "manufacturing", "🧵 纺织女工", "🧵"
            food_item = round(food_price * 1.0, 1)
            soc_deduct = round(inc * (social_contrib_rate * 0.4), 1)
            b_down = {"食堂刷卡饭卡": food_item, "集体宿舍水电": 5.0, "个人社保代扣": soc_deduct, "寄老家家用": 16.0}
            if t_app > 0: b_down["换季新衣成衣"] = t_app
            
            f_tex_status = getattr(f_textile, "status", "operating") if f_textile else "operating"
            if f_tex_status in ["bankrupt", "suspended"]:
                status = "crisis"
                s_desc = "工厂停工停发绩效 · 轮候待业"
                voice = f"朱老板的制衣厂资金断裂停产了，姐妹们都在厂门口等遣散方案，只能领点基本救济，全家生计太艰难了..."
            elif f_tex_status == "downsizing" or (f_textile and f_textile.daily_laid_off > 0):
                status = "warning"
                s_desc = "车间编制缩减 · 提心吊胆"
                voice = f"制衣厂这阵子订单太差，隔壁车间昨天刚裁了上百个姐妹，每天提心吊胆生怕明天轮到自己，加班计件奖金全停了..."
            elif social_contrib_rate > 0.16:
                status = "warning"
                s_desc = "社保代扣偏多"
                voice = f"在朱老板制衣厂踩缝纫机，代表全国70万纺织女工。日收入 {inc:.0f} 块，收支比 {r:.2f}x，寄老家16块，扣完社保饭钱每天净存 {net_saved:.1f} 块。"
            elif inc > 58.0:
                status = "thriving"
                s_desc = "订单饱满加班多"
                voice = f"外贸订单爆满，每天两班倒踩缝纫机，日薪加计件提成能拿 {inc:.0f} 块！寄老家16块后还能存下 {net_saved:.1f} 块！"
            else:
                status = "normal"
                s_desc = "车间两班倒稳定出工"
                voice = f"在朱老板制衣厂踩缝纫机，代表全国70万纺织女工。日收入 {inc:.0f} 块，收支比 {r:.2f}x，寄老家16块，扣完社保饭钱每天净存 {net_saved:.1f} 块。"
            v_title = "外贸制衣流水线员工日工资结算清单"
            v_no = f"TEXW-{state.day:04d}-215"
            lines = [
                {"subject": "外贸成衣平缝车位计件工资", "from_acc": "轻纺织造日用轻工厂 (专户)", "to_acc": "女工小刘银行储蓄账户", "amount_yuan": inc, "direction": "income", "note": "完成65件出口成衣工序报酬"},
                {"subject": "职工大食堂伙食费扣款", "from_acc": "女工小刘银行储蓄账户", "to_acc": "粮油食品精炼联合企业 (专户)", "amount_yuan": food_item, "direction": "expense", "note": "一日三餐工作餐"},
                {"subject": "个人代扣城镇职工社保", "from_acc": "女工小刘银行储蓄账户", "to_acc": "国家社会保障与医保统筹专户", "amount_yuan": soc_deduct, "direction": "expense", "note": f"按个人费率代扣养老医保金"}
            ]

        elif cid == "guan_food_pack":
            title, cat, c_name, ava = "粮油精炼与食品包装车间操作手", "manufacturing", "🍜 粮油轻工", "🍜"
            food_item = round(food_price * 1.1, 1)
            b_down = {"家庭伙食": food_item, "城郊民房租金": 12.0, "日用洗化采购": 6.0}
            if t_eat > 0: b_down["外食快餐简餐"] = t_eat
            status = "normal"
            s_desc = "国资食品企稳健生产"
            voice = f"在食品加工联合厂上班，代表全国50万快消包装工。每天工资 {inc:.0f} 块，收支比 {r:.2f}x，扣掉房租饭钱，每天稳稳攒下 {net_saved:.1f} 块钱。"
            v_title = "粮油食品加工集团职工发薪与消费清单"
            v_no = f"FOOD-{state.day:04d}-408"
            lines = [
                {"subject": "粮油无菌包装车间标准日薪", "from_acc": "粮油食品精炼联合企业 (专户)", "to_acc": "职工小关银行储蓄账户", "amount_yuan": inc, "direction": "income", "note": "自动面粉包装线主控日薪"},
                {"subject": "家庭基础餐食与副食品支出", "from_acc": "职工小关银行储蓄账户", "to_acc": "国家商贸流通与综合商业 (专户)", "amount_yuan": food_item, "direction": "expense", "note": "购买米面蔬菜"},
                {"subject": "城郊小户型自住租房租金", "from_acc": "职工小关银行储蓄账户", "to_acc": "房东个人储蓄账户", "amount_yuan": 12.0, "direction": "expense", "note": "民房租金按日分摊"}
            ]

        elif cid == "yang_cashier":
            title, cat, c_name, ava = "商超收银员与便利零售理货员", "service", "🛒 商超收银", "🛒"
            food_item = round(food_price * 1.0, 1)
            b_down = {"基础口粮": food_item, "城中村隔断租金": 10.0}
            if t_app > 0: b_down["大众平价成衣"] = t_app
            status = "warning" if net_saved < 8.0 else "normal"
            s_desc = "法定最低日薪保底防线"
            voice = f"在王掌柜超市当收银员，代表全国40万最低日薪从业者。工资 {inc:.1f} 块紧贴底线，收支比 {r:.2f}x，饭钱一扣房租一除，每天剩 {net_saved:.1f} 块。"
            v_title = "社区便民平价超市收银员日结薪资单"
            v_no = f"CASH-{state.day:04d}-302"
            lines = [
                {"subject": "超市收银理货劳动报酬进项", "from_acc": "国家商贸流通与综合商业 (专户)", "to_acc": "收银员小杨银行卡", "amount_yuan": inc, "direction": "income", "note": f"法定最低日薪 {min_wage:.1f} 元足额给付"},
                {"subject": "临期便当与基础口粮采购", "from_acc": "收银员小杨银行卡", "to_acc": "粮油食品精炼联合企业 (专户)", "amount_yuan": food_item, "direction": "expense", "note": "基础生活必需品开销"},
                {"subject": "城中村合租房床位租金分摊", "from_acc": "收银员小杨银行卡", "to_acc": "城中村房东个人账户", "amount_yuan": 10.0, "direction": "expense", "note": "廉价合租房床位支出"}
            ]

        elif cid == "he_kitchen":
            title, cat, c_name, ava = "大众快餐连锁后厨配菜打荷工", "catering", "🍳 快餐打荷", "🍳"
            food_item = round(food_price * 0.45, 1)
            b_down = {"城中村床位租金": 12.0, "老家父母赡养": 18.0, "零碎副食": food_item}
            if t_eat > 0: b_down["休班下馆子"] = t_eat
            status = "warning" if food_price > 18.0 else ("thriving" if net_saved > 12.0 else "normal")
            s_desc = "快餐后厨打荷常态出勤"
            voice = f"在张老板快餐店打荷配菜，代表全国40万后厨帮工。日薪 {inc:.1f} 块，收支比 {r:.2f}x，管饭管水，给老家寄18块，每天净存 {net_saved:.1f} 块！"
            v_title = "大众快餐连锁员工劳动报酬与家庭寄款单"
            v_no = f"EAT-{state.day:04d}-083"
            lines = [
                {"subject": "快餐连锁后厨打荷配菜日薪", "from_acc": "大众便民快餐连锁营运户", "to_acc": "打荷工小何个人银行储蓄卡", "amount_yuan": inc, "direction": "income", "note": "全日配菜洗切劳务报酬"},
                {"subject": "按日汇寄老家农村赡养生活费", "from_acc": "打荷工小何个人银行储蓄卡", "to_acc": "老家父母农村信用社存折", "amount_yuan": 18.0, "direction": "expense", "note": "供养老人与子女花销"},
                {"subject": "城中村员工合租房床位分摊", "from_acc": "打荷工小何个人银行储蓄卡", "to_acc": "城中村房东个人微信账户", "amount_yuan": 12.0, "direction": "expense", "note": "4人合租床位费"}
            ]

        elif cid == "sun_machinist":
            title, cat, c_name, ava = "高级八级数控车铣与精密模具技师", "manufacturing", "🛠️ 工业大工匠", "🛠️"
            food_item = round(food_price * 1.8, 1)
            tax_item = round(max(0.0, inc - 80.0) * (0.08 * max(0.2, income_tax_rate / 0.05)), 1)
            b_down = {"改善型优质餐饮": food_item, "夜校与子女教育": 18.0, "超额累进个税": tax_item, "家庭高品质日用": 22.0}
            if t_tour > 0: b_down["周末家庭近郊文旅"] = t_tour
            if t_eat > 0: b_down["带徒弟聚餐下馆子"] = t_eat
            if t_app > 0: b_down["品牌成衣与家纺"] = t_app
            status = "thriving" if buffs.get("capacity_bonus", 0.0) > 100.0 else "normal"
            s_desc = "车间顶梁柱 · 稳定高薪"
            voice = f"在陈厂长车间当机床大师傅，代表全国40万高技能工匠。日到手 {inc:.0f} 块，享受80元起征点，仅缴累进个税 {tax_item:.1f} 块，收支比高达 {r:.2f}x！供孩子读书无压力，周末还带家人去苏老板客栈度假，净存 {net_saved:.1f} 块！"
            v_title = "精密制造集群高级技师岗位薪酬与生活单"
            v_no = f"TECH-{state.day:04d}-088"
            lines = [
                {"subject": "数控精密五轴加工八级技师日薪", "from_acc": "陈厂长五金机械集群 (专户)", "to_acc": "孙师傅银行储蓄账户", "amount_yuan": inc, "direction": "income", "note": "五轴机床编程与实操带徒日薪"},
                {"subject": "高营养家庭餐饮与生鲜采购", "from_acc": "孙师傅银行储蓄账户", "to_acc": "国家商贸流通与综合商业 (专户)", "amount_yuan": food_item, "direction": "expense", "note": "超市采购高品质肉蛋奶"},
                {"subject": "技工进修夜校与子女教育支出", "from_acc": "孙师傅银行储蓄账户", "to_acc": "国家公立学校与职业院校专户", "amount_yuan": 18.0, "direction": "expense", "note": "高端数控研修班学费"},
                {"subject": "超额累进个税代扣代缴 (80元起征点)", "from_acc": "孙师傅银行储蓄账户", "to_acc": "中央政府国库单一账户 (TSA)", "amount_yuan": tax_item, "direction": "expense", "note": "超出法定80元/天起征点部分超额累进代扣"}
            ]

        elif cid == "liu_truck_driver":
            title, cat, c_name, ava = "跨省大宗干线重型卡车长途驾驶员", "logistics", "🚚 货运司机", "🚚"
            food_item = round(food_price * 2.2, 1)
            b_down = {"高速服务区快餐": food_item, "长途抗疲劳功能饮品": 12.0, "车辆轻微损耗备用": 8.0}
            if t_eat > 0: b_down["返程犒劳聚餐"] = t_eat
            status = "warning" if p_oil > 620.0 else "normal"
            s_desc = "千里奔波 · 安全行车"
            voice = f"开重卡拉电煤跨省跑干线，代表全国35万长途司机。日运单提成 {inc:.0f} 块，收支比 {r:.2f}x，扣完服务区饭钱与红牛，净存 {net_saved:.1f} 块存卡里。"
            v_title = "跨省长途干线货运司机运单结付单"
            v_no = f"TRK-{state.day:04d}-519"
            lines = [
                {"subject": "大宗原材料干线货运运费提成", "from_acc": "干线货运车队结算专户", "to_acc": "卡车司机大刘银行卡", "amount_yuan": inc, "direction": "income", "note": "运送电煤650公里准点运费"},
                {"subject": "高速公路服务区餐饮消费", "from_acc": "卡车司机大刘银行卡", "to_acc": "国家商贸流通与综合商业 (专户)", "amount_yuan": food_item, "direction": "expense", "note": "大盘牛肉饭与两餐热食"},
                {"subject": "红牛功能饮料与提神开销", "from_acc": "卡车司机大刘银行卡", "to_acc": "国家商贸流通与综合商业 (专户)", "amount_yuan": 12.0, "direction": "expense", "note": "安全行车抗疲劳饮品"}
            ]

        elif cid == "jiang_taxi_driver":
            title, cat, c_name, ava = "城市出租车与纯电网约车全职驾驶员", "transport", "🚖 客运的哥", "🚖"
            food_item = round(food_price * 1.1, 1)
            fuel_item = round(22.0 * (p_oil / 520.0 * 0.7 + 0.3 * max(0.65, 1.0 - energy_discount)), 1)
            b_down = {"车队份子管理费": 32.0, "充气快充补能": fuel_item, "路边快餐饮水": food_item}
            if t_eat > 0: b_down["收车宵夜加餐"] = t_eat
            status = "warning" if p_oil > 620.0 else ("thriving" if net_saved > 35.0 else "normal")
            s_desc = "全天出车常态营运"
            voice = f"开纯电网约车跑遍大街小巷，代表全国35万城市司机。日流水 {inc:.0f} 块，收支比 {r:.2f}x，交份子钱32块，充电 {fuel_item:.1f} 块，净存 {net_saved:.1f} 块辛苦钱。"
            v_title = "城市出租网约客运司机每日流水结算单"
            v_no = f"TAXI-{state.day:04d}-728"
            lines = [
                {"subject": "计价器与平台接单乘客车费扫码", "from_acc": "市民大众出行支付扫码专户", "to_acc": "出租车司机蒋师傅结算账户", "amount_yuan": inc, "direction": "income", "note": "全日城区客运综合营运流水"},
                {"subject": "车队车辆管理与保险份子钱", "from_acc": "出租车司机蒋师傅结算账户", "to_acc": "城市出租网约客运车队专户", "amount_yuan": 32.0, "direction": "expense", "note": "陆队长车队营运挂靠管理费"},
                {"subject": "直流快充公用充电桩充电电费", "from_acc": "出租车司机蒋师傅结算账户", "to_acc": "国家油气田开采公司 (专户)", "amount_yuan": fuel_item, "direction": "expense", "note": "全天营运补能电费"}
            ]

        elif cid == "xie_electrician":
            title, cat, c_name, ava = "大型社区综合物业工程维保特种水电工", "property", "🔧 物业水电", "🔧"
            food_item = round(food_price * 1.05, 1)
            b_down = {"自建房生活房租": 16.0, "日常体力伙食": food_item, "电工仪表耗材": 6.0}
            if t_eat > 0: b_down["大众快餐堂食"] = t_eat
            status = "thriving" if net_saved > 28.0 else "normal"
            s_desc = "社区水电排障常态出勤"
            voice = f"修水泵换空开，代表全国30万物业水电工。罗经理发日薪加抢修费共 {inc:.1f} 块，收支比 {r:.2f}x，单间房租16块，伙食 {food_item:.1f} 块，净存 {net_saved:.1f} 块供娃上学！"
            v_title = "社区物业工程部水电维修师傅发薪单"
            v_no = f"ELEC-{state.day:04d}-509"
            lines = [
                {"subject": "专职水电维保日薪与应急抢修费", "from_acc": "社区物业管理服务营运账户", "to_acc": "水电工老谢建行储蓄卡", "amount_yuan": inc, "direction": "income", "note": "泵房维护与高层照明抢修报酬"},
                {"subject": "城中村自建房单间租金支出", "from_acc": "水电工老谢建行储蓄卡", "to_acc": "城中村房东个人微信账户", "amount_yuan": 16.0, "direction": "expense", "note": "日常居住单间租金分摊"},
                {"subject": "重体力作业一日三餐饱腹消费", "from_acc": "水电工老谢建行储蓄卡", "to_acc": "国家商贸流通与综合商业 (专户)", "amount_yuan": food_item, "direction": "expense", "note": "菜市场生鲜副食购买"}
            ]

        elif cid == "li_accountant":
            title, cat, c_name, ava = "民营企业与商贸物流总账会计", "middle_class", "💼 工薪中产", "👨‍💻"
            white_collar_h = next((h for h in state.households if h.id == "white_collar"), None)
            if white_collar_h and white_collar_h.population > 0:
                loan_item = round((getattr(white_collar_h, "daily_mortgage_cost", 0.0) * 100_000_000.0) / white_collar_h.population, 1)
                durable_item = round((getattr(white_collar_h, "daily_durable_cost", 0.0) * 100_000_000.0) / white_collar_h.population, 1)
            else:
                loan_item = round((loan_cost_10k_month * 10.0) / 30.0, 1)
                durable_item = 25.0
            live_item = round(food_price * 2.2 + 20.0, 1)
            tax_item = round(max(0.0, inc - 80.0) * (0.08 * max(0.2, income_tax_rate / 0.05)), 1)
            b_down = {"商业房贷月供": loan_item, "品质耐用品购置": durable_item, "家庭品质生活": live_item, "超额累进个税": tax_item}
            if t_tour > 0: b_down["周末精品文旅客栈"] = t_tour
            if t_eat > 0: b_down["中产餐厅家庭就餐"] = t_eat
            if t_app > 0: b_down["商场精品服饰鞋包"] = t_app
            status = "thriving" if loan_rate < 0.055 else ("warning" if loan_rate > 0.075 else "normal")
            if loan_rate < 0.055:
                s_desc = "央行降息利好 · 房贷大减"
                voice = f"在商贸公司管总账，代表全国50万专业白领家庭。法定80元/天起征点免税很暖心，日薪 {inc:.0f} 块仅缴超额累进个税 {tax_item:.1f} 块；央行降息让日均房贷月供降到 {loan_item:.1f} 块，省下的钱刚换了新家电，净存 {net_saved:.1f} 块！"
            elif loan_rate > 0.075:
                s_desc = "房贷按揭沉重 · 压缩耐用品"
                voice = f"在商贸公司管总账。房贷按揭每天要还 {loan_item:.1f} 块，利息高企压得喘不过气，好在个税有80元起征点庇护，眼巴巴盼着央行降息！"
            else:
                s_desc = "都市白领中产家庭"
                voice = f"在商贸公司管总账，代表全国50万专业白领家庭。日薪 {inc:.0f} 块扣掉80元起征点纳税 {tax_item:.1f} 块，公司账上正把前期亏损结转抵扣所得税，每天稳稳净存 {net_saved:.1f} 块！"
            v_title = "城市中产白领银行按揭还款与完税流水"
            v_no = f"MIDD-{state.day:04d}-550"
            lines = [
                {"subject": "民企总账核算与税务统筹岗位薪资", "from_acc": "国家商贸流通与综合商业 (专户)", "to_acc": "李会计个人银行储蓄专户", "amount_yuan": inc, "direction": "income", "note": "总账报表编制与财务审计薪金"},
                {"subject": "商品房按揭贷款每日月供还本付息", "from_acc": "李会计个人银行储蓄专户", "to_acc": "商业银行住房按揭贷款中心", "amount_yuan": loan_item, "direction": "expense", "note": f"按现行利率基准 {(state.base_interest_rate+0.015)*100:.2f}% 执行20年等额本息月供扣款"},
                {"subject": "超额累进个税代扣代缴 (80元起征点)", "from_acc": "李会计个人银行储蓄专户", "to_acc": "中央政府国库单一账户 (TSA)", "amount_yuan": tax_item, "direction": "expense", "note": "超出法定80元/天起征点部分按超额累进申报个税"},
                {"subject": "家用电器与数码耐用品置换", "from_acc": "李会计个人银行储蓄专户", "to_acc": "陈厂长五金机械集群与高科技芯片企业", "amount_yuan": durable_item, "direction": "expense", "note": "变频空调、冰箱模具五金与电控芯片耐用品更新"},
                {"subject": "品质生活采购与宽带物业费", "from_acc": "李会计个人银行储蓄专户", "to_acc": "国家商贸流通与综合商业 (专户)", "amount_yuan": live_item, "direction": "expense", "note": "超市品质生活采购与日常开销"}
            ]

        elif cid == "lin_it_engineer":
            title, cat, c_name, ava = "工业物联网与MES系统软件实施工程师", "middle_class", "💻 技术白领", "💻"
            food_item = round(food_price * 2.0, 1)
            tax_item = round(max(0.0, inc - 80.0) * (0.08 * max(0.2, income_tax_rate / 0.05)), 1)
            b_down = {"餐饮外卖咖啡": food_item, "青年精装公寓": 32.0, "超额累进个税": tax_item}
            if t_tour > 0: b_down["自驾露营精品度假"] = t_tour
            if t_eat > 0: b_down["网红餐厅外食聚餐"] = t_eat
            if t_app > 0: b_down["科技户外运动服饰"] = t_app
            status = "thriving"
            s_desc = "高薪技术白领 · 率先消费"
            voice = f"在张总科技公司搞智能制造实施，代表全国30万IT技术青年。日薪高达 {inc:.0f} 块，扣除80元起征点仅缴累进个税 {tax_item:.1f} 块，收支比达 {r:.2f}x！周末自驾去苏老板民宿露营喝咖啡，花钱毫无压力，每天稳稳存 {net_saved:.1f} 块！"
            v_title = "软件科技企业技术骨干薪资与税务流水"
            v_no = f"SOFT-{state.day:04d}-919"
            lines = [
                {"subject": "工业MES实施与车间物联网联调日薪", "from_acc": "电子芯片与变电设备集团 (专户)", "to_acc": "工程师小林银行储蓄账户", "amount_yuan": inc, "direction": "income", "note": "工厂制造执行系统现场实施"},
                {"subject": "都市外卖简餐与精品咖啡消费", "from_acc": "工程师小林银行储蓄账户", "to_acc": "国家商贸流通与综合商业 (专户)", "amount_yuan": food_item, "direction": "expense", "note": "工作日商业区精品快餐与咖啡"},
                {"subject": "地铁口青年公寓自住月租分摊", "from_acc": "工程师小林银行储蓄账户", "to_acc": "房东个人储蓄账户", "amount_yuan": 32.0, "direction": "expense", "note": "单身精装公寓日租金"},
                {"subject": "超额累进个税代扣代缴 (80元起征点)", "from_acc": "工程师小林银行储蓄账户", "to_acc": "中央政府国库单一账户 (TSA)", "amount_yuan": tax_item, "direction": "expense", "note": "超出法定80元/天起征点部分超额累进代扣"}
            ]

        elif cid == "zhou_nurse":
            title, cat, c_name, ava = "社区卫生服务站与平价门诊部骨干护士", "medical", "👩‍⚕️ 基层护士", "👩‍⚕️"
            food_item = round(food_price * 1.1, 1)
            b_down = {"家庭生活副食": food_item, "医用防护考培": 8.0, "公租房租金水电": 22.0}
            if t_tour > 0: b_down["假日近郊休闲游"] = t_tour
            if t_eat > 0: b_down["大众餐饮聚餐"] = t_eat
            status = "warning" if medicare_rate < 0.50 else ("thriving" if net_saved > 35.0 else "normal")
            s_desc = "基层医保兜底实 · 绩效津贴足" if net_saved > 35.0 else "社区门诊常态接诊"
            voice = f"在何院长门诊部工作，代表全国35万基层护士。日收入 {inc:.1f} 块，收支比 {r:.2f}x，公租房扣22块，伙食 {food_item:.1f} 块，每天净存 {net_saved:.1f} 块，日子踏实！"
            v_title = "社区卫生服务站基层医护薪酬与绩效表"
            v_no = f"NURS-{state.day:04d}-411"
            lines = [
                {"subject": "社区门诊护理日薪与慢病公卫津贴", "from_acc": "基层平价门诊部营运账户", "to_acc": "周护士个人工商银行储蓄卡", "amount_yuan": inc, "direction": "income", "note": "输液换药、慢病档案随访报酬"},
                {"subject": "公租房租金与生活水电费分摊", "from_acc": "周护士个人工商银行储蓄卡", "to_acc": "社区物业管理服务营运账户", "amount_yuan": 22.0, "direction": "expense", "note": "门诊就近自住公租房租金"},
                {"subject": "日常家庭蔬菜肉蛋主副食品采购", "from_acc": "周护士个人工商银行储蓄卡", "to_acc": "国家商贸流通与综合商业 (专户)", "amount_yuan": food_item, "direction": "expense", "note": "菜市场生鲜果蔬生活开销"}
            ]

        elif cid == "chen_teacher":
            title, cat, c_name, ava = "扎根乡村义务教育特岗骨干教师", "education", "🧑‍🏫 乡村特岗", "🧑‍🏫"
            food_item = round(food_price * 0.85, 1)
            b_down = {"定存国家建设公债": 15.0, "学校食堂伙食": food_item, "自费学生文具": 7.0}
            if t_tour > 0: b_down["寒暑期研学旅游"] = t_tour
            status = "warning" if welfare_daily < 0.08 else ("thriving" if net_saved > 25.0 else "normal")
            s_desc = "财政特岗直达 · 乡村教育稳固" if net_saved > 25.0 else "特岗讲台常态教书育人"
            voice = f"在乡村小学支教，代表全国35万特岗教师。国家统发工资补助 {inc:.1f} 块，收支比 {r:.2f}x，食堂吃饭 {food_item:.1f} 块，自掏腰包买教具，每天净存 {net_saved:.1f} 块买国债！"
            v_title = "中央财政统发特岗义务教育薪酬通知书"
            v_no = f"TEAC-{state.day:04d}-219"
            lines = [
                {"subject": "义务教育特岗薪资与艰苦边远津贴", "from_acc": "中央政府国库单一账户 (TSA)", "to_acc": "乡村特岗陈老师工资直发卡", "amount_yuan": inc, "direction": "income", "note": "国库单一账户统发基础日薪与补贴"},
                {"subject": "认购国家特别建设公债储蓄投资", "from_acc": "乡村特岗陈老师工资直发卡", "to_acc": "中央政府国库单一账户 (TSA)", "amount_yuan": 15.0, "direction": "expense", "note": "支持国家基建长期储蓄国债"},
                {"subject": "学校大灶教工集体伙食扣除", "from_acc": "乡村特岗陈老师工资直发卡", "to_acc": "国家商贸流通与综合商业 (专户)", "amount_yuan": food_item, "direction": "expense", "note": "学校集体伙食基本开销"}
            ]

        elif cid == "lin_expert":
            title, cat, c_name, ava = "国家电网与半导体芯片首席科学家", "middle_class", "🔬 战略科学家", "🔬"
            excess_expert = max(0.0, inc - 80.0)
            if excess_expert <= 100.0:
                tax_item = round(excess_expert * 0.12 * max(0.2, income_tax_rate / 0.05), 1)
            elif excess_expert <= 250.0:
                tax_item = round((100.0 * 0.12 + (excess_expert - 100.0) * 0.22) * max(0.2, income_tax_rate / 0.05), 1)
            else:
                tax_item = round((100.0 * 0.12 + 150.0 * 0.22 + (excess_expert - 250.0) * 0.32) * max(0.2, income_tax_rate / 0.05), 1)
            bond_coupon = round((getattr(state, "sovereign_bond_yield", 0.035) * 80000.0) / 360.0, 1)
            live_item = round(food_price * 2.8 + 45.0, 1)
            b_down = {"顶格超额累进个税": tax_item, "国债财富管理票息": bond_coupon, "高品质家庭生活": live_item}
            if t_tour > 0: b_down["高端度假民宿与研学消费"] = t_tour
            if t_eat > 0: b_down["高档餐厅品鉴就餐"] = t_eat
            if t_app > 0: b_down["高品质面料高端定制服饰"] = t_app
            status = "thriving"
            s_desc = "顶尖工程领军专家 · 率先引领消费"
            voice = f"作为特高压与芯片总工，代表全国15万战略科学家。日薪加津贴 {inc:.0f} 块，依法顶格缴纳累进个税 {tax_item:.1f} 块；手头配置的国家特别国债每天派发稳健票息 {bond_coupon:.1f} 块，每天稳稳净存 {net_saved:.1f} 块！"
            v_title = "国家重点实验室领军科学家薪酬与纳税单"
            v_no = f"SCIE-{state.day:04d}-001"
            lines = [
                {"subject": "总工程师岗位薪资与科研攻关津贴", "from_acc": "国家骨干电网公司 (专户)", "to_acc": "林博士个人银行专户", "amount_yuan": inc, "direction": "income", "note": "特高压换流阀重点攻坚日薪"},
                {"subject": "特别国债理财产品票面利息进项", "from_acc": "中央政府国库单一账户 (TSA)", "to_acc": "林博士个人银行专户", "amount_yuan": bond_coupon, "direction": "income", "note": f"持有国家长期建设公债 (年化发债收益率: {getattr(state, 'sovereign_bond_yield', 0.035)*100:.2f}%)"},
                {"subject": "高收入顶格超额累进个税扣缴", "from_acc": "林博士个人银行专户", "to_acc": "中央政府国库单一账户 (TSA)", "amount_yuan": tax_item, "direction": "expense", "note": "依法顶格代扣高收入群体超额累进个税"},
                {"subject": "高品质家庭生活与耐用品消费", "from_acc": "林博士个人银行专户", "to_acc": "国家商贸流通与综合商业 (专户)", "amount_yuan": live_item, "direction": "expense", "note": "精品超市、私家车保养等生活消费"}
            ]

        elif cid == "zheng_tour_guide":
            title, cat, c_name, ava = "文旅精品度假与研学持证地接导游", "tourism", "🎒 文旅地接", "🎒"
            food_item = round(food_price * 1.15, 1)
            fuel_item = round(9.0 * (p_oil / 520.0), 1)
            b_down = {"带团工作简餐补给": food_item, "景区接驳交通通勤": fuel_item, "导服设备折旧": 8.0}
            status = "warning" if sentiment_index < 25.0 else ("thriving" if net_saved > 28.0 else "normal")
            s_desc = "文旅人气火爆 · 满团带队" if net_saved > 28.0 else "常态化景区接待带团"
            voice = f"带团跑苏老板民宿与景区线路，代表全国10万地接导游。日收入 {inc:.1f} 块，收支比 {r:.2f}x，只要全社会旅游信心高，带团提成就能让净存款冲到 {net_saved:.1f} 块！"
            v_title = "文旅精品客栈与地接服务结算凭条"
            v_no = f"TOUR-{state.day:04d}-337"
            lines = [
                {"subject": "景区地接带团日津贴及提成进项", "from_acc": "精品文旅民宿营运专户", "to_acc": "地接导游小郑个人储蓄卡", "amount_yuan": inc, "direction": "income", "note": "讲解调度与带团服务报酬"},
                {"subject": "随团工作简餐与应急饮用水", "from_acc": "地接导游小郑个人储蓄卡", "to_acc": "国家商贸流通与综合商业 (专户)", "amount_yuan": food_item, "direction": "expense", "note": "景区内便携干粮补给"},
                {"subject": "往返景区大巴燃油接驳分摊", "from_acc": "地接导游小郑个人储蓄卡", "to_acc": "国家油气田与石化销售公司", "amount_yuan": fuel_item, "direction": "expense", "note": "带团交通摆渡燃油费"}
            ]

        elif cid == "zhou_rider":
            title, cat, c_name, ava = "同城即时配送外卖跑腿骑手", "service", "🛵 灵活就业", "🛵"
            food_item = round(food_price * 1.3, 1)
            b_down = {"沿街快餐伙食": food_item, "电瓶无线换电月租": 10.0, "抢单大流量套餐": 5.0}
            status = "warning" if sentiment_index < 25.0 else ("thriving" if inc > 75.0 else "normal")
            s_desc = "消费火热 · 爆单接不过来" if inc > 75.0 else "骑行穿梭大街小巷"
            voice = f"代表全国15万同城跑腿外卖骑手。日收入 {inc:.0f} 块，收支比 {r:.2f}x，只要市民下馆子点外卖多，单子就跑不完，扣完换电每天稳存 {net_saved:.1f} 块！"
            v_title = "同城配送平台骑手每日跑单报酬对账单"
            v_no = f"RIDE-{state.day:04d}-628"
            lines = [
                {"subject": "同城餐饮配送按单提成结算", "from_acc": "国家商贸流通与综合商业 (专户)", "to_acc": "骑手小周银行储蓄账户", "amount_yuan": inc, "direction": "income", "note": "送达42单餐饮与跑腿提成"},
                {"subject": "沿街快餐两荤一素工作餐", "from_acc": "骑手小周银行储蓄账户", "to_acc": "国家商贸流通与综合商业 (专户)", "amount_yuan": food_item, "direction": "expense", "note": "送单间隙快餐补给"},
                {"subject": "动力换电柜电池日租服务费", "from_acc": "骑手小周银行储蓄账户", "to_acc": "国家骨干电网公司 (专户)", "amount_yuan": 10.0, "direction": "expense", "note": "锂电池无限次换电租金"}
            ]

        else: # aqiang_unemployed
            title, cat, c_name, ava = "城镇流动待业青年与失业求职者", "welfare", "🆘 兜底待业", "🆘"
            food_item = round(food_price * 0.9, 1)
            ui_std = getattr(state, "unemployment_relief_standard", 28.0)
            b_down = {"生存红线最低口粮": food_item, "法定失业补助存留": round(max(0.0, ui_std - food_item), 1)}
            status = "crisis" if welfare_daily < 0.08 and ui_std < 20.0 else ("warning" if unemployment_rate > 0.18 else "normal")
            s_desc = "财政低保削减 · 濒临断炊" if (welfare_daily < 0.08 and ui_std < 20.0) else (
                f"失业潮席卷 ({unemployment_rate*100:.1f}%) · 法定救济金托底" if unemployment_rate > 0.18 else "社保失业金托底保障生活"
            )
            voice = f"代表全国流动待业青年与失业求职者。失业率达 {unemployment_rate*100:.1f}%，国家社保安全网每天按 {ui_std:.0f} 块发放法定失业保险金，守住了基本温饱底线！"
            v_title = "街道民政失业低保与困难救济发放凭证"
            v_no = f"WELF-{state.day:04d}-057"
            lines = [
                {"subject": "全国社保基金法定失业保险金直达", "from_acc": "国家社会保障与医保统筹专户", "to_acc": "失业人员阿强救济专用卡", "amount_yuan": round(ui_std, 1), "direction": "income", "note": f"法定失业救济保险金 ({ui_std:.0f}元/天标准)"},
                {"subject": "财政兜底特困转移支付补助", "from_acc": "中央政府国库单一账户 (TSA)", "to_acc": "失业人员阿强救济专用卡", "amount_yuan": round(15.0 * (welfare_daily / 0.15), 1), "direction": "income", "note": "国家低保民生救济金"},
                {"subject": "特价平价挂面馒头采购支出", "from_acc": "失业人员阿强救济专用卡", "to_acc": "粮油食品精炼联合企业 (专户)", "amount_yuan": food_item, "direction": "expense", "note": "一日三餐生存口粮开销"}
            ]

        citizens[cid] = {
            "id": cid,
            "name": census.get("name", title.split("·")[-1] if "·" in title else census["role_desc"][:4]),
            "title": title,
            "category": cat,
            "category_name": c_name,
            "avatar": ava,
            "scale_label": f"代表全国 {pop // 10000}万 {census['role_desc']} · 收支比 {r:.2f}x",
            "representative_count": pop,
            "income_expense_ratio": r,
            "savings_cushion_months": c,
            "discretionary_propensity": prop,
            "daily_revenue": inc,
            "daily_expense": total_exp,
            "daily_net": net_saved,
            "accumulated_funds": c_funds,
            "financial_status": status,
            "status_desc": s_desc,
            "breakdown": b_down,
            "voice": voice,
            "voucher_title": v_title,
            "voucher_number": v_no,
            "receipt_lines": lines
        }

    # =========================================================================
    # 🔄 第五阶段：动态链接企业资本池与居民储蓄池，并检查预警
    # =========================================================================
    for eid, emp in employers.items():
        if eid in e_pool:
            emp["accumulated_funds"] = round(e_pool[eid], 2)
            if emp["accumulated_funds"] < 20.0 and emp["daily_net"] < 0:
                emp["financial_status"] = "crisis"
                emp["status_desc"] = "流动资金濒临枯竭 · 面临破产重组"
                emp["voice"] = f"企业流动资金只剩 {emp['accumulated_funds']:.1f} 万元，每日净亏损 {-emp['daily_net']:.0f} 元，再得不到信贷或订单支持就要倒闭破产了！"
            elif emp["accumulated_funds"] < 50.0 and emp["financial_status"] == "normal":
                emp["financial_status"] = "warning"
                emp["status_desc"] = "营运资金承压预警"
                
    for cid, cit in citizens.items():
        if cid in c_pool:
            cit["accumulated_funds"] = round(c_pool[cid], 1)
            if cit["accumulated_funds"] < 300.0 and cit["daily_net"] < 0:
                cit["financial_status"] = "crisis"
                cit["status_desc"] = "家庭储蓄见底 · 生计濒临断炊"
                cit["voice"] = f"家里银行存款只剩 {cit['accumulated_funds']:.0f} 块钱了，每天入不敷出净亏 {-cit['daily_net']:.1f} 块，米缸快要见底，急需国家救助与就业机会！"
            elif cit["accumulated_funds"] < 1000.0 and cit["financial_status"] == "normal" and cit["daily_net"] < 0:
                cit["financial_status"] = "warning"
                cit["status_desc"] = "抗风险积蓄薄弱预警"

    return {
        "employers": employers,
        "citizens": citizens
    }
