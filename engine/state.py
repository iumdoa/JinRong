"""
国家宏观金融体系模拟器 - 核心状态模型 (Economy State)
"""
from dataclasses import dataclass, field
from typing import Dict, List, Any
import random
from engine.resources import ResourceManager
from engine.commodity import CommodityHub
from engine.labor import LaborManager
from engine.factories import FactoryManager

@dataclass
class HouseholdTier:
    """居民阶层模型"""
    id: str = ""                # 阶层与工种对齐ID ("miner_heavy", "farmer", etc.)
    name: str = ""
    population: int = 0         # 人口数量
    labor_force: int = 0        # 劳动力人口
    employed: int = 0           # 就业人口
    base_wage: float = 0.0      # 日常全职工资 (元/天)
    min_food_cost: float = 0.0  # 每人每日最低生存食物支出 (元/人/天)
    comfort_spending_rate: float = 0.5 # 结余资金的消费倾向 (0~1)
    savings: float = 0.0        # 阶层在商业银行的总储蓄存款 (亿元)
    
    # 动态统计指标
    daily_income: float = 0.0       # 当日总收入 (亿元)
    daily_food_cost: float = 0.0     # 当日食物必需品支出 (亿元)
    daily_other_cost: float = 0.0    # 当日改善型消费支出 (亿元)
    daily_savings_delta: float = 0.0 # 当日新增储蓄/支取储蓄 (亿元)
    
    # Phase 2: 消费金字塔与资产蓄水池
    mortgage_debt: float = 0.0       # 阶层个人存量住房按揭贷款余额 (亿元)
    daily_mortgage_cost: float = 0.0 # 每日房贷还本付息总扣款 (亿元)
    daily_durable_cost: float = 0.0  # 每日耐用消费品更新购置支出 (亿元)
    daily_service_cost: float = 0.0  # 每日现代服务业消费支出 (亿元)
    housing_sqm_owned: float = 0.0   # 阶层人均商品住房拥有面积 (平方米/人)

@dataclass
class FlowRecord:
    """资金流记录（注明：钱从哪来，到哪去）"""
    source: str
    target: str
    amount: float
    category: str
    description: str

