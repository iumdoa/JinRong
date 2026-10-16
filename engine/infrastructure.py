"""
国家宏观金融体系模拟器 - 公共基建工程与科研攻坚系统 (Infrastructure & R&D System)
包含：
1. 长周期实体基建（电网、铁路高速、区域公立医疗）- 100%竣工，有持续运维费，收益逐季爬坡释放；
2. 教育与学校基建体系（增设公立学校、综合大学与重点实验室）- 增设学校大幅提高国家科研能力；
3. 概率性前沿尖端科研攻坚（袁隆平杂交水稻、创新原研药与基因疫苗、先进制程芯片）- 绝非100%，由科研能力赋能，但上限严格封顶30%，历经多年失败可多期再攻坚！
"""
import random
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any

def compute_research_success_rate(base_rate: float, research_capability: float, experience_bonus: float = 0.0) -> float:
    """
    计算前沿科研（农业良种、尖端医疗、微电子芯片）突破成功率。
    国家科研能力越高成功率越高，但根据科学规律与法定制约，最高绝对不可超过 30.0%！
    """
    # 每 1 点国家科研能力提供 +0.20% 突破概率加成
    bonus = (research_capability / 100.0) * 0.20 + experience_bonus
    # 严格封顶于 30.0% (0.30)
    return min(0.30, round(base_rate + bonus, 4))

def get_ramp_up_efficiency(quarters_post_completion: int, ramp_up_quarters: int) -> float:
    """
    收益爬坡效应（比如新建了一条路，第一年肯定没第五年走的人多）
    竣工初期释放 25% 基础效益，随着配套与人流物流融入，逐季爬坡至 100% 满负荷。
    """
    R = max(1, ramp_up_quarters)
    if quarters_post_completion <= 0:
        return 0.25
    if quarters_post_completion >= R:
        return 1.0
    return round(0.25 + 0.75 * (quarters_post_completion / R), 3)

@dataclass
class ProjectTemplate:
    id: str
    name: str
    category: str           # 'physical' (实体工业基建), 'social' (民生社会基建), 'education' (教育与学校基建), 'science' (前沿科研攻坚)
    category_name: str      # 显示名称
    total_cost: float       # 总投资预算 (亿元)
    duration_quarters: int  # 计划工期/攻坚周期 (季度)
    base_success_rate: float # 基础成功率 (实体/教育为 1.0 即 100%；科研攻坚为 0.06~0.10)
    daily_maintenance_cost: float # 建成投产后的每日运维/维护成本 (亿元/天)
    ramp_up_quarters: int   # 建成后效益全面爬坡释放周期 (季度, 例如 4~8 季度)
    schools_granted: int    # 建成后增设的公立学校/院所数量 (增设学校直接增强科研能力)
    research_boost: float   # 建成后增加的国家科研能力点数
    intro: str              # 背景与立项说明
    returns_desc: str       # 回报或技术突破收益说明
    buffs: Dict[str, float] = field(default_factory=dict) # 成功后的量化属性增益 (满负荷标准值)
    materials_required_daily: Dict[str, float] = field(default_factory=dict) # 施工攻坚期间每日所需实物物资配额
    
    # 科研多期攻关跟踪 (袁隆平式历经多期试验)
    attempt: int = 1
    failed_attempts: int = 0
    experience_bonus: float = 0.0

    @property
    def cost_per_quarter(self) -> float:
        return round(self.total_cost / max(1, self.duration_quarters), 2)
        
    @property
    def cost_per_day(self) -> float:
        return round(self.total_cost / (max(1, self.duration_quarters) * 90), 4)

