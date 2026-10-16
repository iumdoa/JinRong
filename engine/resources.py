"""
国家地下探明地质储量、矿产勘探采掘与国家实物战略储备中枢
"""
from dataclasses import dataclass, field
from typing import Dict, Any, List, Tuple
import random

@dataclass
class GeologicalReserve:
    """地下探明地质储量实体"""
    id: str
    name: str
    proven_reserves: float         # 当前剩余探明储量 (实物单位)
    initial_reserves: float        # 基期初始探明储量
    daily_extraction: float = 0.0  # 当日开采量
    cumulative_extracted: float = 0.0 # 累计开采量
    unit: str = "万吨"
    is_depleted: bool = False
    
    @property
    def depletion_years(self) -> float:
        """储采比 (年)：按当前日开采强度估算可支撑年限"""
        if self.daily_extraction <= 0.0001:
            return 999.0
        return round(self.proven_reserves / (self.daily_extraction * 360.0), 1)

@dataclass
class StrategicStockpile:
    """国家实物战略储备仓储 (战略粮仓、战略能源电煤库、战略石油储备SPR、战略金属储备)"""
    id: str
    name: str
    current_stock: float           # 当前中央战略储备库结存 (实物单位)
    capacity: float                # 储备库最大设计库容
    unit: str = "万吨"
    target_years: float = 3.0      # 国家战略安全目标年限 (以年为单位，如 3.0 年)
    daily_burn_rate: float = 45.0  # 全社会日基准消耗参考量
    safe_days_target: float = 1080.0 # 折算天数
    mode: str = "normal"           # "normal"(待机), "release"(抛储平抑), "accumulate"(托市收储)
    daily_flow: float = 0.0        # 今日净进出库量 (+入库 / -出库)
    auto_policy_enabled: bool = True # 是否开启战略方针 (自动抛储/托市收储/外汇海外代购补库)
    
    # 战略储备自动化平准机制参数
    min_market_cover_days: float = 10.0      # 市场流动下限(天)：现货大盘周转低于此天数，自动平价抛储救急
    max_market_cover_days: float = 45.0      # 市场积压上限(天)：现货大盘周转高于此天数，自动财政托市收储
    auto_import_reserve_years: float = 1.0   # 战备安全底限(年)：战略储备年限低于此时，自动动用外汇海外进口补库

    @property
    def reserve_years(self) -> float:
        """当前战略实物储备可支撑全社会运行年限"""
        burn = self.daily_burn_rate if self.daily_burn_rate > 0.01 else 1.0
        return round(self.current_stock / (burn * 360.0), 2)

    @property
    def target_stock(self) -> float:
        """根据战略目标年限折算的应备库存总量"""
        burn = self.daily_burn_rate if self.daily_burn_rate > 0.01 else 1.0
        return round(self.target_years * burn * 360.0, 1)

    @property
    def is_target_reached(self) -> bool:
        """是否已达标（已达成设定的战略安全年限或库容已满）"""
        return self.current_stock >= min(self.capacity, self.target_stock)