@dataclass
class MacroState:
    """国家整体宏观经济与金融状态"""
    # 基础信息与时间
    nation_name: str = "索拉尼亚共和国"
    day: int = 1
    quarter: int = 1
    year: int = 1
    
    # 人口大盘与动态年龄结构 (少儿、适龄劳动、银发退休)
    total_population: int = 10_000_000       # 全国总人口 (1000万人)
    child_population: int = 1_800_000        # 少儿人口 (0~14岁, 18.0%, 基础抚养纯消费)
    working_population: int = 6_500_000      # 适龄劳动人口 (15岁~法定退休年龄, 65.0%, 创税创产)
    retired_population: int = 1_700_000      # 银发退休人口 (法定退休年龄以上, 17.0%, 领养老金享医保)
    retirement_age: int = 60                 # 法定退休年龄 (默认 60 岁，可调 55~68 岁)
    fertility_rate: float = 1.65             # 总和生育率 TFR (国际世代更替标准为 2.1)
    elderly_dependency_ratio: float = 26.2   # 老年抚养比 (%) (退休人口 / 劳动人口 * 100)
    total_dependency_ratio: float = 53.8     # 全社会总抚养比 (%) ((少儿 + 退休) / 劳动人口 * 100)
    birth_rate_annual: float = 10.8          # 年化自然出生率 (‰)
    death_rate_annual: float = 7.2           # 年化自然死亡率 (‰)
    pension_daily_standard: float = 26.5     # 基础养老金平均每日发放标准 (元/人/天)
    child_survival_rate: float = 0.965       # 婴幼儿与少儿成活率 (0~1, 由医疗报销、贫困率、失业与口粮物价决定)
    infant_mortality_rate: float = 35.0      # 年化婴幼儿夭折率 (‰, 1000 - 成活率*1000)
    
    # 六大核心指标 (当前值 & 初始基准值，用于对比)
    gdp_quarterly: float = 0.0         # 本季度累计名义GDP (亿元)
    gdp_annual_runrate: float = 0.0    # 年化整体GDP (亿元)
    gdp_per_capita: float = 0.0        # 年化人均GDP (元)
    engel_coefficient: float = 0.60    # 恩格尔系数 (0~1)
    poverty_rate: float = 0.40         # 贫困人口占比 (0~1)
    unemployment_rate: float = 0.20    # 失业率 (0~1)
    consumer_sentiment: float = 30.0   # 消费意向指数 (0~100)
    
    # 初始指标快照（用于对比打分）
    initial_metrics: Dict[str, float] = field(default_factory=dict)
    
    # 居民部门 (底层贫困层、中产工薪层、富裕资本层)
    households: List[HouseholdTier] = field(default_factory=list)
    poverty_line_daily: float = 20.0   # 每日人均贫困线 (元/人/天)
    
    # 企业部门
    corporate_cash: float = 500.0      # 企业未分配营运现金 (亿元)
    corporate_debt: float = 1200.0     # 企业银行贷款总额 (亿元)
    corporate_capacity: float = 3200.0 # 国家工业与服务总产能上限 (亿元/年)
    firm_daily_revenue: float = 0.0    # 企业当日销售收入 (亿元)
    firm_daily_profit: float = 0.0     # 企业当日净利润 (亿元)
    
    # 商业银行体系与监管
    bank_deposits: float = 4000.0      # 居民与企业总存款 (亿元)
    bank_loans: float = 3000.0         # 贷款存量 (亿元)
    household_mortgage_debt: float = 1600.0 # 全社会居民个人住房按揭贷款余额 (亿元)
    
    # Phase 2: 房地产大盘与消费金字塔蓄水池
    housing_stock_sqm: float = 32000.0        # 全社会商品住宅总存量 (万平方米)
    housing_avg_price: float = 5200.0         # 全国商品住宅均价 (元/平方米)
    daily_housing_sales_sqm: float = 3.5      # 今日商品住宅销售面积 (万平方米/天)
    daily_housing_starts_sqm: float = 3.5     # 今日新开工商品住宅施工面积 (万平方米/天)
    daily_housing_sales_yuan: float = 1.82    # 今日商品房成交总金额 (亿元/天)
    daily_housing_downpayment: float = 0.55   # 今日居民购房首付支出 (亿元/天)
    daily_mortgage_issued: float = 1.27       # 今日商业银行新增个人按揭派生 (亿元/天)
    daily_mortgage_repay_total: float = 0.28  # 今日全社会居民按揭还款总额 (亿元/天)
    daily_durable_spending: float = 0.45      # 今日全社会耐用消费品总支出 (亿元/天)
    daily_service_spending: float = 0.65      # 今日现代服务业与文旅餐饮总支出 (亿元/天)
    mortgage_burden_index: float = 32.5       # 居民房贷按揭压力指数 (%) (月供占可支配收入比)
    durable_penetration_rate: float = 68.0    # 全社会耐用家电汽车普及率 (%)
    
    # 商业银行资产负债与信贷周期中枢 (Phase 3: Basel Capital & Credit Cycle)
    bank_capital: float = 300.0        # 银行自有资本金 (风险准备金与净资产) (亿元)
    bad_debt_rate: float = 0.045       # 银行不良贷款率 (4.5%)
    bank_npl_ratio: float = 4.5        # 不良贷款率百分比 (4.5%)
    bank_npl_loans: float = 135.0      # 全社会不良贷款总额 (亿元)
    bank_provisions_pool: float = 200.0 # 贷款损失准备金资金池 (亿元)
    bank_provision_coverage: float = 148.0 # 拨备覆盖率 (%) (准备金/不良贷款)
    deposit_interest_rate: float = 0.02 # 活期/定期综合年化存款利率 (2.0%)
    loan_interest_rate: float = 0.065   # 商业综合年化基准贷款利率 (6.5%)
    bank_reserve_cash: float = 480.0    # 银行在央行法定准备金总额 (亿元)
    loan_to_deposit_ratio: float = 75.0 # 贷存比 (75.0%)
    capital_adequacy_ratio: float = 10.0# 资本充足率 (CAR, %) (监管红线 8.0%)
    risk_weighted_assets: float = 2200.0# 风险加权资产 (RWA, 亿元)
    credit_crunch_active: bool = False  # 是否触发全社会信贷紧缩风暴 (CAR < 8.0%)
    daily_bank_loan_interest_rev: float = 0.0 # 银行每日贷款利息总收入 (亿元/天)
    daily_bank_deposit_interest_cost: float = 0.0 # 银行每日存款利息总支出 (亿元/天)
    daily_bank_net_interest_margin: float = 0.0 # 每日净息差净收益 (亿元/天)
    daily_bank_provision_deduction: float = 0.0 # 每日计提贷款损失准备金 (亿元/天)
    daily_bank_write_offs: float = 0.0  # 每日司法核销坏账呆账 (亿元/天)
    daily_corporate_loans_issued: float = 0.0 # 每日新增企业信贷投放 (亿元/天)
    daily_corporate_loans_repaid: float = 0.0 # 每日企业正常还款 (亿元/天)
    daily_loans_recalled: float = 0.0   # 每日银行主动风控抽贷总额 (亿元/天)
    corporate_credit_ratings: List[Dict[str, Any]] = field(default_factory=list) # 实体工厂企业信用评级矩阵
    
    # 政府与财政部核算大盘 (关键数据全面罗列)
    treasury_cash: float = 150.0       # 国库现金储备 (亿元)
    national_debt: float = 800.0       # 国债总额 (亿元)
    national_debt_rate: float = 0.035  # 国债年化票面利率 (3.5%)
    fiscal_daily_revenue: float = 1.05 # 当日财政总税收 (亿元/天)
    fiscal_daily_expense: float = 1.08 # 当日财政总支出 (亿元/天)
    fiscal_daily_deficit: float = 0.03 # 当日财政赤字 (亿元/天, 支出-收入)
    deficit_to_gdp_rate: float = 2.8   # 年化财政赤字率 (%) (警戒线 3.0%)
    debt_to_gdp_rate: float = 38.5     # 国债占GDP比重 / 债务率 (%) (警戒线 60%)
    tax_breakdown: Dict[str, float] = field(default_factory=dict)     # 税收结构
    expense_breakdown: Dict[str, float] = field(default_factory=dict) # 支出结构

    # Phase 5: 现代公共财政、主权信用评级与安全网大盘
    sovereign_credit_rating: str = "AAA"       # 国家主权信用评级 (AAA ~ D)
    sovereign_risk_spread: float = 0.0         # 主权信用违约风险息差 (基点折算，例如 +1.5%)
    sovereign_bond_yield: float = 0.035        # 国债实际综合收益率 (票面发债利率)
    national_debt_limit: float = 2000.0        # 国家法定国债发行上限 (亿元)
    corp_tax_loss_carry_forward: float = 0.0   # 实体企业亏损结转抵扣池 (亿元，支持后续盈利免税抵扣)
    progressive_tax_stats: Dict[str, Any] = field(default_factory=dict) # 综合超额累进个税征缴实况
    counter_cyclical_boost_active: bool = False # 财政逆周期基建托底与救济激活状态
    unemployment_relief_standard: float = 28.0 # 法定失业救济低保标准 (元/天/人)
    
    # 实体经济生产指标
    capacity_utilization_rate: float = 85.0 # 实体工业与服务产能利用率 (%)
    
    # 玩家日常控制把手 (9大宏观政策杠杆)
    # 1. 货币政策
    base_interest_rate: float = 0.040  # 央行基准利率 (4.0%)
    reserve_ratio: float = 0.12        # 法定存款准备金率 (12%)
    # 2. 财政与税收政策
    corp_tax_rate: float = 0.18        # 企业所得税率 (18%)
    vat_tax_rate: float = 0.08         # 增值与终端消费税率 (8%)
    income_tax_rate: float = 0.05      # 居民综合个人所得税率 (5%)
    # 3. 支出与民生保障政策
    gov_daily_spending: float = 0.75   # 政府日常公用及行政开支 (亿元/天)
    welfare_spending: float = 0.15     # 兜底低保与失业救济金 (亿元/天)
    min_wage_daily: float = 36.0       # 国家法定最低日薪标准 (元/天)
    # 4. 人口与代际调控杠杆
    # retirement_age: int = 60 (已在上方声明，默认 60 岁，可调 55~68 岁)
    
    # 国家社会保险与公立医保服务大盘 (社保医保制度)
    medicare_reimburse_rate: float = 0.65 # 公立医保统筹报销比例 (默认65%, 可调40%~90%)
    social_contrib_rate: float = 0.12     # 综合社保与养老统筹费率 (默认12%, 可调6%~22%)
    social_fund_pool: float = 450.0       # 全国社保医保基金滚存结余 (亿元)
    social_daily_revenue: float = 0.28    # 每日社保基金征缴总收入 (亿元/天)
    social_daily_payout: float = 0.25     # 每日医保报销支付与养老金发放 (亿元/天)
    social_daily_balance: float = 0.03    # 每日社保基金净结余 (亿元/天)
    social_daily_gov_subsidy: float = 0.05# 财政对社保基金的定向补助与利息 (亿元/天)
    
    # 实体基建与重大工程财政结算
    infra_daily_spending: float = 0.0        # 当日所有在建工程与科研划拨总额 (亿元/天)
    infra_maintenance_spending: float = 0.0  # 当日已竣工各类工程与校舍运维管养总开支 (亿元/天)
    
    # 国家教育与科研能力体系 (高校科研所与专项科研经费资助)
    base_research_capability: float = 45.0   # 国家基准科研攻关能力 (0~100 点)
    research_capability: float = 45.0        # 国家综合科研能力 (0~100 点)
    school_count: int = 150                 # 全国各级公立学校与高校科研所数量 (初始 150 所)
    active_research_grant: Dict[str, Any] = field(default_factory=dict) # 当前生效的科研经费专款 (到期加持消失)
    
    # 微观民生与日常生活看板 (真实的柴米油盐)
    food_basket_price: float = 15.0    # 一日基础标准口粮/便当物价 (元/份)
    cpi_index: float = 100.0           # 居民消费价格指数 (基期 100)
    loan_cost_per_10k_month: float = 54.2 # 每借1万元每月利息 (元/月)
    deposit_yield_per_10k_year: float = 200.0 # 每存1万元每年利息 (元/年)
    
    # 三大代表人物画像 (具象化微观个体，兼容保留)
    persona_worker: Dict[str, Any] = field(default_factory=dict) # 底层普工·老张
    persona_middle: Dict[str, Any] = field(default_factory=dict) # 工薪中产·李会计
    persona_boss: Dict[str, Any] = field(default_factory=dict)   # 实体小微·陈厂长
    
    # 全景微观真实账本矩阵持久化资金池 (真实逐日滚存，拒绝静态写死)
    citizen_savings_pool: Dict[str, float] = field(default_factory=dict)  # 22类国民个人储蓄存折 (元)
    employer_capital_pool: Dict[str, float] = field(default_factory=dict) # 15位产业资本企业存款 (万元)
    citizen_census: Dict[str, Any] = field(default_factory=dict)          # 全国人口普查矩阵 (1000万人严格闭环)
    employer_census: Dict[str, Any] = field(default_factory=dict)         # 全国实体商业与工业企业普查 (98,300家实体)
    employers_ledger: Dict[str, Any] = field(default_factory=dict)
    citizens_ledger: Dict[str, Any] = field(default_factory=dict)
    
    # 政策公信力机制 (朝令夕改惩罚与十年稳健长效培养)
    policy_credibility: float = 75.0   # 政策公信力 (0~100)
    last_policy_change_day: int = -90  # 上次调整政策的天数
    policy_change_count: int = 0       # 调整次数
    
    # 游戏难度模式与剧本
    difficulty_mode: str = "frugal"    # "standard" | "frugal" | "crisis"
    difficulty_name: str = "艰难求生 (孟加拉型 · 量入为出)"
    
    # 当日资金流动穿透流水明细
    daily_flows: List[FlowRecord] = field(default_factory=list)
    quarterly_flow_summary: Dict[str, float] = field(default_factory=dict)
    
    # 宏观经济学理论因果链记录 (给玩家学习的经济学机制)
    active_theory_insights: List[Dict[str, str]] = field(default_factory=list)
    citizen_voices: List[Dict[str, str]] = field(default_factory=list)
    
    # 季度历史统计
    quarterly_history: List[Dict[str, Any]] = field(default_factory=list)

    # 极度硬核：探明地质储量、大宗实物物资中枢、实体工厂矩阵与技能劳动力
    resources: Dict[str, Any] = field(default_factory=dict)
    commodities: Dict[str, Any] = field(default_factory=dict)
    market_clearing_summary: Dict[str, Any] = field(default_factory=dict)
    factories: Dict[str, Any] = field(default_factory=dict)
    labor_market: Dict[str, Any] = field(default_factory=dict)
    foreign_reserves_usd: float = 25.0 # 国家主权外汇储备 (亿美元)
    exchange_rate: float = 7.20        # 官方指导汇率 (本币/美元)
    exchange_rate_baseline: float = 7.20 # 基准平价汇率 (7.20)
    
    # 国际收支平衡表与外汇机制 (Phase 4: Balance of Payments & Dutch Disease)
    bop_current_account_usd: float = 0.0 # 当日经常账户净收支 (出口 - 进口) (亿美元)
    bop_exports_usd: float = 0.0         # 当日全口径出口创汇 (亿美元)
    bop_imports_usd: float = 0.0         # 当日全口径进口耗汇 (亿美元)
    bop_trade_surplus_cny: float = 0.0   # 当日贸易顺差本币折算值 (亿元)
    fx_sterilization_ratio: float = 0.0  # 主权外汇冲销比例 (0.0~0.8, 吸收多余美元防汇率过快升值)
    sovereign_wealth_fund_usd: float = 0.0 # 海外主权财富投资基金池 (亿美元)
    swf_daily_yield_usd: float = 0.0     # 海外主权财富基金每日投资收益 (亿美元)
    manufacturing_competitiveness_index: float = 100.0 # 制造业出口价格竞争力指数 (基期 100.0)
    dutch_disease_active: bool = False   # 荷兰病警报：大宗过度出口致本币过快升值，反噬轻工制造
    anti_dumping_tariffs: Dict[str, float] = field(default_factory=dict) # 海外反倾销惩罚性关税率
    commodity_export_quotas: Dict[str, float] = field(default_factory=dict) # 各商品国际市场配额容量与消耗度


