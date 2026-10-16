"""
国家战略大宗实物物资大盘与国内商品供求流转中枢
包含物料守恒平衡方程、现货价格发现机制与安全库存预警
"""
from dataclasses import dataclass, field
from typing import Dict, Any, List, Tuple
import math

@dataclass
class CommodityItem:
    """战略大宗实物商品"""
    id: str
    name: str
    category: str                   # "energy", "raw_material", "equipment", "consumer", "hightech"
    unit: str                       # 实物计量单位
    stock: float                    # 当前国内商业与周转库存
    base_stock: float               # 正常稳态周转基准库存
    domestic_price: float           # 国内本币现货指导价 (元/单位)
    base_price: float               # 基期物价
    import_price_usd: float         # 国际离岸进口现货参考价 (美元/单位)
    
    # 每日动态物料流水台账
    daily_production: float = 0.0   # 今日国内工厂开采与生产量
    daily_imports: float = 0.0      # 今日海关报关进口量
    daily_consumed_factories: float = 0.0  # 工厂作为原材料中间品消耗
    daily_consumed_households: float = 0.0 # 百姓家庭民生消费消耗
    daily_consumed_projects: float = 0.0   # 国家重大基建工程调拨消耗
    daily_exports: float = 0.0      # 海关报关出口外销
    last_day_demand: float = 1.0    # 近日全社会日均实际需求量 (供排产决策参考)
    
    # 宏观出清与动态供求寻优指标
    clearance_status: str = "🟢 稳态出清"
    clearance_rate: float = 100.0          # 订单与消费满足出清率 (%)
    market_commentary: str = "供求平衡度高，现货价格在基准线附近窄幅出清。"
    
    # 自动贸易与进出口平准方针配置 (针对二级制造商品与一般大宗)
    is_secondary: bool = True               # 是否为二级制造商品 (False表示初级原料或公用事业)
    auto_trade_enabled: bool = True         # 是否开启自动贸易进出口
    auto_import_cover_days: float = 12.0    # 商业周转低于此天数，自动外汇进口保供
    auto_export_cover_days: float = 38.0    # 商业周转高于此天数，自动海关商检外销出口
    max_daily_import: float = 0.50          # 单日最大自动进口限额 (实物单位)
    max_daily_export: float = 0.50          # 单日最大自动出口限额 (实物单位)
    
    # 动态演化时序历史 (维持最近 30 天轨迹)
    price_history: List[float] = field(default_factory=list)
    supply_history: List[float] = field(default_factory=list)
    demand_history: List[float] = field(default_factory=list)
    stock_history: List[float] = field(default_factory=list)
    cover_history: List[float] = field(default_factory=list)

    def __post_init__(self):
        if not self.price_history:
            self.price_history = [round(self.base_price, 2)] * 15
        if not self.supply_history:
            self.supply_history = [round(self.last_day_demand, 2)] * 15
        if not self.demand_history:
            self.demand_history = [round(self.last_day_demand, 2)] * 15
        if not self.stock_history:
            self.stock_history = [round(self.stock, 2)] * 15
        if not self.cover_history:
            self.cover_history = [round(self.inventory_cover_days, 1)] * 15

    @property
    def total_daily_supply(self) -> float:
        return self.daily_production + self.daily_imports
        
    @property
    def total_daily_demand(self) -> float:
        return self.daily_consumed_factories + self.daily_consumed_households + self.daily_consumed_projects + self.daily_exports
        
    @property
    def inventory_cover_days(self) -> float:
        """库存可支撑天数 (根据近日常态化需求平滑核算)"""
        if self.id == "electricity":
            # 电力为即时平衡能源，储能有上限(30亿度)，安全度取决于【日发电能力 vs 日用电需求】的备用率
            eff_demand = self.total_daily_demand if self.total_daily_demand > 0.01 else self.last_day_demand
            reserve_ratio = self.daily_production / max(0.1, eff_demand)
            if reserve_ratio >= 1.25:
                return 32.0 # 发电能力大幅富余
            elif reserve_ratio >= 1.05:
                return 25.0  # 发电能力正常充裕
            elif reserve_ratio >= 0.98:
                return 18.0  # 供求紧平衡
            else:
                return round(max(0.5, reserve_ratio * 15.0), 1) # 缺电拉闸
        demand = self.last_day_demand if self.last_day_demand > 0.01 else self.total_daily_demand
        if demand <= 0.001:
            return 999.0
        return round(self.stock / demand, 1)

