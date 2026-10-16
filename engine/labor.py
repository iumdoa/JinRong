"""
国家六级专业技能劳动力体系与国民技工培训升阶模型
包括各工种就业供求匹配、职业技能培训转化与薪资阶梯
"""
from dataclasses import dataclass
from typing import Dict, Any, List

@dataclass
class LaborSkillTier:
    """专业技能工种实体"""
    id: str
    name: str
    total_population: int      # 该技能工种总人口
    labor_force: int           # 适龄劳动人口
    employed: int              # 当前在岗受雇人数
    daily_wage: float          # 行业基准日薪 (元/天)
    skill_rank: int            # 技能等级 (1:非熟练体力 -> 5:高精尖工程专家)
    description: str

    @property
    def unemployment_rate(self) -> float:
        if self.labor_force <= 0:
            return 0.0
        return max(0.0, 1.0 - (self.employed / self.labor_force))

class LaborManager:
    """国家人力资源与劳动就业管理总局"""
    def __init__(self, total_population: int = 10_000_000):
        # 1000万人口国家的专业化职业技能结构
        self.tiers: Dict[str, LaborSkillTier] = {
            "miner_heavy": LaborSkillTier(
                id="miner_heavy",
                name="采矿与重体力劳工 (老张主力)",
                total_population=int(total_population * 0.22), # 220万
                labor_force=int(total_population * 0.22 * 0.65),
                employed=int(total_population * 0.22 * 0.65 * 0.72),
                daily_wage=38.0,
                skill_rank=1,
                description="从事煤矿开采、铁矿装卸、基础建设工地重体力搬运"
            ),
            "farmer": LaborSkillTier(
                id="farmer",
                name="农耕自耕农与种植散工",
                total_population=int(total_population * 0.24), # 240万
                labor_force=int(total_population * 0.24 * 0.60),
                employed=int(total_population * 0.24 * 0.60 * 0.85),
                daily_wage=32.0,
                skill_rank=1,
                description="农村粮田种植、经济作物培育与基础灌溉农林作业"
            ),
            "operator_light": LaborSkillTier(
                id="operator_light",
                name="轻工制造流水线操作工",
                total_population=int(total_population * 0.20), # 200万
                labor_force=int(total_population * 0.20 * 0.62),
                employed=int(total_population * 0.20 * 0.62 * 0.88),
                daily_wage=52.0,
                skill_rank=2,
                description="服装纺织、食品精炼包装、日用五金总装流水线操作"
            ),
            "technician_skilled": LaborSkillTier(
                id="technician_skilled",
                name="熟练数控车铣技工 (陈厂长顶梁柱)",
                total_population=int(total_population * 0.14), # 140万
                labor_force=int(total_population * 0.14 * 0.65),
                employed=int(total_population * 0.14 * 0.65 * 0.94),
                daily_wage=115.0,
                skill_rank=3,
                description="八级车铣钳工、数控机床编程、高精模具铸造与机床实操"
            ),
            "white_collar": LaborSkillTier(
                id="white_collar",
                name="白领财务、管理与商业文职 (李会计主力)",
                total_population=int(total_population * 0.15), # 150万
                labor_force=int(total_population * 0.15 * 0.62),
                employed=int(total_population * 0.15 * 0.62 * 0.92),
                daily_wage=105.0,
                skill_rank=4,
                description="企业成本核算、报税审计、供应链跟单与行政运营"
            ),
            "engineer_expert": LaborSkillTier(
                id="engineer_expert",
                name="工业电气工程师与科研专家",
                total_population=int(total_population * 0.05), # 50万
                labor_force=int(total_population * 0.05 * 0.60),
                employed=int(total_population * 0.05 * 0.60 * 0.97),
                daily_wage=280.0,
                skill_rank=5,
                description="特高压电网调度、高炉冶金调优、尖端杂交水稻与光刻研发"
            )
        }
        
    def train_and_upgrade_skills(self, vocational_school_count: int, university_count: int) -> List[str]:
        """
        根据技校与综合大学办学规模，定期将普工升阶培训为熟练技工，技师深造为工程师
        """
        events = []
        # 职校实训基地：将轻工普工升阶为高级技工
        if vocational_school_count > 0:
            upgrade_count = int(vocational_school_count * 150) # 每所职校每季培训150名熟练技师
            avail = min(self.tiers["operator_light"].labor_force - self.tiers["operator_light"].employed, upgrade_count)
            if avail > 50:
                self.tiers["operator_light"].total_population -= avail
                self.tiers["operator_light"].labor_force -= avail
                self.tiers["technician_skilled"].total_population += avail
                self.tiers["technician_skilled"].labor_force += avail
                self.tiers["technician_skilled"].employed += int(avail * 0.95)
                events.append(f"🛠️ 【产业工人技能升阶】全国职业技术学院实训结业，新增 {avail} 名高级数控车铣技工进驻制造车间，有效缓解了陈厂长等实体工厂的技工荒！")
                
        # 综合大学与重点实验室：培育高级工程专家
        if university_count > 0:
            engineer_graduates = int(university_count * 50)
            avail = min(self.tiers["white_collar"].labor_force - self.tiers["white_collar"].employed, engineer_graduates)
            if avail > 20:
                self.tiers["white_collar"].total_population -= avail
                self.tiers["white_collar"].labor_force -= avail
                self.tiers["engineer_expert"].total_population += avail
                self.tiers["engineer_expert"].labor_force += avail
                self.tiers["engineer_expert"].employed += int(avail * 0.98)
                events.append(f"🎓 【高层次工程人才涌现】综合大学理工学院向国家战略电网与科研攻坚项目输送了 {avail} 名青年工程师与科研专家！")
                
        return events

    def get_national_unemployment_rate(self) -> float:
        """加权全社会总体失业率"""
        total_labor = sum(t.labor_force for t in self.tiers.values())
        total_emp = sum(t.employed for t in self.tiers.values())
        if total_labor <= 0:
            return 0.05
        return max(0.01, min(0.60, 1.0 - (total_emp / total_labor)))

    def get_industrial_workforce_matrix(self, factories: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        全景生成各大工业体系下的细分产业劳工编制与薪酬矩阵
        体现具体工种岗位、技能阶层、在册人数、基准日薪与直接发薪专户
        """
        matrix = []
        if factories:
            for fid, f in factories.items():
                tier_id = getattr(f, "primary_labor_tier", "")
                tier = self.tiers.get(tier_id)
                workers = getattr(f, "workers_employed", 0)
                wage = tier.daily_wage if tier else 50.0
                daily_payroll = getattr(f, "daily_wage_cost", round((workers * wage) / 100_000_000.0, 4))
                util = getattr(f, "utilization_rate", 85.0)
                
                if util >= 90:
                    status_text = "🔥 订单饱满 · 三班倒满负荷"
                    status_color = "#10b981"
                elif util >= 75:
                    status_text = "🟢 产能平稳 · 双班常态开工"
                    status_color = "#38bdf8"
                else:
                    status_text = "⚠️ 原料或电费受限 · 降负荷开工"
                    status_color = "#f59e0b"
                    
                matrix.append({
                    "industry_id": f.id,
                    "industry_name": f.name,
                    "category": f.category,
                    "account_id": getattr(f, "account_id", f"corp_{f.id}"),
                    "labor_title": getattr(f, "labor_title", "产业工人"),
                    "skill_rank": getattr(f, "skill_rank", 1),
                    "primary_roles": getattr(f, "primary_roles", []),
                    "primary_roles_str": "、".join(getattr(f, "primary_roles", [])),
                    "tier_id": tier_id,
                    "tier_name": tier.name if tier else "产业工人",
                    "workers": workers,
                    "daily_wage": wage,
                    "daily_payroll": round(daily_payroll, 3),
                    "utilization": util,
                    "status_text": status_text,
                    "status_color": status_color
                })
                
        # 补充：农业现代种植体系劳工
        farmer_tier = self.tiers.get("farmer")
        if farmer_tier:
            matrix.append({
                "industry_id": "agriculture_grain",
                "industry_name": "国家现代农业与粮棉油高产农林体系",
                "category": "agriculture",
                "account_id": "corp_food_processing",
                "labor_title": "现代农机手与农田粮油种植工",
                "skill_rank": 1,
                "primary_roles": ["大型联合收割机驾驶员", "农田水利灌溉管护工", "高产杂交稻良种育秧工"],
                "primary_roles_str": "大型联合收割机驾驶员、农田水利灌溉管护工、高产杂交稻良种育秧工",
                "tier_id": "farmer",
                "tier_name": farmer_tier.name,
                "workers": farmer_tier.employed,
                "daily_wage": farmer_tier.daily_wage,
                "daily_payroll": round((farmer_tier.employed * farmer_tier.daily_wage) / 100_000_000.0, 3),
                "utilization": 95.0,
                "status_text": "🌾 稳产保供 · 春耕秋收常态化运作",
                "status_color": "#10b981"
            })
            
        # 补充：城市商贸流通与财务管理文职体系 (李会计主力)
        white_tier = self.tiers.get("white_collar")
        if white_tier:
            matrix.append({
                "industry_id": "commercial_logistics",
                "industry_name": "全社会综合供应链、商贸流通与财务结算体系",
                "category": "commercial",
                "account_id": "corp_commercial",
                "labor_title": "企业成本总账会计与供应链运营专员",
                "skill_rank": 4,
                "primary_roles": ["李会计对标企业总账会计", "大宗物资供应链调度专员", "银企清算与税务统筹员"],
                "primary_roles_str": "李会计对标企业总账会计、大宗物资供应链调度专员、银企清算与税务统筹员",
                "tier_id": "white_collar",
                "tier_name": white_tier.name,
                "workers": white_tier.employed,
                "daily_wage": white_tier.daily_wage,
                "daily_payroll": round((white_tier.employed * white_tier.daily_wage) / 100_000_000.0, 3),
                "utilization": 92.0,
                "status_text": "💼 商业流转活跃 · 财会结算高效运转",
                "status_color": "#a78bfa"
            })
            
        return matrix

    def to_dict(self, factories: Dict[str, Any] = None) -> Dict[str, Any]:
        """序列化输出 (兼具六级工种与各大工业体系细分劳工全景)"""
        res = {
            tid: {
                "id": t.id,
                "name": t.name,
                "total_pop": t.total_population,
                "labor_force": t.labor_force,
                "employed": t.employed,
                "unemployed": t.labor_force - t.employed,
                "unemployment_rate": round(t.unemployment_rate * 100.0, 1),
                "wage": t.daily_wage,
                "skill_rank": t.skill_rank
            } for tid, t in self.tiers.items()
        }
        res["industrial_matrix"] = self.get_industrial_workforce_matrix(factories)
        return res