@dataclass
class ActiveProject:
    id: str
    template_id: str
    name: str
    category: str
    category_name: str
    total_cost: float
    duration_quarters: int
    cost_per_day: float
    daily_maintenance_cost: float
    ramp_up_quarters: int
    base_success_rate: float
    success_rate: float     # 开工时基于科研能力核定的突破率 (上限30%)
    schools_granted: int
    research_boost: float
    attempt: int
    intro: str
    returns_desc: str
    buffs: Dict[str, float]
    materials_required_daily: Dict[str, float] = field(default_factory=dict)
    materials_shortage: bool = False
    
    # 施工/研发进度跟踪
    days_elapsed: int = 0
    quarters_elapsed: int = 0
    funds_spent: float = 0.0
    status: str = "constructing" # 'constructing', 'completed', 'failed'
    status_text: str = "正常建设/攻坚中"

def get_project_templates() -> Dict[str, ProjectTemplate]:
    """定义国家可选立项的重大公共工程、教育学校与尖端科研攻坚库"""
    return {
        # ==========================================
        # 1. 实体工业基建 (100% 竣工，有日常运维费，收益逐步爬坡释放)
        # ==========================================
        "grid_energy": ProjectTemplate(
            id="grid_energy",
            name="国家特高压骨干电网与清洁能源枢纽",
            category="physical",
            category_name="实体工业基建",
            total_cost=120.0,
            duration_quarters=8,   # 2年工期
            base_success_rate=1.0, # 实体基建 100% 竣工
            daily_maintenance_cost=0.028, # 约10亿/年线损与巡检维护费
            ramp_up_quarters=6,    # 建成后并网负荷需 6 季爬坡释放
            schools_granted=0,
            research_boost=0.0,
            intro="重组国家电力主干网，兴建大型水电机组与清洁变电站，彻底解决全国工商业拉闸限电与高用电成本。",
            returns_desc="工商业综合电力成本降低 25%，陈厂长等实体企业营业成本下降 12%，国家工业总产能上限提升 220 亿元 (效益随用电负荷逐季爬坡释放，日维护费 0.028 亿)！",
            buffs={
                "capacity_bonus": 220.0,
                "corp_cost_discount": 0.12
            },
            materials_required_daily={"steel": 0.12, "cement": 0.15, "hardware": 0.08}
        ),
        
        "rail_highway": ProjectTemplate(
            id="rail_highway",
            name="国家跨省高速铁路与多式联运大通道",
            category="physical",
            category_name="实体工业基建",
            total_cost=180.0,
            duration_quarters=12,  # 3年工期
            base_success_rate=1.0,
            daily_maintenance_cost=0.040, # 路网养护维保 0.040 亿/天
            ramp_up_quarters=8,    # 建成后客流物流需 8 季爬坡（第一年车流少，第五年达峰）
            schools_granted=0,
            research_boost=0.0,
            intro="打通全国核心经济圈干线铁路，建设集装箱枢纽。建设期吸纳底层劳工就业，建成后全社会商品流通速度显著加快。",
            returns_desc="建设期吸纳 2.5 万劳工就业；全社会物流成本显著降低，年化 GDP 稳步拉升 120 亿元 (第一年车流少，效益随客货运流逐步爬坡释放，日维护费 0.040 亿)！",
            buffs={
                "gdp_boost": 120.0,
                "employed_hired_construction": 25_000
            },
            materials_required_daily={"steel": 0.25, "cement": 0.35, "hardware": 0.12}
        ),
        
        # ==========================================
        # 2. 教育与学校基建 (增设学校大幅提升国家科研能力，有办学维护费)
        # ==========================================
        "basic_schools": ProjectTemplate(
            id="basic_schools",
            name="全国公立基础义务教育网与希望校舍",
            category="education",
            category_name="教育与科研基建",
            total_cost=45.0,
            duration_quarters=4,   # 1年工期
            base_success_rate=1.0,
            daily_maintenance_cost=0.015, # 教师工资与校舍维护
            ramp_up_quarters=4,
            schools_granted=80,    # 增设 80 所基础公立学校
            research_boost=15.0,   # 国家科研能力提升 +15.0 点
            intro="面向广大农村与工薪社区普及公立基础教育，免除学杂费。增设学校打牢全社会基础识字与劳动技能底座。",
            returns_desc="全国新增 80 所公立学校，国家科研能力底座永久提升 +15.0 点！普工基本文化素养提升，最低法定日薪支持空间提升 4 元 (日办学维护费 0.015 亿)！",
            buffs={
                "research_boost": 15.0,
                "min_wage_upgrade": 4.0
            },
            materials_required_daily={"steel": 0.03, "cement": 0.06, "hardware": 0.02}
        ),
        
        "university_campus": ProjectTemplate(
            id="university_campus",
            name="国家一流综合大学与前沿重点实验室集群",
            category="education",
            category_name="教育与科研基建",
            total_cost=90.0,
            duration_quarters=8,   # 2年工期
            base_success_rate=1.0,
            daily_maintenance_cost=0.032, # 科研经费与高校日常运营
            ramp_up_quarters=6,    # 学术梯队成型需 6 季爬坡
            schools_granted=20,    # 增设 20 所大学与重点国家实验室
            research_boost=35.0,   # 国家科研能力暴增 +35.0 点
            intro="兴建顶尖高等学府与国家级前沿实验室，重金延揽学者教授，培育青年学者，全方位强化国家科研能力，为农业、医疗与科技攻关提供智力引擎。",
            returns_desc="新增 20 所综合大学与国家实验室，国家科研能力暴增 +35.0 点！大幅拉高农业育种、尖端医疗靶向药及光刻芯片的研发突破概率 (日高校维护费 0.032 亿)！",
            buffs={
                "research_boost": 35.0
            },
            materials_required_daily={"steel": 0.05, "cement": 0.08, "hardware": 0.03}
        ),
        
        "vocational_edu": ProjectTemplate(
            id="vocational_edu",
            name="现代职业技术实训基地与公立工程学院",
            category="education",
            category_name="教育与科研基建",
            total_cost=60.0,
            duration_quarters=6,   # 1.5年工期
            base_success_rate=1.0,
            daily_maintenance_cost=0.020,
            ramp_up_quarters=4,
            schools_granted=40,    # 增设 40 所实训技术院校
            research_boost=12.0,   # 国家科研能力提升 +12.0 点
            intro="普及现代机械、电气及数字技能实训，培养紧缺的高素质蓝领工匠与应用型工程技术人员。",
            returns_desc="全国新增 40 所职业工程院校，科研工程化能力 +12.0 点！劳工日薪上限由 38元 提升至 48元，结构性失业率下降 3.5% (日办学维护费 0.020 亿)！",
            buffs={
                "research_boost": 12.0,
                "min_wage_upgrade": 8.0,
                "unemployment_relief": 0.035
            },
            materials_required_daily={"steel": 0.04, "cement": 0.07, "hardware": 0.03}
        ),
        
        # ==========================================
        # 3. 民生社会基建 (100% 竣工，有维护费，收益逐季爬坡)
        # ==========================================
        "public_hospital": ProjectTemplate(
            id="public_hospital",
            name="国家区域三甲公立医疗中心与基层卫生网",
            category="social",
            category_name="民生社会基建",
            total_cost=80.0,
            duration_quarters=8,   # 2年工期
            base_success_rate=1.0,
            daily_maintenance_cost=0.026, # 医疗设备折旧与日常运转补贴
            ramp_up_quarters=6,    # 门诊接诊量逐季爬坡
            schools_granted=0,
            research_boost=0.0,
            intro="兴建公立综合医疗中心，覆盖基层社区卫生所，配置平价救命药源，从根源上降低老百姓大病返贫概率。",
            returns_desc="公立医疗供给大幅增加，居民因病致贫率永久削减 6.0%，大病自费支出骤降，群众消费意向提升 +12 点 (门诊量逐步爬坡，日维护费 0.026 亿)！",
            buffs={
                "poverty_reduction": 0.06,
                "sentiment_bonus": 12.0
            },
            materials_required_daily={"steel": 0.04, "cement": 0.06, "hardware": 0.03}
        ),
        
        # ==========================================
        # 4. 前沿尖端科研攻坚 (农业、医疗、科技：绝非100%！基础突破率低，科研能力赋能，最高严格封顶30%，失败可多期再攻坚！)
        # ==========================================
        "agri_hybrid_rice": ProjectTemplate(
            id="agri_hybrid_rice",
            name="袁隆平杂交水稻与抗旱高产农业育种攻坚",
            category="science",
            category_name="前沿农业科研",
            total_cost=45.0,
            duration_quarters=6,   # 1.5年/期
            base_success_rate=0.10,# 基础成功率仅 10.0% (前沿育种极度艰险)
            daily_maintenance_cost=0.008, # 良种试验田推广维护
            ramp_up_quarters=4,    # 良种推广需 4 季播种爬坡
            schools_granted=0,
            research_boost=0.0,
            intro="【袁隆平式科学攻坚】攻关三系杂交水稻与分子抗旱育种。前沿生物育种历经数代试验，中途经历过无数次失败！科研能力越高成功率越高，但法定严格封顶 30%！若攻坚受挫，试验数据将保留，支持开启下一期攻坚！",
            returns_desc="【突破成功】全国主粮亩产革命性暴涨，一日基础便当物价由 15.0元 断崖下跌至 11.2元 (-25%)，恩格尔系数暴跌，告别饥荒！\n【攻关受挫】走入技术瓶颈，资金沉没，但沉淀试验数据，支持开展第 2 期攻关。",
            buffs={
                "food_price_discount": 0.25,
                "engel_direct_relief": 0.06
            },
            materials_required_daily={"fertilizer": 0.02}
        ),
        
        "medical_cutting_edge": ProjectTemplate(
            id="medical_cutting_edge",
            name="国家重大疾病创新原研靶向药与基因疫苗攻坚",
            category="science",
            category_name="尖端医疗科研",
            total_cost=65.0,
            duration_quarters=8,   # 2年/期
            base_success_rate=0.08,# 基础成功率仅 8.0% (临床双盲极高淘汰率)
            daily_maintenance_cost=0.010, # GMP公立药厂维保
            ramp_up_quarters=4,
            schools_granted=0,
            research_boost=0.0,
            intro="【医疗科研绝非100%】组织全国顶尖医学院攻坚恶性肿瘤靶向药与心脑血管原研分子。新药研发极具风险，多轮双盲试验淘汰率极高！科研能力越高成功率越高，最高上限 30%！失败可发起下一期临床攻坚。",
            returns_desc="【突破成功】攻克关键救命药专利壁垒，平价新药全额纳入公立医保，大病自费率锐减，居民因病致贫率永久削减 8.0%！\n【攻关受挫】临床阶段未达终点，研发预算沉没，支持发起第 2 期攻关。",
            buffs={
                "poverty_reduction": 0.08,
                "sentiment_bonus": 8.0
            },
            materials_required_daily={"medicine": 0.01}
        ),
        
        "chip_semiconductor": ProjectTemplate(
            id="chip_semiconductor",
            name="先进制程光刻机与高精度工业母机技术攻坚",
            category="science",
            category_name="尖端科技科研",
            total_cost=110.0,
            duration_quarters=10,  # 2.5年/期
            base_success_rate=0.06,# 基础成功率仅 6.0% (工业皇冠技术壁垒)
            daily_maintenance_cost=0.020,
            ramp_up_quarters=6,
            schools_granted=0,
            research_boost=0.0,
            intro="【工业皇冠核心攻坚】集中力量突破纳米级光学光源与超高精五轴工业母机。遭遇尖端工艺瓶颈，突破极难！科研能力越高成功率越高，最高不得超过 30%！失败可发起下一期攻坚。",
            returns_desc="【突破成功】高端制造附加值暴涨，陈厂长等实体企业利润直接翻倍，国家工业总产能上限暴增 320 亿元！\n【攻关受挫】良品率未达标，资金沉没，但保留研发图纸，支持发起下一期攻坚。",
            buffs={
                "capacity_bonus": 320.0,
                "firm_profit_multiplier": 1.5
            },
            materials_required_daily={"hardware": 0.02, "chips": 0.01}
        )
    }