class CommodityHub:
    """国家大宗商品现货交易与实物调拨中枢"""
    def __init__(self):
        self.commodities: Dict[str, CommodityItem] = {
            # 1. 基础能源与采掘矿产 (初级原材料，归入国家战略储备局储备与平准)
            "coal": CommodityItem("coal", "原煤", "energy", "万吨", 30.0, 30.0, 480.0, 480.0, 75.0, last_day_demand=2.0, is_secondary=False, auto_trade_enabled=True, auto_import_cover_days=10.0, auto_export_cover_days=45.0, max_daily_import=1.0, max_daily_export=1.0),
            "iron_ore": CommodityItem("iron_ore", "铁矿石", "raw_material", "万吨", 25.0, 25.0, 650.0, 650.0, 100.0, last_day_demand=1.8, is_secondary=False, auto_trade_enabled=True, auto_import_cover_days=12.0, auto_export_cover_days=40.0, max_daily_import=1.0, max_daily_export=1.0),
            "crude_oil": CommodityItem("crude_oil", "原油", "energy", "万桶", 15.0, 15.0, 520.0, 520.0, 80.0, last_day_demand=1.0, is_secondary=False, auto_trade_enabled=True, auto_import_cover_days=10.0, auto_export_cover_days=35.0, max_daily_import=0.5, max_daily_export=0.5),
            "copper_ore": CommodityItem("copper_ore", "铜铝有色矿", "raw_material", "万吨", 4.0, 4.0, 3800.0, 3800.0, 600.0, last_day_demand=0.20, is_secondary=False, auto_trade_enabled=True, auto_import_cover_days=10.0, auto_export_cover_days=45.0, max_daily_import=0.1, max_daily_export=0.1),
            "electricity": CommodityItem("electricity", "全社会电力", "energy", "亿度", 1.5, 1.5, 0.45, 0.45, 0.07, last_day_demand=1.3, is_secondary=False, auto_trade_enabled=False),
            
            # 2. 中游重工业与化工原材料
            "steel": CommodityItem("steel", "粗钢与工业型材", "raw_material", "万吨", 15.0, 15.0, 3200.0, 3200.0, 500.0, last_day_demand=1.3, is_secondary=False, auto_trade_enabled=True, auto_import_cover_days=10.0, auto_export_cover_days=40.0, max_daily_import=0.6, max_daily_export=0.6),
            "cement": CommodityItem("cement", "水泥建材", "raw_material", "万吨", 20.0, 20.0, 350.0, 350.0, 55.0, last_day_demand=1.4, is_secondary=True, auto_trade_enabled=True, auto_import_cover_days=12.0, auto_export_cover_days=40.0, max_daily_import=0.5, max_daily_export=0.5),
            "fertilizer": CommodityItem("fertilizer", "农用化肥", "raw_material", "万吨", 5.0, 5.0, 2100.0, 2100.0, 320.0, last_day_demand=0.10, is_secondary=True, auto_trade_enabled=True, auto_import_cover_days=12.0, auto_export_cover_days=35.0, max_daily_import=0.10, max_daily_export=0.10),
            
            # 3. 农业与大众轻工民生
            "raw_grain": CommodityItem("raw_grain", "国家原粮", "consumer", "万吨", 25.0, 25.0, 2200.0, 2200.0, 340.0, last_day_demand=1.5, is_secondary=False, auto_trade_enabled=True, auto_import_cover_days=12.0, auto_export_cover_days=40.0, max_daily_import=0.5, max_daily_export=0.5),
            "food_pack": CommodityItem("food_pack", "精炼口粮食品包", "consumer", "万吨", 12.0, 12.0, 3600.0, 3600.0, 550.0, last_day_demand=0.9, is_secondary=True, auto_trade_enabled=True, auto_import_cover_days=15.0, auto_export_cover_days=35.0, max_daily_import=0.4, max_daily_export=0.4),
            "textile": CommodityItem("textile", "纺织服装与日用百货", "consumer", "万件", 60.0, 60.0, 45.0, 45.0, 7.0, last_day_demand=6.0, is_secondary=True, auto_trade_enabled=True, auto_import_cover_days=12.0, auto_export_cover_days=38.0, max_daily_import=2.0, max_daily_export=2.5),
            "medicine": CommodityItem("medicine", "基础医疗药品耗材", "consumer", "万箱", 6.0, 6.0, 120.0, 120.0, 18.0, last_day_demand=4.0, is_secondary=True, auto_trade_enabled=True, auto_import_cover_days=12.0, auto_export_cover_days=35.0, max_daily_import=1.5, max_daily_export=1.5),
            
            # 4. 装备制造与高精尖 (二级制造商品)
            "hardware": CommodityItem("hardware", "机械五金配件与紧固件", "equipment", "万套", 12.0, 12.0, 180.0, 180.0, 28.0, last_day_demand=1.0, is_secondary=True, auto_trade_enabled=True, auto_import_cover_days=12.0, auto_export_cover_days=35.0, max_daily_import=0.4, max_daily_export=0.4),
            "heavy_machinery": CommodityItem("heavy_machinery", "重装工程机械与机床", "equipment", "台", 40.0, 40.0, 480_000.0, 480_000.0, 72_000.0, last_day_demand=3.5, is_secondary=True, auto_trade_enabled=True, auto_import_cover_days=12.0, auto_export_cover_days=35.0, max_daily_import=2.0, max_daily_export=2.0),
            "chips": CommodityItem("chips", "电子元器件与芯片", "hightech", "万片", 4.0, 4.0, 450.0, 450.0, 70.0, last_day_demand=0.30, is_secondary=True, auto_trade_enabled=True, auto_import_cover_days=12.0, auto_export_cover_days=35.0, max_daily_import=0.15, max_daily_export=0.15),
            "power_equipment": CommodityItem("power_equipment", "特高压成套变电设备", "hightech", "组", 1.0, 1.0, 18_000_000.0, 18_000_000.0, 2_800_000.0, last_day_demand=0.03, is_secondary=True, auto_trade_enabled=True, auto_import_cover_days=15.0, auto_export_cover_days=45.0, max_daily_import=0.03, max_daily_export=0.03)
        }
        
    def reset_daily_flows(self):
        """每日开始前结转前日消耗并清空单日物理流向统计"""
        for c in self.commodities.values():
            if c.total_daily_demand > 0.01:
                c.last_day_demand = round(c.last_day_demand * 0.7 + c.total_daily_demand * 0.3, 2)
            c.daily_production = 0.0
            c.daily_imports = 0.0
            c.daily_consumed_factories = 0.0
            c.daily_consumed_households = 0.0
            c.daily_consumed_projects = 0.0
            c.daily_exports = 0.0

    def produce(self, cid: str, amount: float):
        """工厂生产产出入库"""
        if cid in self.commodities and amount > 0:
            self.commodities[cid].daily_production += amount

    def consume_factory(self, cid: str, amount: float) -> float:
        """工厂生产线领料中间品消耗，返回实际满足量"""
        if cid not in self.commodities or amount <= 0:
            return 0.0
        c = self.commodities[cid]
        actual = min(c.stock + c.daily_production, amount)
        c.daily_consumed_factories += actual
        return actual

    def consume_household(self, cid: str, amount: float) -> float:
        """居民民生市场日常购买消费"""
        if cid not in self.commodities or amount <= 0:
            return 0.0
        c = self.commodities[cid]
        actual = min(c.stock + c.daily_production, amount)
        c.daily_consumed_households += actual
        return actual

    def consume_project(self, cid: str, amount: float) -> Tuple[float, bool]:
        """
        国家重大基建工程领料调拨
        返回: (实际领料量, 是否足额满足)
        """
        if cid not in self.commodities or amount <= 0:
            return 0.0, True
        c = self.commodities[cid]
        avail = c.stock
        if avail >= amount:
            c.daily_consumed_projects += amount
            return amount, True
        else:
            # 缺料
            c.daily_consumed_projects += avail
            return avail, False

    def settle_daily_balance(self) -> List[str]:
        """
        每日闭市：执行严格物料守恒方程更新库存，并依据供求缺口与库存偏离运行蛛网动态价格发现与阻尼出清机制
        返回: 市场突发供需预警事件
        """
        events = []
        for cid, c in self.commodities.items():
            # 严格物料守恒定律：
            # 每日工厂开采生产入库，扣除工厂中间品消耗、居民消费与基建工程调拨
            # 注：海关进出口已在报关到港/离岸出关时即时结算至 c.stock，此处不重复计入进出口，避免双重计算
            net_change = c.daily_production - (
                c.daily_consumed_factories + c.daily_consumed_households + c.daily_consumed_projects
            )
            
            s = c.total_daily_supply
            d = c.total_daily_demand if c.total_daily_demand > 0.01 else c.last_day_demand
            
            if cid == "electricity":
                # 电网物理储能上限约 30 亿度，多余电力弃风弃光弃水无法长期留存
                c.stock = min(30.0, max(0.0, c.stock + net_change))
                eff_demand = c.total_daily_demand if c.total_daily_demand > 0.01 else c.last_day_demand
                reserve_ratio = c.daily_production / max(0.1, eff_demand)
                if reserve_ratio < 0.96:
                    c.domestic_price = min(round(c.base_price * 1.5, 2), round(c.domestic_price * 1.015, 2))
                    c.clearance_status = "⚡ 缺电紧平衡"
                    c.market_commentary = f"全社会用电负荷超出发电出力(备用率{reserve_ratio*100:.0f}%)，现货电价微调激励火电与新能源机组全力并网。"
                    events.append(f"⚡ 【电力供应紧张】全社会用电负荷超过发电出力，现货电价微调至 {c.domestic_price:.2f} 元/度！")
                elif reserve_ratio > 1.20:
                    c.domestic_price = max(round(c.base_price * 0.85, 2), round(c.domestic_price * 0.99, 2))
                    c.clearance_status = "🟢 发电充沛"
                    c.market_commentary = f"国家骨干电网出力充沛(备用率{reserve_ratio*100:.0f}%)，电价优惠实体工业降低用电成本。"
                else:
                    c.domestic_price = round(c.domestic_price * 0.96 + c.base_price * 0.04, 2)
                    c.clearance_status = "🟢 稳态出清"
                    c.market_commentary = f"骨干电网出力与全社会工业负荷精准动态平衡，电网频率与供电质量稳定。"
                c.clearance_rate = min(100.0, round((c.daily_production / max(0.1, eff_demand)) * 100.0, 1))
            else:
                c.stock = max(0.0, c.stock + net_change)
                cover = c.inventory_cover_days
                
                # 蛛网供需剪刀差 (Scissors gap: 供大于求为正，供不应求为负)
                gap = (s - d) / max(0.1, d)
                
                # 价格发现三元动力方程 (Cobweb Damped Market Clearing Equation):
                # 1. 剪刀差项 (-0.018 * gap): 供过于求则价格下调，供不应求则价格上浮
                # 2. 库存支撑偏离项 (0.012 * (1 - cover/25)): 偏离25天基准安全库存
                # 3. 价值均值引力项 (0.005 * (base_price - price)/base_price): 抑制发散
                gravity = (c.base_price - c.domestic_price) / max(1.0, c.base_price)
                drift = -0.018 * gap + 0.012 * (1.0 - (cover / 25.0)) + 0.005 * gravity
                drift = max(-0.035, min(0.035, drift))
                
                new_price = round(c.domestic_price * (1.0 + drift), 2)
                # 宏观价格安全走廊 [0.45 * base, 2.50 * base]
                min_p = round(c.base_price * 0.45, 2)
                max_p = round(c.base_price * 2.50, 2)
                c.domestic_price = max(min_p, min(max_p, new_price))
                
                # 满足率与出清状态评级
                avail = c.stock + s
                c.clearance_rate = min(100.0, round((avail / max(0.01, d)) * 100.0, 1))
                
                if abs(gap) <= 0.08 and 18.0 <= cover <= 38.0:
                    c.clearance_status = "🟢 稳态出清"
                    c.market_commentary = f"供需平衡度高(剪刀差{gap*100:+.1f}%)，周转{cover:.0f}天处于黄金安全期，现货价格窄幅震荡出清。"
                elif gap < -0.08 and cover < 18.0:
                    c.clearance_status = "📈 扩产追赶"
                    c.market_commentary = f"下游订单旺盛(缺口{abs(gap)*100:.1f}%)，现货周转仅{cover:.1f}天，现货价格走强引导上游加大排产。"
                    if cover < 5.0 and c.stock < 10.0:
                        events.append(f"📦 【物资短缺警报】全国【{c.name}】商业库存告急（仅剩 {cover:.1f} 天），现货价格升至 {c.domestic_price:.1f} 元/{c.unit}！")
                elif gap > 0.08 and cover > 38.0:
                    c.clearance_status = "📉 去库出清"
                    c.market_commentary = f"市场现货供给过剩(富余{gap*100:+.1f}%)，周转积压{cover:.1f}天，价格理性回调倒逼低效产能减产。"
                else:
                    c.clearance_status = "🌊 震荡寻优中"
                    c.market_commentary = f"市场正经历宏观供需蛛网震荡寻优(剪刀差{gap*100:+.1f}%)，价格与企业排产正向新稳态阻尼收敛。"

            # 记录时序轨迹 (维持最近 30 天)
            c.price_history.append(round(c.domestic_price, 2))
            c.supply_history.append(round(c.total_daily_supply, 2))
            c.demand_history.append(round(c.total_daily_demand, 2))
            c.stock_history.append(round(c.stock, 2))
            c.cover_history.append(round(c.inventory_cover_days, 1))
            if len(c.price_history) > 30:
                c.price_history.pop(0)
                c.supply_history.pop(0)
                c.demand_history.pop(0)
                c.stock_history.pop(0)
                c.cover_history.pop(0)
                    
        return events

    def calculate_customs_usd(self, cid: str, amount: float, tariff: float = 0.0) -> float:
        """折算进出口大宗物资对应国际离岸美元货值 (亿美元，支持反倾销关税扣减)"""
        if cid not in self.commodities or amount <= 0:
            return 0.0
        c = self.commodities[cid]
        eff_usd_price = c.import_price_usd * max(0.40, (1.0 - tariff))
        if cid in ["heavy_machinery", "power_equipment"]:
            return round((amount * eff_usd_price) / 100_000_000.0, 4)
        elif cid == "electricity":
            return round((amount * eff_usd_price), 4)
        else:
            return round((amount * eff_usd_price) / 10_000.0, 4)

    def import_customs(self, cid: str, amount: float) -> Tuple[bool, float, float, str]:
        """
        海关报关进口到港入库 (即刻增加入库现货)
        返回: (是否成功, 实际进口量, 耗用外汇美元(亿美元), 结果说明)
        """
        if cid not in self.commodities:
            return False, 0.0, 0.0, f"未知大宗物资编码: {cid}"
        if amount <= 0:
            return False, 0.0, 0.0, "进口数量必须大于 0"
        c = self.commodities[cid]
        usd_cost = self.calculate_customs_usd(cid, amount)
        c.daily_imports += amount
        c.stock = round(c.stock + amount, 2)
        if c.domestic_price > c.base_price:
            c.domestic_price = max(c.base_price, round(c.domestic_price * 0.96, 2))
        msg = f"🚢 【海关到港入库】成功报关进口【{c.name}】{amount:.1f} {c.unit}（实物即刻入库，现货库存增至 {c.stock:.1f} {c.unit}），耗用国际外汇 {usd_cost:.3f} 亿美元。"
        return True, amount, usd_cost, msg

    def export_customs(self, cid: str, amount: float, tariff: float = 0.0) -> Tuple[bool, float, float, str]:
        """
        海关商检外销出口创汇 (即刻调出离岸现货，支持反倾销关税)
        返回: (是否成功, 实际出口量, 创汇美元(亿美元), 结果说明)
        """
        if cid not in self.commodities:
            return False, 0.0, 0.0, f"未知大宗物资编码: {cid}"
        if amount <= 0:
            return False, 0.0, 0.0, "出口数量必须大于 0"
        c = self.commodities[cid]
        avail = c.stock + c.daily_production
        if avail <= 0.1:
            return False, 0.0, 0.0, f"国内【{c.name}】商业现货库存告急，无多余物资可供外贸出口！"
        actual = min(c.stock, amount) if c.stock >= 0.1 else min(avail, amount)
        usd_revenue = self.calculate_customs_usd(cid, actual, tariff=tariff)
        c.daily_exports += actual
        c.stock = max(0.0, round(c.stock - actual, 2))
        tariff_note = f" (扣减反倾销税 {tariff*100:.0f}%)" if tariff > 0.001 else ""
        msg = f"🚢 【外贸离岸出口】国内企业成功出口【{c.name}】{actual:.1f} {c.unit}（结余现货库存 {c.stock:.1f} {c.unit}），海关结关创汇 +{usd_revenue:.3f} 亿美元{tariff_note}！"
        return True, actual, usd_revenue, msg

    def get_macro_clearance_report(self, factory_manager: Any = None) -> Dict[str, Any]:
        """
        宏观市场动态出清综合评估报告与调节全周期复盘 (Macro Market Clearance & Equilibration Report)
        """
        total_items = len(self.commodities)
        steady_count = sum(1 for c in self.commodities.values() if "稳态" in c.clearance_status or "充沛" in c.clearance_status)
        scarcity_count = sum(1 for c in self.commodities.values() if "扩产" in c.clearance_status or "短缺" in c.clearance_status or "紧平衡" in c.clearance_status)
        glut_count = sum(1 for c in self.commodities.values() if "去库" in c.clearance_status)
        hunting_count = sum(1 for c in self.commodities.values() if "震荡" in c.clearance_status)
        
        # 宏观出清综合健康得分 (0 ~ 100)
        health_score = round((steady_count * 100.0 + hunting_count * 75.0 + (scarcity_count + glut_count) * 55.0) / max(1, total_items), 1)
        
        # 全社会供求加权剪刀差
        total_s = sum(c.total_daily_supply for c in self.commodities.values())
        total_d = sum(c.total_daily_demand for c in self.commodities.values())
        agg_gap_pct = round(((total_s - total_d) / max(0.1, total_d)) * 100.0, 1)
        
        # 平均物价偏离度
        avg_price_dev = round(sum(abs((c.domestic_price - c.base_price) / max(0.1, c.base_price)) * 100.0 for c in self.commodities.values()) / max(1, total_items), 1)
        
        # 实体产业平均利润率
        avg_margin_pct = 12.5
        if factory_manager and hasattr(factory_manager, "factories"):
            tot_rev = sum(f.daily_revenue for f in factory_manager.factories.values())
            tot_prof = sum(f.daily_profit for f in factory_manager.factories.values())
            if tot_rev > 0.01:
                avg_margin_pct = round((tot_prof / tot_rev) * 100.0, 1)

        # 调控全周期复盘四阶段总结报告
        if health_score >= 82.0:
            stage_shock = "内阁制定的战略平准政策与宏观信贷走廊平稳运行，未发生大规模外生断裂性冲击。"
            stage_osc = "主要基础大宗物资(煤、电、钢、粮)供需剪刀差维持在窄幅区间，现货价格波动衰减在±2%内。"
            stage_adj = "微观实体工厂依循以销定产与利润信号自发微调开工率，上下游领料与生产节奏高度契合。"
            stage_res = f"【稳态均衡出清】：全市场综合健康度高达 {health_score} 分！平均产业利润率维持在 {avg_margin_pct}%，大宗现货库存周转充盈，市场已完成自然寻优与自我出清。"
        elif scarcity_count > glut_count:
            stage_shock = "下游民生消费与国家重大战略基建提速，带动物资中间品消耗快速攀升，引发局部供求紧平衡。"
            stage_osc = "现货价格在短缺压力下温和上浮，企业毛利走阔，市场经历第一波产能扩产追赶震荡。"
            stage_adj = "高价格与订单爆满激励上游矿山与制造厂加班排产，部分短缺物资依靠海关进口与战略储备平准补齐缺口。"
            stage_res = f"【扩产追赶收敛中】：全市场供需剪刀差暂居 {agg_gap_pct:+.1f}%。随着企业有效产能逐步释放，价格涨势趋缓，正在逼近新的动态高位平衡点。"
        else:
            stage_shock = "前期产能集中释放或外部需求调整，导致部分原材料现货商业库存周转天数拉长。"
            stage_osc = "现货价格承压向下微调，触发中央战略储备库自动化托市收储与企业限产去库。"
            stage_adj = "价格回落引导亏损产线主动降低负荷率，同时低成本原材料传导至下游制造业，刺激中下游消费回暖。"
            stage_res = f"【去库出清探底修复】：全社会库存去化平稳推进，未发生系统性价格崩塌。企业平均利润率稳定在 {avg_margin_pct}%，市场自发调节初见成效。"
            
        return {
            "health_score": health_score,
            "steady_count": steady_count,
            "scarcity_count": scarcity_count,
            "glut_count": glut_count,
            "hunting_count": hunting_count,
            "aggregate_gap_pct": agg_gap_pct,
            "avg_price_dev_pct": avg_price_dev,
            "avg_margin_pct": avg_margin_pct,
            "outcome_report": {
                "phase_shock": stage_shock,
                "phase_oscillation": stage_osc,
                "phase_self_adjustment": stage_adj,
                "phase_equilibrium_result": stage_res
            }
        }

    def set_auto_trade_policy(
        self,
        cid: str,
        enabled: bool = None,
        min_cover: float = None,
        max_cover: float = None,
        max_import: float = None,
        max_export: float = None
    ) -> Tuple[bool, str]:
        """调整某项工业商品的海关外贸自动平准与进出口方针策略"""
        if cid not in self.commodities:
            return False, f"未找到商品: {cid}"
        c = self.commodities[cid]
        if enabled is not None:
            c.auto_trade_enabled = bool(enabled)
        if min_cover is not None:
            c.auto_import_cover_days = max(3.0, min(60.0, round(float(min_cover), 1)))
        if max_cover is not None:
            c.auto_export_cover_days = max(c.auto_import_cover_days + 5.0, min(180.0, round(float(max_cover), 1)))
        if max_import is not None:
            c.max_daily_import = max(0.01, round(float(max_import), 2))
        if max_export is not None:
            c.max_daily_export = max(0.01, round(float(max_export), 2))
        
        status_txt = (
            f"开启 [周转<{c.auto_import_cover_days:.0f}天自动外汇进口保供 | >{c.auto_export_cover_days:.0f}天自动商检出口创汇]"
            if c.auto_trade_enabled else "关闭(纯手动调度)"
        )
        return True, f"🚢 【外贸调度方针】已调整【{c.name}】自动进出口策略: {status_txt} (单日额度: 进{c.max_daily_import:.2f} / 出{c.max_daily_export:.2f} {c.unit})。"

    def to_dict(self) -> Dict[str, Any]:
        """序列化供前端渲染"""
        return {
            cid: {
                "id": c.id,
                "name": c.name,
                "category": c.category,
                "unit": c.unit,
                "stock": round(c.stock, 1),
                "cover_days": c.inventory_cover_days,
                "price": round(c.domestic_price, 2),
                "base_price": c.base_price,
                "import_price_usd": c.import_price_usd,
                "price_diff_pct": round(((c.domestic_price - c.base_price) / max(0.01, c.base_price)) * 100.0, 1),
                "daily_prod": round(c.daily_production, 2),
                "daily_demand": round(c.total_daily_demand, 2),
                "daily_imports": round(c.daily_imports, 2),
                "daily_exports": round(c.daily_exports, 2),
                "net_surplus": round(c.daily_production + c.daily_imports - c.total_daily_demand, 2),
                "clearance_status": c.clearance_status,
                "clearance_rate": c.clearance_rate,
                "market_commentary": c.market_commentary,
                "is_secondary": c.is_secondary,
                "auto_trade_enabled": c.auto_trade_enabled,
                "auto_import_cover_days": c.auto_import_cover_days,
                "auto_export_cover_days": c.auto_export_cover_days,
                "max_daily_import": c.max_daily_import,
                "max_daily_export": c.max_daily_export,
                "price_history": c.price_history[-30:],
                "supply_history": c.supply_history[-30:],
                "demand_history": c.demand_history[-30:],
                "stock_history": c.stock_history[-30:],
                "cover_history": c.cover_history[-30:]
            } for cid, c in self.commodities.items()
        }
