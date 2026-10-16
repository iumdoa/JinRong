"""
国家十大实体工厂门类体系与投入产出生产函数矩阵
涵盖采矿、电力、重工冶炼、化肥建材、陈厂长通用五金机械、轻纺食品及芯片高精尖厂
"""
from dataclasses import dataclass, field
from typing import Dict, Any, List, Tuple
from engine.resources import ResourceManager
from engine.commodity import CommodityHub
from engine.labor import LaborManager

def get_commodity_value_in_yi(cid: str, amount: float, unit_price: float) -> float:
    """计算实物数量对应的货币价值 (亿元)"""
    if cid == "electricity":
        return amount * unit_price
    elif cid in ["heavy_machinery", "power_equipment"]:
        return (amount * unit_price) / 100_000_000.0
    else:
        return (amount * unit_price) / 10_000.0

# 大宗物资标准工业供给企业映射表 (用于B2B中间品记账结算)
COMMODITY_SUPPLIER_MAP = {
    "coal": ("corp_coal_mine", "现代化煤矿集团 (专户)"),
    "iron_ore": ("corp_iron_mine", "大型铁矿采选联合体 (专户)"),
    "crude_oil": ("corp_oil_field", "国家油气田开采公司 (专户)"),
    "copper_ore": ("corp_copper_mine", "铜铝有色采选联合体 (专户)"),
    "electricity": ("corp_power_plant", "国家骨干电网公司 (专户)"),
    "steel": ("corp_steel_mill", "特大型钢铁联合体 (专户)"),
    "cement": ("corp_cement_plant", "新型干法水泥建材厂 (专户)"),
    "fertilizer": ("corp_fertilizer_chem", "合成化肥石化集团 (专户)"),
    "raw_grain": ("corp_state_farm", "大型农垦原粮集团 (专户)"),
    "food_pack": ("corp_food_processing", "粮油食品精炼联合企业 (专户)"),
    "textile": ("corp_textile_light", "轻纺织造日用轻工厂 (专户)"),
    "medicine": ("corp_pharma_corp", "现代生物制药集团 (专户)"),
    "hardware": ("corp_hardware_machinery", "陈厂长五金机械集群 (专户)"),
    "heavy_machinery": ("corp_heavy_machinery", "重型机械装备制造厂 (专户)"),
    "chips": ("corp_hightech_electronics", "电子芯片与微电子集团 (专户)"),
    "power_equipment": ("corp_power_equipment", "特高压电力装备集团 (专户)")
}

@dataclass
class IndustrialFactory:
    """实体工业工厂形态"""
    id: str
    name: str
    category: str                   # "mining", "energy", "metallurgy", "machinery", "consumer", "hightech"
    capital_stock: float            # 机器与厂房固定资产原值 (亿元)
    capacity_limit: float           # 日设计最大产能上限 (实物单位)
    output_commodity_id: str        # 主导产出品物资ID
    inputs_ratio: Dict[str, float]  # 每生产1单位制成品所需消耗的中间品配比 {cid: 消耗量}
    power_demand_per_unit: float    # 每生产1单位制成品所需动力电力 (亿度)
    primary_labor_tier: str         # 主力对口工种ID
    workers_employed: int           # 在册产业工人数
    
    # 细分产业劳工体现与工种职系
    account_id: str = ""            # 商业银行法定分户账账号
    labor_title: str = ""           # 行业核心工种职称
    skill_rank: int = 1             # 技能等级 (1~5级)
    primary_roles: List[str] = field(default_factory=list) # 具体细分工种岗位清单
    
    # 动态生产经营指标 (按日结算)
    utilization_rate: float = 85.0  # 开工负荷率 (%)
    daily_output: float = 0.0       # 今日实际合格产出量
    daily_revenue: float = 0.0      # 营业额 (亿元)
    daily_material_cost: float = 0.0# 原料采购成本 (亿元)
    daily_power_cost: float = 0.0   # 动力电费支出 (亿元)
    daily_wage_cost: float = 0.0    # 工人工资发放 (亿元)
    daily_profit: float = 0.0       # 今日留存经营净利润 (亿元)
    power_shortage_penalty: float = 1.0 # 缺电停机折损系数 (1.0为满负荷)
    
    # 真实企业分户财务账本明细 (当日会计借贷凭证流水)
    daily_ledger: List[Dict[str, Any]] = field(default_factory=list)

    # =========================================================================
    # Phase 1: 资产折旧、技术迭代与企业生命周期出清引擎
    # =========================================================================
    capital_stock_original: float = 0.0 # 初始固定资产原值 (亿元)
    equipment_health: float = 100.0      # 设备完好率与现代化率 (%)
    depreciation_rate_daily: float = 0.0003 # 每日磨损折旧率 (~10%/年)
    capex_spending_daily: float = 0.0   # 当日资本性再投资与设备维保 (亿元)
    
    status: str = "operating"           # "operating" | "downsizing" | "suspended" | "bankrupt"
    consecutive_loss_days: int = 0      # 连续亏损天数
    consecutive_negative_cash_days: int = 0 # 连续现金流告急天数
    workers_baseline: int = 0           # 额定产业工人数
    daily_laid_off: int = 0             # 今日净裁员人数
    daily_hired: int = 0                # 今日净增补人数
    total_laid_off: int = 0             # 历史累计裁员人数
    reorganize_days_left: int = 0       # 破产清算与司法重组剩余天数

    # =========================================================================
    # Phase 3: 商业银行风险评级、授信与信贷周期
    # =========================================================================
    debt_principal: float = 100.0        # 企业在商业银行的贷款本金存量 (亿元)
    credit_rating: str = "A"             # 信用评级: "AAA" | "AA" | "A" | "BBB" | "BB" | "B" | "CCC" | "D"
    credit_score: float = 85.0           # 综合信用评分 (0~100)
    leverage_ratio: float = 45.0         # 资产负债率 (%)
    interest_coverage_ratio: float = 3.5 # 利息保障倍数 (ICR)
    borrowing_rate: float = 0.065        # 企业个体适用的借贷年化利率
    credit_limit: float = 150.0          # 银行核定综合授信额度上限 (亿元)
    loan_status: str = "normal"          # 贷款五级分类: "normal" | "special_mention" | "substandard" | "doubtful" | "loss"
    recalled_loans_today: float = 0.0    # 当日被银行主动抽贷金额 (亿元)
    new_borrowing_today: float = 0.0     # 当日新增借款 (亿元)

    def __post_init__(self):
        if self.capital_stock_original <= 0.0:
            self.capital_stock_original = self.capital_stock
        if self.workers_baseline <= 0:
            self.workers_baseline = self.workers_employed

    def evaluate_credit_rating(
        self,
        base_loan_rate: float,
        inventory_val: float = 0.0,
        cash_balance: float = 0.0,
        credit_crunch_active: bool = False
    ) -> Dict[str, Any]:
        """
        商业银行企业信用风险评级模型 (Corporate Credit Rating Model):
        根据资产负债率、利息保障倍数 (ICR)、连续亏损天数与现金流评定信用等级与授信额度
        """
        total_assets = self.capital_stock + max(0.0, inventory_val) + max(0.0, cash_balance)
        total_debt = max(0.0, self.debt_principal)
        
        # 1. 资产负债率 (Leverage Ratio)
        leverage = (total_debt / max(1.0, total_assets + total_debt)) * 100.0
        self.leverage_ratio = round(leverage, 1)
        
        # 2. 利息保障倍数 (ICR = EBIT / 利息支出)
        ebit_daily = self.daily_revenue - self.daily_material_cost - self.daily_power_cost - self.daily_wage_cost
        ebit_annual = ebit_daily * 360.0
        interest_daily = (total_debt * max(0.03, self.borrowing_rate)) / 360.0
        interest_annual = max(0.01, interest_daily * 360.0)
        icr = round(ebit_annual / interest_annual, 2)
        self.interest_coverage_ratio = icr
        
        # 3. 基础信用评分 (0 ~ 100)
        score = 80.0
        # 杠杆惩罚/奖励
        if leverage < 35.0: score += 15.0
        elif leverage < 50.0: score += 5.0
        elif leverage > 75.0: score -= 20.0
        elif leverage > 85.0: score -= 35.0
        
        # ICR 惩罚/奖励
        if icr >= 4.0: score += 10.0
        elif icr >= 2.0: score += 5.0
        elif icr < 1.0: score -= 20.0
        elif icr < 0.0: score -= 30.0
        
        # 连续亏损惩罚
        score -= min(35.0, self.consecutive_loss_days * 2.5)
        if cash_balance < 0:
            score -= min(25.0, abs(cash_balance) * 4.0)
            
        score = max(5.0, min(100.0, score))
        self.credit_score = round(score, 1)
        
        # 4. 评级等级映射 (AAA ~ D) 与贷款五级分类
        if self.status == "bankrupt" or (self.consecutive_loss_days >= 25 and cash_balance < -2.0):
            rating = "D"
            loan_status = "loss"
            rate_spread = 0.05
            limit_mult = 0.0
        elif score < 30.0 or self.consecutive_loss_days >= 15 or leverage >= 88.0:
            rating = "CCC"
            loan_status = "doubtful" # 可疑类 (不良)
            rate_spread = 0.035
            limit_mult = 0.2
        elif score < 45.0 or self.consecutive_loss_days >= 8 or leverage >= 78.0:
            rating = "B"
            loan_status = "substandard" # 次级类 (不良)
            rate_spread = 0.025
            limit_mult = 0.4
        elif score < 60.0 or self.consecutive_loss_days >= 3 or icr < 1.2:
            rating = "BB"
            loan_status = "special_mention" # 关注类
            rate_spread = 0.015
            limit_mult = 0.6
        elif score < 72.0:
            rating = "BBB"
            loan_status = "normal"
            rate_spread = 0.005
            limit_mult = 0.8
        elif score < 85.0:
            rating = "A"
            loan_status = "normal"
            rate_spread = 0.0
            limit_mult = 1.0
        elif score < 93.0:
            rating = "AA"
            loan_status = "normal"
            rate_spread = -0.005
            limit_mult = 1.2
        else:
            rating = "AAA"
            loan_status = "normal"
            rate_spread = -0.010
            limit_mult = 1.5
            
        self.credit_rating = rating
        self.loan_status = loan_status
        self.borrowing_rate = max(0.025, round(base_loan_rate + rate_spread, 4))
        
        # 信贷紧缩时全面压降额度
        if credit_crunch_active:
            limit_mult *= 0.5
            
        self.credit_limit = round(self.capital_stock * limit_mult, 2)
        
        return {
            "rating": rating,
            "score": self.credit_score,
            "leverage": self.leverage_ratio,
            "icr": self.interest_coverage_ratio,
            "rate": self.borrowing_rate,
            "limit": self.credit_limit,
            "loan_status": loan_status
        }