def create_country_state(mode: str = "frugal", seed: int = 42) -> MacroState:
    """
    根据剧本难度生成初始世界状态：
    - 'standard': 🟢 标准新兴模式 (印尼/肯尼亚型 · 稳步繁荣，收支约1.0亿，适合新手)
    - 'frugal': 🟡 艰难求生模式 (孟加拉型 · 稳态量入为出，收支约0.52亿，核心拟真默认)
    - 'crisis': 🔴 深渊拆弹模式 (斯里兰卡型 · 债务危局，日亏0.62亿，200天倒计时)
    """
    rng = random.Random(seed)
    total_pop = 10_000_000
    
    if mode == "standard":
        nation_name = "阿维拉联邦"
        diff_name = "标准新兴 (肯尼亚型 · 稳步繁荣)"
        
        households = [
            HouseholdTier(id="miner_heavy", name="采矿与重体力劳工 (老张主力)", population=2_000_000, labor_force=1_300_000, employed=1_100_000, base_wage=56.0, min_food_cost=16.0, comfort_spending_rate=0.80, savings=450.0, mortgage_debt=0.0, housing_sqm_owned=22.0),
            HouseholdTier(id="farmer", name="农耕自耕农与种植散工", population=2_200_000, labor_force=1_320_000, employed=1_180_000, base_wage=48.0, min_food_cost=15.0, comfort_spending_rate=0.75, savings=550.0, mortgage_debt=0.0, housing_sqm_owned=26.0),
            HouseholdTier(id="operator_light", name="轻工制造流水线操作工", population=2_200_000, labor_force=1_360_000, employed=1_250_000, base_wage=75.0, min_food_cost=18.0, comfort_spending_rate=0.70, savings=850.0, mortgage_debt=120.0, housing_sqm_owned=28.0),
            HouseholdTier(id="technician_skilled", name="熟练数控车铣技工 (陈厂长顶梁柱)", population=1_600_000, labor_force=1_040_000, employed=1_000_000, base_wage=165.0, min_food_cost=24.0, comfort_spending_rate=0.60, savings=1600.0, mortgage_debt=450.0, housing_sqm_owned=35.0),
            HouseholdTier(id="white_collar", name="白领财务、管理与商业文职 (李会计主力)", population=1_400_000, labor_force=870_000, employed=840_000, base_wage=150.0, min_food_cost=25.0, comfort_spending_rate=0.55, savings=2200.0, mortgage_debt=1050.0, housing_sqm_owned=42.0),
            HouseholdTier(id="engineer_expert", name="工业电气工程师与科研专家", population=600_000, labor_force=360_000, employed=350_000, base_wage=380.0, min_food_cost=36.0, comfort_spending_rate=0.40, savings=1800.0, mortgage_debt=480.0, housing_sqm_owned=55.0),
        ]
        
        corp_capacity = rng.uniform(3600.0, 4000.0)
        corp_cash = rng.uniform(750.0, 850.0)
        corp_debt = rng.uniform(950.0, 1100.0)
        treasury_cash = rng.uniform(230.0, 270.0)
        national_debt = rng.uniform(900.0, 1000.0)
        vat_tax = 0.10
        corp_tax = 0.20
        income_tax = 0.07
        gov_spending = 0.60
        welfare_spending = 0.18
        social_subsidy = 0.08
        min_wage = 48.0
        policy_cred = 82.0
        foreign_reserves = 45.0
        
    elif mode == "crisis":
        nation_name = "埃尔瓦尔多共和国"
        diff_name = "深渊拆弹 (斯里兰卡型 · 债务危局)"
        
        households = [
            HouseholdTier(id="miner_heavy", name="采矿与重体力劳工 (老张主力)", population=2_400_000, labor_force=1_560_000, employed=950_000, base_wage=34.0, min_food_cost=13.0, comfort_spending_rate=0.85, savings=100.0, mortgage_debt=0.0, housing_sqm_owned=15.0),
            HouseholdTier(id="farmer", name="农耕自耕农与种植散工", population=2_500_000, labor_force=1_500_000, employed=1_200_000, base_wage=30.0, min_food_cost=12.0, comfort_spending_rate=0.80, savings=150.0, mortgage_debt=0.0, housing_sqm_owned=18.0),
            HouseholdTier(id="operator_light", name="轻工制造流水线操作工", population=2_100_000, labor_force=1_300_000, employed=1_040_000, base_wage=46.0, min_food_cost=14.5, comfort_spending_rate=0.70, savings=280.0, mortgage_debt=60.0, housing_sqm_owned=22.0),
            HouseholdTier(id="technician_skilled", name="熟练数控车铣技工 (陈厂长顶梁柱)", population=1_300_000, labor_force=840_000, employed=750_000, base_wage=98.0, min_food_cost=19.0, comfort_spending_rate=0.60, savings=550.0, mortgage_debt=280.0, housing_sqm_owned=28.0),
            HouseholdTier(id="white_collar", name="白领财务、管理与商业文职 (李会计主力)", population=1_300_000, labor_force=800_000, employed=720_000, base_wage=92.0, min_food_cost=20.0, comfort_spending_rate=0.55, savings=1200.0, mortgage_debt=720.0, housing_sqm_owned=32.0),
            HouseholdTier(id="engineer_expert", name="工业电气工程师与科研专家", population=400_000, labor_force=240_000, employed=230_000, base_wage=240.0, min_food_cost=30.0, comfort_spending_rate=0.40, savings=800.0, mortgage_debt=280.0, housing_sqm_owned=40.0),
        ]
        
        corp_capacity = rng.uniform(2300.0, 2500.0)
        corp_cash = rng.uniform(450.0, 520.0)
        corp_debt = rng.uniform(1150.0, 1250.0)
        treasury_cash = rng.uniform(115.0, 130.0)
        national_debt = rng.uniform(860.0, 920.0)
        vat_tax = 0.08
        corp_tax = 0.18
        income_tax = 0.05
        gov_spending = 0.85  # 行政开支严重臃肿!
        welfare_spending = 0.15
        social_subsidy = 0.05
        min_wage = 36.0
        policy_cred = 60.0   # 公信力低迷
        foreign_reserves = 8.5 # 外汇储备告急
        
    else: # "frugal" (核心默认推荐剧本)
        mode = "frugal"
        nation_name = "索拉尼亚共和国"
        diff_name = "艰难求生 (孟加拉型 · 量入为出)"
        
        households = [
            HouseholdTier(id="miner_heavy", name="采矿与重体力劳工 (老张主力)", population=2_200_000, labor_force=1_430_000, employed=1_030_000, base_wage=38.0, min_food_cost=13.5, comfort_spending_rate=0.85, savings=140.0, mortgage_debt=0.0, housing_sqm_owned=18.0),
            HouseholdTier(id="farmer", name="农耕自耕农与种植散工", population=2_400_000, labor_force=1_440_000, employed=1_220_000, base_wage=32.0, min_food_cost=12.0, comfort_spending_rate=0.80, savings=200.0, mortgage_debt=0.0, housing_sqm_owned=22.0),
            HouseholdTier(id="operator_light", name="轻工制造流水线操作工", population=2_000_000, labor_force=1_240_000, employed=1_090_000, base_wage=52.0, min_food_cost=15.0, comfort_spending_rate=0.70, savings=350.0, mortgage_debt=80.0, housing_sqm_owned=25.0),
            HouseholdTier(id="technician_skilled", name="熟练数控车铣技工 (陈厂长顶梁柱)", population=1_400_000, labor_force=910_000, employed=855_000, base_wage=115.0, min_food_cost=20.0, comfort_spending_rate=0.60, savings=700.0, mortgage_debt=320.0, housing_sqm_owned=32.0),
            HouseholdTier(id="white_collar", name="白领财务、管理与商业文职 (李会计主力)", population=1_500_000, labor_force=930_000, employed=855_000, base_wage=105.0, min_food_cost=22.0, comfort_spending_rate=0.55, savings=1600.0, mortgage_debt=850.0, housing_sqm_owned=38.0),
            HouseholdTier(id="engineer_expert", name="工业电气工程师与科研专家", population=500_000, labor_force=300_000, employed=291_000, base_wage=280.0, min_food_cost=32.0, comfort_spending_rate=0.40, savings=1100.0, mortgage_debt=350.0, housing_sqm_owned=48.0),
        ]
        
        corp_capacity = rng.uniform(2300.0, 2500.0)
        corp_cash = rng.uniform(450.0, 520.0)
        corp_debt = rng.uniform(1150.0, 1250.0)
        treasury_cash = rng.uniform(145.0, 160.0)
        national_debt = rng.uniform(780.0, 820.0)
        vat_tax = 0.08
        corp_tax = 0.18
        income_tax = 0.05
        gov_spending = 0.24  # 精简公用行政采购，量入为出稳态！
        welfare_spending = 0.15
        social_subsidy = 0.05
        min_wage = 36.0
        policy_cred = 75.0
        foreign_reserves = 25.0
    
    state = MacroState(
        nation_name=nation_name,
        difficulty_mode=mode,
        difficulty_name=diff_name,
        total_population=total_pop,
        households=households,
        corporate_cash=corp_cash,
        corporate_debt=corp_debt,
        corporate_capacity=corp_capacity,
        bank_deposits=sum(h.savings for h in households) + corp_cash + 450.0,
        household_mortgage_debt=round(sum(h.mortgage_debt for h in households), 1),
        bank_loans=round(corp_debt + sum(h.mortgage_debt for h in households), 1),
        bank_capital=round(rng.uniform(280.0, 320.0), 1),
        bad_debt_rate=round(rng.uniform(0.042, 0.048), 4),
        treasury_cash=treasury_cash,
        national_debt=national_debt,
        base_interest_rate=0.04,
        reserve_ratio=0.12,
        corp_tax_rate=corp_tax,
        vat_tax_rate=vat_tax,
        income_tax_rate=income_tax,
        gov_daily_spending=gov_spending,
        welfare_spending=welfare_spending,
        social_daily_gov_subsidy=social_subsidy,
        min_wage_daily=min_wage,
        policy_credibility=policy_cred,
        foreign_reserves_usd=foreign_reserves,
        research_capability=12.0,
        school_count=150,
    )
    
    # 计算初始指标并固化初始基准
    total_labor = sum(h.labor_force for h in households)
    total_employed = sum(h.employed for h in households)
    state.unemployment_rate = 1.0 - (total_employed / total_labor)
    low_pop = households[0].population + households[1].population
    state.poverty_rate = low_pop / total_pop # 底层全处于贫困线边缘
    state.engel_coefficient = 0.58           # 困难国家标准高恩格尔
    state.gdp_annual_runrate = 3800.0 if mode == "standard" else 2300.0
    state.gdp_per_capita = (state.gdp_annual_runrate * 100_000_000) / total_pop
    
    # 初始化初始财政收支明细与宏观赤字率
    daily_debt_interest = (state.national_debt * (0.045 if mode == "crisis" else 0.035)) / 360.0
    init_expense = state.gov_daily_spending + state.welfare_spending + state.social_daily_gov_subsidy + daily_debt_interest
    if mode == "standard":
        init_revenue = 1.05
        init_vat, init_income, init_corp = 0.48, 0.42, 0.15
    elif mode == "crisis":
        init_revenue = 0.51
        init_vat, init_income, init_corp = 0.26, 0.23, 0.02
    else: # frugal
        init_revenue = 0.52
        init_vat, init_income, init_corp = 0.26, 0.24, 0.02
    init_deficit = init_expense - init_revenue

    state.fiscal_daily_revenue = round(init_revenue, 4)
    state.fiscal_daily_expense = round(init_expense, 4)
    state.fiscal_daily_deficit = round(init_deficit, 4)
    state.deficit_to_gdp_rate = round((init_deficit * 360.0 / state.gdp_annual_runrate) * 100.0, 2)
    state.debt_to_gdp_rate = round((state.national_debt / state.gdp_annual_runrate) * 100.0, 1)
    state.tax_breakdown = {
        "corp_tax": round(init_corp, 3),
        "vat_tax": round(init_vat, 3),
        "income_tax": round(init_income, 3)
    }
    state.expense_breakdown = {
        "gov_works": round(state.gov_daily_spending, 3),
        "welfare": round(state.welfare_spending, 3),
        "infra_projects": 0.0,
        "infra_maintenance": 0.0,
        "medicare_subsidy": round(state.social_daily_gov_subsidy, 3),
        "debt_interest": round(daily_debt_interest, 3)
    }

    # 主权信用评级与国债收益率初始化
    state.sovereign_credit_rating = "AAA" if mode == "standard" else ("AA" if mode == "frugal" else "BBB")
    state.sovereign_risk_spread = 0.0 if mode == "standard" else (0.005 if mode == "frugal" else 0.015)
    state.sovereign_bond_yield = round(state.base_interest_rate + state.sovereign_risk_spread, 4)
    state.national_debt_rate = state.sovereign_bond_yield
    state.national_debt_limit = round(state.gdp_annual_runrate * 0.75, 1) # 75% 警戒上限
    state.corp_tax_loss_carry_forward = 0.0
    state.counter_cyclical_boost_active = False
    state.unemployment_relief_standard = 28.0
    state.total_population = total_pop
    state.child_population = int(total_pop * 0.18)      # 180万人 (18.0%)
    state.working_population = int(total_pop * 0.65)    # 650万人 (65.0%)
    state.retired_population = total_pop - state.child_population - state.working_population # 170万人 (17.0%)
    state.retirement_age = 60
    state.fertility_rate = 1.65
    state.elderly_dependency_ratio = round((state.retired_population / max(1, state.working_population)) * 100.0, 1)
    state.total_dependency_ratio = round(((state.child_population + state.retired_population) / max(1, state.working_population)) * 100.0, 1)
    state.birth_rate_annual = 10.8
    state.death_rate_annual = 7.2
    state.pension_daily_standard = 26.5
    state.child_survival_rate = 0.965
    state.infant_mortality_rate = 35.0
    state.base_research_capability = 45.0
    state.research_capability = 45.0
    state.household_mortgage_debt = 1600.0
    
    state.citizen_savings_pool = {
        "tian_farmer": 4500.0,
        "xu_farm_driver": 7200.0,
        "zhang_miner": 5500.0,
        "zhao_builder": 4800.0,
        "liu_textile": 6200.0,
        "guan_food_pack": 6800.0,
        "sun_machinist": 18000.0,
        "liu_truck_driver": 12000.0,
        "yang_cashier": 3800.0,
        "zhou_rider": 4200.0,
        "li_accountant": 42000.0,
        "lin_it_engineer": 65000.0,
        "lin_expert": 180000.0,
        "aqiang_unemployed": 800.0,
        "zhang_elder": 3200.0,
        "he_kitchen": 5200.0,
        "zheng_tour_guide": 4800.0,
        "zhou_nurse": 15000.0,
        "chen_teacher": 18000.0,
        "jiang_taxi_driver": 8500.0,
        "xie_electrician": 9200.0,
        "zhao_cleaner": 2400.0
    }
    state.employer_capital_pool = {
        "qian_farm": 180.0,
        "sun_coal": 450.0,
        "chen_machinery": 320.0,
        "zhu_textile": 260.0,
        "wu_construction": 280.0,
        "wei_logistics": 350.0,
        "wang_retail": 120.0,
        "zhang_tech": 580.0,
        "gao_bank": 1200.0,
        "zhang_catering": 150.0,
        "su_tourism": 180.0,
        "he_clinic": 320.0,
        "liang_training": 160.0,
        "lu_taxi_fleet": 220.0,
        "luo_property": 550.0
    }
    from engine.personas import CITIZEN_CENSUS, EMPLOYER_CENSUS
    state.citizen_census = CITIZEN_CENSUS
    state.employer_census = EMPLOYER_CENSUS
    
    state.initial_metrics = {
        "annual_gdp": state.gdp_annual_runrate,
        "gdp_per_capita": state.gdp_per_capita,
        "engel_coefficient": state.engel_coefficient,
        "poverty_rate": state.poverty_rate,
        "unemployment_rate": state.unemployment_rate,
        "consumer_sentiment": state.consumer_sentiment,
        "treasury_cash": state.treasury_cash,
        "bad_debt_rate": state.bad_debt_rate,
        "research_capability": state.research_capability,
        "school_count": state.school_count,
        "food_basket_price": 15.0,
        "loan_cost_per_10k": 54.2,
        "deposit_yield_per_10k": 200.0,
        "fertility_rate": state.fertility_rate,
        "retirement_age": state.retirement_age,
        "elderly_dependency_ratio": state.elderly_dependency_ratio
    }
    
    # 初始化三大具象化代表人物画像
    state.persona_worker = {
        "name": "老张",
        "identity": "底层劳工·建筑零工 (代表420万底层群众)",
        "daily_income": 38.0,
        "food_expense": 24.5,
        "disposable_left": 13.5,
        "savings": 140.0,
        "employment_status": "受雇中 (零工不稳定)",
        "voice": "每天干完重体力活，拿到38块钱，光填饱肚子买米买菜就去了24块5。手头就剩十几块，生怕哪天工地上停工没饭吃。"
    }
    
    state.persona_middle = {
        "name": "李会计",
        "identity": "工薪中产·民企职员 (代表480万中产家庭)",
        "daily_income": 105.0,
        "loan_interest_daily": 18.2,   # 房贷消费贷还息
        "living_expense": 58.0,
        "savings": 2000.0,
        "employment_status": "稳定雇佣",
        "voice": "每天到手105块，房贷利息一天就要分摊扣掉18块多！真希望央行能降息，只要贷款利息降一点，我们家下个月就能给孩子多报个补习班。"
    }
    
    state.persona_boss = {
        "name": "陈厂长",
        "identity": "实体小微·机械五金制造厂 (代表企业与投资)",
        "daily_revenue": 1200.0,
        "daily_wages_paid": 720.0,
        "daily_energy_cost": 160.0,    # 动力电费与机油耗材
        "daily_loan_interest": 180.0,  # 银行贷款利息
        "daily_tax_paid": 30.0,        # 企业所得税
        "daily_profit": 110.0,
        "willingness_to_expand": "正常运营",
        "voice": "日营收1200块，付工人工资720块，动力电费160块，还利息180块，净利润110块。电费和利息都不少，盼着电网升级降电价！"
    }
    
    state.active_theory_insights = [
        {
            "school": "【发展经济学·低水平均衡陷阱 (Poverty Trap)】",
            "core": "在无外生强力干预时，困难国家会长期锁定在'贫困-低储蓄-低投资'的封闭循环。",
            "causality": "老张收入仅够糊口无储蓄 ➔ 银行资本金浅 ➔ 陈老板借贷成本高无法扩产 ➔ 系统保持低水平动态稳态。"
        }
    ]
    
    state.citizen_voices = [
        {"author": "老张 (底层劳工)", "text": "物价千万别再涨了，这年头只要菜价涨一块钱，我晚上就得少吃一个窝头。"},
        {"author": "李会计 (工薪中产)", "text": "房贷月供压得喘不过气，全家眼巴巴盼着央行降息。"},
        {"author": "陈厂长 (实体老板)", "text": "开厂利润比纸还薄，税负和利息两座大山压在头上，不敢招人。"}
    ]
    
    # 极度硬核：探明地质储量、大宗实物物资中枢、实体工厂矩阵与技能劳动力初始挂载
    res_mgr = ResourceManager(rng_seed=seed)
    comm_hub = CommodityHub()
    fac_mgr = FactoryManager()
    labor_mgr = LaborManager(total_population=total_pop)
    
    state.resources = res_mgr.to_dict()
    state.commodities = comm_hub.to_dict()
    state.factories = fac_mgr.to_dict()
    state.labor_market = labor_mgr.to_dict()
    
    return state

def create_difficult_country_state(seed: int = 42) -> MacroState:
    """向下兼容原有调用，默认采用艰难求生量入为出稳态模式"""
    return create_country_state(mode="frugal", seed=seed)