class InfrastructureManager:
    """国家公共基建与科研项目工程局"""
    def __init__(self, rng_seed: int = 42):
        self.rng = random.Random(rng_seed)
        self.templates: Dict[str, ProjectTemplate] = get_project_templates()
        self.active_projects: Dict[str, ActiveProject] = {}
        self.completed_projects: List[Dict[str, Any]] = []
        self.failed_projects: List[Dict[str, Any]] = []
        
        # 财政直接增设学校的额外办学维护费
        self.direct_school_maintenance: float = 0.0
        
        # 财政向高校与科研机构拨付的专项科研经费 (到期加持消失)
        self.active_research_grant: Dict[str, Any] = {
            "tier_id": "",
            "tier_name": "",
            "cost": 0.0,
            "boost": 0.0,
            "duration_days": 0,
            "days_left": 0,
            "is_active": False
        }
        
        # 累计永久生效的加成池 (已根据各项目的爬坡效率动态加权缩放)
        self.accumulated_buffs: Dict[str, float] = self._empty_buffs()

    def _empty_buffs(self) -> Dict[str, float]:
        return {
            "capacity_bonus": 0.0,
            "corp_cost_discount": 0.0,
            "gdp_boost": 0.0,
            "poverty_reduction": 0.0,
            "sentiment_bonus": 0.0,
            "min_wage_upgrade": 0.0,
            "unemployment_relief": 0.0,
            "food_price_discount": 0.0,
            "engel_direct_relief": 0.0,
            "research_boost": 0.0,
            "firm_profit_multiplier": 1.0,
            "employed_hired_construction": 0.0
        }

    def start_project(self, template_id: str, current_research_capability: float = 12.0) -> tuple[bool, str]:
        if template_id not in self.templates:
            return False, "未找到该项目规划案。"
            
        tpl = self.templates[template_id]
        
        # 检查是否已在建
        if template_id in self.active_projects:
            return False, f"工程【{tpl.name}】已在施工/研发中，不可重复立项！"
            
        # 检查是否已建成（实体基建不可重复立项，科研项目若失败过允许开启下一期攻坚，已突破成功的不可重复立项）
        for c in self.completed_projects:
            if c["template_id"] == template_id:
                return False, f"【{tpl.name}】已大获全胜/竣工投产，其巨大红利正在源源不断反哺国家！"
                
        # 槽位限制：最多同时推进 3 项重大国家工程
        if len(self.active_projects) >= 3:
            return False, "国家财政工程局同时在建重大项目已达上限 (最多同时推进 3 项重大国家工程)！"
            
        # 计算当前核定的突破成功率 (实体为1.0，科研攻坚由科研能力加成，但最高封顶30%)
        if tpl.category == "science":
            eff_rate = compute_research_success_rate(tpl.base_success_rate, current_research_capability, tpl.experience_bonus)
            phase_info = f" (第 {tpl.attempt} 期攻关，当前科研能力赋能突破率: {eff_rate*100:.1f}%，最高限额30%)"
        else:
            eff_rate = 1.0
            phase_info = " (确定保竣工 100%)"

        proj = ActiveProject(
            id=f"{template_id}_a{tpl.attempt}",
            template_id=template_id,
            name=tpl.name if tpl.attempt == 1 else f"{tpl.name} (第{tpl.attempt}期)",
            category=tpl.category,
            category_name=tpl.category_name,
            total_cost=tpl.total_cost,
            duration_quarters=tpl.duration_quarters,
            cost_per_day=tpl.cost_per_day,
            daily_maintenance_cost=tpl.daily_maintenance_cost,
            ramp_up_quarters=tpl.ramp_up_quarters,
            base_success_rate=tpl.base_success_rate,
            success_rate=eff_rate,
            schools_granted=tpl.schools_granted,
            research_boost=tpl.research_boost,
            attempt=tpl.attempt,
            intro=tpl.intro,
            returns_desc=tpl.returns_desc,
            buffs=tpl.buffs.copy(),
            materials_required_daily=tpl.materials_required_daily.copy(),
            status="constructing",
            status_text=f"正常建设/攻关中{phase_info}"
        )
        self.active_projects[template_id] = proj
        return True, f"国家重大规划【{proj.name}】正式批复立项！预计周期 {tpl.duration_quarters} 季度，每日自国库划拨预算 {proj.cost_per_day:.3f} 亿元。{phase_info}"

    def cancel_project(self, template_id: str) -> tuple[bool, str]:
        """停工缓建/废除工程（前期资金沉没）"""
        if template_id not in self.active_projects:
            return False, "该项目并不在开工列表中。"
            
        proj = self.active_projects.pop(template_id)
        return True, f"⚠️ 工程【{proj.name}】已被强制终止！已耗资 {proj.funds_spent:.1f} 亿元成为沉没成本。"

    def grant_research_funds(self, tier_id: str, tier_name: str, cost: float, boost: float, duration_days: int) -> tuple[bool, str]:
        """向高校及科研机构拨发专项科研经费，提供限期科研能力加持 (到期后加持消失)"""
        self.active_research_grant = {
            "tier_id": tier_id,
            "tier_name": tier_name,
            "cost": cost,
            "boost": boost,
            "duration_days": duration_days,
            "days_left": duration_days,
            "is_active": True
        }
        return True, f"🔬 【科研专项拨款批复】中央财政成功划拨 {cost:.1f} 亿元专项资助【{tier_name}】！将在接下来的 {duration_days} 天内为全国科研能力提供 +{boost:.1f} 点强力加持（资助期满后加持消失）。"

    def add_direct_schools(self, count: int, daily_maint: float) -> None:
        """财政直接增设公立学校增加日常办学维护费"""
        self.direct_school_maintenance += daily_maint

    def recalculate_accumulated_buffs(self) -> None:
        """根据所有已竣工项目的实际爬坡释放度 (efficiency_rate) 动态合成宏观增益加成池"""
        new_buffs = self._empty_buffs()
        for p in self.completed_projects:
            eff = p.get("efficiency_rate", 1.0)
            buffs = p.get("buffs", {})
            for k, v in buffs.items():
                if k == "firm_profit_multiplier":
                    curr = new_buffs.get(k, 1.0)
                    new_buffs[k] = curr * (1.0 + (v - 1.0) * eff)
                else:
                    curr = new_buffs.get(k, 0.0)
                    new_buffs[k] = curr + v * eff
        self.accumulated_buffs = new_buffs

    def tick_daily(self, current_research_capability: float = 12.0, commodity_hub: Optional[Any] = None) -> tuple[float, float, List[str]]:
        """
        每日为所有在建工程扣减财政建设预算、为已竣工设施结算日常运维维护费，推进科研经费资助倒计时并推进工期与爬坡进度
        返回: (今日基建划拨建设金, 今日已建设施日常运维费, 触发事件消息列表)
        """
        total_construction_cost = 0.0
        events = []
        finished_template_ids = []
        
        # 0. 推进科研经费资助周期与到期失效机制 (拨款时间结束，加持消失)
        if self.active_research_grant.get("is_active"):
            self.active_research_grant["days_left"] -= 1
            if self.active_research_grant["days_left"] <= 0:
                self.active_research_grant["is_active"] = False
                events.append(
                    f"⌛ 【科研经费资助期届满】前沿科技专项拨款【{self.active_research_grant['tier_name']}】资助周期已正式结束！"
                    f"临时科研能力加持 (+{self.active_research_grant['boost']:.1f} 点) 已失效。如需维持高突破率，请内阁重新审批拨款。"
                )
        
        # 1. 推进在建重大工程
        for template_id, proj in list(self.active_projects.items()):
            # 检查实物物料配给是否满足
            is_material_short = False
            missing_items = []
            if commodity_hub is not None and proj.materials_required_daily:
                for cid, req_amt in proj.materials_required_daily.items():
                    got_amt, satisfied = commodity_hub.consume_project(cid, req_amt)
                    if not satisfied:
                        is_material_short = True
                        cname = commodity_hub.commodities[cid].name if cid in commodity_hub.commodities else cid
                        missing_items.append(cname)
            
            if is_material_short:
                proj.materials_shortage = True
                proj.status_text = f"⚠️ 缺少【{'、'.join(missing_items)}】待料停工中"
                if proj.days_elapsed % 30 == 0:
                    events.append(f"⚠️ 【工程缺料停工】国家重大项目【{proj.name}】因国内【{'、'.join(missing_items)}】商业现货库存枯竭，工程被迫停工待料！请尽快扩大相关工厂产能！")
                cost = round(proj.cost_per_day * 0.15, 4) # 仅保留现场看护基础开支
                total_construction_cost += cost
                proj.funds_spent += cost
                continue
            else:
                proj.materials_shortage = False
                if proj.status == "constructing" and "待料停工" in proj.status_text:
                    proj.status_text = "正常建设/攻关中"

            cost = proj.cost_per_day
            total_construction_cost += cost
            proj.funds_spent += cost
            proj.days_elapsed += 1
            
            # 动态更新科研项目最新突破率（随国家增设学校/科研能力动态提升，但最高封顶30%）
            if proj.category == "science":
                tpl = self.templates[template_id]
                proj.success_rate = compute_research_success_rate(tpl.base_success_rate, current_research_capability, tpl.experience_bonus)
            
            # 季度进度节点播报 (每90天)
            if proj.days_elapsed % 90 == 0:
                proj.quarters_elapsed += 1
                q_left = proj.duration_quarters - proj.quarters_elapsed
                if q_left > 0:
                    events.append(f"🏗️ 重大项目【{proj.name}】已完成第 {proj.quarters_elapsed} 阶段攻坚施工，剩余 {q_left} 季度。")
                    
            # 检查是否工期届满
            total_target_days = proj.duration_quarters * 90
            if proj.days_elapsed >= total_target_days:
                finished_template_ids.append(template_id)

        # 2. 结算届满的项目（实体保竣工 100%，尖端科研概率突破 <=30%）
        for tid in finished_template_ids:
            proj = self.active_projects.pop(tid)
            tpl = self.templates[tid]
            
            if proj.category == "science":
                # 科研攻坚概率判定 (袁隆平式探索，绝非100%)
                final_success_rate = compute_research_success_rate(tpl.base_success_rate, current_research_capability, tpl.experience_bonus)
                roll = self.rng.random()
                is_success = roll <= final_success_rate
            else:
                # 实体工业与教育民生基建 100% 竣工投产
                is_success = True
                
            if is_success:
                proj.status = "completed"
                proj.status_text = "🎉 竣工投产 / 核心技术重大突破！"
                completed_entry = {
                    "template_id": tid,
                    "name": proj.name,
                    "category": proj.category,
                    "category_name": proj.category_name,
                    "total_cost": proj.total_cost,
                    "daily_maintenance_cost": proj.daily_maintenance_cost,
                    "ramp_up_quarters": proj.ramp_up_quarters,
                    "quarters_post_completion": 0,
                    "days_post_completion": 0,
                    "efficiency_rate": 0.25, # 投产初期释放 25% 基础效益（路网刚通车/良种刚推广）
                    "buffs": proj.buffs,
                    "returns_desc": proj.returns_desc,
                    "schools_granted": proj.schools_granted,
                    "research_boost": proj.research_boost,
                    "breakthrough": True
                }
                self.completed_projects.append(completed_entry)
                
                # 若为教育基建增设了学校，提升模板状态
                tpl.attempt += 1
                
                if proj.category == "science":
                    msg = (f"🎊 【尖端科研历史性重大突破】历经艰险攻关，重大课题【{proj.name}】成功攻克核心理论与工艺难题！"
                           f"（突破概率: {proj.success_rate*100:.1f}%，最高限额30%）\n"
                           f"收益兑现：{proj.returns_desc.splitlines()[0]}")
                elif proj.category == "education":
                    msg = (f"🎓 【国家教育体系重大里程碑】重大工程【{proj.name}】正式落成！全国新增学校/院所 {proj.schools_granted} 所，"
                           f"国家综合科研能力提升 +{proj.research_boost:.1f} 点！每日办学维护成本 {proj.daily_maintenance_cost:.3f} 亿元。")
                else:
                    msg = (f"🎊 【国家重大喜讯】重大工程【{proj.name}】正式全面竣工！"
                           f"效益将随客流/负荷在接下来的 {proj.ramp_up_quarters} 个季度内逐步爬坡释放至 100% 满负荷，每日基础设施维护费 {proj.daily_maintenance_cost:.3f} 亿元。")
                events.append(msg)
            else:
                # 科研攻坚阶段性受挫 (如袁隆平早期多代杂交水稻探索受阻)
                proj.status = "failed"
                proj.status_text = "❌ 攻关受阻，未达到指标"
                tpl.attempt += 1
                tpl.failed_attempts += 1
                # 失败沉淀宝贵试验数据 (为下一期提供 +1.5% 基础经验累积，但总率仍严受30%封顶)
                tpl.experience_bonus += 0.015
                
                self.failed_projects.append({
                    "template_id": tid,
                    "name": proj.name,
                    "attempt": proj.attempt,
                    "category_name": proj.category_name,
                    "funds_lost": proj.funds_spent,
                    "experience_gained": "+1.5% 核心试验数据积累",
                    "reason": "未达到核心良品率与生物性状预期，但保留了宝贵基因图谱与试制经验"
                })
                msg = (f"⚠️ 【科研攻坚受挫】前沿科研工程【{proj.name}】在最后阶段攻坚未达预期指标，试验走入理论死胡同！"
                       f"投入的 {proj.funds_spent:.1f} 亿元预算沉没。但正如袁隆平历经多年攻坚杂交水稻，科研团队已沉淀宝贵试验数据，"
                       f"随时可在候选库启动【第 {tpl.attempt} 期攻关】！")
                events.append(msg)

        # 3. 推进已竣工项目的日常运维费用与收益爬坡周期 (新建路第一年走的人少，第五年走的人多)
        total_maintenance_cost = self.direct_school_maintenance
        for p in self.completed_projects:
            total_maintenance_cost += p.get("daily_maintenance_cost", 0.0)
            p["days_post_completion"] = p.get("days_post_completion", 0) + 1
            
            # 季度爬坡推进
            if p["days_post_completion"] % 90 == 0:
                p["quarters_post_completion"] = p.get("quarters_post_completion", 0) + 1
                p["efficiency_rate"] = get_ramp_up_efficiency(p["quarters_post_completion"], p.get("ramp_up_quarters", 4))
                if p["efficiency_rate"] >= 1.0 and p.get("quarters_post_completion", 0) == p.get("ramp_up_quarters", 4):
                    events.append(f"📈 【工程效益完全达峰】已建工程【{p['name']}】经过充分整合与客流负荷爬坡，今日正式达到 100% 满负荷运营状态！")

        # 4. 重新计算当前所有竣工项目的爬坡加权增益
        self.recalculate_accumulated_buffs()

        return round(total_construction_cost, 4), round(total_maintenance_cost, 4), events