class FactoryManager:
    """国家工信部与实体工业企业制造局"""
    def __init__(self):
        self.factories: Dict[str, IndustrialFactory] = {
            # 1. 采掘与能源矿山
            "coal_mine": IndustrialFactory(
                id="coal_mine",
                name="现代化大型综合煤矿集团",
                category="mining",
                capital_stock=180.0,
                capacity_limit=3.0,   # 3.0万吨/天 (匹配1000万人口小国规模)
                output_commodity_id="coal",
                inputs_ratio={},       # 直接采掘地下储量
                power_demand_per_unit=0.0015,
                primary_labor_tier="miner_heavy",
                workers_employed=6_000,
                account_id="corp_coal_mine",
                labor_title="煤矿机电采掘重工",
                skill_rank=1,
                primary_roles=["采煤机操作司机", "井下掘进开拓工", "巷道支护与防尘机修工"]
            ),
            "iron_mine": IndustrialFactory(
                id="iron_mine",
                name="大型露天铁矿采选联合体",
                category="mining",
                capital_stock=140.0,
                capacity_limit=2.5,   # 2.5万吨/天
                output_commodity_id="iron_ore",
                inputs_ratio={},       # 采掘铁矿储量
                power_demand_per_unit=0.0018,
                primary_labor_tier="miner_heavy",
                workers_employed=5_000,
                account_id="corp_iron_mine",
                labor_title="露天采掘与选矿重工",
                skill_rank=1,
                primary_roles=["露天采剥穿孔手", "重型电铲矿卡司机", "磁选重介选矿主控"]
            ),
            "oil_field": IndustrialFactory(
                id="oil_field",
                name="国家主力油气田开采公司",
                category="mining",
                capital_stock=220.0,
                capacity_limit=1.5,   # 1.5万桶/天
                output_commodity_id="crude_oil",
                inputs_ratio={},
                power_demand_per_unit=0.0035,
                primary_labor_tier="miner_heavy",
                workers_employed=3_000,
                account_id="corp_oil_field",
                labor_title="油气田钻井与输送工",
                skill_rank=2,
                primary_roles=["高压钻井试油修井工", "输油加压泵站巡检员", "测井地质技术员"]
            ),
            "copper_mine": IndustrialFactory(
                id="copper_mine",
                name="国家重点铜铝有色金属采选联合体",
                category="mining",
                capital_stock=130.0,
                capacity_limit=0.30,  # 0.30万吨/天
                output_commodity_id="copper_ore",
                inputs_ratio={},       # 采掘有色金属储量
                power_demand_per_unit=0.0020,
                primary_labor_tier="miner_heavy",
                workers_employed=2_000,
                account_id="corp_copper_mine",
                labor_title="有色金属采选与选矿重工",
                skill_rank=2,
                primary_roles=["有色露天采矿电铲司机", "浮选重介质主控手", "精矿脱水过滤工"]
            ),
            
            # 2. 国家主力电网与发电厂
            "power_plant": IndustrialFactory(
                id="power_plant",
                name="国家骨干电网与主力发电枢纽",
                category="energy",
                capital_stock=350.0,
                capacity_limit=1.8,   # 1.8亿度/天
                output_commodity_id="electricity",
                inputs_ratio={"coal": 0.40}, # 发1亿度电耗煤约0.40万吨标煤
                power_demand_per_unit=0.0,
                primary_labor_tier="engineer_expert",
                workers_employed=2_500,
                account_id="corp_power_plant",
                labor_title="特高压电网与发电电气工程专家",
                skill_rank=5,
                primary_roles=["特高压变电运维工程师", "超临界汽轮发电机值长", "骨干电网继电保护调度专家"]
            ),
            
            # 3. 基础原材料与重化工
            "steel_mill": IndustrialFactory(
                id="steel_mill",
                name="特大型钢铁冶炼联合联合体",
                category="metallurgy",
                capital_stock=290.0,
                capacity_limit=1.8,   # 1.8万吨型钢/天
                output_commodity_id="steel",
                inputs_ratio={"iron_ore": 1.6, "coal": 0.45}, # 1吨钢=1.6吨矿+0.45吨煤
                power_demand_per_unit=0.012,
                primary_labor_tier="miner_heavy",
                workers_employed=5_000,
                account_id="corp_steel_mill",
                labor_title="高炉冶炼与轧钢重工",
                skill_rank=2,
                primary_roles=["高炉炼铁大炉长", "转炉炼钢配料工", "热连轧卷板机操作手"]
            ),
            "cement_plant": IndustrialFactory(
                id="cement_plant",
                name="大型新型干法水泥建材厂",
                category="metallurgy",
                capital_stock=110.0,
                capacity_limit=2.0,   # 2.0万吨/天
                output_commodity_id="cement",
                inputs_ratio={"coal": 0.12},
                power_demand_per_unit=0.004,
                primary_labor_tier="miner_heavy",
                workers_employed=3_500,
                account_id="corp_cement_plant",
                labor_title="建材窑炉与散装重工",
                skill_rank=1,
                primary_roles=["干法回转窑看火工", "生料磨立磨主操手", "散装水泥物料调度员"]
            ),
            "fertilizer_chem": IndustrialFactory(
                id="fertilizer_chem",
                name="国家第一合成氨与石化化肥集团",
                category="metallurgy",
                capital_stock=150.0,
                capacity_limit=0.25,  # 0.25万吨/天
                output_commodity_id="fertilizer",
                inputs_ratio={"coal": 0.40, "crude_oil": 0.20},
                power_demand_per_unit=0.015,
                primary_labor_tier="operator_light",
                workers_employed=2_500,
                account_id="corp_fertilizer_chem",
                labor_title="化工合成与石化操作工",
                skill_rank=2,
                primary_roles=["高压合成氨压缩机操作工", "尿素造粒塔主控", "化工防爆管线巡检员"]
            ),
            
            # 4. 通用机械与装备制造 (陈厂长旗舰企业)
            "hardware_machinery": IndustrialFactory(
                id="hardware_machinery",
                name="机械五金配件与高精紧固件制造厂 (陈厂长实体厂集群)",
                category="machinery",
                capital_stock=160.0,
                capacity_limit=1.5,   # 1.5万套高强五金/天
                output_commodity_id="hardware",
                inputs_ratio={"steel": 0.025}, # 1万套高精五金配件耗用0.025万吨(250吨)合金型钢 (25kg/套)
                power_demand_per_unit=0.0035,
                primary_labor_tier="technician_skilled",
                workers_employed=3_500,
                account_id="corp_hardware_machinery",
                labor_title="数控五金精密加工核心技工",
                skill_rank=3,
                primary_roles=["精密数控车铣工", "多工位冷镦机师傅", "模具钳工实操手 (陈厂长核心车间)"]
            ),
            "heavy_machinery": IndustrialFactory(
                id="heavy_machinery",
                name="重装工程机械与数控机床制造厂",
                category="machinery",
                capital_stock=240.0,
                capacity_limit=6.0,   # 6.0台工程重装/天
                output_commodity_id="heavy_machinery",
                inputs_ratio={"steel": 0.0035, "hardware": 0.04}, # 1台重装用35吨钢(0.0035万吨)+400套五金(0.04万套)
                power_demand_per_unit=0.0008,
                primary_labor_tier="technician_skilled",
                workers_employed=2_000,
                account_id="corp_heavy_machinery",
                labor_title="重型装备与数控机床制造技师",
                skill_rank=4,
                primary_roles=["重载工程机床总装钳工", "五轴联动龙门铣操作手", "重型液压调试技师"]
            ),
            "power_equipment_factory": IndustrialFactory(
                id="power_equipment_factory",
                name="特高压成套变电与重大电力装备集团",
                category="hightech",
                capital_stock=180.0,
                capacity_limit=0.08,  # 0.08组/天 (特高压重大成套装备)
                output_commodity_id="power_equipment",
                inputs_ratio={"steel": 0.02, "copper_ore": 0.015, "chips": 0.05, "hardware": 0.05},
                power_demand_per_unit=0.0030,
                primary_labor_tier="engineer_expert",
                workers_employed=600,
                account_id="corp_power_equipment",
                labor_title="特高压重型变电设备总装专家",
                skill_rank=5,
                primary_roles=["换流变压器总装电气工程师", "特高压GIS开关调试技师", "绝缘检测与高压试验工程师"]
            ),
            
            # 5. 轻纺食品与民生消费
            "textile_light": IndustrialFactory(
                id="textile_light",
                name="现代纺织制衣与大众日用品轻工厂",
                category="consumer",
                capital_stock=130.0,
                capacity_limit=8.0,   # 8.0万件/天
                output_commodity_id="textile",
                inputs_ratio={},       # 农用纤维与合成原料
                power_demand_per_unit=0.0008,
                primary_labor_tier="operator_light",
                workers_employed=5_000,
                account_id="corp_textile_light",
                labor_title="轻纺织造与服装流水线工",
                skill_rank=2,
                primary_roles=["高速喷气织机巡回工", "自动络筒挡车工", "服装立体打版缝纫工"]
            ),
            "state_farm": IndustrialFactory(
                id="state_farm",
                name="国家大型机械化农垦与原粮生产集团",
                category="consumer",
                capital_stock=140.0,
                capacity_limit=2.0,   # 2.0万吨/天
                output_commodity_id="raw_grain",
                inputs_ratio={"fertilizer": 0.035}, # 1吨原粮耗用0.035吨农用化肥
                power_demand_per_unit=0.0005,
                primary_labor_tier="farmer",
                workers_employed=8_000,
                account_id="corp_state_farm",
                labor_title="现代农垦机械化种植技工",
                skill_rank=1,
                primary_roles=["大马力拖拉机联合收割手", "智慧农田水肥一体化主控", "原粮初烘干仓储调度员"]
            ),
            "food_processing": IndustrialFactory(
                id="food_processing",
                name="国家粮油食品精炼加工联合企业",
                category="consumer",
                capital_stock=120.0,
                capacity_limit=1.2,   # 1.2万吨/天口粮加工
                output_commodity_id="food_pack",
                inputs_ratio={"raw_grain": 1.15}, # 1.15吨原粮出1吨精炼米面
                power_demand_per_unit=0.0012,
                primary_labor_tier="operator_light",
                workers_employed=4_000,
                account_id="corp_food_processing",
                labor_title="粮油精炼与食品加工流水线工",
                skill_rank=2,
                primary_roles=["油脂浸出精炼主控工", "面粉研磨配粉主操", "无菌灌装杀菌操作手"]
            ),
            "pharma_corp": IndustrialFactory(
                id="pharma_corp",
                name="国家现代生物医药与战略药械制造集团",
                category="consumer",
                capital_stock=110.0,
                capacity_limit=6.0,   # 6.0万箱/天
                output_commodity_id="medicine",
                inputs_ratio={"fertilizer": 0.02}, # 基础化工与生物发酵中间原料
                power_demand_per_unit=0.0020,
                primary_labor_tier="operator_light",
                workers_employed=2_500,
                account_id="corp_pharma_corp",
                labor_title="现代生物制药与无菌制剂工",
                skill_rank=3,
                primary_roles=["发酵纯化生物反应器主操", "无菌冻干针剂联动线操作工", "制药质量GMP在线质检员"]
            ),
            
            # 6. 尖端芯片与战略高精尖
            "hightech_electronics": IndustrialFactory(
                id="hightech_electronics",
                name="电子芯片与战略微电子集团",
                category="hightech",
                capital_stock=310.0,
                capacity_limit=0.50,  # 0.50万片芯片/天
                output_commodity_id="chips",
                inputs_ratio={"copper_ore": 0.02, "hardware": 0.08},
                power_demand_per_unit=0.004,
                primary_labor_tier="engineer_expert",
                workers_employed=800,
                account_id="corp_hightech_electronics",
                labor_title="半导体芯片工艺专家",
                skill_rank=5,
                primary_roles=["芯片晶圆光刻工艺工程师", "超大规模集成电路测试专家", "半导体芯片封装测试员"]
            )
        }

        # 初始化各行业企业初始贷款本金存量 (全国总计 1400.0 亿元，与宏观状态对齐)
        initial_debts = {
            "coal_mine": 90.0,
            "iron_mine": 70.0,
            "oil_field": 95.0,
            "copper_mine": 70.0,
            "power_plant": 160.0,
            "steel_mill": 145.0,
            "cement_plant": 60.0,
            "fertilizer_chem": 65.0,
            "hardware_machinery": 80.0,
            "heavy_machinery": 120.0,
            "power_equipment_factory": 50.0,
            "textile_light": 75.0,
            "state_farm": 80.0,
            "food_processing": 60.0,
            "pharma_corp": 60.0,
            "hightech_electronics": 120.0
        }
        for fid, debt in initial_debts.items():
            if fid in self.factories:
                self.factories[fid].debt_principal = debt

    def run_production_cycle(
        self,
        resource_mgr: ResourceManager,
        commodity_hub: CommodityHub,
        labor_mgr: LaborManager,
        power_grid_efficiency: float = 1.0,
        uhv_cost_discount: float = 0.0,
        accounting_bus: Any = None
    ) -> List[str]:
        """
        运行单日工业投入产出全闭环生产流转：
        1. 采掘矿山从地下探明储量开采资源并入库，工厂专户直接向采掘工人发薪
        2. 电厂向煤矿采购标煤，发电供给全网并向电气工程师发薪
        3. 下游工厂按配比领用原材料、向电网交纳电费、向对口产业工人发薪，完成真实账本双边清算
        """
        events = []
        for f in self.factories.values():
            f.daily_ledger = []
            f.daily_laid_off = 0
            f.daily_hired = 0
            f.capex_spending_daily = 0.0
            
            # 若处于破产司法重组倒计时
            if f.status == "bankrupt":
                f.reorganize_days_left -= 1
                if f.reorganize_days_left <= 0:
                    # 司法重组完成：剥离25%落后产能，精简编制轻装上阵
                    f.status = "operating"
                    f.capacity_limit = round(f.capacity_limit * 0.75, 1)
                    f.workers_baseline = int(f.workers_baseline * 0.75)
                    f.workers_employed = f.workers_baseline
                    f.capital_stock_original = f.capital_stock
                    f.consecutive_loss_days = 0
                    f.consecutive_negative_cash_days = 0
                    events.append(f"🔄 【司法重组完成】{f.name}剥离25%落后产能并出清债务，轻装上阵恢复常态化挂牌生产！")
        
        # 1. 采掘开采生产阶段
        # 煤矿开采
        coal_mine = self.factories["coal_mine"]
        coal_item = commodity_hub.commodities["coal"]
        c_cover = coal_item.inventory_cover_days
        if coal_mine.status in ["bankrupt", "suspended"]:
            coal_mine.utilization_rate = 0.0
        else:
            if c_cover < 15.0:
                coal_mine.utilization_rate = min(98.0, round(coal_mine.utilization_rate * 0.85 + 95.0 * 0.15, 1))
            elif c_cover > 90.0:
                coal_mine.utilization_rate = max(18.0, round(coal_mine.utilization_rate * 0.85 + 25.0 * 0.15, 1))
            elif c_cover > 45.0:
                coal_mine.utilization_rate = max(35.0, round(coal_mine.utilization_rate * 0.85 + 50.0 * 0.15, 1))
            else:
                coal_mine.utilization_rate = round(coal_mine.utilization_rate * 0.85 + 85.0 * 0.15, 1)
            if coal_mine.status == "downsizing":
                coal_mine.utilization_rate = min(coal_mine.utilization_rate, 40.0)

        eff_cap_coal = coal_mine.capacity_limit * (0.60 + 0.40 * (coal_mine.equipment_health / 100.0))
        target_coal = eff_cap_coal * (coal_mine.utilization_rate / 100.0)
        actual_coal, depleted_coal = resource_mgr.extract("coal", target_coal)
        coal_mine.daily_output = actual_coal
        commodity_hub.produce("coal", actual_coal)
        if depleted_coal:
            events.append("⚠️ 【矿产告急】国内煤田地下探明储量已彻底采空！煤矿开采量暴跌为零，全社会面临灭顶之灾的燃煤荒！")
            
        # 铁矿开采
        iron_mine = self.factories["iron_mine"]
        fe_item = commodity_hub.commodities["iron_ore"]
        fe_cover = fe_item.inventory_cover_days
        if iron_mine.status in ["bankrupt", "suspended"]:
            iron_mine.utilization_rate = 0.0
        else:
            if fe_cover < 15.0:
                iron_mine.utilization_rate = min(98.0, round(iron_mine.utilization_rate * 0.85 + 95.0 * 0.15, 1))
            elif fe_cover > 80.0:
                iron_mine.utilization_rate = max(20.0, round(iron_mine.utilization_rate * 0.85 + 35.0 * 0.15, 1))
            else:
                iron_mine.utilization_rate = round(iron_mine.utilization_rate * 0.85 + 85.0 * 0.15, 1)
            if iron_mine.status == "downsizing":
                iron_mine.utilization_rate = min(iron_mine.utilization_rate, 40.0)

        eff_cap_iron = iron_mine.capacity_limit * (0.60 + 0.40 * (iron_mine.equipment_health / 100.0))
        target_iron = eff_cap_iron * (iron_mine.utilization_rate / 100.0)
        actual_iron, _ = resource_mgr.extract("iron_ore", target_iron)
        iron_mine.daily_output = actual_iron
        commodity_hub.produce("iron_ore", actual_iron)
        
        # 原油开采
        oil_field = self.factories["oil_field"]
        oil_item = commodity_hub.commodities["crude_oil"]
        oil_cover = oil_item.inventory_cover_days
        if oil_field.status in ["bankrupt", "suspended"]:
            oil_field.utilization_rate = 0.0
        else:
            if oil_cover < 15.0:
                oil_field.utilization_rate = min(98.0, round(oil_field.utilization_rate * 0.85 + 95.0 * 0.15, 1))
            elif oil_cover > 60.0:
                oil_field.utilization_rate = max(25.0, round(oil_field.utilization_rate * 0.85 + 45.0 * 0.15, 1))
            else:
                oil_field.utilization_rate = round(oil_field.utilization_rate * 0.85 + 85.0 * 0.15, 1)
            if oil_field.status == "downsizing":
                oil_field.utilization_rate = min(oil_field.utilization_rate, 40.0)

        eff_cap_oil = oil_field.capacity_limit * (0.60 + 0.40 * (oil_field.equipment_health / 100.0))
        target_oil = eff_cap_oil * (oil_field.utilization_rate / 100.0)
        actual_oil, _ = resource_mgr.extract("crude_oil", target_oil)
        oil_field.daily_output = actual_oil
        commodity_hub.produce("crude_oil", actual_oil)
        
        # 铜铝有色矿开采
        copper_mine = self.factories.get("copper_mine")
        if copper_mine:
            cu_item = commodity_hub.commodities["copper_ore"]
            cu_cover = cu_item.inventory_cover_days
            if copper_mine.status in ["bankrupt", "suspended"]:
                copper_mine.utilization_rate = 0.0
            else:
                if cu_cover < 15.0:
                    copper_mine.utilization_rate = min(98.0, round(copper_mine.utilization_rate * 0.85 + 95.0 * 0.15, 1))
                elif cu_cover > 45.0:
                    copper_mine.utilization_rate = max(18.0, round(copper_mine.utilization_rate * 0.85 + 28.0 * 0.15, 1))
                elif cu_cover > 30.0:
                    copper_mine.utilization_rate = max(28.0, round(copper_mine.utilization_rate * 0.85 + 45.0 * 0.15, 1))
                else:
                    copper_mine.utilization_rate = round(copper_mine.utilization_rate * 0.85 + 75.0 * 0.15, 1)
                if copper_mine.status == "downsizing":
                    copper_mine.utilization_rate = min(copper_mine.utilization_rate, 40.0)

            eff_cap_cu = copper_mine.capacity_limit * (0.60 + 0.40 * (copper_mine.equipment_health / 100.0))
            target_cu = eff_cap_cu * (copper_mine.utilization_rate / 100.0)
            actual_cu, depleted_cu = resource_mgr.extract("copper_ore", target_cu)
            copper_mine.daily_output = actual_cu
            commodity_hub.produce("copper_ore", actual_cu)
            if depleted_cu:
                events.append("⚠️ 【矿产告急】国内铜铝有色金属探明储量已采空！")
        else:
            cu_item = commodity_hub.commodities["copper_ore"]
            cu_cover = cu_item.inventory_cover_days
            target_cu = 4.0 if cu_cover < 20.0 else (1.5 if cu_cover > 90.0 else 2.8)
            actual_cu, _ = resource_mgr.extract("copper_ore", target_cu)
            commodity_hub.produce("copper_ore", actual_cu)
        
        # 3. 电力发电阶段 (先发电，确保全社会供电)
        power_plant = self.factories["power_plant"]
        elec_item = commodity_hub.commodities["electricity"]
        elec_cover = elec_item.inventory_cover_days
        if power_plant.status in ["bankrupt", "suspended"]:
            power_plant.utilization_rate = 0.0
        else:
            if elec_cover < 5.0:
                power_plant.utilization_rate = min(98.0, round(power_plant.utilization_rate * 0.85 + 95.0 * 0.15, 1))
            elif elec_cover > 20.0:
                power_plant.utilization_rate = max(45.0, round(power_plant.utilization_rate * 0.85 + 55.0 * 0.15, 1))
            else:
                power_plant.utilization_rate = round(power_plant.utilization_rate * 0.85 + 85.0 * 0.15, 1)
            if power_plant.status == "downsizing":
                power_plant.utilization_rate = min(power_plant.utilization_rate, 50.0)

        eff_cap_elec = power_plant.capacity_limit * (0.60 + 0.40 * (power_plant.equipment_health / 100.0))
        target_elec = eff_cap_elec * (power_plant.utilization_rate / 100.0) * power_grid_efficiency
        # 发电需领用煤炭
        coal_needed = target_elec * power_plant.inputs_ratio.get("coal", 0.035)
        coal_got = commodity_hub.consume_factory("coal", coal_needed)
        fuel_ratio = (coal_got / max(0.01, coal_needed)) if coal_needed > 0 else 1.0
        
        actual_elec = target_elec * fuel_ratio
        power_plant.daily_output = actual_elec
        commodity_hub.produce("electricity", actual_elec)
        if fuel_ratio < 0.8:
            events.append("⚡ 【电厂燃煤荒】由于电煤库存告急，发电厂发电机组被迫降负荷压产，全社会电力供应极度紧张！")
            
        # 电厂向煤矿结算电煤采购款 (真实 B2B 记账)
        coal_price = commodity_hub.commodities["coal"].domestic_price
        coal_cost = get_commodity_value_in_yi("coal", coal_got, coal_price)
        power_plant.daily_material_cost = round(coal_cost, 4)
        if accounting_bus and coal_cost > 0.0001:
            accounting_bus.transfer(
                "corp_power_plant", "corp_coal_mine", coal_cost,
                "原料中间品采购", f"主力电厂向现代化煤矿采购{coal_got:.1f}万吨发电标煤"
            )
            power_plant.daily_ledger.append({
                "category": "原料采购", "direction": "贷 (支出)",
                "counterparty": "现代化煤矿集团 (专户)", "amount": round(coal_cost, 4),
                "desc": f"采购交付{coal_got:.1f}万吨主力发电标煤"
            })
            coal_mine.daily_ledger.append({
                "category": "中间品销售", "direction": "借 (流入)",
                "counterparty": "国家骨干电网公司 (专户)", "amount": round(coal_cost, 4),
                "desc": f"向主力电厂交付{coal_got:.1f}万吨电煤销售回款"
            })
            
        # 4. 全社会各制造业工厂投入产出阶段
        elec_item = commodity_hub.commodities["electricity"]
        
        for fid, f in self.factories.items():
            if f.category in ["mining", "energy"]:
                # 矿山与电厂根据全社会工业开工与电煤消耗动态调整负荷
                out_item = commodity_hub.commodities[f.output_commodity_id]
                cover = out_item.inventory_cover_days
                if f.status in ["bankrupt", "suspended"]:
                    f.utilization_rate = 0.0
                else:
                    if cover < 12.0:
                        f.utilization_rate = min(98.0, round(f.utilization_rate * 0.90 + 95.0 * 0.10, 1))
                    elif cover > 120.0:
                        # 严重积压，停产检修或限产保价
                        f.utilization_rate = max(18.0, round(f.utilization_rate * 0.90 + 20.0 * 0.10, 1))
                    elif cover > 60.0:
                        f.utilization_rate = max(35.0, round(f.utilization_rate * 0.90 + 45.0 * 0.10, 1))
                    elif cover > 35.0:
                        f.utilization_rate = round(f.utilization_rate * 0.90 + 70.0 * 0.10, 1)
                    else:
                        f.utilization_rate = round(f.utilization_rate * 0.90 + 85.0 * 0.10, 1)
                    if f.status == "downsizing":
                        f.utilization_rate = min(f.utilization_rate, 40.0)
                
                f_price = out_item.domestic_price
                f.daily_revenue = get_commodity_value_in_yi(f.output_commodity_id, f.daily_output, f_price)
                wage_rate = labor_mgr.tiers[f.primary_labor_tier].daily_wage
                workers_paid = f.workers_employed if f.status not in ["bankrupt", "suspended"] else max(int(f.workers_baseline * 0.10), f.workers_employed)
                w_factor = 0.5 if f.status in ["bankrupt", "suspended"] else 1.0
                f.daily_wage_cost = round((workers_paid * wage_rate * w_factor) / 100_000_000.0, 4)
                f.daily_profit = round(f.daily_revenue - f.daily_material_cost - f.daily_wage_cost, 4)
                
                # 采矿/电厂企业专户向在册产业工人直发工资 (真实记账)
                if accounting_bus and f.daily_wage_cost > 0.0001:
                    hh_id = f"household_{f.primary_labor_tier}"
                    hh_name = labor_mgr.tiers[f.primary_labor_tier].name
                    accounting_bus.transfer(
                        f.account_id, hh_id, f.daily_wage_cost,
                        "工人工资直发", f"{f.name}向{workers_paid//10000}万在册{f.labor_title}直发日薪"
                    )
                    f.daily_ledger.append({
                        "category": "工资直发", "direction": "贷 (支出)",
                        "counterparty": f"{hh_name}专户", "amount": round(f.daily_wage_cost, 4),
                        "desc": f"直发{workers_paid//10000}万在册{f.labor_title}岗位薪酬"
                    })
                
                # 评估生命周期与设备折旧出清
                self._evaluate_factory_lifecycle_and_depreciation(f, accounting_bus, commodity_hub, events)
                continue
                
            # 动态市场订单与利润率双轮驱动负荷：库存告急或毛利丰厚则扩产，库存积压或大幅亏损则限产
            out_item = commodity_hub.commodities[f.output_commodity_id]
            cover = out_item.inventory_cover_days
            target_util = 85.0
            if f.status in ["bankrupt", "suspended"]:
                target_util = 0.0
            else:
                # 1. 下游市场订单需求牵引基准 (以销定产)
                demand_ratio = (out_item.last_day_demand / max(0.1, f.capacity_limit)) * 100.0
                if cover < 12.0:
                    target_util = min(100.0, max(88.0, demand_ratio * 1.15)) # 现货紧俏，开足马力加班
                elif cover < 22.0:
                    target_util = min(95.0, max(75.0, demand_ratio * 1.05))
                elif cover > 100.0:
                    # 严重积压，严格以销定产，防止盲目堆库
                    target_util = max(8.0, min(35.0, demand_ratio * 0.75))
                elif cover > 55.0:
                    target_util = max(15.0, min(55.0, demand_ratio * 0.90))
                elif cover > 35.0:
                    target_util = max(25.0, min(70.0, demand_ratio * 0.98))
                else:
                    target_util = min(88.0, max(60.0, demand_ratio))
                
                # 2. 微观经营利润信号激励 (自发产能弹性调节)
                if f.daily_revenue > 0.001:
                    margin = f.daily_profit / f.daily_revenue
                    if margin > 0.18:
                        target_util = min(100.0, target_util + 10.0) # 暴利超额供给
                    elif margin > 0.08:
                        target_util = min(100.0, target_util + 5.0)
                    elif margin < -0.15:
                        target_util = max(10.0, target_util - 18.0) # 严重亏损主动控产止血
                    elif margin < -0.05:
                        target_util = max(15.0, target_util - 8.0)

                if f.status == "downsizing":
                    target_util = min(target_util, 45.0)
                
            # 特高压骨干电网电能质量加成：消除拉闸限电与电压波动损耗
            target_util *= power_grid_efficiency
            min_u = 0.0 if f.status in ["bankrupt", "suspended"] else 5.0
            # 蛛网阻尼收敛：0.82 生产惯性 + 0.18 边际动态响应，形成自然平滑的供需动态震荡收敛曲线
            f.utilization_rate = min(100.0, max(min_u, round(f.utilization_rate * 0.82 + target_util * 0.18, 1)))

            # 计算目标排产计划 (考虑设备完好率有效产能上限)
            eff_cap = f.capacity_limit * (0.60 + 0.40 * (f.equipment_health / 100.0))
            target_prod = eff_cap * (f.utilization_rate / 100.0)
            
            # 原料中间品领料约束 (木桶效应：短缺哪种原料就以哪种为上限)
            material_limit_ratio = 1.0
            mat_cost_total = 0.0
            for in_cid, in_rate in f.inputs_ratio.items():
                in_needed = target_prod * in_rate
                in_got = commodity_hub.consume_factory(in_cid, in_needed)
                ratio = min(1.0, in_got / in_needed) if in_needed > 1e-6 else 1.0
                material_limit_ratio = min(material_limit_ratio, ratio)
                mat_price = commodity_hub.commodities[in_cid].domestic_price
                cost_item = get_commodity_value_in_yi(in_cid, in_got, mat_price)
                mat_cost_total += cost_item
                
                # B2B 原料采购真实记账划转
                supplier_info = COMMODITY_SUPPLIER_MAP.get(in_cid, ("corporate_sector", "国家工业原材料专户"))
                supplier_acc, supplier_name = supplier_info
                if accounting_bus and cost_item > 0.0001:
                    accounting_bus.transfer(
                        f.account_id, supplier_acc, cost_item,
                        "原料中间品采购", f"{f.name}采购{commodity_hub.commodities[in_cid].name}"
                    )
                    f.daily_ledger.append({
                        "category": "原料采购", "direction": "贷 (支出)",
                        "counterparty": supplier_name, "amount": round(cost_item, 4),
                        "desc": f"采购{in_got:.2f}{commodity_hub.commodities[in_cid].unit}{commodity_hub.commodities[in_cid].name}"
                    })
                    for sf in self.factories.values():
                        if sf.account_id == supplier_acc:
                            sf.daily_ledger.append({
                                "category": "中间品销售", "direction": "借 (流入)",
                                "counterparty": f.name, "amount": round(cost_item, 4),
                                "desc": f"向{f.name}交付{commodity_hub.commodities[in_cid].name}销售回款"
                            })
                            break
                
            # 电力供应约束与特高压电费打折
            p_needed = target_prod * f.power_demand_per_unit
            p_got = commodity_hub.consume_factory("electricity", p_needed)
            p_ratio = min(1.0, p_got / p_needed) if p_needed > 1e-6 else 1.0
            f.power_shortage_penalty = p_ratio
            
            # 实际最终产出 = 目标排产 * 原料瓶颈 * 供电满足率
            f.daily_output = target_prod * material_limit_ratio * p_ratio
            commodity_hub.produce(f.output_commodity_id, f.daily_output)
            
            # 财务账本结算 (亿元)
            out_price = commodity_hub.commodities[f.output_commodity_id].domestic_price
            f.daily_revenue = get_commodity_value_in_yi(f.output_commodity_id, f.daily_output, out_price)
            f.daily_material_cost = round(mat_cost_total, 4)
            
            # 动力电费 (若特高压电网并网送电，享 uhv_cost_discount 降本优惠)
            elec_unit_price = elec_item.domestic_price * (1.0 - uhv_cost_discount * 1.5)
            f.daily_power_cost = round(p_got * elec_unit_price, 4) # p_got是亿度，单位元/度 -> 亿元
            
            # 向电网交纳电费真实记账
            if accounting_bus and f.daily_power_cost > 0.0001:
                accounting_bus.transfer(
                    f.account_id, "corp_power_plant", f.daily_power_cost,
                    "工业动力电费", f"{f.name}结算工业动力电费"
                )
                f.daily_ledger.append({
                    "category": "动力电费", "direction": "贷 (支出)",
                    "counterparty": "国家骨干电网公司 (专户)", "amount": round(f.daily_power_cost, 4),
                    "desc": f"交纳{p_got:.2f}亿度工业动力电费"
                })
                self.factories["power_plant"].daily_ledger.append({
                    "category": "电费电费结算", "direction": "借 (流入)",
                    "counterparty": f.name, "amount": round(f.daily_power_cost, 4),
                    "desc": f"收取{f.name}工业动力电费"
                })
            
            # 工人工资发放真实记账
            wage_rate = labor_mgr.tiers[f.primary_labor_tier].daily_wage
            workers_paid = f.workers_employed if f.status not in ["bankrupt", "suspended"] else max(int(f.workers_baseline * 0.10), f.workers_employed)
            w_factor = 0.5 if f.status in ["bankrupt", "suspended"] else 1.0
            f.daily_wage_cost = round((workers_paid * wage_rate * w_factor) / 100_000_000.0, 4)
            if accounting_bus and f.daily_wage_cost > 0.0001:
                hh_id = f"household_{f.primary_labor_tier}"
                hh_name = labor_mgr.tiers[f.primary_labor_tier].name
                accounting_bus.transfer(
                    f.account_id, hh_id, f.daily_wage_cost,
                    "工人工资直发", f"{f.name}向{workers_paid//10000}万在册{f.labor_title}直发日薪"
                )
                f.daily_ledger.append({
                    "category": "工资直发", "direction": "贷 (支出)",
                    "counterparty": f"{hh_name}专户", "amount": round(f.daily_wage_cost, 4),
                    "desc": f"直发{workers_paid//10000}万在册{f.labor_title}岗位薪酬"
                })
            
            # 记录产品出厂与销售流水
            f.daily_ledger.append({
                "category": "产品出厂结算", "direction": "借 (流入)",
                "counterparty": "市场与下游采购订单", "amount": round(f.daily_revenue, 4),
                "desc": f"出厂合格品{f.daily_output:.1f}{commodity_hub.commodities[f.output_commodity_id].unit}"
            })
            
            # 留存净利润
            f.daily_profit = round(f.daily_revenue - f.daily_material_cost - f.daily_power_cost - f.daily_wage_cost, 4)
            
            # 评估生命周期与折旧出清
            self._evaluate_factory_lifecycle_and_depreciation(f, accounting_bus, commodity_hub, events)
            
        return events

    def _evaluate_factory_lifecycle_and_depreciation(
        self,
        f: IndustrialFactory,
        accounting_bus: Any,
        commodity_hub: CommodityHub,
        events: List[str]
    ):
        """
        Phase 1: 资产折旧、技改再投资、经营盈亏评估、减产裁员与破产重组状态机
        """
        f_cash = accounting_bus.accounts[f.account_id].balance if accounting_bus and hasattr(accounting_bus, "accounts") and f.account_id in accounting_bus.accounts else 0.0
        out_item = commodity_hub.commodities.get(f.output_commodity_id)
        cover = out_item.inventory_cover_days if out_item else 30.0

        # 1. 物理设备磨损折旧
        if f.status in ["operating", "downsizing"] and f.utilization_rate > 0:
            wear_rate = f.depreciation_rate_daily * (f.utilization_rate / 85.0)
            depr_amt = round(f.capital_stock * wear_rate, 4)
            f.capital_stock = max(0.5, round(f.capital_stock - depr_amt, 4))
            f.equipment_health = round(min(100.0, max(15.0, (f.capital_stock / f.capital_stock_original) * 100.0)), 1)

        # 2. 资本性再投资与设备维保 (Capex: 盈利且账面资金充裕时，自发采购五金机床构件维保)
        if f.daily_profit > 0.03 and f_cash > 1.5 and f.equipment_health < 98.0:
            target_capex = min(f.daily_profit * 0.40, 0.45, max(0.01, f.capital_stock_original - f.capital_stock))
            if target_capex > 0.005 and f_cash >= target_capex:
                if accounting_bus:
                    accounting_bus.transfer(
                        f.account_id, "corp_hardware_machinery", target_capex,
                        "固定资产维保再投资", f"{f.name}采购高精机床紧固件配件进行产线现代化维保"
                    )
                    f.daily_ledger.append({
                        "category": "资本再投资(Capex)", "direction": "贷 (支出)",
                        "counterparty": "陈厂长五金机械集群 (专户)", "amount": round(target_capex, 4),
                        "desc": "更新检修母机关键受损构件"
                    })
                    if "hardware_machinery" in self.factories:
                        self.factories["hardware_machinery"].daily_ledger.append({
                            "category": "高端技改装备销售", "direction": "借 (流入)",
                            "counterparty": f.name, "amount": round(target_capex, 4),
                            "desc": f"向{f.name}交付产线检修装备构件"
                        })
                f.capital_stock = round(f.capital_stock + target_capex, 4)
                f.capex_spending_daily = target_capex
                f.equipment_health = round(min(100.0, (f.capital_stock / f.capital_stock_original) * 100.0), 1)

        # 3. 经营盈亏与现金流追踪
        if f.daily_profit < -0.001:
            f.consecutive_loss_days += 1
        elif f.daily_profit > 0.005:
            f.consecutive_loss_days = max(0, f.consecutive_loss_days - 1)

        if f_cash < 0.0:
            f.consecutive_negative_cash_days += 1
        else:
            f.consecutive_negative_cash_days = max(0, f.consecutive_negative_cash_days - 2)

        # 4. 企业生命周期状态机迁移
        if f.status == "operating":
            # 严重积压、长期亏损或现金流断裂 -> 减产裁员
            if f.consecutive_loss_days >= 7 or cover > 65.0 or (f_cash < 0.2 and cover > 45.0):
                f.status = "downsizing"
                events.append(f"⚠️ 【供需失衡·减产自救】{f.name}因产品严重积压、连日亏损，启动减产自救与编制优化！")
            elif f.consecutive_loss_days == 0 and f.workers_employed < f.workers_baseline and f_cash > 3.0:
                # 经营恢复后扩招
                hire_cnt = min(int(f.workers_baseline * 0.03), f.workers_baseline - f.workers_employed)
                if hire_cnt > 0:
                    f.workers_employed += hire_cnt
                    f.daily_hired = hire_cnt

        elif f.status == "downsizing":
            # 每日裁员降本 (裁员 1.5%~2.5%)
            laid_off = max(80, int(f.workers_employed * 0.02))
            min_keep = int(f.workers_baseline * 0.40)
            if f.workers_employed > min_keep:
                actual_laid = min(laid_off, f.workers_employed - min_keep)
                f.workers_employed -= actual_laid
                f.daily_laid_off = actual_laid
                f.total_laid_off += actual_laid

            if f.consecutive_loss_days >= 20 and f_cash < -1.0:
                f.status = "suspended"
                events.append(f"🛑 【停机封炉整顿】{f.name}流动资金彻底见底，进入全面停机封炉整顿，仅保留最低限度值守！")
            elif f.consecutive_loss_days == 0 and f_cash > 0.5 and cover <= 45.0:
                f.status = "operating"
                events.append(f"🌱 【经营企稳】{f.name}通过减员降本和市场回暖，经营现金流转正，恢复常态排产！")

        elif f.status == "suspended":
            f.utilization_rate = 0.0
            # 资不抵债严重 -> 破产清算重组
            if f.consecutive_negative_cash_days >= 30 and f_cash < -5.0:
                f.status = "bankrupt"
                f.reorganize_days_left = 30
                events.append(f"🚨 【重大司法破产出清】{f.name}严重资不抵债，正式宣告破产清算并进入为期30天的司法重组！全社会落后产能强制出清！")
                # 银行坏账核销 (SFC 资产负债表出清平衡)
                if accounting_bus and hasattr(accounting_bus, "write_off_corporate_bad_debt"):
                    bad_debt = f.debt_principal + max(0.0, -f_cash)
                    if bad_debt > 0.01:
                        if hasattr(accounting_bus, "accounts") and f.account_id in accounting_bus.accounts and f_cash < 0:
                            accounting_bus.accounts[f.account_id].balance = 0.0
                        actual_written = accounting_bus.write_off_corporate_bad_debt(f.account_id, bad_debt, f"核销{f.name}破产不良贷款呆账")
                        f.debt_principal = 0.0
                        f.loan_status = "loss"
                        events.append(f"⚖️ 【司法破产清算与坏账核销】商业银行对{f.name}核销坏账呆账 {actual_written:.2f} 亿元，银行资本金受到直接核减！")
            elif out_item and (out_item.domestic_price > out_item.base_price * 1.15 or cover < 15.0):
                # 市场大出清后价格暴涨唤醒复工
                f.status = "downsizing"
                events.append(f"🔥 【市场出清反弹】{out_item.name}库存见底、价格暴涨，停产的{f.name}被暴利信号唤醒复工！")

    def to_dict(self, accounting_bus: Any = None) -> Dict[str, Any]:
        """序列化供前端面板展示"""
        return {
            fid: {
                "id": f.id,
                "name": f.name,
                "category": f.category,
                "capacity": round(f.capacity_limit, 2),
                "effective_capacity": round(f.capacity_limit * (0.60 + 0.40 * (f.equipment_health / 100.0)), 2),
                "utilization": f.utilization_rate,
                "daily_output": round(f.daily_output, 2),
                "output_commodity": f.output_commodity_id,
                "revenue": round(f.daily_revenue, 3),
                "mat_cost": round(f.daily_material_cost, 3),
                "power_cost": round(f.daily_power_cost, 3),
                "wage_cost": round(f.daily_wage_cost, 3),
                "profit": round(f.daily_profit, 3),
                "workers": f.workers_employed,
                "workers_baseline": f.workers_baseline,
                "power_penalty": round(f.power_shortage_penalty, 2),
                # 真实账本与细分劳工全新字段
                "account_id": f.account_id,
                "cash_balance": round(accounting_bus.accounts[f.account_id].balance, 3) if accounting_bus and hasattr(accounting_bus, "accounts") and f.account_id in accounting_bus.accounts else 0.0,
                "labor_title": f.labor_title,
                "skill_rank": f.skill_rank,
                "primary_roles": f.primary_roles,
                "daily_payroll": round(f.daily_wage_cost, 3),
                "daily_ledger": f.daily_ledger[-8:], # 最新收支借贷凭证明细
                # Phase 1: 企业生死与出清指标
                "status": f.status,
                "status_label": "正常开工" if f.status == "operating" else (
                    "亏损减产裁员" if f.status == "downsizing" else (
                        "停产整顿中" if f.status == "suspended" else "破产重组清算中"
                    )
                ),
                "equipment_health": round(f.equipment_health, 1),
                "capital_stock": round(f.capital_stock, 2),
                "capex_spending": round(f.capex_spending_daily, 4),
                "consecutive_loss_days": f.consecutive_loss_days,
                "daily_laid_off": f.daily_laid_off,
                "daily_hired": f.daily_hired,
                "total_laid_off": f.total_laid_off,
                "reorganize_days_left": f.reorganize_days_left,
                # Phase 3: 信用评级与信贷指标
                "debt_principal": round(f.debt_principal, 2),
                "credit_rating": f.credit_rating,
                "credit_score": f.credit_score,
                "leverage_ratio": f.leverage_ratio,
                "icr": f.interest_coverage_ratio,
                "borrowing_rate": round(f.borrowing_rate * 100, 2),
                "credit_limit": round(f.credit_limit, 2),
                "loan_status": f.loan_status,
                "recalled_today": round(f.recalled_loans_today, 3)
            } for fid, f in self.factories.items()
        }