class ResourceManager:
    """国家地质矿产资源与实物战略储备总局"""
    def __init__(self, rng_seed: int = 42):
        self.rng = random.Random(rng_seed)
        
        # 1. 地下探明地质储量大盘
        self.reserves: Dict[str, GeologicalReserve] = {
            "coal": GeologicalReserve(
                id="coal",
                name="煤炭地质储量",
                proven_reserves=50_000.0, # 5 亿吨 = 50,000 万吨 (储采比约68年)
                initial_reserves=50_000.0,
                unit="万吨"
            ),
            "iron_ore": GeologicalReserve(
                id="iron_ore",
                name="铁矿地质储量",
                proven_reserves=35_000.0,  # 3.5 亿吨 = 35,000 万吨 (储采比约53年)
                initial_reserves=35_000.0,
                unit="万吨"
            ),
            "crude_oil": GeologicalReserve(
                id="crude_oil",
                name="原油地质储量",
                proven_reserves=12_000.0,   # 1.2 亿桶 = 12,000 万桶 (储采比约33年)
                initial_reserves=12_000.0,
                unit="万桶"
            ),
            "copper_ore": GeologicalReserve(
                id="copper_ore",
                name="有色铜铝矿储量",
                proven_reserves=450.0,     # 450 万吨 (储采比约60年)
                initial_reserves=450.0,
                unit="万吨"
            ),
            "arable_land": GeologicalReserve(
                id="arable_land",
                name="有效耕地储备红线",
                proven_reserves=1_200.0,     # 1,200 万亩
                initial_reserves=1_200.0,
                unit="万亩"
            )
        }
        
        # 2. 国家战略实物储备仓储中枢 (以年为安全维度的国家战备底气)
        self.stockpiles: Dict[str, StrategicStockpile] = {
            "coal": StrategicStockpile(
                id="coal",
                name="国家战略能源电煤储备库",
                current_stock=720.0,       # 720 万吨 = 1.0 年战略储备底气
                capacity=1800.0,           # 最大库容 1800 万吨 (可容纳 2.5 年战略储备)
                unit="万吨",
                target_years=2.0,          # 战略目标储备 2.0 年 (1440 万吨)
                daily_burn_rate=2.0,
                safe_days_target=720.0,
                min_market_cover_days=12.0,  # 电厂与供暖电煤堆场安全底线 12 天
                max_market_cover_days=45.0,  # 坑口滞销堆存 45 天启动托市收储
                auto_import_reserve_years=0.5 # 战备不足 0.5 年动用外汇海外代购
            ),
            "iron_ore": StrategicStockpile(
                id="iron_ore",
                name="国家战略铁矿石储备堆场",
                current_stock=540.0,       # 540 万吨 = ~1.0 年战略铁矿储备
                capacity=1400.0,           # 最大库容 1400 万吨 (可容纳 2.5 年储备)
                unit="万吨",
                target_years=1.5,          # 战略目标储备 1.5 年
                daily_burn_rate=1.2,
                safe_days_target=540.0,
                min_market_cover_days=12.0,  # 钢厂高炉原料周转底线 12 天
                max_market_cover_days=35.0,  # 港口现货堆存超 35 天启动托市收储
                auto_import_reserve_years=0.6 # 战备不足 0.6 年动用外汇海外采购铁矿
            ),
            "oil": StrategicStockpile(
                id="oil",
                name="国家战略石油储备基地(SPR)",
                current_stock=360.0,       # 360 万桶 = 1.0 年战略石油
                capacity=800.0,            # 最大库容 800 万桶
                unit="万桶",
                target_years=1.5,          # 战略目标储备 1.5 年
                daily_burn_rate=1.0,
                safe_days_target=540.0,
                min_market_cover_days=10.0,  # 炼油厂与保供油库周转底线 10 天
                max_market_cover_days=35.0,  # 油罐库容溢流 35 天收储入地下盐穴
                auto_import_reserve_years=0.5 # 战备不足 0.5 年动用外汇海外采购原油
            ),
            "copper": StrategicStockpile(
                id="copper",
                name="国家战略铜铝有色金属储备库",
                current_stock=72.0,        # 72 万吨 = ~1.2 年战略有色金属储备
                capacity=180.0,            # 最大库容 180 万吨
                unit="万吨",
                target_years=1.5,          # 战略目标储备 1.5 年
                daily_burn_rate=0.16,
                safe_days_target=540.0,
                min_market_cover_days=10.0,  # 电网装备与精工有色周转底线 10 天
                max_market_cover_days=32.0,  # 堆场积压 32 天启动托市收储
                auto_import_reserve_years=0.5 # 战备不足 0.5 年动用外汇海外采购铜矿
            ),
            "grain": StrategicStockpile(
                id="grain",
                name="国家战略粮食储备库(中储粮)",
                current_stock=800.0,       # 800 万吨 = ~1.5 年战略口粮储备底线
                capacity=1600.0,           # 最大库容 1600 万吨
                unit="万吨",
                target_years=2.0,          # 战略目标储备 2.0 年
                daily_burn_rate=1.5,
                safe_days_target=720.0,
                min_market_cover_days=15.0,  # 粮油平价商超与成品粮周转底线 15 天
                max_market_cover_days=40.0,  # 农民谷贱伤农滞销 40 天启动托市收储
                auto_import_reserve_years=0.8 # 战备不足 0.8 年动用外汇海外采购口粮
            ),
            "steel": StrategicStockpile(
                id="steel",
                name="国家战略型钢与工建储备库",
                current_stock=300.0,       # 300 万吨 = ~0.63 年战略储备
                capacity=800.0,            # 最大库容 800 万吨
                unit="万吨",
                target_years=1.0,          # 战略目标储备 1.0 年
                daily_burn_rate=1.3,
                safe_days_target=360.0,
                min_market_cover_days=10.0,  # 钢结构与工程现场备料 10 天
                max_market_cover_days=40.0,  # 钢厂坯材爆库 40 天启动基建战略收储
                auto_import_reserve_years=0.4 # 战备不足 0.4 年动用外汇海外采购型材
            )
        }
        
        # 3. 地质勘探投入机制
        self.exploration_budget_daily: float = 0.05 # 每天地质找矿拨款 (亿元/天)
        self.exploration_progress_days: int = 0
        self.exploration_focus: str = "balanced"   # "balanced", "coal", "iron_ore", "crude_oil", "copper_ore"
        self.cumulative_new_coal_found: float = 0.0
        self.cumulative_new_iron_found: float = 0.0
        self.cumulative_new_oil_found: float = 0.0
        self.cumulative_new_copper_found: float = 0.0

    def extract(self, res_id: str, amount: float) -> Tuple[float, bool]:
        """
        开采地下资源，返回 (实际开采量, 是否已枯竭)
        """
        if res_id not in self.reserves:
            return 0.0, True
        res = self.reserves[res_id]
        if res.is_depleted or res.proven_reserves <= 0:
            res.is_depleted = True
            res.proven_reserves = 0.0
            res.daily_extraction = 0.0
            return 0.0, True
            
        actual = min(res.proven_reserves, amount)
        res.proven_reserves -= actual
        res.daily_extraction = actual
        res.cumulative_extracted += actual
        
        if res.proven_reserves <= 0.01:
            res.is_depleted = True
            res.proven_reserves = 0.0
            return actual, True
            
        return actual, False

    def tick_daily(self, commodity_hub=None) -> List[str]:
        """
        每日流转：推进地质勘探、检查储量告警、结算实物战略储备库与宏观平抑机制
        """
        events = []
        self.exploration_progress_days += 1
        
        # 重置储备库单日流水
        for sp in self.stockpiles.values():
            sp.daily_flow = 0.0
            
        # 宏观战略储备平抑与轮换机制
        if commodity_hub:
            # 1. 粮食储备库：粮价暴涨平抑，粮价暴跌托市，季度轮换
            sp_grain = self.stockpiles.get("grain")
            c_grain = commodity_hub.commodities.get("raw_grain")
            if sp_grain and c_grain:
                if c_grain.domestic_price > c_grain.base_price * 1.18 and sp_grain.current_stock > 10.0:
                    rel_amt = min(0.3, sp_grain.current_stock * 0.02)
                    sp_grain.current_stock = round(sp_grain.current_stock - rel_amt, 2)
                    sp_grain.daily_flow = round(sp_grain.daily_flow - rel_amt, 2)
                    commodity_hub.produce("raw_grain", rel_amt)
                    events.append(f"🏛️ 【战略粮仓平抑】原粮价格上扬至 {c_grain.domestic_price:.0f} 元/吨，国家战略粮库定向抛储 {rel_amt:.1f} 万吨平抑物价！")
                elif c_grain.domestic_price < c_grain.base_price * 0.85 and (sp_grain.capacity - sp_grain.current_stock) > 2.0:
                    acc_amt = min(0.2, sp_grain.capacity - sp_grain.current_stock)
                    sp_grain.current_stock = round(sp_grain.current_stock + acc_amt, 2)
                    sp_grain.daily_flow = round(sp_grain.daily_flow + acc_amt, 2)
                    commodity_hub.consume_factory("raw_grain", acc_amt)
                    events.append(f"🏛️ 【战略粮仓托市】原粮市场低迷，国家粮食局启动最低收购价托市收储 +{acc_amt:.1f} 万吨！")
                elif self.exploration_progress_days % 90 == 0 and sp_grain.current_stock > 5.0:
                    # 90天例行推陈出新轮换
                    rot_amt = min(0.3, sp_grain.current_stock * 0.03)
                    commodity_hub.produce("raw_grain", rot_amt)
                    commodity_hub.consume_factory("raw_grain", rot_amt)
                    events.append(f"🌾 【战略粮库轮换】执行季度储备粮推陈出新轮换作业，轮入轮出各 {rot_amt:.1f} 万吨。")

            # 2. 原油 SPR 储备库平抑
            sp_oil = self.stockpiles.get("oil")
            c_oil = commodity_hub.commodities.get("crude_oil")
            if sp_oil and c_oil:
                if c_oil.domestic_price > c_oil.base_price * 1.20 and sp_oil.current_stock > 10.0:
                    rel_amt = min(0.2, sp_oil.current_stock * 0.01)
                    sp_oil.current_stock = round(sp_oil.current_stock - rel_amt, 2)
                    sp_oil.daily_flow = round(sp_oil.daily_flow - rel_amt, 2)
                    commodity_hub.produce("crude_oil", rel_amt)
                    events.append(f"🛢️ 【战略石油平抑】国内原油现货偏紧，国家战略石油储备(SPR)紧急投放 {rel_amt:.1f} 万桶！")
                elif c_oil.domestic_price < c_oil.base_price * 0.85 and (sp_oil.capacity - sp_oil.current_stock) > 2.0:
                    acc_amt = min(0.2, sp_oil.capacity - sp_oil.current_stock)
                    sp_oil.current_stock = round(sp_oil.current_stock + acc_amt, 2)
                    sp_oil.daily_flow = round(sp_oil.daily_flow + acc_amt, 2)
                    commodity_hub.consume_factory("crude_oil", acc_amt)

            # 3. 钢材战略储备平抑
            sp_steel = self.stockpiles.get("steel")
            c_steel = commodity_hub.commodities.get("steel")
            if sp_steel and c_steel:
                if c_steel.domestic_price > c_steel.base_price * 1.20 and sp_steel.current_stock > 5.0:
                    rel_amt = min(0.2, sp_steel.current_stock * 0.02)
                    sp_steel.current_stock = round(sp_steel.current_stock - rel_amt, 2)
                    sp_steel.daily_flow = round(sp_steel.daily_flow - rel_amt, 2)
                    commodity_hub.produce("steel", rel_amt)
                elif c_steel.domestic_price < c_steel.base_price * 0.85 and (sp_steel.capacity - sp_steel.current_stock) > 1.0:
                    acc_amt = min(0.2, sp_steel.capacity - sp_steel.current_stock)
                    sp_steel.current_stock = round(sp_steel.current_stock + acc_amt, 2)
                    sp_steel.daily_flow = round(sp_steel.daily_flow + acc_amt, 2)
                    commodity_hub.consume_factory("steel", acc_amt)
        
        # 每 90 天为一个地质找矿勘探周期
        if self.exploration_progress_days % 90 == 0 and self.exploration_budget_daily > 0.005:
            # 勘探突破概率受勘探经费与专项主攻方向动态加权
            success_chance = min(0.85, 0.25 + self.exploration_budget_daily * 4.0)
            if self.rng.random() < success_chance:
                # 决定探获矿种
                focus = self.exploration_focus
                if focus == "coal" or (focus == "balanced" and self.rng.random() < 0.35):
                    new_coal = round(self.rng.uniform(100.0, 300.0) * (1.2 if focus == "coal" else 1.0), 1)
                    self.reserves["coal"].proven_reserves += new_coal
                    self.cumulative_new_coal_found += new_coal
                    events.append(f"⛏️ 【新矿脉大发现】国家地质勘探队探明大型整装煤田，新增探明煤炭储量 +{new_coal:.0f} 万吨！")
                elif focus == "iron_ore" or (focus == "balanced" and self.rng.random() < 0.60):
                    new_iron = round(self.rng.uniform(80.0, 200.0) * (1.2 if focus == "iron_ore" else 1.0), 1)
                    self.reserves["iron_ore"].proven_reserves += new_iron
                    self.cumulative_new_iron_found += new_iron
                    events.append(f"🏔️ 【战略铁矿突破】地质物探组在东部基底查明高品位磁铁矿体，新增探明铁矿储量 +{new_iron:.0f} 万吨！")
                elif focus == "crude_oil" or (focus == "balanced" and self.rng.random() < 0.85):
                    new_oil = round(self.rng.uniform(50.0, 150.0) * (1.2 if focus == "crude_oil" else 1.0), 1)
                    self.reserves["crude_oil"].proven_reserves += new_oil
                    self.cumulative_new_oil_found += new_oil
                    events.append(f"🛢️ 【战略油气突破】深层油气打出高产工业自喷油流，新增证实地质原油储量 +{new_oil:.0f} 万桶！")
                else: # copper_ore
                    new_cu = round(self.rng.uniform(15.0, 45.0) * (1.2 if focus == "copper_ore" else 1.0), 1)
                    self.reserves["copper_ore"].proven_reserves += new_cu
                    self.cumulative_new_copper_found += new_cu
                    events.append(f"🥉 【战略有色突破】深部勘探圈定大型斑岩铜钼矿床，新增探明铜矿储量 +{new_cu:.0f} 万吨！")
                    
        # 储量枯竭临界警戒线检查 (储采比 < 5年)
        for rid, r in self.reserves.items():
            if not r.is_depleted and r.depletion_years < 5.0 and r.daily_extraction > 0.1:
                events.append(f"⚠️ 【地质储量枯竭警报】国家【{r.name}】剩余探明储量仅剩 {r.proven_reserves:.0f} {r.unit}，储采比已跌破 5 年！必须加大地质找矿投入或尽早布局海外进口！")
                
        return events

    def release_stockpile(self, sid: str, amount: float) -> Tuple[bool, float, str]:
        """抛储平抑：从国家战略储备库向现货市场投放物资以平抑物价"""
        if sid == "crude_oil" and "oil" in self.stockpiles:
            sid = "oil"
        elif sid == "copper_ore" and "copper" in self.stockpiles:
            sid = "copper"
        elif sid == "raw_grain" and "grain" in self.stockpiles:
            sid = "grain"
        if sid not in self.stockpiles:
            return False, 0.0, f"未找到储备库: {sid}"
        sp = self.stockpiles[sid]
        if amount <= 0:
            return False, 0.0, "抛储数量必须大于 0"
        actual = min(sp.current_stock, amount)
        if actual <= 0.001:
            return False, 0.0, f"【{sp.name}】库存已见底，无物资可供平抑抛储！"
        sp.current_stock = round(sp.current_stock - actual, 2)
        sp.daily_flow = round(sp.daily_flow - actual, 2)
        return True, actual, f"🏛️ 【战略平抑抛储】国家实物战略储备局向大宗现货市场投放【{sp.name}】{actual:.1f} {sp.unit}！"

    def accumulate_stockpile(self, sid: str, amount: float) -> Tuple[bool, float, str]:
        """托市收储：国家出资采购现货充实战略储备"""
        if sid == "crude_oil" and "oil" in self.stockpiles:
            sid = "oil"
        elif sid == "copper_ore" and "copper" in self.stockpiles:
            sid = "copper"
        elif sid == "raw_grain" and "grain" in self.stockpiles:
            sid = "grain"
        if sid not in self.stockpiles:
            return False, 0.0, f"未找到储备库: {sid}"
        sp = self.stockpiles[sid]
        if amount <= 0:
            return False, 0.0, "收储数量必须大于 0"
        avail_space = sp.capacity - sp.current_stock
        if avail_space <= 0.001:
            return False, 0.0, f"【{sp.name}】仓容已满 (已达设计库容 {sp.capacity:.0f} {sp.unit})，无法继续收储！"
        actual = min(avail_space, amount)
        sp.current_stock = round(sp.current_stock + actual, 2)
        sp.daily_flow = round(sp.daily_flow + actual, 2)
        return True, actual, f"🏛️ 【托市收储入库】国家实物战略储备局采购现货入库【{sp.name}】+{actual:.1f} {sp.unit}！"

    def set_stockpile_target(
        self,
        sid: str,
        target_years: float,
        auto_enabled: bool = None,
        min_market_cover_days: float = None,
        max_market_cover_days: float = None,
        auto_import_reserve_years: float = None
    ) -> Tuple[bool, str]:
        """调整某项战略储备库的目标年限与自动化方针策略"""
        if sid == "crude_oil" and "oil" in self.stockpiles:
            sid = "oil"
        elif sid == "copper_ore" and "copper" in self.stockpiles:
            sid = "copper"
        elif sid == "raw_grain" and "grain" in self.stockpiles:
            sid = "grain"
        if sid not in self.stockpiles:
            return False, f"未找到储备库: {sid}"
        sp = self.stockpiles[sid]
        if target_years is not None:
            sp.target_years = max(0.5, min(10.0, round(float(target_years), 1)))
            sp.safe_days_target = sp.target_years * 360.0
        if auto_enabled is not None:
            sp.auto_policy_enabled = bool(auto_enabled)
        if min_market_cover_days is not None:
            sp.min_market_cover_days = max(3.0, min(60.0, round(float(min_market_cover_days), 1)))
        if max_market_cover_days is not None:
            sp.max_market_cover_days = max(sp.min_market_cover_days + 5.0, min(180.0, round(float(max_market_cover_days), 1)))
        if auto_import_reserve_years is not None:
            sp.auto_import_reserve_years = max(0.2, min(5.0, round(float(auto_import_reserve_years), 1)))

        status_txt = (
            f"开启 [周转<{sp.min_market_cover_days:.0f}天自动抛储 | >{sp.max_market_cover_days:.0f}天自动收储 | 储备<{sp.auto_import_reserve_years:.1f}年外汇补库]"
            if sp.auto_policy_enabled else "关闭(纯手动调度)"
        )
        return True, f"🏛️ 【国家战略储备方针】已调整【{sp.name}】目标储备为 {sp.target_years:.1f} 年，战略方针: {status_txt}。"

    def set_exploration(self, daily_budget: float, focus: str = None) -> Tuple[bool, str]:
        """调整地质找矿勘探预算与攻坚方向"""
        self.exploration_budget_daily = max(0.0, min(0.50, round(daily_budget, 4)))
        if focus and focus in ["balanced", "coal", "iron_ore", "crude_oil", "copper_ore"]:
            self.exploration_focus = focus
        focus_names = {
            "balanced": "全面综合勘查",
            "coal": "重点找煤专项",
            "iron_ore": "富铁矿攻坚专项",
            "crude_oil": "深层油气勘探突破",
            "copper_ore": "战略有色铜铝矿专项"
        }
        f_name = focus_names.get(self.exploration_focus, self.exploration_focus)
        success_chance = min(0.85, 0.25 + self.exploration_budget_daily * 4.0) * 100.0 if self.exploration_budget_daily > 0.005 else 0.0
        return True, f"🧭 【国家地质找矿部署】每日物探经费调整为 {self.exploration_budget_daily:.2f} 亿元/天，主攻【{f_name}】！预计每季探矿突破概率 {success_chance:.1f}%，筑牢实体工业资源安全底线。"

    def to_dict(self) -> Dict[str, Any]:
        """序列化输出供前端驾驶舱展示"""
        return {
            "reserves": {
                k: {
                    "id": v.id,
                    "name": v.name,
                    "proven_reserves": round(v.proven_reserves, 1),
                    "initial_reserves": round(v.initial_reserves, 1),
                    "daily_extraction": round(v.daily_extraction, 2),
                    "depletion_years": v.depletion_years,
                    "unit": v.unit,
                    "is_depleted": v.is_depleted,
                    "remaining_pct": round((v.proven_reserves / max(1.0, v.initial_reserves)) * 100.0, 1)
                } for k, v in self.reserves.items()
            },
            "stockpiles": {
                k: {
                    "id": v.id,
                    "name": v.name,
                    "current_stock": round(v.current_stock, 1),
                    "capacity": v.capacity,
                    "unit": v.unit,
                    "target_years": v.target_years,
                    "reserve_years": v.reserve_years,
                    "target_stock": v.target_stock,
                    "is_target_reached": v.is_target_reached,
                    "auto_policy_enabled": v.auto_policy_enabled,
                    "min_market_cover_days": v.min_market_cover_days,
                    "max_market_cover_days": v.max_market_cover_days,
                    "auto_import_reserve_years": v.auto_import_reserve_years,
                    "safe_days_target": v.safe_days_target,
                    "mode": v.mode
                } for k, v in self.stockpiles.items()
            },
            "exploration": {
                "daily_budget": self.exploration_budget_daily,
                "progress_days": self.exploration_progress_days,
                "focus": self.exploration_focus,
                "total_new_coal": self.cumulative_new_coal_found,
                "total_new_iron": self.cumulative_new_iron_found,
                "total_new_oil": self.cumulative_new_oil_found,
                "total_new_copper": self.cumulative_new_copper_found
            }
        }
