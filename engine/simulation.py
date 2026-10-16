"""
国家宏观金融体系模拟器 - 核心动力学与推演引擎 (Simulation Engine)
"""
import math
import random
from typing import List, Dict, Any, Tuple
from engine.state import MacroState, FlowRecord, HouseholdTier
from engine.policy_cards import PolicyCardManager
from engine.infrastructure import InfrastructureManager
from engine.resources import ResourceManager
from engine.commodity import CommodityHub
from engine.labor import LaborManager
from engine.factories import FactoryManager, get_commodity_value_in_yi, COMMODITY_SUPPLIER_MAP
from engine.accounting import AccountingBus
from engine.personas import calculate_micro_ledgers

class FlowExecutorAdapter:
    """资金流执行适配器：将工厂内部 B2B/工资划转同时登记入 AccountingBus 与 FlowRecord"""
    def __init__(self, bus, execute_flow_fn):
        self.bus = bus
        self.accounts = bus.accounts
        self.execute_flow_fn = execute_flow_fn
        
    def transfer(self, from_acc: str, to_acc: str, amount: float, category: str, description: str):
        return self.execute_flow_fn(from_acc, to_acc, amount, category, description)

class SimulationEngine:
    def __init__(self, state: MacroState, card_manager: PolicyCardManager, infra_manager: InfrastructureManager = None, seed: int = 1024):
        self.state = state
        self.card_manager = card_manager
        self.infra_manager = infra_manager if infra_manager is not None else InfrastructureManager(rng_seed=seed)
        self.rng = random.Random(seed)
        
        # 极度硬核：探明地质储量、大宗实物物资中枢、实体工厂矩阵与技能劳动力
        self.resource_manager = ResourceManager(rng_seed=seed)
        self.commodity_hub = CommodityHub()
        self.factory_manager = FactoryManager()
        self.labor_manager = LaborManager(total_population=state.total_population)
        
        # 极度硬核：五大部门中央资金清算总线 (SFC 存量-流量一致性框架)
        self.accounting_bus = AccountingBus(exchange_rate=state.exchange_rate)
        h_configs = [
            {"id": getattr(h, "id", f"tier_{i}"), "name": h.name, "savings": h.savings}
            for i, h in enumerate(state.households)
        ]
        self.accounting_bus.initialize_standard_matrix(
            households_config=h_configs,
            corporate_cash=state.corporate_cash,
            corporate_debt=state.corporate_debt,
            treasury_cash=state.treasury_cash,
            national_debt=state.national_debt,
            social_fund=state.social_fund_pool,
            bank_capital=state.bank_capital,
            foreign_reserves_usd=state.foreign_reserves_usd,
            exchange_rate=state.exchange_rate,
            household_debt=state.household_mortgage_debt
        )
        
        # 初始企业负债与宏观国情严格对齐 (确保各厂贷款总和严格等于 state.corporate_debt)
        cur_tot_debt = sum(f.debt_principal for f in self.factory_manager.factories.values())
        if cur_tot_debt > 0 and state.corporate_debt > 0:
            debt_scale = state.corporate_debt / cur_tot_debt
            for f in self.factory_manager.factories.values():
                f.debt_principal = round(f.debt_principal * debt_scale, 4)
        
        # 初始企业信用风险评级评估
        for f in self.factory_manager.factories.values():
            cash_bal = self.accounting_bus.accounts[f.account_id].balance if f.account_id in self.accounting_bus.accounts else 0.0
            f.evaluate_credit_rating(state.loan_interest_rate, cash_balance=cash_bal)
            
        state.corporate_credit_ratings = [
            {
                "id": f.id,
                "name": f.name,
                "rating": f.credit_rating,
                "score": f.credit_score,
                "credit_score": f.credit_score,
                "leverage_ratio": f.leverage_ratio,
                "icr": f.interest_coverage_ratio,
                "interest_coverage_ratio": f.interest_coverage_ratio,
                "debt_principal": round(f.debt_principal, 2),
                "borrowing_rate": round(f.borrowing_rate * 100, 2),
                "loan_status": f.loan_status,
                "status": f.loan_status,
                "credit_limit": round(f.credit_limit, 2),
                "recalled_today": round(f.recalled_loans_today, 3),
                "new_borrowing_today": round(f.new_borrowing_today, 3)
            } for f in self.factory_manager.factories.values()
        ]
            
        # 初始状态同步至 state (包含真实企业分户账本与细分劳工全景矩阵)
        state.resources = self.resource_manager.to_dict()
        state.commodities = self.commodity_hub.to_dict()
        state.market_clearing_summary = self.commodity_hub.get_macro_clearance_report(self.factory_manager)
        state.factories = self.factory_manager.to_dict(self.accounting_bus)
        state.labor_market = self.labor_manager.to_dict(self.factory_manager.factories)
        
        # 记录基准锚点，用于负反馈收敛（确保无干预时不崩盘、不暴富、微幅波动）
        self.baseline_employed = [h.employed for h in state.households]
        self.baseline_capacity = state.corporate_capacity
        self.baseline_bank_loans = state.bank_loans
        self.baseline_debt = state.national_debt
        self.baseline_treasury = state.treasury_cash
        
        # 初始化微观9大雇主经营账本与15大工种民生家庭账本
        self.sync_personas_and_ledgers()

    def sync_personas_and_ledgers(self):
        """全景计算9大微观雇主经营账本与15大工种家庭账本，并兼容映射三大代表人物"""
        state = self.state
        micro_data = calculate_micro_ledgers(
            state=state,
            accounting_bus=self.accounting_bus,
            factory_manager=self.factory_manager,
            commodity_hub=self.commodity_hub,
            labor_manager=self.labor_manager,
            infra_manager=self.infra_manager
        )
        state.employers_ledger = micro_data["employers"]
        state.citizens_ledger = micro_data["citizens"]
        
        # 兼容保留原三大代表人物画像
        if "zhang_miner" in state.citizens_ledger:
            zm = state.citizens_ledger["zhang_miner"]
            state.persona_worker = {
                "name": zm["name"],
                "identity": f"{zm['title']} ({zm['scale_label']})",
                "daily_income": zm["daily_revenue"],
                "food_expense": zm["breakdown"].get("高热量重体力口粮", 24.5),
                "disposable_left": zm["daily_net"],
                "employment_status": zm["status_desc"],
                "savings": zm["accumulated_funds"],
                "voice": zm["voice"]
            }
        if "li_accountant" in state.citizens_ledger:
            la = state.citizens_ledger["li_accountant"]
            state.persona_middle = {
                "name": la["name"],
                "identity": f"{la['title']} ({la['scale_label']})",
                "daily_income": la["daily_revenue"],
                "loan_interest_daily": la["breakdown"].get("银行商业房贷利息", 18.2),
                "living_expense": la["breakdown"].get("品质生活与家庭日常", 58.0),
                "disposable_left": la["daily_net"],
                "savings": la["accumulated_funds"],
                "voice": la["voice"]
            }
        if "chen_machinery" in state.employers_ledger:
            cm = state.employers_ledger["chen_machinery"]
            state.persona_boss = {
                "name": cm["name"],
                "identity": f"{cm['title']} ({cm['scale_label']})",
                "daily_revenue": cm["daily_revenue"],
                "daily_wages_paid": cm["breakdown"].get("技工薪酬", 720.0),
                "daily_energy_cost": cm["breakdown"].get("车间动力电费", 160.0),
                "daily_loan_interest": cm["breakdown"].get("机床经营贷利息", 100.0),
                "daily_tax_paid": cm["breakdown"].get("企业所得税", 35.0),
                "daily_profit": cm["daily_net"],
                "willingness_to_expand": cm["status_desc"],
                "voice": cm["voice"]
            }

    def update_state_corporate_cash(self):
        """汇总全社会所有实体企业银行活期存款余额"""
        self.state.corporate_cash = round(
            sum(acc.balance for acc in self.accounting_bus.accounts.values() if acc.sector == "corporate"),
            4
        )

    def record_flow(self, source: str, target: str, amount: float, category: str, description: str):
        """记录一笔资金流动（钱从哪来，到哪去）"""
        if amount <= 0:
            return
        rec = FlowRecord(
            source=source,
            target=target,
            amount=round(amount, 4),
            category=category,
            description=description
        )
        self.state.daily_flows.append(rec)
        # 累加到季度汇总
        key = f"{source} -> {target} [{category}]"
        self.state.quarterly_flow_summary[key] = self.state.quarterly_flow_summary.get(key, 0.0) + amount

    def execute_flow(self, from_acc: str, to_acc: str, amount: float, category: str, description: str):
        """原子执行记账并登记在流向表中"""
        if amount <= 0.0000001:
            return
        self.accounting_bus.transfer(from_acc, to_acc, amount, category, description)
        from_name = self.accounting_bus.accounts[from_acc].name if from_acc in self.accounting_bus.accounts else from_acc
        to_name = self.accounting_bus.accounts[to_acc].name if to_acc in self.accounting_bus.accounts else to_acc
        self.record_flow(
            source=from_name,
            target=to_name,
            amount=amount,
            category=category,
            description=description
        )

    def step_day(self) -> List[str]:
        """推进 1 天的时间与经济流转"""
        state = self.state
        state.daily_flows.clear()
        daily_events = []
        self.accounting_bus.start_day(state.day)
        
        # 0. 推进政策卡与公共基建/科研攻关工程计时
        card_events = self.card_manager.tick_daily()
        daily_events.extend(card_events)
        
        # 推进硬核地下探明储量采掘与地质勘探流转
        self.commodity_hub.reset_daily_flows()
        res_events = self.resource_manager.tick_daily(self.commodity_hub)
        daily_events.extend(res_events)
        
        # 财政地质找矿与物探专项资金划拨
        exp_budget = self.resource_manager.exploration_budget_daily
        if exp_budget > 0.001 and state.treasury_cash >= exp_budget:
            self.execute_flow(
                from_acc="treasury_cash",
                to_acc="corporate_sector",
                amount=exp_budget,
                category="地质找矿勘探预算",
                description=f"中央财政向地质调查局与深部找矿科研院所划拨专款 ({self.resource_manager.exploration_focus})"
            )
            state.treasury_cash = round(self.accounting_bus.accounts["treasury_cash"].balance, 4)
            self.update_state_corporate_cash()
        
        # 生效已竣工工程的累积永久属性加成 (由收益爬坡效率动态加权)
        buffs = self.infra_manager.accumulated_buffs
        uhv_buff = buffs.get("corp_cost_discount", 0.0)
        power_eff = 1.0 + (buffs.get("capacity_bonus", 0.0) / 2200.0) * 0.15
        
        # 运行十大实体工业投入产出生产闭环 (连接真实资金清算总线与双边企业账本)
        flow_adapter = FlowExecutorAdapter(self.accounting_bus, self.execute_flow)
        factory_events = self.factory_manager.run_production_cycle(
            self.resource_manager,
            self.commodity_hub,
            self.labor_manager,
            power_grid_efficiency=power_eff,
            uhv_cost_discount=uhv_buff,
            accounting_bus=flow_adapter
        )
        daily_events.extend(factory_events)
        
        # 推进重大公共基建与科研攻关工程 (消耗工程物资，缺料则停工待料)
        infra_daily_cost, infra_maint_cost, infra_events = self.infra_manager.tick_daily(
            state.research_capability,
            commodity_hub=self.commodity_hub
        )
        daily_events.extend(infra_events)
        state.infra_daily_spending = round(infra_daily_cost, 4)
        state.infra_maintenance_spending = round(infra_maint_cost, 4)
        if infra_daily_cost > 0:
            c_mach = round(infra_daily_cost * 0.45, 4)
            c_steel = round(infra_daily_cost * 0.35, 4)
            c_cement = round(infra_daily_cost - c_mach - c_steel, 4)
            self.execute_flow(
                from_acc="treasury_cash",
                to_acc="corp_heavy_machinery",
                amount=c_mach,
                category="基建重装设备采购",
                description="国家财政拨付在建重大电网铁路等大型数控机床与重工装备款"
            )
            self.execute_flow(
                from_acc="treasury_cash",
                to_acc="corp_steel_mill",
                amount=c_steel,
                category="基建特种型钢采购",
                description="国家财政采购重大桥梁高压铁塔与轨道交通特种合金型钢"
            )
            self.execute_flow(
                from_acc="treasury_cash",
                to_acc="corp_cement_plant",
                amount=c_cement,
                category="基建高标号水泥采购",
                description="国家财政采购高铁枢纽与特高压变电站高标号水泥建材"
            )
        if infra_maint_cost > 0:
            self.execute_flow(
                from_acc="treasury_cash",
                to_acc="corp_hardware_machinery",
                amount=infra_maint_cost,
                category="基础设施与五金管养",
                description="国家财政向陈厂长五金机械集群采购已建电网道路公立医院校舍检修紧固件配件"
            )
            
        # 百姓民生日常实物消费消耗与全社会实体运转自然磨损消耗 (1000万人口小国基准)
        # 1. 精炼口粮食品包由居民部门各阶层日常口粮开支动态核算领用 (_run_household_sector)
        
        # 2. 原粮 (农村自留口粮、种用储备与散户家禽生猪养殖饲料)
        self.commodity_hub.consume_household("raw_grain", 0.45)
        
        # 3. 大众纺织与日用轻工百货
        textile_demand = round((state.total_population / 10_000_000.0) * 5.5 * (state.consumer_sentiment / 50.0), 2)
        self.commodity_hub.consume_household("textile", max(4.0, textile_demand))
        
        # 4. 全社会民生日常用电与交通商用油料与基本医疗
        self.commodity_hub.consume_household("electricity", 0.35)
        self.commodity_hub.consume_household("crude_oil", 0.40)
        self.commodity_hub.consume_household("medicine", 3.8)
        
        # 5. 全社会常态市政管网维护与电网工业维保 (零星路桥、电网变电与农具机床维保)
        self.commodity_hub.consume_household("cement", 0.20)
        self.commodity_hub.consume_factory("copper_ore", 0.08)
        self.commodity_hub.consume_factory("steel", 0.15)
        self.commodity_hub.consume_factory("hardware", 0.10)
        self.commodity_hub.consume_factory("chips", 0.04)
        self.commodity_hub.consume_factory("power_equipment", 0.02)
        self.commodity_hub.consume_household("heavy_machinery", 0.05)
        
        # 市政管网与医疗物资维保费用真实结算款
        maint_cost_stl = round((0.15 * self.commodity_hub.commodities["steel"].domestic_price) / 10000.0, 4)
        maint_cost_hw = round((0.10 * self.commodity_hub.commodities["hardware"].domestic_price) / 10000.0, 4)
        maint_cost_pe = round((0.02 * self.commodity_hub.commodities["power_equipment"].domestic_price) / 100_000_000.0, 4)
        maint_cost_med = round((3.8 * self.commodity_hub.commodities["medicine"].domestic_price) / 10000.0, 4)
        total_maint = maint_cost_stl + maint_cost_hw + maint_cost_pe + maint_cost_med
        if self.accounting_bus.accounts["corporate_sector"].balance >= total_maint and total_maint > 0.0001:
            self.accounting_bus.transfer(
                "corporate_sector", "corp_steel_mill", maint_cost_stl,
                "市政管网维修型钢结算", "市政公用部门采购路桥管网检修钢材"
            )
            self.accounting_bus.transfer(
                "corporate_sector", "corp_hardware_machinery", maint_cost_hw,
                "市政工程紧固五金结算", "市政公用部门采购标准维修五金配件"
            )
            self.accounting_bus.transfer(
                "corporate_sector", "corp_power_equipment", maint_cost_pe,
                "电网成套变电设备更新", "国家电网采购特高压与主网成套变电设备更新"
            )
            self.accounting_bus.transfer(
                "corporate_sector", "corp_pharma_corp", maint_cost_med,
                "公立医院药品耗材采购", "公立医疗机构平价集采调拨基础医疗药品耗材"
            )
        
        # 职业技校与综合大学职业技能培育升阶
        voc_count = sum(p.get("schools_granted", 0) for p in self.infra_manager.completed_projects if p.get("template_id") == "vocational_edu")
        univ_count = sum(p.get("schools_granted", 0) for p in self.infra_manager.completed_projects if p.get("template_id") == "university_campus")
        labor_events = self.labor_manager.train_and_upgrade_skills(voc_count, univ_count)
        daily_events.extend(labor_events)
            
        # 生效已竣工工程的累积永久属性加成 (由收益爬坡效率动态加权)
        buffs = self.infra_manager.accumulated_buffs
        state.corporate_capacity = self.baseline_capacity + buffs["capacity_bonus"]
        
        # 国家综合科研能力 = 困难初始底座(12) + 永久教育基建大学成果 + 限期专项科研经费专款
        grant_boost = (
            self.infra_manager.active_research_grant.get("boost", 0.0)
            if self.infra_manager.active_research_grant.get("is_active")
            else 0.0
        )
        base_res = getattr(state, "base_research_capability", 45.0)
        state.research_capability = min(100.0, base_res + buffs["research_boost"] + grant_boost)
        state.active_research_grant = self.infra_manager.active_research_grant.copy()
        
        # 全国学校总数 = 初始150所 + 竣工项目增设学校
        state.school_count = 150 + sum(p.get("schools_granted", 0) for p in self.infra_manager.completed_projects)
        
        # 检查当前激活的政策卡
        active_cards = {c.id: c for c in self.card_manager.cards.values() if c.is_active}
        has_new_deal = "roosevelt_new_deal" in active_cards
        has_reagan = "reagan_tax_cut" in active_cards
        has_helicopter = "helicopter_money" in active_cards
        has_austerity = "austerity_reform" in active_cards
        has_digital_tax = "digital_tax_reform" in active_cards
        
        # 1. 政策公信力十年长效演化（与国家财政状况四大支柱深度绑定）
        # 现实逻辑：国家公信力从低到高至少需 10 年 (3600天) 的审慎经营；财政恶化与赤字失控会迅速侵蚀公信力。
        days_since_policy_change = state.day - state.last_policy_change_day
        base_cred_growth = 0.0138  # 基准日累积约 +0.0138点/天 (年均约 5.0 点，10年累积 50 点)
        
        # 支柱 1：财政赤字率考核 (Deficit to GDP)
        deficit_rate = state.deficit_to_gdp_rate
        if deficit_rate <= 2.0:
            fiscal_factor = 1.0       # 财政健康平衡，完全支持信誉稳固增长
        elif deficit_rate <= 4.5:
            fiscal_factor = 0.5       # 温和赤字，信誉增长速度减半
        elif deficit_rate <= 7.5:
            fiscal_factor = 0.0       # 赤字偏高，市场担忧可持续性，暂停增长
        else:
            fiscal_factor = -1.2      # 恶性赤字 (>7.5%)，巨额亏空反噬主权公信力 (-0.016点/天)
            
        # 支柱 2：国库流动性安全垫考核
        cash_penalty = 0.0
        if state.treasury_cash <= 0.0:
            cash_penalty = 0.035      # 国库见底断流，每日严厉扣除
            fiscal_factor = min(fiscal_factor, -1.0)
        elif state.treasury_cash < 15.0:
            cash_penalty = 0.010      # 流动性警报
            fiscal_factor = min(fiscal_factor, 0.0)
        elif state.treasury_cash < 50.0:
            fiscal_factor = min(fiscal_factor, 0.5)

        # 支柱 3：政策稳定性考核（不折腾奖励）
        stability_multiplier = 1.0
        if days_since_policy_change < 60:
            stability_multiplier = 0.0  # 距上次调控不足60天，市场观望消化，暂不加分
        elif days_since_policy_change > 360:
            stability_multiplier = 1.25 # 连续1年以上政策稳定，奖励治道有常

        # 支柱 4：政策卡主动赋能 (铁腕财政整顿阳光采购)
        card_cred_boost = 0.008 if has_austerity else 0.0

        # 计算每日综合净变动
        daily_cred_delta = (base_cred_growth * fiscal_factor * stability_multiplier) - cash_penalty + card_cred_boost

        # 债务悬顶天花板考核 (Debt Overhang Cap)
        # 若负债率超过 60% 警戒线，公信力设置硬性天花板 (70点)，逼迫内阁化债
        cred_max_cap = 98.0
        if state.debt_to_gdp_rate > 60.0:
            cred_max_cap = 70.0
        elif state.debt_to_gdp_rate > 50.0:
            cred_max_cap = 80.0

        if daily_cred_delta > 0:
            if state.policy_credibility < cred_max_cap:
                state.policy_credibility = min(cred_max_cap, state.policy_credibility + daily_cred_delta)
        else:
            state.policy_credibility = max(5.0, state.policy_credibility + daily_cred_delta)
        
        credibility_factor = state.policy_credibility / 100.0  # 0~1
        
        # 2. 利率与商业银行传导
        # 若公信力低，银行加收风险溢价
        risk_premium = max(0.0, (1.0 - credibility_factor) * 0.03)
        state.loan_interest_rate = state.base_interest_rate + 0.025 + risk_premium
        state.deposit_interest_rate = max(0.005, state.base_interest_rate * 0.6)
        
        # 3. 政策卡特异性资金流与干预效果
        extra_gov_hired_workers = 0
        extra_helicopter_subsidy_low = 0.0
        extra_helicopter_subsidy_mid = 0.0
        
        effective_corp_tax_rate = state.corp_tax_rate
        if has_reagan:
            effective_corp_tax_rate = 0.12 # 里根减税强制12%
            
        if has_new_deal:
            # 罗斯福新政：国库每天支出0.35亿，直接雇佣底层45万失业工人
            card = active_cards["roosevelt_new_deal"]
            cost = card.daily_cost_amount
            # 40%靠国债赤字借款由银行认购出资
            gov_debt_part = round(cost * 0.4, 4)
            self.accounting_bus.bank_treasury_bonds += gov_debt_part
            state.national_debt += gov_debt_part
            self.execute_flow(
                from_acc="bank_operations",
                to_acc="treasury_cash",
                amount=gov_debt_part,
                category="特别国债发行",
                description="商业银行认购罗斯福新政以工代赈专项国债"
            )
            self.execute_flow(
                from_acc="treasury_cash",
                to_acc="household_miner_heavy",
                amount=cost,
                category="以工代赈公共支出",
                description="罗斯福新政专项：雇佣45万失业者参与路桥与水利建设"
            )
            extra_gov_hired_workers = 450_000
            
        if has_helicopter:
            # 直升机撒钱：央行每天注水印钞0.40亿，70%发给底层，30%发给中产
            card = active_cards["helicopter_money"]
            amount = card.daily_cost_amount
            extra_helicopter_subsidy_low = round(amount * 0.70, 4)
            extra_helicopter_subsidy_mid = round(amount * 0.30, 4)
            self.accounting_bus.central_bank_inject("household_miner_heavy", extra_helicopter_subsidy_low, "全民抗疫/纾困现金支票直达底层账户")
            self.record_flow(
                source="央行印钞机",
                target="采矿与重体力劳工 (老张)",
                amount=extra_helicopter_subsidy_low,
                category="直升机无偿现金",
                description="全民抗疫/纾困现金支票直达底层账户"
            )
            self.accounting_bus.central_bank_inject("household_white_collar", extra_helicopter_subsidy_mid, "全民纾困现金支票直达中产账户")
            self.record_flow(
                source="央行印钞机",
                target="白领工薪与管理群体 (李会计)",
                amount=extra_helicopter_subsidy_mid,
                category="直升机无偿现金",
                description="全民纾困现金支票直达中产账户"
            )

        # 4. 就业市场与劳动力动态 (微观微调 + 负反馈稳态)
        # 实体企业投资意愿取决于（借贷成本 vs 稳态产能）
        rate_gap = (state.base_interest_rate - 0.04)
        investment_sentiment = 1.0 - (rate_gap * 3.5) + (0.15 if has_reagan else 0.0)
        investment_sentiment = max(0.5, min(1.5, investment_sentiment * (0.8 + 0.2 * credibility_factor)))
        
        # 统计各工种当日实体工厂净解雇与净招聘 (Phase 1 联动)
        tier_net_layoffs: Dict[str, int] = {}
        for f in self.factory_manager.factories.values():
            net_change = f.daily_laid_off - f.daily_hired
            if net_change != 0:
                tier_net_layoffs[f.primary_labor_tier] = tier_net_layoffs.get(f.primary_labor_tier, 0) + net_change

        # 稳态吸引子：无干预时各层就业人数向 baseline 缓慢收敛，叠加小幅随机扰动 (±0.3%)
        for idx, h in enumerate(state.households):
            noise = self.rng.uniform(-0.003, 0.003)
            base = self.baseline_employed[idx] if idx < len(self.baseline_employed) else int(h.labor_force * 0.8)
            # 目标就业人数受到投资景气度影响
            target_emp = int(base * investment_sentiment * (1.0 + noise))
            # 限制单日变动幅度（劳动力粘性）
            h.employed = int(h.employed * 0.98 + target_emp * 0.02)
            
            # 叠加实体工业工厂减产裁员与破产出清对劳工的真实冲击
            net_layoff = tier_net_layoffs.get(h.id, 0)
            if net_layoff > 0:
                h.employed = max(int(h.labor_force * 0.35), h.employed - net_layoff)
            elif net_layoff < 0:
                h.employed = min(h.labor_force, h.employed - net_layoff)
                
            # 限制上下限
            h.employed = min(h.labor_force, max(int(h.labor_force * 0.35), h.employed))
            
        # 叠加罗斯福新政的直接雇佣
        state.households[0].employed = min(
            state.households[0].labor_force,
            state.households[0].employed + extra_gov_hired_workers
        )
        # 同步劳动力市场微观在岗人数
        for h in state.households:
            if h.id in self.labor_manager.tiers:
                self.labor_manager.tiers[h.id].employed = h.employed

        # 5. Phase 2: 居民多元消费金字塔与房地产蓄水池引擎
        total_food_spending = 0.0
        total_comfort_spending = 0.0
        total_household_spending = 0.0
        total_durable_spending = 0.0
        total_mortgage_repay = 0.0
        total_housing_downpayment = 0.0
        total_mortgage_issued = 0.0
        total_housing_sales_sqm = 0.0
        total_housing_sales_yuan = 0.0
        total_service_spending = 0.0
        total_disposable_income = 0.0
        total_income_tax_collected = 0.0
        total_wages_paid = 0.0
        total_worker_social_contrib = 0.0
        
        tax_bracket_stats = {
            "tier_exempt": {"name": "法定免征(低保与自耕农)", "pop": 0, "tax": 0.0},
            "tier_low": {"name": "普工轻税档(2%~5%)", "pop": 0, "tax": 0.0},
            "tier_mid": {"name": "中产基准档(8%~14%)", "pop": 0, "tax": 0.0},
            "tier_high": {"name": "高管专家顶格累进档(12%~32%)", "pop": 0, "tax": 0.0}
        }
        
        impoverished_population = 0
        
        for idx, h in enumerate(state.households):
            hid = f"household_{h.id}" if getattr(h, "id", "") else f"household_tier_{idx}"
            
            # (1) 工资收入发放 (工厂专户直接发薪 + 商业/辅助工直发)
            unemployed_count = h.labor_force - h.employed
            employed_wages = (h.employed * h.base_wage) / 100_000_000
            informal_income = (unemployed_count * h.base_wage * 0.25) / 100_000_000
            wage_income = round(employed_wages + informal_income, 4)
            total_wages_paid += wage_income
            
            # 统计当日该工种已由各大实体工业工厂专户直发的部分
            factory_direct_wages = sum(
                f.daily_wage_cost for f in self.factory_manager.factories.values()
                if f.primary_labor_tier == getattr(h, "id", "")
            )
            auxiliary_wage = max(0.0, round(wage_income - factory_direct_wages, 4))
            if auxiliary_wage > 0.0001:
                self.execute_flow(
                    from_acc="corporate_sector",
                    to_acc=hid,
                    amount=auxiliary_wage,
                    category="商业与辅助用工薪酬",
                    description=f"商贸流通、农林协作与城镇灵活用工向{h.name}发放在岗劳动报酬"
                )
            
            # (2) 存款利息收益 (商业银行资本运营户 -> 居民储蓄账户)
            h_acc_balance = self.accounting_bus.accounts[hid].balance
            daily_interest_yield = round((h_acc_balance * state.deposit_interest_rate) / 360.0, 4)
            if daily_interest_yield > 0.00001:
                self.execute_flow(
                    from_acc="bank_operations",
                    to_acc=hid,
                    amount=daily_interest_yield,
                    category="存款利息",
                    description=f"商业银行向{h.name}支付储蓄存款利息"
                )
            
            # (3) Phase 5 现代综合超额累进个人所得税 (Super-Progressive PIT)
            # 法定免征起征点 80 元/天 (折合月薪 2400 元/月，底层普工与自耕农 100% 依法免税)
            gross_taxable = wage_income + daily_interest_yield
            pop_tier = max(1, h.population)
            n_earners = max(1, h.employed)
            earner_gross_yuan = (wage_income * 100_000_000.0) / n_earners
            
            tax_rate_policy_scale = max(0.2, state.income_tax_rate / 0.05)
            tax_amount = 0.0
            excess_yuan = max(0.0, earner_gross_yuan - 80.0)
            
            if excess_yuan <= 0.0 or idx in [0, 1]:
                # 采矿重工、农村自耕农及人均日收入 <= 80元处于法定免征线，免缴个税
                tax_amount = 0.0
                tax_bracket_stats["tier_exempt"]["pop"] += pop_tier
            elif idx == 2:
                # 轻工操作工：仅对超出 80 元部分征收 3.5% 轻税
                tax_yuan_pc = excess_yuan * (0.035 * tax_rate_policy_scale)
                tax_amount = round((tax_yuan_pc * n_earners) / 100_000_000.0, 4)
                tax_bracket_stats["tier_low"]["pop"] += pop_tier
                tax_bracket_stats["tier_low"]["tax"] += tax_amount
            elif idx in [3, 4]:
                # 熟练技师与中产白领：超出 80 元部分实行 8%~14% 超额累进
                if excess_yuan <= 60.0:
                    tax_yuan_pc = excess_yuan * (0.08 * tax_rate_policy_scale)
                else:
                    tax_yuan_pc = (60.0 * 0.08 + (excess_yuan - 60.0) * 0.14) * tax_rate_policy_scale
                tax_amount = round((tax_yuan_pc * n_earners) / 100_000_000.0, 4)
                tax_bracket_stats["tier_mid"]["pop"] += pop_tier
                tax_bracket_stats["tier_mid"]["tax"] += tax_amount
            else:
                # 顶尖专家高管科研阶层 (idx == 5)：超出部分实行 12%~32% 顶格超额累进
                if excess_yuan <= 100.0:
                    tax_yuan_pc = excess_yuan * 0.12
                elif excess_yuan <= 250.0:
                    tax_yuan_pc = 100.0 * 0.12 + (excess_yuan - 100.0) * 0.22
                else:
                    tax_yuan_pc = 100.0 * 0.12 + 150.0 * 0.22 + (excess_yuan - 250.0) * 0.32
                tax_yuan_pc *= tax_rate_policy_scale
                tax_amount = round((tax_yuan_pc * n_earners) / 100_000_000.0, 4)
                tax_bracket_stats["tier_high"]["pop"] += pop_tier
                tax_bracket_stats["tier_high"]["tax"] += tax_amount

            if tax_amount > 0.00001:
                self.execute_flow(
                    from_acc=hid,
                    to_acc="treasury_cash",
                    amount=tax_amount,
                    category="超额累进个人所得税",
                    description=f"{h.name}代扣超额累进个税(法定起征点80元/天，实缴{tax_amount:.4f}亿)"
                )
            total_income_tax_collected += tax_amount
            
            # (4) 职工个人社保缴费 (40%部分：居民储蓄账户 -> 全国社保基金)
            worker_contrib = round(wage_income * (state.social_contrib_rate * 0.4), 4)
            if worker_contrib > 0.00001:
                self.execute_flow(
                    from_acc=hid,
                    to_acc="social_security_fund",
                    amount=worker_contrib,
                    category="个人社保缴费",
                    description=f"{h.name}职工工资代扣代缴个人社保养老医保金"
                )
            total_worker_social_contrib += worker_contrib
            
            # (5) Phase 2 消费金字塔分层流转 (Tier 1 ~ Tier 5)
            net_daily_flow = (wage_income + daily_interest_yield) - tax_amount - worker_contrib
            total_disposable_income += max(0.0, net_daily_flow)
            current_avail_cash = self.accounting_bus.accounts[hid].balance
            sentiment_ratio = state.consumer_sentiment / 100.0
            mortgage_rate = max(0.025, round(state.base_interest_rate + 0.015, 4))
            
            # --- Tier 1: 生存必需品 (必需口粮与基础日用轻纺水电) ---
            food_price_factor = max(0.5, state.food_basket_price / 15.0)
            food_cost = round((h.population * h.min_food_cost * food_price_factor) / 100_000_000, 4)
            food_cost = min(current_avail_cash, food_cost)
            if food_cost > 0.0001:
                self.execute_flow(
                    from_acc=hid,
                    to_acc="corp_food_processing",
                    amount=food_cost,
                    category="口粮食品消费",
                    description=f"{h.name}向国家粮油食品加工联合企业购买米面油脂副食品"
                )
                p_food = self.commodity_hub.commodities["food_pack"].domestic_price
                # 居民食品篮子开支中约20%为工厂精炼米面粮油食品包实物领用 (对应0.9万吨/天口粮大宗)
                food_tons = round(((food_cost * 0.20) * 10000.0) / max(100.0, p_food), 2)
                self.commodity_hub.consume_household("food_pack", food_tons)
            
            current_avail_cash = self.accounting_bus.accounts[hid].balance
            
            per_capita_essential_nonfood = (
                5.0 if idx == 0 else (
                    4.5 if idx == 1 else (
                        10.0 if idx == 2 else (
                            18.0 if idx == 3 else (
                                25.0 if idx == 4 else 45.0
                            )
                        )
                    )
                )
            )
            cpi_factor = max(0.5, state.cpi_index / 100.0)
            nonfood_essential = round((h.population * per_capita_essential_nonfood * cpi_factor) / 100_000_000, 4)
            nonfood_essential = min(current_avail_cash, nonfood_essential)
            if nonfood_essential > 0.0001:
                c_textile_essential = round(nonfood_essential * 0.40, 4)
                c_other_essential = round(nonfood_essential - c_textile_essential, 4)
                if c_textile_essential > 0.0001:
                    self.execute_flow(
                        from_acc=hid,
                        to_acc="corp_textile_light",
                        amount=c_textile_essential,
                        category="日用轻纺基本消费",
                        description=f"{h.name}采购日常工作服饰与家纺被服"
                    )
                if c_other_essential > 0.0001:
                    self.execute_flow(
                        from_acc=hid,
                        to_acc="corporate_sector",
                        amount=c_other_essential,
                        category="生活公用水电与交通必需",
                        description=f"{h.name}支付生活照明用电、燃气与基础通勤"
                    )
            
            current_avail_cash = self.accounting_bus.accounts[hid].balance
            
            # --- Tier 2: 个人住房按揭还本付息扣款 (利率传导核心通道) ---
            tier_mortgage = getattr(h, "mortgage_debt", 0.0)
            if tier_mortgage > 0.001 and current_avail_cash > 0.05:
                principal_due = round(tier_mortgage / 7200.0, 5)
                interest_due = round((tier_mortgage * mortgage_rate) / 360.0, 5)
                self.accounting_bus.repay_household_mortgage(
                    h.id, principal_due, interest_due,
                    f"{h.name}住房按揭月供还本付息"
                )
                h.mortgage_debt = max(0.0, round(tier_mortgage - principal_due, 4))
                h.daily_mortgage_cost = round(principal_due + interest_due, 4)
                total_mortgage_repay += h.daily_mortgage_cost
            else:
                h.daily_mortgage_cost = 0.0
                
            current_avail_cash = self.accounting_bus.accounts[hid].balance
            
            # --- Tier 3: 耐用消费品更新购置 (汽车、家电、数码) ---
            surplus = max(0.0, net_daily_flow - food_cost - nonfood_essential - h.daily_mortgage_cost)
            per_capita_durable = (
                1.5 if idx == 0 else (
                    1.8 if idx == 1 else (
                        6.5 if idx == 2 else (
                            18.0 if idx == 3 else (
                                25.0 if idx == 4 else 45.0
                            )
                        )
                    )
                )
            )
            durable_target = round((h.population * per_capita_durable * (0.8 + 0.4 * sentiment_ratio)) / 100_000_000, 4)
            durable_actual = round(min(durable_target, surplus * 0.45, max(0.0, current_avail_cash - 1.0)), 4)
            if durable_actual > 0.0001:
                amt_hw = round(durable_actual * 0.45, 4)
            if durable_actual > 0.0001:
                amt_hw = round(durable_actual * 0.04, 4)
                amt_chip = round(durable_actual * 0.04, 4)
                amt_steel = round(durable_actual * 0.03, 4)
                rem_durable = round(durable_actual - amt_hw - amt_chip - amt_steel, 4)
                
                self.execute_flow(from_acc=hid, to_acc="corp_hardware_machinery", amount=amt_hw, category="汽车家电五金配件采购", description=f"{h.name}购置家用电器与汽车消费配件")
                self.execute_flow(from_acc=hid, to_acc="corp_hightech_electronics", amount=amt_chip, category="消费电子与智能芯片采购", description=f"{h.name}购置智能数码与家电主控元器件")
                self.execute_flow(from_acc=hid, to_acc="corp_steel_mill", amount=amt_steel, category="汽车家电专用板材结算", description=f"{h.name}消费品间接消耗汽车冷轧薄板与合金特钢")
                if rem_durable > 0.0001:
                    self.execute_flow(from_acc=hid, to_acc="corporate_sector", amount=rem_durable, category="耐用品总装与商贸结算", description=f"{h.name}支付家电整机与汽车总装装配款")
                
                p_hw = self.commodity_hub.commodities["hardware"].domestic_price
                p_chip = self.commodity_hub.commodities["chips"].domestic_price
                p_stl = self.commodity_hub.commodities["steel"].domestic_price
                self.commodity_hub.consume_factory("hardware", round((amt_hw * 10000.0) / max(10.0, p_hw), 2))
                self.commodity_hub.consume_factory("chips", round((amt_chip * 10000.0) / max(10.0, p_chip), 2))
                self.commodity_hub.consume_factory("steel", round((amt_steel * 10000.0) / max(100.0, p_stl), 2))
                
                h.daily_durable_cost = durable_actual
                total_durable_spending += durable_actual
            else:
                h.daily_durable_cost = 0.0
                
            current_avail_cash = self.accounting_bus.accounts[hid].balance
            
            # --- Tier 4: 改善型住房置业与按揭派生 (李会计白领、数控技工、电气专家主力) ---
            if idx in [3, 4, 5] and current_avail_cash > (h.population * 0.00004) and getattr(h, "housing_sqm_owned", 30.0) < 55.0:
                rate_stimulus = max(0.6, min(1.8, 1.0 + (0.045 - state.base_interest_rate) * 12.0))
                # 1000万人小国单日商品房正常成交量 (各阶层每日置业约 0.2~0.4万平米，折合全国年化新增商品房约400~500万平米)
                sales_sqm_tier = round((h.population * 0.0000018 * rate_stimulus * sentiment_ratio), 2)
                sales_val_yi = round((sales_sqm_tier * state.housing_avg_price) / 10000.0, 4)
                downpayment = round(sales_val_yi * 0.30, 4)
                mortgage_loan = round(sales_val_yi * 0.70, 4)
                
                if current_avail_cash >= (downpayment + 2.0):
                    self.execute_flow(
                        from_acc=hid, to_acc="corporate_sector", amount=downpayment,
                        category="商品住宅置业首付款", description=f"{h.name}购入{sales_sqm_tier:.1f}万平米商品住宅支付30%首付"
                    )
                    self.accounting_bus.disburse_household_mortgage(
                        h.id, mortgage_loan, "corporate_sector",
                        f"商业银行为{h.name}购房发放20年期首套住房按揭贷款"
                    )
                    h.mortgage_debt = round(h.mortgage_debt + mortgage_loan, 4)
                    h.housing_sqm_owned = round(getattr(h, "housing_sqm_owned", 30.0) + (sales_sqm_tier * 10000.0) / h.population, 2)
                    
                    total_housing_sales_sqm += sales_sqm_tier
                    total_housing_downpayment += downpayment
                    total_mortgage_issued += mortgage_loan
                    total_housing_sales_yuan += sales_val_yi
            
            current_avail_cash = self.accounting_bus.accounts[hid].balance
            
            # --- Tier 5: 现代服务与文旅消费 (大众餐饮、周末文旅、健康医疗) ---
            rem_surplus = max(0.0, surplus - h.daily_durable_cost)
            tier_activity = max(0.05, min(0.95, (surplus / max(0.1, net_daily_flow)) * sentiment_ratio))
            service_spending = round(rem_surplus * (h.comfort_spending_rate * tier_activity * 0.65), 4)
            service_actual = min(service_spending, max(0.0, current_avail_cash - 0.5))
            if service_actual > 0.0001:
                self.execute_flow(
                    from_acc=hid, to_acc="corporate_sector", amount=service_actual,
                    category="文旅餐饮与现代服务消费", description=f"{h.name}在大众餐饮、文化旅游、医疗及现代服务业消费"
                )
                h.daily_service_cost = service_actual
                total_service_spending += service_actual
            else:
                h.daily_service_cost = 0.0
                
            # 结转阶层日度快照指标
            living_total = round(food_cost + nonfood_essential + h.daily_mortgage_cost + h.daily_durable_cost + h.daily_service_cost, 4)
            h.savings = round(self.accounting_bus.accounts[hid].balance, 4)
            h.daily_income = round(wage_income + daily_interest_yield, 4)
            h.daily_food_cost = food_cost
            h.daily_other_cost = round(living_total - food_cost, 4)
            h.daily_savings_delta = round(net_daily_flow - living_total, 4)
            
            total_food_spending += food_cost
            total_comfort_spending += (nonfood_essential + h.daily_service_cost)
            total_household_spending += living_total
            
            # 贫困判定：人均日可支配净资金 < 20元/天
            per_capita_daily_yuan = (max(0.0, net_daily_flow - h.daily_mortgage_cost) * 100_000_000) / h.population
            if per_capita_daily_yuan < state.poverty_line_daily:
                impoverished_population += h.population
            elif idx in [0, 1] and per_capita_daily_yuan < (state.poverty_line_daily * 1.25):
                ratio = max(0.0, min(1.0, (per_capita_daily_yuan - state.poverty_line_daily) / (state.poverty_line_daily * 0.25)))
                impoverished_population += int(h.population * (1.0 - ratio * 0.6))

        # 固化超额累进个税全景统计
        state.progressive_tax_stats = {
            "exemption_line": 80.0,
            "total_income_tax": round(total_income_tax_collected, 4),
            "brackets": {
                k: {
                    "name": v["name"],
                    "population": v["pop"],
                    "tax_collected": round(v["tax"], 4)
                } for k, v in tax_bracket_stats.items()
            }
        }

        # 房地产新开工与建筑施工实物拉动 (消纳钢铁、水泥、重型工程机械)
        daily_starts_sqm = round(max(0.6, total_housing_sales_sqm * 0.95), 2)
        steel_tons = round(daily_starts_sqm * 0.065, 2)     # 万吨抗震螺纹钢与结构型钢
        cement_tons = round(daily_starts_sqm * 0.20, 2)     # 万吨干法水泥与商品混凝土
        mach_units = round(daily_starts_sqm * 2.2, 1)       # 台工程重机/挖掘机台班
        
        # 现货市场领用
        self.commodity_hub.consume_factory("steel", steel_tons)
        self.commodity_hub.consume_factory("cement", cement_tons)
        self.commodity_hub.consume_household("heavy_machinery", mach_units)
        
        # 房地产开发企业向供货工厂结算工程款
        p_steel = self.commodity_hub.commodities["steel"].domestic_price
        p_cement = self.commodity_hub.commodities["cement"].domestic_price
        p_mach = self.commodity_hub.commodities["heavy_machinery"].domestic_price
        
        cost_steel = round((steel_tons * p_steel) / 10000.0, 4)
        cost_cement = round((cement_tons * p_cement) / 10000.0, 4)
        cost_mach = round((mach_units * p_mach) / 100_000_000.0, 4)
        
        corp_bal = self.accounting_bus.accounts["corporate_sector"].balance
        if corp_bal >= (cost_steel + cost_cement + cost_mach):
            if cost_steel > 0.0001:
                self.execute_flow(
                    "corporate_sector", "corp_steel_mill", cost_steel,
                    "商品住宅建筑型钢结算", f"房地产建筑施工采购{steel_tons:.2f}万吨抗震螺纹钢与型钢"
                )
            if cost_cement > 0.0001:
                self.execute_flow(
                    "corporate_sector", "corp_cement_plant", cost_cement,
                    "商品混凝土水泥建材结算", f"商品房施工采购{cement_tons:.2f}万吨高标号水泥"
                )
            if cost_mach > 0.0001:
                self.execute_flow(
                    "corporate_sector", "corp_heavy_machinery", cost_mach,
                    "重装工程机械施工台班结算", f"房地产总包方租赁支付{mach_units:.1f}台套挖掘机与起重机台班费"
                )

        state.housing_stock_sqm = round(getattr(state, "housing_stock_sqm", 32000.0) + total_housing_sales_sqm, 1)
        state.daily_housing_sales_sqm = round(total_housing_sales_sqm, 2)
        state.daily_housing_starts_sqm = round(daily_starts_sqm, 2)
        state.daily_housing_sales_yuan = round(total_housing_sales_yuan, 4)
        state.daily_housing_downpayment = round(total_housing_downpayment, 4)
        state.daily_mortgage_issued = round(total_mortgage_issued, 4)
        state.daily_mortgage_repay_total = round(total_mortgage_repay, 4)
        state.daily_durable_spending = round(total_durable_spending, 4)
        state.daily_service_spending = round(total_service_spending, 4)
        state.household_mortgage_debt = round(sum(h.mortgage_debt for h in state.households), 1)
        
        # 恩格尔系数与房贷压力指数更新
        total_all_spending = total_food_spending + total_comfort_spending + total_durable_spending + total_mortgage_repay
        state.engel_coefficient = round(total_food_spending / max(0.01, total_all_spending), 4)
        state.mortgage_burden_index = round((total_mortgage_repay / max(0.01, total_disposable_income)) * 100.0, 1)

        # =========================================================================
        # 5.5 国家战略储备托市收储与富余大宗平准外销出口 (Buffer Stock & Export Clearance)
        # 此时下游实体工业、居民消费、基建与房地产实物建材消耗已全数就绪入账
        # =========================================================================
        strategic_policy_map = [
            ("coal", "coal", 0.30, 0.05, 1.0),
            ("raw_grain", "grain", 0.20, 0.05, 0.5),
            ("crude_oil", "oil", 0.15, 0.04, 0.5),
            ("steel", "steel", 0.10, 0.05, 0.5),
            ("iron_ore", "iron_ore", 0.30, 0.05, 1.0),
            ("copper_ore", "copper", 0.12, 0.04, 0.15),
        ]
        daily_stockpile_spent = 0.0
        max_daily_stockpile_budget = min(0.15, max(0.02, self.accounting_bus.accounts["treasury_cash"].balance * 0.002))

        for cid, sp_id, max_daily_action, item_budget_cap, max_daily_exp in strategic_policy_map:
            c_item = self.commodity_hub.commodities.get(cid)
            sp = self.resource_manager.stockpiles.get(sp_id)
            if not c_item or not sp:
                continue
            if not getattr(sp, "auto_policy_enabled", True):
                continue
            surplus = c_item.daily_production - c_item.total_daily_demand
            if surplus <= 0.02 or c_item.stock <= c_item.base_stock * 0.8:
                continue
            
            supplier_acc = COMMODITY_SUPPLIER_MAP.get(cid, ("corporate_sector", "国家工业"))[0]
            acc_name = self.accounting_bus.accounts[supplier_acc].name if supplier_acc in self.accounting_bus.accounts else "实体企业专户"
            price_soft = (c_item.domestic_price <= c_item.base_price * 1.02) or (c_item.stock > c_item.base_stock * 1.2)
            buy_vol = 0.0
            
            # 若战备库未满且市价偏软且预算充裕 -> 财政托市收储
            if not sp.is_target_reached and price_soft and daily_stockpile_spent < max_daily_stockpile_budget:
                avail_cap = sp.capacity - sp.current_stock
                raw_buy_vol = min(max_daily_action, surplus * 0.8, avail_cap, max(0.0, c_item.stock - c_item.base_stock * 0.5))
                rem_budget = max(0.0, min(item_budget_cap, max_daily_stockpile_budget - daily_stockpile_spent))
                max_vol_by_budget = rem_budget * 10000.0 / max(1.0, c_item.domestic_price)
                buy_vol = round(min(raw_buy_vol, max_vol_by_budget), 2)
                if buy_vol > 0.02:
                    buy_cost = round((buy_vol * c_item.domestic_price) / 10000.0, 4)
                    treasury_bal = self.accounting_bus.accounts["treasury_cash"].balance
                    if treasury_bal >= buy_cost and buy_cost > 0.0001:
                        self.execute_flow(
                            from_acc="treasury_cash",
                            to_acc=supplier_acc,
                            amount=buy_cost,
                            category="战略储备托市收储",
                            description=f"中央财政出资向{acc_name}托市收购【{c_item.name}】{buy_vol:.2f} {c_item.unit} 充实国家战备库"
                        )
                        sp.current_stock = round(sp.current_stock + buy_vol, 2)
                        sp.daily_flow = round(sp.daily_flow + buy_vol, 2)
                        c_item.stock = max(0.0, round(c_item.stock - buy_vol, 2))
                        daily_stockpile_spent += buy_cost
                        if c_item.domestic_price < c_item.base_price * 1.05:
                            c_item.domestic_price = round(c_item.domestic_price * 1.002, 2)
            
            # 战备库已满或商业周转超警戒线后的富余产能出口创汇 (防商业库存超限积压)
            rem_surplus = max(0.0, surplus - buy_vol)
            max_cover_thr = getattr(sp, "max_market_cover_days", 35.0)
            market_overstocked = (c_item.inventory_cover_days > max_cover_thr)
            allow_export = (sp.is_target_reached or market_overstocked)
            if getattr(sp, "auto_policy_enabled", True) and allow_export and (rem_surplus > 0.02 or market_overstocked) and c_item.stock > c_item.base_stock * 0.8:
                raw_exp_vol = rem_surplus * 0.85 if rem_surplus > 0.02 else (c_item.stock - c_item.base_stock * 0.8) * 0.3
                exp_vol = round(min(max_daily_exp, raw_exp_vol, max(0.0, c_item.stock - c_item.base_stock * 0.5)), 2)
                if exp_vol > 0.02:
                    usd_earn = self.commodity_hub.calculate_customs_usd(cid, exp_vol)
                    if usd_earn > 0.0001:
                        c_item.daily_exports += exp_vol
                        c_item.stock = max(0.0, round(c_item.stock - exp_vol, 2))
                        cny_gained = self.accounting_bus.fx_settle_export(
                            exporter_acc_id=supplier_acc,
                            usd_amount=usd_earn,
                            description=f"{c_item.name}富余产能海关商检出口创汇结汇"
                        )
                        state.foreign_reserves_usd = round(self.accounting_bus.foreign_reserves_usd, 2)
                        state.corporate_cash = round(self.accounting_bus.accounts["corporate_sector"].balance, 4)
                        self.record_flow(
                            source="外贸口岸与海外市场",
                            target=acc_name,
                            amount=cny_gained,
                            category="外贸结汇投放(M2+)",
                            description=f"海关商检出口富余【{c_item.name}】{exp_vol:.2f} {c_item.unit}，创汇 +{usd_earn:.3f} 亿美元，央行结汇投放本币 {cny_gained:.2f} 亿元入【{acc_name}】"
                        )

        # =========================================================================
        # 5.6 二级制造商品自动化进出口平准机制 (Secondary Goods Automated Trade Clearance)
        # 针对化肥、水泥、五金、机械、芯片、电力设备、纺织、药品、包装食品等非战备库二级工业品
        # =========================================================================
        for cid, c_item in self.commodity_hub.commodities.items():
            if not getattr(c_item, "is_secondary", False):
                continue
            if not getattr(c_item, "auto_trade_enabled", False):
                continue
                
            cover_days = c_item.inventory_cover_days
            demand = max(0.05, c_item.total_daily_demand or c_item.last_day_demand or 0.1)
            
            # 1. 供应紧缺预警线：周转天数低于 auto_import_cover_days 自动进口保供
            if cover_days < c_item.auto_import_cover_days:
                shortfall_days = c_item.auto_import_cover_days - cover_days
                target_import = min(
                    c_item.max_daily_import,
                    shortfall_days * demand * 0.5,
                    demand * 2.0
                )
                usd_cost = self.commodity_hub.calculate_customs_usd(cid, target_import)
                cny_cost = usd_cost * self.state.exchange_rate
                corp_cash = self.accounting_bus.accounts["corporate_sector"].balance
                if (
                    target_import >= 0.01
                    and self.state.foreign_reserves_usd > 5.0
                    and usd_cost <= min(0.20, self.state.foreign_reserves_usd * 0.02)
                    and corp_cash > cny_cost + 1.0
                ):
                    ok, msg = self.customs_import_commodity(cid, round(target_import, 2))
                    if ok and (state.day % 15 == 1 or cover_days < c_item.auto_import_cover_days * 0.5):
                        daily_events.append(f"🚢 【二级工业品自动进口】国内【{c_item.name}】商业库存偏紧({cover_days:.1f}天 < {c_item.auto_import_cover_days:.0f}天)，口岸商检保供进口 {target_import:.2f} {c_item.unit}！")
                        
            # 2. 产能过剩平准线：周转天数高于 auto_export_cover_days 自动外销创汇
            elif cover_days > c_item.auto_export_cover_days and c_item.stock > c_item.base_stock * 0.8:
                surplus_days = cover_days - c_item.auto_export_cover_days
                target_export = min(
                    c_item.max_daily_export,
                    surplus_days * demand * 0.5,
                    max(0.0, c_item.stock - c_item.base_stock * 0.5)
                )
                if target_export >= 0.01:
                    ok, msg = self.customs_export_commodity(cid, round(target_export, 2))
                    if ok and (state.day % 15 == 1 or cover_days > c_item.auto_export_cover_days * 1.5):
                        daily_events.append(f"🚢 【二级工业品自动出口】国内【{c_item.name}】产销富余({cover_days:.1f}天 > {c_item.auto_export_cover_days:.0f}天)，海关报关出口 {target_export:.2f} {c_item.unit} 创汇结汇！")

        # 物资紧缺预警
        critical_shortages = [("crude_oil", 5.0), ("raw_grain", 8.0), ("chips", 1.5)]
        for cid, warn_threshold in critical_shortages:
            c_item = self.commodity_hub.commodities.get(cid)
            if c_item and c_item.stock < warn_threshold and state.day % 15 == 1:
                daily_events.append(f"⚠️ 【物资供应偏紧】国内【{c_item.name}】商业库存仅剩 {c_item.stock:.1f} {c_item.unit}，建议内阁在【产业大宗】中使用外汇【进口保供】或动用战略储备【平抑放储】！")

        # 每日大宗市场出清结算与蛛网价格发现 (此时下游各行业物理采购已全数入账)
        market_events = self.commodity_hub.settle_daily_balance()
        daily_events.extend(market_events)

        # 战略储备自动化平准与外汇出海补库
        auto_stockpile_events = self.run_automated_strategic_buffer_and_replenishment()
        daily_events.extend(auto_stockpile_events)

        # 6. 企业部门生产、投资与纳税结算 (GDP = C + I + G)
        # 每日居民消费 C
        C = total_household_spending
        
        # 每日企业投资 I (设备更新、再生产、扩产)
        base_I = (1.50 + buffs.get("capacity_bonus", 0.0) * 0.0005) * investment_sentiment
        if has_reagan:
            base_I += 0.35
        I = base_I
        self.record_flow(
            source="企业部门",
            target="企业部门",
            amount=I,
            category="私人资本投资(I)",
            description="企业采购机械设备、升级厂房与扩大再生产"
        )
        
        # 每日政府采购与公用行政开支 (G_operating)
        # 注：重大在建工程 infra_daily_cost 和运维管养 infra_maint_cost 已在前期划拨入企业部门
        G_operating = state.gov_daily_spending * 0.60 if has_austerity else state.gov_daily_spending
        desc_g = "【铁腕阳光采购】精简行政采购与杜绝吃空饷，压缩公款开支40%" if has_austerity else "政府日常行政运转公用采购与公共服务采购订单"
        self.execute_flow(
            from_acc="treasury_cash",
            to_acc="corporate_sector",
            amount=G_operating,
            category="政府采购与公共工程(G)",
            description=desc_g
        )
        G = G_operating + infra_daily_cost + infra_maint_cost
        
        # 当日名义 GDP (叠加已建成工程与科技成果拉动的年化GDP增益)
        gdp_infra_boost = (buffs.get("gdp_boost", 0.0) / 360.0)
        daily_gdp = C + I + G + gdp_infra_boost
        state.gdp_quarterly += daily_gdp
        state.firm_daily_revenue = daily_gdp
        
        # 企业贷款还息：企业账户 -> 商业银行资本运营户
        daily_loan_interest = round((state.corporate_debt * state.loan_interest_rate) / 360.0, 4)
        if daily_loan_interest > 0:
            self.execute_flow(
                from_acc="corporate_sector",
                to_acc="bank_operations",
                amount=daily_loan_interest,
                category="企业贷款还息",
                description="企业向商业银行按日偿还信贷利息"
            )
            
        # 企业统筹社保缴费 (60%部分)：企业账户 -> 全国社保基金
        firm_social_contrib = round(total_wages_paid * (state.social_contrib_rate * 0.6), 4)
        if firm_social_contrib > 0:
            self.execute_flow(
                from_acc="corporate_sector",
                to_acc="social_security_fund",
                amount=firm_social_contrib,
                category="企业统筹社保缴费",
                description="企业按员工工资基数代缴养老与工伤失业统筹金"
            )
            
        # 商品流转增值税与消费税：企业代扣代缴 -> 政府国库 (消除幽灵货币)
        vat_collected = round(C * state.vat_tax_rate, 4)
        if has_digital_tax:
            vat_collected = round(vat_collected * 1.25, 4)
        if vat_collected > 0:
            self.execute_flow(
                from_acc="corporate_sector",
                to_acc="treasury_cash",
                amount=vat_collected,
                category="增值与消费税",
                description="企业代扣代缴商品增值税与消费流转税" + (" (金税工程穿透增缴+25%)" if has_digital_tax else "")
            )
            
        # Phase 5: 企业所得税 (CIT, 20%~25%) 与亏损结转抵扣 (Loss Carry-Forward) 机制
        # 企业账户 -> 政府国库
        raw_taxable_profit = daily_gdp - total_wages_paid - daily_loan_interest - firm_social_contrib
        cur_carry = getattr(state, "corp_tax_loss_carry_forward", 0.0)
        corp_tax_deducted_loss = 0.0
        
        if raw_taxable_profit < 0:
            # 实体企业整体陷入营运亏损，亏损额计入亏损结转抵扣池 (Loss Carry-Forward)
            loss_today = round(abs(raw_taxable_profit), 4)
            state.corp_tax_loss_carry_forward = round(cur_carry + loss_today, 4)
            taxable_profit_est = 0.0
        else:
            # 处于盈利状态，优先使用历史亏损结转抵扣 (最高允许抵扣当期应税所得的 75%)
            if cur_carry > 0.0001:
                loss_offset = round(min(raw_taxable_profit * 0.75, cur_carry), 4)
                taxable_profit_est = max(0.0, round(raw_taxable_profit - loss_offset, 4))
                state.corp_tax_loss_carry_forward = round(max(0.0, cur_carry - loss_offset), 4)
                corp_tax_deducted_loss = loss_offset
            else:
                taxable_profit_est = raw_taxable_profit

        corp_tax_collected = round(taxable_profit_est * effective_corp_tax_rate, 4)
        if has_digital_tax:
            corp_tax_collected = round(corp_tax_collected * 1.25, 4)
        if corp_tax_collected > 0:
            desc_str = "企业按营业所得向税务部门申报缴纳所得税"
            if corp_tax_deducted_loss > 0:
                desc_str += f" (前期亏损结转抵扣 {corp_tax_deducted_loss:.2f} 亿)"
            if has_digital_tax:
                desc_str += " (金税工程穿透增缴+25%)"
            self.execute_flow(
                from_acc="corporate_sector",
                to_acc="treasury_cash",
                amount=corp_tax_collected,
                category="企业所得税",
                description=desc_str
            )
            
        # 金税工程运维支出 (若激活)
        if has_digital_tax:
            self.execute_flow(
                from_acc="treasury_cash",
                to_acc="corporate_sector",
                amount=0.04,
                category="金税系统运维",
                description="国家金税工程发票集群运维与数字穿透稽查支出"
            )
            
        # 企业营运净利润与指标
        cost_savings_bonus = (total_wages_paid * 0.35) * buffs.get("corp_cost_discount", 0.0)
        operating_profit = (daily_gdp - total_wages_paid - daily_loan_interest - corp_tax_collected - firm_social_contrib + cost_savings_bonus)
        operating_profit *= buffs.get("firm_profit_multiplier", 1.0)
        state.firm_daily_profit = round(max(0.10, operating_profit), 3)
        
        # 同步企业银行存款
        self.update_state_corporate_cash()
        
        # =========================================================================
        # Phase 3: 实体工业企业信用风险评级、差别化授信、还贷与银行主动抽贷风控 (严格SFC法则)
        # =========================================================================
        tot_issued = 0.0
        tot_repaid = 0.0
        tot_recalled = 0.0
        
        for f in self.factory_manager.factories.values():
            f.recalled_loans_today = 0.0
            f.new_borrowing_today = 0.0
            acc = self.accounting_bus.accounts.get(f.account_id)
            f_cash = acc.balance if acc else 0.0
            
            # 每日动态评估企业信用等级、利息保障倍数、授信额度与五级贷款分类
            f.evaluate_credit_rating(
                base_loan_rate=state.loan_interest_rate,
                cash_balance=f_cash,
                credit_crunch_active=getattr(state, "credit_crunch_active", False)
            )
            
            # (1) 违约/破产状态 (D级 / loss): 银行停止展期，进入司法破产清算与坏账核销 (在工厂lifecycle中处置)
            if f.credit_rating == "D" or f.status == "bankrupt":
                continue
                
            # (2) 预警高危企业 (CCC级 / doubtful): 银行风控启动主动抽贷 (Loan Recall)
            elif f.credit_rating == "CCC":
                # 银行优先从企业账上扣划款项偿还本金，压降敞口
                if f_cash > 0.5 and f.debt_principal > 2.0:
                    recall_amt = min(0.15, round(f_cash * 0.20, 4), round(f.debt_principal * 0.05, 4))
                    if recall_amt > 0.001:
                        self.accounting_bus.bank_credit_repay(f.account_id, recall_amt, is_corporate=True, description=f"商业银行风控触发对{f.name}强制抽贷压降敞口")
                        f.debt_principal = max(0.0, round(f.debt_principal - recall_amt, 4))
                        f.recalled_loans_today = recall_amt
                        tot_recalled += recall_amt
                        tot_repaid += recall_amt
                        daily_events.append(f"⚠️ 【商业银行风控抽贷】因连续亏损且评级跌入CCC，商业银行对{f.name}执行强制抽贷 {recall_amt:.2f} 亿元！")
                        
            # (3) 关注类与次级类企业 (BB / B级 / special_mention / substandard): 冻结新增授信，富余资金自主还款
            elif f.credit_rating in ["BB", "B"]:
                if f_cash > 6.0 and f.debt_principal > 10.0:
                    repay_amt = min(0.08, round(f_cash - 5.0, 4), round(f.debt_principal, 4))
                    if repay_amt > 0.001:
                        self.accounting_bus.bank_credit_repay(f.account_id, repay_amt, is_corporate=True, description=f"{f.name}用富余资金提前偿还银行贷款本金")
                        f.debt_principal = max(0.0, round(f.debt_principal - repay_amt, 4))
                        tot_repaid += repay_amt
                        
            # (4) 优良标杆与正常企业 (AAA ~ BBB级 / normal): 正常周转借贷与富余资金还贷
            else:
                # 缺流动资金备料且在授信额度内：申请银行周转贷款
                if f_cash < 1.0 and f.debt_principal < f.credit_limit and not getattr(state, "credit_crunch_active", False):
                    borrow_amt = min(0.12, round(f.credit_limit - f.debt_principal, 4), max(0.02, round(1.5 - f_cash, 4)))
                    if borrow_amt > 0.001:
                        self.accounting_bus.bank_credit_expand(f.account_id, borrow_amt, is_corporate=True, description=f"商业银行向优质企业{f.name}发放流动资金周转贷款 (评级:{f.credit_rating})")
                        f.debt_principal = round(f.debt_principal + borrow_amt, 4)
                        f.new_borrowing_today = borrow_amt
                        tot_issued += borrow_amt
                # 现金充裕时自主提前还贷，节约利息支出
                elif f_cash > 8.0 and f.debt_principal > 20.0:
                    repay_amt = min(0.12, round(f_cash - 6.0, 4), round(f.debt_principal, 4))
                    if repay_amt > 0.001:
                        self.accounting_bus.bank_credit_repay(f.account_id, repay_amt, is_corporate=True, description=f"{f.name}用经营利润结余偿还银行贷款本金")
                        f.debt_principal = max(0.0, round(f.debt_principal - repay_amt, 4))
                        tot_repaid += repay_amt

        # 汇总企业信贷统计
        state.daily_corporate_loans_issued = round(tot_issued, 4)
        state.daily_corporate_loans_repaid = round(tot_repaid, 4)
        state.daily_loans_recalled = round(tot_recalled, 4)
        state.corporate_debt = round(sum(f.debt_principal for f in self.factory_manager.factories.values()), 4)
        self.accounting_bus.bank_loans_corporate = state.corporate_debt
        self.update_state_corporate_cash()

        # 7. 政府财政与社会保障闭环结算 (全口径穿透式财政与社保决算)
        # (1) 财政支出执行：
        gov_welfare = state.welfare_spending
        medicare_subsidy = state.social_daily_gov_subsidy
        daily_gov_debt_interest = round((state.national_debt * state.national_debt_rate) / 360.0, 4)
        
        # 兜底救济金：政府国库 -> 特困居民账户
        if gov_welfare > 0:
            welfare_miner = round(gov_welfare * 0.6, 4)
            welfare_farmer = round(gov_welfare * 0.4, 4)
            self.execute_flow(
                from_acc="treasury_cash",
                to_acc="household_miner_heavy",
                amount=welfare_miner,
                category="低保与失业救济金",
                description="财政专项转移支付，直接补助采矿与建筑特困劳工"
            )
            self.execute_flow(
                from_acc="treasury_cash",
                to_acc="household_farmer",
                amount=welfare_farmer,
                category="低保与农资扶持救济",
                description="财政专项转移支付，补助农耕困难家庭"
            )
            
        # 医保社保财政常规补贴：政府国库 -> 全国社保基金
        total_medicare_subsidy_paid = medicare_subsidy
        if medicare_subsidy > 0:
            self.execute_flow(
                from_acc="treasury_cash",
                to_acc="social_security_fund",
                amount=medicare_subsidy,
                category="财政医保贴息补贴",
                description="财政部向国家医保与基本养老统筹基金注入财政托底补贴"
            )
            
        # 财政对社保医保蓄水池的自动托底注资机制 (若资金池低于 60 亿元且国库有可用现金)
        current_ss_pool = self.accounting_bus.accounts["social_security_fund"].balance
        if current_ss_pool < 60.0 and state.treasury_cash > 10.0:
            emergency_ss_backstop = round(min(5.0, max(1.0, (60.0 - current_ss_pool) * 0.25)), 2)
            self.execute_flow(
                from_acc="treasury_cash",
                to_acc="social_security_fund",
                amount=emergency_ss_backstop,
                category="财政社保托底注资",
                description=f"全国社保医保蓄水池偏低({current_ss_pool:.1f}亿)，中央财政启动刚性托底注资"
            )
            total_medicare_subsidy_paid = round(total_medicare_subsidy_paid + emergency_ss_backstop, 4)
            daily_events.append(f"🛡️ 【医保社保财政托底】全国社保医保资金池偏紧，财政部紧急注资 {emergency_ss_backstop:.1f} 亿元确保养老与医疗报销刚性兑付！")
            
        # 存量国债利息：商业银行持有85%，高净值科研专家与投资居民国债理财持有15%
        if daily_gov_debt_interest > 0:
            bank_bond_int = round(daily_gov_debt_interest * 0.85, 4)
            retail_bond_int = round(daily_gov_debt_interest - bank_bond_int, 4)
            if bank_bond_int > 0:
                self.execute_flow(
                    from_acc="treasury_cash",
                    to_acc="bank_operations",
                    amount=bank_bond_int,
                    category="国债利息支出(银行持有)",
                    description="财政部按期向商业银行间市场划付存量国债利息"
                )
            if retail_bond_int > 0:
                self.execute_flow(
                    from_acc="treasury_cash",
                    to_acc="household_engineer_expert",
                    amount=retail_bond_int,
                    category="国债利息支出(居民理财)",
                    description="财政部向高净值科研专家与投资居民划付储蓄国债票面分红"
                )
            
        # (2) 医保社保基金闭环独立收支结算：
        # 社保基金协议存款利息：商业银行资本运营户 -> 全国社保基金
        ss_balance = self.accounting_bus.accounts["social_security_fund"].balance
        daily_ss_interest = round((ss_balance * state.deposit_interest_rate) / 360.0, 4)
        if daily_ss_interest > 0.00001:
            self.execute_flow(
                from_acc="bank_operations",
                to_acc="social_security_fund",
                amount=daily_ss_interest,
                category="社保基金存单利息",
                description="商业银行向全国社保基金支付协议存款利息"
            )
            
        # 医保报销支出：受消费品市场就医购药与老年退休人口医疗负荷拉动
        ret_pop = getattr(state, "retired_population", 1_700_000)
        elder_med_weight = 1.0 + (ret_pop / 1_700_000.0 - 1.0) * 0.4
        daily_medicare_reimbursed = round((C * 0.10) * state.medicare_reimburse_rate * elder_med_weight, 4)
        if daily_medicare_reimbursed > 0:
            self.execute_flow(
                from_acc="social_security_fund",
                to_acc="corporate_sector",
                amount=daily_medicare_reimbursed,
                category="医保统筹报销结算",
                description="国家医保中心向定点医院与医药企业结算医保统筹报销款"
            )
            
        # 基础养老金发放：全国社保基金 -> 各阶层退休家庭 (真实受退休人口规模与人均标准驱动)
        pension_std = getattr(state, "pension_daily_standard", 26.5)
        daily_pension_payout = round((ret_pop * pension_std) / 100_000_000.0, 4)
        self.execute_flow(
            from_acc="social_security_fund",
            to_acc="household_miner_heavy",
            amount=round(daily_pension_payout * 0.35, 4),
            category="基本养老金发放",
            description="国家社保基金向采矿普工退休老人发放养老金"
        )
        self.execute_flow(
            from_acc="social_security_fund",
            to_acc="household_farmer",
            amount=round(daily_pension_payout * 0.35, 4),
            category="农村基础养老金",
            description="国家社保基金向农村高龄自耕农发放基础养老金"
        )
        self.execute_flow(
            from_acc="social_security_fund",
            to_acc="household_operator_light",
            amount=round(daily_pension_payout * 0.20, 4),
            category="职工养老金发放",
            description="国家社保基金向轻工退休老工人发放退休金"
        )
        self.execute_flow(
            from_acc="social_security_fund",
            to_acc="household_technician_skilled",
            amount=round(daily_pension_payout * 0.10, 4),
            category="技师退休金发放",
            description="国家社保基金向高技能退休老技师发放养老金"
        )
        
        # 法定失业救济金 (UI Auto-Stabilizer): 依照在册失业人口与法定标准自动逆周期发放
        unemployed_count_total = int(state.working_population * state.unemployment_rate)
        daily_ui_standard = getattr(state, "unemployment_relief_standard", 28.0) # 元/天/人
        total_ui_disbursement = round((unemployed_count_total * daily_ui_standard) / 100_000_000.0, 4) # 亿元/天
        
        ss_avail = self.accounting_bus.accounts["social_security_fund"].balance
        actual_ui = 0.0
        if total_ui_disbursement > 0.0001 and ss_avail > 0.1:
            actual_ui = min(total_ui_disbursement, ss_avail * 0.4)
            ui_miner = round(actual_ui * 0.55, 4)
            ui_farmer = round(actual_ui - ui_miner, 4)
            self.execute_flow(
                from_acc="social_security_fund",
                to_acc="household_miner_heavy",
                amount=ui_miner,
                category="失业保险待遇发放(UI)",
                description=f"全国社保基金向失业重工及矿工发放失业保险金({daily_ui_standard:.0f}元/天标准)"
            )
            self.execute_flow(
                from_acc="social_security_fund",
                to_acc="household_farmer",
                amount=ui_farmer,
                category="失业保险待遇发放(UI)",
                description="全国社保基金向失业转岗及进城零工发放失业兜底保险金"
            )

        # 逆周期以工代赈与重大工程拉动 (Counter-Cyclical Public Works)
        if state.unemployment_rate > 0.15 or state.consumer_sentiment < 30.0:
            if not getattr(state, "counter_cyclical_boost_active", False):
                daily_events.append("🏗️ 【财政逆周期调控启动】失业率走高或民间消费信心低迷，财政部启动以工代赈与重大基建定向采购托底！")
            state.counter_cyclical_boost_active = True
        elif state.unemployment_rate <= 0.10 and state.consumer_sentiment >= 45.0:
            if getattr(state, "counter_cyclical_boost_active", False):
                daily_events.append("🌱 【财政逆周期调控退出】实体就业与民间信心恢复，重大工程托底平稳转入常态运维。")
            state.counter_cyclical_boost_active = False

        # 汇总社保基金大盘动态
        total_social_rev = firm_social_contrib + total_worker_social_contrib + total_medicare_subsidy_paid + daily_ss_interest
        total_social_payout = daily_medicare_reimbursed + daily_pension_payout + actual_ui
        state.social_daily_revenue = round(total_social_rev, 4)
        state.social_daily_payout = round(total_social_payout, 4)
        state.social_daily_balance = round(total_social_rev - total_social_payout, 4)
        state.social_fund_pool = round(self.accounting_bus.accounts["social_security_fund"].balance, 2)
        
        # 同步国库与财政决算指标
        state.treasury_cash = round(self.accounting_bus.accounts["treasury_cash"].balance, 4)
        daily_total_tax = corp_tax_collected + vat_collected + total_income_tax_collected
        daily_total_expense = G_operating + infra_daily_cost + infra_maint_cost + gov_welfare + total_medicare_subsidy_paid + daily_gov_debt_interest
        if has_digital_tax:
            daily_total_expense += 0.04
        daily_gov_deficit = daily_total_expense - daily_total_tax
        state.fiscal_daily_revenue = round(daily_total_tax, 4)
        state.fiscal_daily_expense = round(daily_total_expense, 4)
        state.fiscal_daily_deficit = round(daily_gov_deficit, 4)
        
        annual_gdp_est = max(1.0, daily_gdp * 360.0)
        state.deficit_to_gdp_rate = round(((daily_gov_deficit * 360.0) / annual_gdp_est) * 100.0, 2)
        state.debt_to_gdp_rate = round((state.national_debt / annual_gdp_est) * 100.0, 1)

        # Phase 5: 现代国家主权信用评级 (Sovereign Credit Rating) 4要素模型
        # 1. 债务率 (Debt/GDP): 警戒线 60%
        # 2. 赤字率 (Deficit/GDP): 警戒线 3%
        # 3. 国库流动性储备天数: 国库现金 / 日均总支出
        # 4. 政策公信力: 0 ~ 100
        buffer_days = round(state.treasury_cash / max(0.01, daily_total_expense), 1)
        score = 100.0
        score -= min(40.0, max(0.0, (state.debt_to_gdp_rate - 30.0) / 40.0 * 30.0))
        score -= min(35.0, max(0.0, (state.deficit_to_gdp_rate - 2.5) / 4.0 * 30.0))
        if buffer_days < 20.0:
            score -= min(25.0, (20.0 - buffer_days) * 1.25)
        else:
            score += min(10.0, (buffer_days - 20.0) * 0.2)
        score += (state.policy_credibility - 60.0) * 0.25
        score = round(max(0.0, min(100.0, score)), 1)

        if score >= 82.0:
            rating, spread = "AAA", 0.0
        elif score >= 70.0:
            rating, spread = "AA", 0.0035
        elif score >= 55.0:
            rating, spread = "A", 0.0080
        elif score >= 40.0:
            rating, spread = "BBB", 0.0160
        elif score >= 25.0:
            rating, spread = "BB", 0.0300
        elif score >= 12.0:
            rating, spread = "B", 0.0500
        else:
            rating, spread = "CCC/D", 0.0800

        prev_rating = getattr(state, "sovereign_credit_rating", "AAA")
        state.sovereign_credit_rating = rating
        state.sovereign_risk_spread = spread
        state.sovereign_bond_yield = round(max(0.015, state.base_interest_rate + 0.010 + spread), 4)
        state.national_debt_rate = state.sovereign_bond_yield

        if prev_rating != rating and state.day > 1:
            daily_events.append(f"📊 【主权信用评级变动】国际评级机构将本国主权评级调整为 [{rating}] (综合得分: {score:.1f})！国债违约风险息差调整为 +{spread*10000:.0f} bps，发债收益率调整为 {state.sovereign_bond_yield*100:.2f}%！")
        
        state.tax_breakdown = {
            "corp_tax": round(corp_tax_collected, 3),
            "vat_tax": round(vat_collected, 3),
            "income_tax": round(total_income_tax_collected, 3)
        }
        state.expense_breakdown = {
            "gov_works": round(G_operating, 3),
            "welfare": round(gov_welfare, 3),
            "infra_projects": round(infra_daily_cost, 3),
            "infra_maintenance": round(infra_maint_cost, 3),
            "medicare_subsidy": round(total_medicare_subsidy_paid, 3),
            "debt_interest": round(daily_gov_debt_interest, 3)
        }
        
        # 国库现金头寸与国债自动发行机制 (赤字融资闭环)
        if state.treasury_cash < 35.0 and daily_gov_deficit > 0:
            borrow_amt = round(max(15.0, daily_gov_deficit * 30.0), 1)
            debt_limit = getattr(state, "national_debt_limit", 2500.0)
            if state.national_debt + borrow_amt <= debt_limit:
                # 通过 accounting_bus 从商业银行吸收存款认购国债，注入国库
                self.execute_flow(
                    from_acc="bank_operations",
                    to_acc="treasury_cash",
                    amount=borrow_amt,
                    category="财政部发售国债",
                    description=f"中央财政发行记账式国债 {borrow_amt:.1f} 亿元补充国库现金流动性"
                )
                state.national_debt = round(state.national_debt + borrow_amt, 2)
                self.accounting_bus.bank_treasury_bonds += borrow_amt
                state.treasury_cash = round(self.accounting_bus.accounts["treasury_cash"].balance, 4)
                daily_events.append(f"📜 【国债定期承销】中央国库现金头寸偏紧，财政部面向银行间市场成功招标发行 {borrow_amt:.1f} 亿元国债 (主权评级: {state.sovereign_credit_rating}, 发债年化收益率: {state.sovereign_bond_yield*100:.2f}%)！")
            else:
                daily_events.append(f"🚨 【触及国债法定上限】存量国债已达 {state.national_debt:.1f} 亿元，逼近法定发行上限 {debt_limit:.1f} 亿元，国债承销暂缓，急需财政节流或议会提高限额！")
        
        # 国库流动性监管预警
        if state.treasury_cash < 15.0 and state.treasury_cash > 0.0:
            if state.day % 30 == 0:
                daily_events.append(f"⚠️ 【财政流动性紧缩警报】中央国库现金仅剩 {state.treasury_cash:.1f} 亿元！资金即将断流，请内阁及时在财政控制台主动发行国债补充现金！")
        elif state.treasury_cash <= 0.0:
            state.treasury_cash = 0.0
            if state.day % 15 == 0:
                daily_events.append("🚨 【国库资金链告罄】国库现金为 0！因未及时发行国债募集资金，部分财政与工程开支被延期，政策公信力受到惩罚 (-0.3)！")
            state.policy_credibility = max(5.0, state.policy_credibility - 0.01)

        # 8. 商业银行体系资产负债与监管指标 (Phase 3: Basel Capital & Credit Cycle)
        # 同步各阶层最新居民储蓄 (包含日内发放的国债利息、失业救济金与退休金)
        for idx, h in enumerate(state.households):
            hid = f"household_{h.id}" if getattr(h, "id", "") else f"household_tier_{idx}"
            if hid in self.accounting_bus.accounts:
                h.savings = round(self.accounting_bus.accounts[hid].balance, 4)

        # 同步全社会存款总额 = 居民存款 + 企业现金 + 社保基金存款
        h_total_savings = sum(h.savings for h in state.households)
        state.bank_deposits = round(h_total_savings + state.corporate_cash + state.social_fund_pool, 2)
        self.accounting_bus.bank_deposits = state.bank_deposits
        
        # 商业银行信贷总额 = 实体企业贷款本金存量 + 居民住房按揭贷款
        mortgage = getattr(state, "household_mortgage_debt", 1600.0)
        state.bank_loans = round(state.corporate_debt + mortgage, 2)
        self.accounting_bus.bank_loans = state.bank_loans
        
        # 商业银行自有资本净资产 = bank_operations 账户余额
        state.bank_capital = round(self.accounting_bus.accounts["bank_operations"].balance, 2)
        
        # 商业银行过剩留存利润派发股息分红 (分红给 engineer_expert 高管科研专家)
        if state.bank_capital > 420.0:
            dividend = min(0.08, round((state.bank_capital - 380.0) * 0.08, 4))
            self.execute_flow(
                from_acc="bank_operations",
                to_acc="household_engineer_expert",
                amount=dividend,
                category="银行经营分红",
                description="商业银行向股东派发留存利润现金股利分红"
            )
            state.bank_capital = round(self.accounting_bus.accounts["bank_operations"].balance, 2)
            state.households[-1].savings = round(self.accounting_bus.accounts["household_engineer_expert"].balance, 4)
            
        # 央行法定准备金池
        state.bank_reserve_cash = round(state.bank_deposits * state.reserve_ratio, 1)
        # 贷存比 (LDR, 监管预警线 85.0%)
        state.loan_to_deposit_ratio = round((state.bank_loans / max(1.0, state.bank_deposits)) * 100.0, 1)

        # 巴塞尔资本充足率 (CAR, 监管红线 8.0%)
        # 风险加权资产 RWA = 企业贷款*100% + 居民房贷*50% + 国债*0%
        rwa = state.corporate_debt * 1.0 + mortgage * 0.5
        state.risk_weighted_assets = round(rwa, 2)
        car = round((state.bank_capital / max(1.0, rwa)) * 100.0, 2)
        state.capital_adequacy_ratio = car
        if car < 8.0:
            if not getattr(state, "credit_crunch_active", False):
                daily_events.append(f"⚠️ 【巴塞尔监管红线告警】商业银行资本充足率跌至 {car:.1f}% (低于8.0%监管红线)！全面触发信贷紧缩（Credit Crunch），银行全面收紧授信！")
            state.credit_crunch_active = True
        else:
            state.credit_crunch_active = False

        # 不良贷款统计与拨备计提 (五级分类五层穿透)
        npl_corp = sum(f.debt_principal for f in self.factory_manager.factories.values() if f.loan_status in ["substandard", "doubtful", "loss"])
        npl_household = mortgage * max(0.012, min(0.12, state.poverty_rate * 0.08 + max(0.0, state.base_interest_rate - 0.03) * 0.4))
        tot_npl = round(npl_corp + npl_household, 2)
        state.bank_npl_loans = tot_npl
        state.bad_debt_rate = round(tot_npl / max(1.0, state.bank_loans), 4)
        state.bank_npl_ratio = round(state.bad_debt_rate * 100.0, 2)

        # 每日计提贷款损失准备金
        norm_loans = sum(f.debt_principal for f in self.factory_manager.factories.values() if f.loan_status == "normal")
        spec_loans = sum(f.debt_principal for f in self.factory_manager.factories.values() if f.loan_status == "special_mention")
        sub_loans = sum(f.debt_principal for f in self.factory_manager.factories.values() if f.loan_status == "substandard")
        doubt_loans = sum(f.debt_principal for f in self.factory_manager.factories.values() if f.loan_status == "doubtful")
        loss_loans = sum(f.debt_principal for f in self.factory_manager.factories.values() if f.loan_status == "loss")
        daily_prov = (norm_loans * 0.015 + spec_loans * 0.03 + sub_loans * 0.20 + doubt_loans * 0.50 + loss_loans * 1.0) / 360.0
        state.daily_bank_provision_deduction = round(daily_prov, 4)
        state.bank_provisions_pool = round(max(50.0, getattr(state, "bank_provisions_pool", 200.0) + daily_prov - self.accounting_bus.daily_bad_debt_write_off), 2)
        state.bank_provision_coverage = round((state.bank_provisions_pool / max(1.0, tot_npl)) * 100.0, 1)

        # 息差核算与坏账统计
        corp_int_rev = sum((f.debt_principal * f.borrowing_rate) / 360.0 for f in self.factory_manager.factories.values())
        mort_int_rev = (mortgage * (state.base_interest_rate + 0.015)) / 360.0
        state.daily_bank_loan_interest_rev = round(corp_int_rev + mort_int_rev, 4)
        state.daily_bank_deposit_interest_cost = round((state.bank_deposits * state.deposit_interest_rate) / 360.0, 4)
        state.daily_bank_net_interest_margin = round(state.daily_bank_loan_interest_rev - state.daily_bank_deposit_interest_cost, 4)
        state.daily_bank_write_offs = round(self.accounting_bus.daily_bad_debt_write_off, 4)

        # 企业信用评级矩阵导出 (列表格式)
        state.corporate_credit_ratings = [
            {
                "id": f.id,
                "name": f.name,
                "rating": f.credit_rating,
                "score": f.credit_score,
                "credit_score": f.credit_score,
                "leverage_ratio": f.leverage_ratio,
                "icr": f.interest_coverage_ratio,
                "interest_coverage_ratio": f.interest_coverage_ratio,
                "debt_principal": round(f.debt_principal, 2),
                "borrowing_rate": round(f.borrowing_rate * 100, 2),
                "loan_status": f.loan_status,
                "status": f.loan_status,
                "credit_limit": round(f.credit_limit, 2),
                "recalled_today": round(f.recalled_loans_today, 3),
                "new_borrowing_today": round(f.new_borrowing_today, 3)
            } for f in self.factory_manager.factories.values()
        ]

        # 实体产能利用率
        state.capacity_utilization_rate = round(min(100.0, (state.gdp_annual_runrate / max(1.0, state.corporate_capacity)) * 100.0), 1)

        # =========================================================================
        # 8.2 Phase 4: 国际收支平衡表 (BOP)、浮动汇率、主权外汇基金与荷兰病博弈
        # =========================================================================
        # (1) 实体轻工制造与机加出口自主外贸结算 (受制造业价格竞争力指数 MCI 联动)
        curr_mci = getattr(state, "manufacturing_competitiveness_index", 100.0)
        mci_mult = max(0.20, min(2.0, curr_mci / 100.0))
        
        # 1.1 轻纺成衣外销自主结汇 (朱老板等全国1800家轻工服装厂)
        f_textile = self.factory_manager.factories.get("textile_light")
        if f_textile and f_textile.status not in ["bankrupt", "suspended"]:
            textile_tariff = state.anti_dumping_tariffs.get("textile", 0.0)
            base_apparel_usd = 0.022 # 约 1600 万元/天 (以 7.20 汇率折算)
            daily_apparel_usd = round(base_apparel_usd * mci_mult * (1.0 - textile_tariff), 4)
            if daily_apparel_usd > 0.0001:
                self.accounting_bus.fx_settle_export(
                    exporter_acc_id="corp_textile_light",
                    usd_amount=daily_apparel_usd,
                    description=f"轻纺服装海关报关结汇创汇 (MCI竞争力:{curr_mci:.1f})"
                )
                
        # 1.2 精密机械五金零部件自主外销创汇 (陈厂长等全国2500家五金机加厂)
        f_mach = self.factory_manager.factories.get("hardware_machinery")
        if f_mach and f_mach.status not in ["bankrupt", "suspended"]:
            base_mach_usd = 0.012 # 约 860 万元/天
            daily_mach_usd = round(base_mach_usd * mci_mult, 4)
            if daily_mach_usd > 0.0001:
                self.accounting_bus.fx_settle_export(
                    exporter_acc_id="corp_hardware_machinery",
                    usd_amount=daily_mach_usd,
                    description=f"精密机械配件海关报关结汇 (MCI竞争力:{curr_mci:.1f})"
                )
                
        # 1.3 工业高精芯片与特种工业耗材日常刚性进口付汇
        if state.foreign_reserves_usd > 3.0:
            daily_rigid_import_usd = 0.018 # 约 1300 万元/天
            self.accounting_bus.fx_purchase_import(
                importer_acc_id="corporate_sector",
                usd_amount=daily_rigid_import_usd,
                description="工业企业进口高端电子芯片与核心耗材付汇"
            )

        # 1.4 民用原油缺口与化工原料日常商贸进口付汇 (随全社会刚性需求流转)
        if state.foreign_reserves_usd > 5.0:
            daily_energy_import_usd = 0.015 # 约 1100 万元/天
            self.accounting_bus.fx_purchase_import(
                importer_acc_id="corporate_sector",
                usd_amount=daily_energy_import_usd,
                description="民用能源化工与大宗工业原料常态化商贸进口付汇"
            )

        # (2) 全社会国际收支平衡表 (BOP Current Account) 统计
        curr_fx = state.exchange_rate if state.exchange_rate > 0 else 7.20
        daily_exports_usd = round(self.accounting_bus.daily_fx_inflow_cny / curr_fx, 4)
        daily_imports_usd = round(self.accounting_bus.daily_fx_outflow_cny / curr_fx, 4)
        current_account_usd = round(daily_exports_usd - daily_imports_usd, 4)
        
        state.bop_exports_usd = daily_exports_usd
        state.bop_imports_usd = daily_imports_usd
        state.bop_current_account_usd = current_account_usd
        state.bop_trade_surplus_cny = round(current_account_usd * curr_fx, 4)
        state.foreign_reserves_usd = round(self.accounting_bus.foreign_reserves_usd, 2)

        # (3) 海外主权财富基金 (SWF) 与外汇冲销运作 (Sterilization)
        # 顺差时按冲销比例将多余外汇转入海外主权投资专户，避免即期外汇市场供需失衡推动本币过快升值
        sterilize_ratio = getattr(state, "fx_sterilization_ratio", 0.0)
        sterilized_amount_usd = 0.0
        if sterilize_ratio > 0.01 and current_account_usd > 0.0:
            sterilized_amount_usd = round(current_account_usd * sterilize_ratio, 4)
            state.sovereign_wealth_fund_usd = round(getattr(state, "sovereign_wealth_fund_usd", 0.0) + sterilized_amount_usd, 3)
            # 从央行即期外汇储备池划转到海外主权基金专户
            self.accounting_bus.foreign_reserves_usd = max(2.0, round(self.accounting_bus.foreign_reserves_usd - sterilized_amount_usd, 4))
            state.foreign_reserves_usd = round(self.accounting_bus.foreign_reserves_usd, 2)
            
        # 海外主权财富基金每日海外资产投资收益 (年化 3.6% 美债/全球稳健组合)
        swf_principal = getattr(state, "sovereign_wealth_fund_usd", 0.0)
        if swf_principal > 0.05:
            daily_swf_yield = round((swf_principal * 0.036) / 360.0, 6)
            state.swf_daily_yield_usd = daily_swf_yield
            # 分红收益全额结汇注入中央国库单一账户 (TSA) 充实财政实力
            if daily_swf_yield > 0.000001:
                self.accounting_bus.fx_settle_export(
                    exporter_acc_id="treasury_cash",
                    usd_amount=daily_swf_yield,
                    description="海外主权财富基金(SWF)投资收益结汇归入中央国库"
                )
                state.foreign_reserves_usd = round(self.accounting_bus.foreign_reserves_usd, 2)
        else:
            state.swf_daily_yield_usd = 0.0

        # (4) 浮动汇率自动调节模型 (Floating Exchange Rate Engine)
        res_baseline = 25.0 if state.difficulty_mode == "frugal" else (45.0 if state.difficulty_mode == "standard" else 10.0)
        res_ratio = max(0.20, min(3.50, state.foreign_reserves_usd / max(5.0, res_baseline)))
        
        # 即期市场上未被冲销的净结售汇对外汇供需造成压力
        effective_market_surplus = current_account_usd - sterilized_amount_usd
        ca_pressure = max(-0.25, min(0.25, effective_market_surplus / max(6.0, state.foreign_reserves_usd)))
        
        # 目标均衡汇率：顺差越大/储备越多 -> 本币越升值(汇率越低)；逆差/储备枯竭 -> 本币越贬值(汇率越高)
        fx_base = getattr(state, "exchange_rate_baseline", 7.20)
        target_fx = round(fx_base / ((res_ratio ** 0.40) * (1.0 + ca_pressure * 1.5)), 2)
        target_fx = max(4.50, min(12.00, target_fx)) # 设定汇率宏观安全走廊 [4.50, 12.00]
        
        # 粘性平滑汇率走势 (每日向目标汇率收敛 5%)
        old_fx = state.exchange_rate
        state.exchange_rate = round(old_fx * 0.95 + target_fx * 0.05, 2)
        self.accounting_bus.exchange_rate = state.exchange_rate

        # (5) 制造业价格竞争力指数 (MCI) 与荷兰病 (Dutch Disease) 判定
        new_mci = round(((state.exchange_rate / fx_base) ** 1.35) * 100.0, 1)
        state.manufacturing_competitiveness_index = new_mci
        
        # 统计滚动资源型大宗商品出口创汇占比 (煤矿、原油等)
        c_coal = self.commodity_hub.commodities.get("coal")
        coal_exp_usd = self.commodity_hub.calculate_customs_usd("coal", c_coal.daily_exports) if c_coal else 0.0
        recent_resource_exp = getattr(state, "recent_resource_exports_usd", 0.0) * 0.95 + coal_exp_usd
        recent_total_exp = getattr(state, "recent_total_exports_usd", 0.0) * 0.95 + daily_exports_usd
        state.recent_resource_exports_usd = round(recent_resource_exp, 4)
        state.recent_total_exports_usd = round(recent_total_exp, 4)
        resource_share = (recent_resource_exp / max(0.01, recent_total_exp)) if recent_total_exp > 0.01 else 0.0
        
        # 荷兰病触发条件：资源大宗出口占比高(>=25%) + 本币汇率持续升值(≤6.65) + 制造业竞争力被削弱(<90.0)
        # 或者 汇率出现深度升值(≤5.80) 伴随外汇储备激增(res_ratio >= 1.3)
        is_dutch_condition = (
            (resource_share >= 0.25 and state.exchange_rate <= 6.65 and new_mci < 90.0) or
            (state.exchange_rate <= 5.80 and new_mci < 75.0) or
            (res_ratio >= 1.3 and state.exchange_rate <= 6.70 and resource_share >= 0.20)
        )
        if is_dutch_condition:
            if not getattr(state, "dutch_disease_active", False):
                daily_events.append(f"🚨 【荷兰病危机爆发 (Dutch Disease)】大宗资源暴利出口导致本币剧烈升值至 1 USD = {state.exchange_rate:.2f} CNY！制造业价格竞争力跌至 {new_mci:.1f}，朱老板外贸成衣订单遭腰斩，实体轻工面临洗牌风险！")
            state.dutch_disease_active = True
        elif getattr(state, "dutch_disease_active", False) and (state.exchange_rate > 6.75 or new_mci >= 92.0):
            daily_events.append(f"✅ 【荷兰病警报解除】随着汇率回温与外汇冲销调控，本币汇率回升至 1 USD = {state.exchange_rate:.2f} CNY，制造业竞争力指数回升至 {new_mci:.1f}！")
            state.dutch_disease_active = False

        # (6) 海外反倾销调查与惩罚性关税动态退坡 (煤炭、钢材等重点大宗)
        for target_cid, quota_thr, penalty_rate in [("coal", 4.5, 0.20), ("steel", 2.5, 0.25)]:
            c_target = self.commodity_hub.commodities.get(target_cid)
            if c_target and c_target.daily_exports > quota_thr:
                if state.anti_dumping_tariffs.get(target_cid, 0.0) < penalty_rate:
                    state.anti_dumping_tariffs[target_cid] = penalty_rate
                    daily_events.append(f"⚠️ 【国际反倾销调查】因我国【{c_target.name}】单日出口 ({c_target.daily_exports:.1f}{c_target.unit}) 远超国际配额承受极限，海外市场正式立案征收 {penalty_rate*100:.0f}% 惩罚性反倾销关税！")
            elif state.anti_dumping_tariffs.get(target_cid, 0.0) > 0:
                if c_target and c_target.daily_exports < 0.5 and state.day % 15 == 0:
                    state.anti_dumping_tariffs[target_cid] = max(0.0, round(state.anti_dumping_tariffs[target_cid] - 0.05, 2))
                    if state.anti_dumping_tariffs[target_cid] == 0.0:
                        daily_events.append(f"✅ 【反倾销制裁撤销】海外进口国撤销对我国【{c_target.name}】的反倾销关税，出口秩序恢复正常。")
        
        # 每日终章：五大部门资金清算审计大盘执行
        audit = self.accounting_bus.end_day_and_audit()
        self.last_audit = audit
        if not audit.is_balanced:
            daily_events.append(f"⚠️ 【资金清算异常】当日宏观资金流转存在借贷不平衡: 误差额={audit.flow_discrepancy:.4f} 亿元！")


        # 9. 六大核心指标更新
        total_labor = sum(h.labor_force for h in state.households)
        total_emp = sum(h.employed for h in state.households)
        state.unemployment_rate = max(0.01, min(0.60, 1.0 - (total_emp / total_labor)))
        
        # 贫困率 (扣除民生工程直接减贫与医疗大病救助加成)
        base_pov = impoverished_population / state.total_population
        state.poverty_rate = max(0.01, min(1.0, base_pov - buffs.get("poverty_reduction", 0.0)))
        
        # 恩格尔系数 (扣除超级杂交良种农业增产带来的主粮降本直接减免)
        if total_household_spending > 0:
            raw_engel = total_food_spending / total_household_spending
        else:
            raw_engel = 0.60
        state.engel_coefficient = max(0.15, min(0.90, raw_engel - buffs.get("engel_direct_relief", 0.0)))
            
        # 年化整体 GDP 与 人均 GDP
        state.gdp_annual_runrate = daily_gdp * 360.0
        state.gdp_per_capita = (state.gdp_annual_runrate * 100_000_000) / state.total_population
        
        # 消费意向受【失业率】、【贫困率】、【政策公信力】、【政策卡】及【民生基建】驱动
        base_sentiment = 30.0
        emp_bonus = (0.20 - state.unemployment_rate) * 60.0 # 失业降则信心升
        poverty_penalty = (state.poverty_rate - 0.40) * 40.0
        cred_bonus = (state.policy_credibility - 80.0) * 0.3
        card_sentiment = 0.0
        if has_new_deal: card_sentiment += 14.0
        if has_reagan: card_sentiment += 6.0
        if has_helicopter: card_sentiment += 25.0
        
        target_sentiment = base_sentiment + emp_bonus - poverty_penalty + cred_bonus + card_sentiment + buffs.get("sentiment_bonus", 0.0)
        # 平滑过渡
        state.consumer_sentiment = round(max(5.0, min(95.0, state.consumer_sentiment * 0.95 + target_sentiment * 0.05)), 1)
        
        # 10. 微观民生物价与金融借贷成本更新 (贴近真实生活)
        # (1) 菜篮子与口粮物价：受供求缺口、货币注入与农业良种育种突破打折影响
        capacity_pressure = max(-0.15, min(0.40, (state.gdp_annual_runrate - state.corporate_capacity) / state.corporate_capacity))
        money_push = 0.08 if has_helicopter else 0.0
        interest_suppress = max(-0.10, (state.base_interest_rate - 0.04) * 1.5)
        inflation_rate_est = max(-0.05, capacity_pressure * 0.5 + money_push - interest_suppress)
        
        # 每日平滑口粮价格 (基期 15.0 元，联动大宗原粮现货价与农业育种突破)
        food_discount = buffs.get("food_price_discount", 0.0)
        grain_c = self.commodity_hub.commodities.get("raw_grain") if hasattr(self, "commodity_hub") else None
        grain_factor = (grain_c.domestic_price / 2200.0) if grain_c else 1.0
        target_food_price = 15.0 * (1.0 + inflation_rate_est) * (1.0 - food_discount) * (0.6 + 0.4 * grain_factor)
        state.food_basket_price = round(state.food_basket_price * 0.98 + target_food_price * 0.02, 2)
        
        # 综合全社会居民消费价格指数 (CPI 篮子权重拆解：30%食品口粮 + 25%住房居住 + 20%轻工日用品 + 15%医疗服务 + 10%交通能源)
        comms = self.commodity_hub.commodities if hasattr(self, "commodity_hub") else {}
        w_food = state.food_basket_price / 15.0
        w_housing = max(0.8, 1.0 + (state.loan_interest_rate - 0.065) * 2.0)
        w_textile = (comms.get("textile").domestic_price / 45.0) if "textile" in comms else 1.0
        w_med = ((comms.get("medicine").domestic_price / 120.0) * (1.5 - state.medicare_reimburse_rate * 0.5)) if "medicine" in comms else 1.0
        p_oil = (comms.get("crude_oil").domestic_price / 520.0) if "crude_oil" in comms else 1.0
        p_elec = (comms.get("electricity").domestic_price / 0.45) if "electricity" in comms else 1.0
        w_energy = 0.5 * p_oil + 0.5 * p_elec
        
        cpi_basket_ratio = 0.30 * w_food + 0.25 * w_housing + 0.20 * w_textile + 0.15 * w_med + 0.10 * w_energy
        state.cpi_index = round(cpi_basket_ratio * 100.0, 1)
        
        # (2) 金融借贷真实成本
        # 每借 1 万元每月要还的商业贷款利息 (元/月)
        state.loan_cost_per_10k_month = round((10000.0 * state.loan_interest_rate) / 12.0, 1)
        # 每存 1 万元在银行一年能拿到的利息 (元/年)
        state.deposit_yield_per_10k_year = round(10000.0 * state.deposit_interest_rate, 1)
        
        # (3) 动态人口结构、生育意愿与少儿成活率 (受教育程度/学历、贫困失业、医疗保障及口粮物价驱动)
        # 经典人口学与贝克尔数量-质量替代假说：
        # - 平均学历与教育普及 (school_count / research)：最核心的负相关因子 (高学历推迟婚育、抚养精英化)
        # - 贫困率与失业率：正相关因果 (低机会成本、养儿防老对冲生存风险)
        # - 现代社保养老金充足度：负向替代 (削弱传统多子养老依赖)
        base_tfr = 1.65
        edu_suppression = (state.school_count - 150) * 0.006 + (getattr(state, "research_capability", 45.0) - 45.0) * 0.008
        poverty_boost = (state.poverty_rate - 0.35) * 1.5
        unemp_boost = (state.unemployment_rate - 0.18) * 0.8
        pension_substitution = (state.social_fund_pool - 450.0) * 0.0004
        interest_penalty = (state.loan_interest_rate - 0.065) * 1.5
        
        target_tfr = base_tfr - edu_suppression + poverty_boost + unemp_boost - pension_substitution - interest_penalty
        state.fertility_rate = max(0.80, min(3.20, round(getattr(state, "fertility_rate", 1.65) * 0.98 + target_tfr * 0.02, 2)))
        state.birth_rate_annual = round((state.fertility_rate / 2.1) * 11.5, 1)
        
        # 少儿/婴幼儿成活率 (Child Survival Rate)：
        # 由公立医保报销率 (正向)、贫困率 (负向营养不良)、口粮物价 (负向生存压力) 和失业率共同决定
        base_survival = 0.965
        medicare_bonus = (state.medicare_reimburse_rate - 0.65) * 0.10
        poverty_penalty = (state.poverty_rate - 0.35) * 0.12
        food_penalty = max(0.0, (state.food_basket_price - 15.0) * 0.006)
        unemp_penalty = (state.unemployment_rate - 0.18) * 0.06
        
        target_survival = base_survival + medicare_bonus - poverty_penalty - food_penalty - unemp_penalty
        state.child_survival_rate = max(0.78, min(0.998, round(getattr(state, "child_survival_rate", 0.965) * 0.95 + target_survival * 0.05, 3)))
        state.infant_mortality_rate = round((1.0 - state.child_survival_rate) * 1000.0, 1)
        
        # 自然老龄与成年死亡率 (‰)
        state.death_rate_annual = round(max(4.5, 7.2 - (state.medicare_reimburse_rate - 0.65) * 2.5 + (getattr(state, "retired_population", 1_700_000) / 1_700_000.0 - 1.0) * 1.5 + max(0.0, (state.food_basket_price - 25.0) * 0.15)), 1)

        # (4) 微观居民储蓄池与企业资本池滚动结余累积
        if hasattr(state, "citizen_savings_pool") and state.citizens_ledger:
            for cid, cit in state.citizens_ledger.items():
                if cid in state.citizen_savings_pool:
                    net_chg = cit.get("daily_net", 0.0)
                    state.citizen_savings_pool[cid] = max(0.0, round(state.citizen_savings_pool[cid] + net_chg, 2))
                    
        if hasattr(state, "employer_capital_pool") and state.employers_ledger:
            for eid, emp in state.employers_ledger.items():
                if eid in state.employer_capital_pool:
                    net_chg_wan = emp.get("daily_net", 0.0) / 10000.0
                    state.employer_capital_pool[eid] = max(0.0, round(state.employer_capital_pool[eid] + net_chg_wan, 4))
        
        # (5) 全景微观真实账本矩阵 (15大产业微观雇主 + 22大工种民生阶层)
        self.sync_personas_and_ledgers()
        
        # (4) 动态经济学理论知识卡 (教育与理论因果链)
        state.active_theory_insights.clear()
        if has_new_deal:
            state.active_theory_insights.append({
                "school": "【凯恩斯主义·有效需求原理】",
                "core": "当经济萧条、私人部门陈老板不愿投资时，政府必须充当'最后雇主'。",
                "causality": "政府财政赤字 ➔ 启动公共以工代赈 ➔ 直接给老张发工资 ➔ 老张购买口粮 ➔ 激活全社会商品流转与总需求。"
            })
        if has_reagan:
            state.active_theory_insights.append({
                "school": "【供给学派·拉弗曲线与资本积累】",
                "core": "降低企业税负才能激发微观企业家的投资冒险精神与产能释放。",
                "causality": "削减企业税 ➔ 陈厂长留存利润暴增 ➔ 刺激资本开支(I)与GDP狂飙；但对底层老张的工资改善较为滞后（K型分化）。"
            })
        if has_helicopter:
            state.active_theory_insights.append({
                "school": "【现代货币理论(MMT) 与 费雪货币数量论】",
                "core": "央行直接印钞发钱能瞬时兜底民生，但逃不过供需定律的惩罚。",
                "causality": "央行凭空注水 ➔ 老张和李会计手头现金激增、贫困率暴跌 ➔ 但若实体总产能跟不上，多印的钞票将转化为菜价上涨（通胀税）。"
            })
        if state.base_interest_rate < 0.03:
            state.active_theory_insights.append({
                "school": "【宏观金融·扩张性货币政策传导】",
                "core": "央行降息通过降低资金使用成本刺激全社会信贷扩张。",
                "causality": "降息 ➔ 李会计房贷减轻 ➔ 陈厂长贷款成本下降、投资扩产 ➔ 就业增加；但也推高全社会债务杠杆率。"
            })
        elif state.base_interest_rate > 0.06:
            state.active_theory_insights.append({
                "school": "【新古典综合·紧缩性货币政策与沃尔克时刻】",
                "core": "以短期的经济衰退与企业阵痛，彻底扑灭全社会通胀预期。",
                "causality": "加息 ➔ 借贷成本高企 ➔ 陈厂长停止招工甚至裁员、失业率上升 ➔ 全社会需求降温 ➔ 迫使物价回落。"
            })
        if not state.active_theory_insights:
            state.active_theory_insights.append({
                "school": "【发展经济学·低水平均衡陷阱 (Poverty Trap)】",
                "core": "在无外生强力干预时，困难国家会长期锁定在'贫困-低储蓄-低投资'的封闭循环。",
                "causality": "老张收入仅够糊口无储蓄 ➔ 银行资本金浅 ➔ 陈老板借贷成本高无法扩产 ➔ 系统保持低水平动态稳态。"
            })
            
        # (5) 时代之声广播 (每周更新一条，从全社会微观各角色中轮选最新心声)
        if state.day % 7 == 0:
            speaker_pool = []
            if getattr(state, "citizens_ledger", None):
                speaker_pool.extend(list(state.citizens_ledger.values()))
            if getattr(state, "employers_ledger", None):
                speaker_pool.extend(list(state.employers_ledger.values()))
            
            if speaker_pool:
                chosen = speaker_pool[(state.day // 7) % len(speaker_pool)]
                new_voice = {
                    "day": state.day,
                    "author": f"{chosen.get('avatar', '📢')} {chosen.get('name', '国民')} ({chosen.get('title', '')})",
                    "text": chosen.get("voice", "")
                }
            else:
                new_voice = {
                    "day": state.day,
                    "author": "老张",
                    "text": state.persona_worker.get("voice", "")
                }
            state.citizen_voices.insert(0, new_voice)
            state.citizen_voices = state.citizen_voices[:15]
        
        # 11. 日期推进 (90天/季，360天/年)
        state.day += 1
        is_quarter_end = (state.day % 90 == 0)
        is_year_end = (state.day % 360 == 0)
        
        if is_quarter_end:
            q_info = self._handle_quarter_end()
            daily_events.append(q_info)
            
        if is_year_end:
            y_info = self._handle_year_end()
            daily_events.append(y_info)
            
        # 12. 极度硬核：探明地质储量、大宗物资中枢、实体工厂与技能劳动力最新状态持久化
        state.resources = self.resource_manager.to_dict()
        state.commodities = self.commodity_hub.to_dict()
        state.market_clearing_summary = self.commodity_hub.get_macro_clearance_report(self.factory_manager)
        state.factories = self.factory_manager.to_dict(self.accounting_bus)
        state.labor_market = self.labor_manager.to_dict(self.factory_manager.factories)
            
        return daily_events

    def _handle_quarter_end(self) -> str:
        """季度总结报告与人口代际演变"""
        state = self.state
        quarter_gdp = state.gdp_quarterly
        
        # 运行季度人口梯队自然演进 (出生与成活、少儿成长毕业、劳动者按退休年龄退休、自然死亡)
        quarterly_births = int((state.total_population * (state.birth_rate_annual / 1000.0)) / 4.0)
        # 婴幼儿成活率决定实际顺利存活并成长进入少儿梯队的新生儿
        survived_births = int(quarterly_births * state.child_survival_rate)
        infant_deaths = quarterly_births - survived_births

        quarterly_graduates = int(state.child_population / (15 * 4)) # 15岁成年入职
        work_span = max(35, state.retirement_age - 15)
        quarterly_retirees = int(state.working_population / (work_span * 4)) # 满退休年龄退役
        quarterly_deaths = int((state.total_population * (state.death_rate_annual / 1000.0)) / 4.0)
        retiree_deaths = int(quarterly_deaths * 0.85)
        other_deaths = quarterly_deaths - retiree_deaths
        
        state.child_population = max(100_000, state.child_population + survived_births - quarterly_graduates)
        state.working_population = max(500_000, state.working_population + quarterly_graduates - quarterly_retirees - other_deaths)
        state.retired_population = max(200_000, state.retired_population + quarterly_retirees - retiree_deaths)
        state.total_population = state.child_population + state.working_population + state.retired_population
        state.elderly_dependency_ratio = round((state.retired_population / max(1, state.working_population)) * 100.0, 1)
        state.total_dependency_ratio = round(((state.child_population + state.retired_population) / max(1, state.working_population)) * 100.0, 1)

        state.quarterly_history.append({
            "year": state.year,
            "quarter": state.quarter,
            "quarter_gdp": quarter_gdp,
            "annual_runrate": state.gdp_annual_runrate,
            "gdp_per_capita": state.gdp_per_capita,
            "engel": state.engel_coefficient,
            "poverty": state.poverty_rate,
            "unemployment": state.unemployment_rate,
            "sentiment": state.consumer_sentiment,
            "treasury": state.treasury_cash,
            "debt": state.national_debt,
            "credibility": state.policy_credibility,
            "fertility_rate": round(state.fertility_rate, 2),
            "child_survival_rate": round(state.child_survival_rate * 100.0, 1),
            "elderly_dependency": state.elderly_dependency_ratio,
            "total_population": state.total_population
        })
        
        warnings = []
        if state.elderly_dependency_ratio > 28.0:
            warnings.append(f"⚠️ 老年抚养比达 {state.elderly_dependency_ratio:.1f}% (老龄化加深)")
        if state.fertility_rate < 1.30:
            warnings.append(f"⚠️ 总和生育率仅 {state.fertility_rate:.2f} (极低生育警戒)")
        if state.child_survival_rate < 0.90:
            warnings.append(f"⚠️ 少儿成活率跌至 {state.child_survival_rate*100.0:.1f}% (受医疗薄弱与贫困影响，夭折率攀升)")
        if state.social_fund_pool < 120.0:
            warnings.append(f"🚨 社保基金滚存仅剩 {state.social_fund_pool:.1f} 亿元 (穿底高危)")
            
        warn_str = (" · " + " · ".join(warnings)) if warnings else ""
        msg = f"🔔 【第 {state.year} 年 第 {state.quarter} 季度 报告】名义GDP {quarter_gdp:.1f} 亿元 · 生育率 {state.fertility_rate:.2f} · 老年抚养比 {state.elderly_dependency_ratio:.1f}%{warn_str}"
        
        state.gdp_quarterly = 0.0
        state.quarter += 1
        if state.quarter > 4:
            state.quarter = 1
            state.year += 1
            
        return msg

    def _handle_year_end(self) -> str:
        """年度审计报告"""
        state = self.state
        msg = f"🏆 【第 {state.year - 1} 年度 宏观经济与民生审计决算】已生成！请查看年度六维综合评分！"
        return msg

    def change_policy_levers(self, 
                             base_rate: float = None, 
                             reserve_ratio: float = None,
                             corp_tax: float = None, 
                             vat_tax: float = None,
                             income_tax: float = None,
                             daily_gov_spending: float = None,
                             welfare_spending: float = None,
                             min_wage: float = None,
                             retirement_age: int = None,
                             fx_sterilization: float = None) -> Tuple[bool, str]:
        """
        调整宏观九大政策把手（朝令夕改机制）
        频繁调整会扣除 policy_credibility
        """
        state = self.state
        days_since_last = state.day - state.last_policy_change_day
        penalty = 0.0
        
        if days_since_last < 30:
            penalty = 12.0
            warning = "⚠️【严重警告】距上次调整不足30天！市场痛斥政策朝令夕改，公信力重挫 -12 点！"
        elif days_since_last < 90:
            penalty = 5.0
            warning = "⚠️【注意】距上次调整不足一季度，市场预期出现震荡，政策公信力 -5 点。"
        else:
            warning = "✅ 政策调整合理，市场平稳消化新政预期。"
            
        state.policy_credibility = max(10.0, state.policy_credibility - penalty)
        state.last_policy_change_day = state.day
        state.policy_change_count += 1
        
        changes = []
        if base_rate is not None:
            old = state.base_interest_rate
            state.base_interest_rate = base_rate
            changes.append(f"基准利率: {old*100:.1f}% -> {base_rate*100:.1f}%")
            # 立即传导至商业银行贷款与存款利率及万元月供
            credibility_factor = state.policy_credibility / 100.0
            risk_premium = max(0.0, (1.0 - credibility_factor) * 0.03)
            state.loan_interest_rate = round(state.base_interest_rate + 0.025 + risk_premium, 4)
            state.deposit_interest_rate = round(max(0.005, state.base_interest_rate * 0.6), 4)
            state.loan_cost_per_10k_month = round((10000.0 * state.loan_interest_rate) / 12.0, 1)
        if reserve_ratio is not None:
            old = state.reserve_ratio
            state.reserve_ratio = reserve_ratio
            changes.append(f"存款准备金率: {old*100:.1f}% -> {reserve_ratio*100:.1f}%")
        if corp_tax is not None:
            old = state.corp_tax_rate
            state.corp_tax_rate = corp_tax
            changes.append(f"企业所得税率: {old*100:.1f}% -> {corp_tax*100:.1f}%")
        if vat_tax is not None:
            old = state.vat_tax_rate
            state.vat_tax_rate = vat_tax
            changes.append(f"增值消费税率: {old*100:.1f}% -> {vat_tax*100:.1f}%")
        if income_tax is not None:
            old = state.income_tax_rate
            state.income_tax_rate = income_tax
            changes.append(f"个人所得税率: {old*100:.1f}% -> {income_tax*100:.1f}%")
        if daily_gov_spending is not None:
            old = state.gov_daily_spending
            state.gov_daily_spending = daily_gov_spending
            changes.append(f"行政公用开支: {old:.2f}亿 -> {daily_gov_spending:.2f}亿/天")
        if welfare_spending is not None:
            old = state.welfare_spending
            state.welfare_spending = welfare_spending
            changes.append(f"失业低保救济: {old:.2f}亿 -> {welfare_spending:.2f}亿/天")
        if min_wage is not None:
            old = state.min_wage_daily
            state.min_wage_daily = min_wage
            # 立即影响底层普工基准日薪
            state.households[0].base_wage = max(min_wage, state.households[0].base_wage)
            changes.append(f"法定最低日薪: {old:.0f}元 -> {min_wage:.0f}元/天")
        if retirement_age is not None:
            old_age = getattr(state, "retirement_age", 60)
            new_age = max(55, min(68, int(retirement_age)))
            if new_age != old_age:
                state.retirement_age = new_age
                # 每延迟/提前 1 岁退休，对应年届人口约为 14.4万人/岁
                age_diff = new_age - old_age
                shift_pop = int(age_diff * 144_000)
                state.retired_population = max(300_000, state.retired_population - shift_pop)
                state.working_population = min(state.total_population - state.child_population, state.working_population + shift_pop)
                
                state.elderly_dependency_ratio = round((state.retired_population / max(1, state.working_population)) * 100.0, 1)
                state.total_dependency_ratio = round(((state.child_population + state.retired_population) / max(1, state.working_population)) * 100.0, 1)
                
                if age_diff > 0:
                    changes.append(f"法定退休年龄: {old_age}岁 -> {new_age}岁 (延迟退休 {age_diff} 年，社保减负释放 {shift_pop//10000} 万银发劳力)")
                else:
                    changes.append(f"法定退休年龄: {old_age}岁 -> {new_age}岁 (提前退休 {-age_diff} 年，腾出青年岗位但社保养老金负担加重)")
            
        if fx_sterilization is not None:
            old_steril = getattr(state, "fx_sterilization_ratio", 0.0)
            self.set_fx_sterilization(fx_sterilization)
            changes.append(f"主权外汇平准冲销比例: {old_steril*100:.0f}% -> {state.fx_sterilization_ratio*100:.0f}% (划转海外主权基金 SWF 防范荷兰病)")

        # 立即同步计算37大微观账本
        self.sync_personas_and_ledgers()

        msg = f"{warning}\n新政策已正式签署生效：\n• " + "\n• ".join(changes) + f"\n(当前政策公信力: {state.policy_credibility:.1f}/100)"
        return True, msg

    def change_social_security_policy(self, medicare_rate: float = None, social_contrib_rate: float = None) -> Tuple[bool, str]:
        """调整国家社会保障与公立医保报销制度"""
        changes = []
        if medicare_rate is not None:
            old = self.state.medicare_reimburse_rate
            self.state.medicare_reimburse_rate = max(0.40, min(0.95, medicare_rate))
            changes.append(f"公立医保报销比例: {old*100:.0f}% -> {self.state.medicare_reimburse_rate*100:.0f}%")
        if social_contrib_rate is not None:
            old = self.state.social_contrib_rate
            self.state.social_contrib_rate = max(0.06, min(0.24, social_contrib_rate))
            changes.append(f"社会保障综合费率: {old*100:.0f}% -> {self.state.social_contrib_rate*100:.0f}%")
        
        # 立即同步微观账本与心声
        self.sync_personas_and_ledgers()
        msg = "✅ 国家医保与社保制度改革令已发布生效：\n• " + "\n• ".join(changes)
        return True, msg

    def issue_national_debt(self, amount: float) -> Tuple[bool, str]:
        """由玩家主动决策发售记账式国债募集国库资金，掌控国家负债规模"""
        if amount <= 0:
            return False, "发售金额必须大于 0 亿元。"
        debt_limit = getattr(self.state, "national_debt_limit", 2500.0)
        if self.state.national_debt + amount > debt_limit:
            return False, f"⚠️ 发债被议会否决！累计国债将达到 {self.state.national_debt + amount:.1f} 亿元，突破法定国债发行上限 {debt_limit:.1f} 亿元！"
            
        self.state.national_debt += amount
        self.accounting_bus.bank_treasury_bonds += amount
        self.execute_flow(
            from_acc="bank_operations",
            to_acc="treasury_cash",
            amount=amount,
            category="特别国债发行",
            description=f"中央政府主动发售记账式国债 {amount:.1f} 亿元，商业银行认购出资充实国库"
        )
        self.state.treasury_cash = round(self.accounting_bus.accounts["treasury_cash"].balance, 4)
        msg = f"📜 【财政部发债公告】中央政府正式发售国债 {amount:.1f} 亿元！国库现金增加至 {self.state.treasury_cash:.1f} 亿元，存量国债升至 {self.state.national_debt:.1f} 亿元 (负债率: {self.state.debt_to_gdp_rate:.1f}%, 主权评级: {self.state.sovereign_credit_rating}, 发债年化收益率: {self.state.sovereign_bond_yield*100:.2f}%)。"
        return True, msg

    def repay_national_debt(self, amount: float) -> Tuple[bool, str]:
        """由玩家主动决策使用国库资金提前赎回/偿还国债本金"""
        if amount <= 0:
            return False, "偿还金额必须大于 0 亿元。"
        if self.state.treasury_cash < amount:
            return False, f"国库可用现金不足！当前仅存 {self.state.treasury_cash:.1f} 亿元，无法偿付 {amount:.1f} 亿元国债本金。"
        if self.state.national_debt <= 0:
            return False, "当前国家未背负任何存量国债，无需赎回。"
            
        actual_repay = min(amount, self.state.national_debt)
        self.state.national_debt -= actual_repay
        self.accounting_bus.bank_treasury_bonds = max(0.0, self.accounting_bus.bank_treasury_bonds - actual_repay)
        self.execute_flow(
            from_acc="treasury_cash",
            to_acc="bank_operations",
            amount=actual_repay,
            category="国债本金赎回",
            description=f"财政部主动使用国库盈余资金赎回偿付国债本金 {actual_repay:.1f} 亿元"
        )
        self.state.treasury_cash = round(self.accounting_bus.accounts["treasury_cash"].balance, 4)
        msg = f"📜 【国债本金赎回】财政部划拨 {actual_repay:.1f} 亿元资金提前偿付国债本金！存量国债降至 {self.state.national_debt:.1f} 亿元，每日利息支出相应减轻。"
        return True, msg

    # =========================================================================
    # 第三阶段：国家实物战略储备、地质勘探与海关外贸主动调控
    # =========================================================================

    def release_strategic_stockpile(self, stockpile_id: str, amount: float) -> Tuple[bool, str]:
        """抛储平抑：从国家战略储备库向大宗现货市场平价抛售物资，平抑物价并收回国库流动性"""
        stockpile_to_cid = {
            "grain": "raw_grain",
            "raw_grain": "raw_grain",
            "coal": "coal",
            "oil": "crude_oil",
            "crude_oil": "crude_oil",
            "steel": "steel",
            "iron_ore": "iron_ore",
            "copper": "copper_ore",
            "copper_ore": "copper_ore"
        }
        cid = stockpile_to_cid.get(stockpile_id, stockpile_id)
        if cid not in self.commodity_hub.commodities:
            return False, f"未知的战略物资对应类别: {stockpile_id}"
            
        sp_id = "oil" if stockpile_id == "crude_oil" else ("copper" if stockpile_id == "copper_ore" else ("grain" if stockpile_id == "raw_grain" else stockpile_id))
        ok, actual, msg = self.resource_manager.release_stockpile(sp_id, amount)
        if not ok:
            return False, msg
            
        # 现货市场增加实物供应并平抑价格尖峰 (若现货价处于1.25倍高位天花板以上，则启动保供平抑)
        c = self.commodity_hub.commodities[cid]
        c.stock = round(c.stock + actual, 2)
        if c.domestic_price > c.base_price * 1.25:
            c.domestic_price = max(round(c.base_price * 1.20, 2), round(c.domestic_price * 0.98, 2))
        
        # 财务账目结算：企业/市场购买战略物资支付资金入国库
        val = round(get_commodity_value_in_yi(cid, actual, c.domestic_price), 4)
        if val > 0.0001:
            self.execute_flow(
                from_acc="corporate_sector",
                to_acc="treasury_cash",
                amount=val,
                category="平抑抛储收入",
                description=f"国家战略储备局向市场抛售投放【{c.name}】{actual:.1f} {c.unit}，收回国库现金 {val:.2f} 亿元"
            )
            self.state.treasury_cash = round(self.accounting_bus.accounts["treasury_cash"].balance, 4)
            self.update_state_corporate_cash()
            
        if stockpile_id in ["grain", "raw_grain"]:
            self.state.food_basket_price = max(8.0, round(self.state.food_basket_price * 0.95, 2))
            self.state.cpi_index = round((self.state.food_basket_price / 15.0) * 100.0, 1)
        self.sync_personas_and_ledgers()

        res_msg = f"{msg}\n💰 国库回收储备变现流动性资金 +{val:.2f} 亿元！国内【{c.name}】现货价格下调至 {c.domestic_price:.1f} 元/{c.unit}。"
        return True, res_msg

    def accumulate_strategic_stockpile(self, stockpile_id: str, amount: float) -> Tuple[bool, str]:
        """托市收储：财政部划拨资金向市场采购大宗现货充实战略储备，托底产业物价"""
        stockpile_to_cid = {
            "grain": "raw_grain",
            "raw_grain": "raw_grain",
            "coal": "coal",
            "oil": "crude_oil",
            "crude_oil": "crude_oil",
            "steel": "steel",
            "iron_ore": "iron_ore",
            "copper": "copper_ore",
            "copper_ore": "copper_ore"
        }
        cid = stockpile_to_cid.get(stockpile_id, stockpile_id)
        if cid not in self.commodity_hub.commodities:
            return False, f"未知的战略物资对应类别: {stockpile_id}"
            
        c = self.commodity_hub.commodities[cid]
        avail = c.stock
        if avail <= 0.1:
            return False, f"国内【{c.name}】商业现货库存枯竭，无法进行战略物资收储！"
            
        actual_buy = min(avail, amount)
        val = round(get_commodity_value_in_yi(cid, actual_buy, c.domestic_price), 4)
        
        if self.state.treasury_cash < val:
            return False, f"国库可用现金不足！收储采购【{c.name}】需资金 {val:.2f} 亿元，当前国库仅存 {self.state.treasury_cash:.2f} 亿元。"
            
        sp_id = "oil" if stockpile_id == "crude_oil" else ("copper" if stockpile_id == "copper_ore" else ("grain" if stockpile_id == "raw_grain" else stockpile_id))
        ok, actual_acc, msg = self.resource_manager.accumulate_stockpile(sp_id, actual_buy)
        if not ok:
            return False, msg
            
        # 现货市场扣减实物库存并托市防崩 (若现货价跌破0.85倍成本支撑线，则实施温和托底保护)
        c.stock = round(c.stock - actual_acc, 2)
        if c.domestic_price < c.base_price * 0.85:
            c.domestic_price = min(round(c.base_price * 0.88, 2), round(c.domestic_price * 1.015, 2))
        
        # 财政划拨资金给企业采购实物
        self.execute_flow(
            from_acc="treasury_cash",
            to_acc="corporate_sector",
            amount=val,
            category="战略物资收储支出",
            description=f"财政部出资收储【{c.name}】{actual_acc:.1f} {c.unit} 充实国家储备库"
        )
        self.state.treasury_cash = round(self.accounting_bus.accounts["treasury_cash"].balance, 4)
        self.update_state_corporate_cash()
        
        if stockpile_id in ["grain", "raw_grain"]:
            self.state.food_basket_price = min(25.0, round(self.state.food_basket_price * 1.03, 2))
            self.state.cpi_index = round((self.state.food_basket_price / 15.0) * 100.0, 1)
        self.sync_personas_and_ledgers()

        res_msg = f"{msg}\n🏛️ 财政部划拨储备采购专款 {val:.2f} 亿元！现货需求得到托底提振，现货价小幅回升至 {c.domestic_price:.1f} 元/{c.unit}。"
        return True, res_msg

    def replenish_strategic_stockpile_via_fx(self, stockpile_id: str, amount: float) -> Tuple[bool, str]:
        """战略外汇出海补库：国家动用外汇储备从海外大宗市场直接采购物资，运入中央战略储备库"""
        stockpile_to_cid = {
            "grain": "raw_grain",
            "raw_grain": "raw_grain",
            "coal": "coal",
            "oil": "crude_oil",
            "crude_oil": "crude_oil",
            "steel": "steel",
            "iron_ore": "iron_ore",
            "copper": "copper_ore",
            "copper_ore": "copper_ore"
        }
        cid = stockpile_to_cid.get(stockpile_id, stockpile_id)
        if cid not in self.commodity_hub.commodities:
            return False, f"未知的战略物资对应类别: {stockpile_id}"
            
        sp_id = "oil" if stockpile_id == "crude_oil" else ("copper" if stockpile_id == "copper_ore" else ("grain" if stockpile_id == "raw_grain" else stockpile_id))
        if sp_id not in self.resource_manager.stockpiles:
            return False, f"未找到国家战略储备库: {stockpile_id}"
            
        sp = self.resource_manager.stockpiles[sp_id]
        avail_space = sp.capacity - sp.current_stock
        if avail_space <= 0.1:
            return False, f"【{sp.name}】已达到设计库容上限 ({sp.capacity:.0f} {sp.unit})，无需海外补库！"
            
        actual_import = min(avail_space, amount)
        usd_cost = self.commodity_hub.calculate_customs_usd(cid, actual_import)
        
        if self.state.foreign_reserves_usd < usd_cost:
            return False, f"国家外汇储备不足！海外代购补库所需 ${usd_cost:.2f} 亿美元，当前外汇储备仅剩 ${self.state.foreign_reserves_usd:.2f} 亿美元。"
            
        # 购汇结算：中央财政 (treasury_cash) 向央行办理购汇并支付外汇至海外口岸 (SFC 零和闭环)
        cny_spent = self.accounting_bus.fx_purchase_import(
            importer_acc_id="treasury_cash",
            usd_amount=usd_cost,
            description=f"中央财政动用外汇海外代购充实【{sp.name}】战略储备"
        )
        self.state.treasury_cash = round(self.accounting_bus.accounts["treasury_cash"].balance, 4)
        self.state.foreign_reserves_usd = round(self.accounting_bus.foreign_reserves_usd, 2)
        
        # 战备实物直接入中央战略储备库
        sp.current_stock = round(sp.current_stock + actual_import, 2)
        sp.daily_flow = round(sp.daily_flow + actual_import, 2)
        
        # 记入 BOP 经常账户进口
        self.state.bop_imports_usd = round(self.state.bop_imports_usd + usd_cost, 4)
        self.state.bop_current_account_usd = round(self.state.bop_exports_usd - self.state.bop_imports_usd, 4)
        
        c = self.commodity_hub.commodities[cid]
        self.record_flow(
            source="中央国库",
            target="海关外贸口岸",
            amount=cny_spent,
            category="战略物资购汇补库(M2-)",
            description=f"中央财政支付本币 {cny_spent:.2f} 亿元 (购汇 ${usd_cost:.2f} 亿美元) 进口【{c.name}】{actual_import:.1f} {sp.unit} 直接充实国家战略储备库"
        )
        
        msg = f"🌐 【战略外汇海外补库】中央财政动用外汇储备 ${usd_cost:.2f} 亿美元 (折合本币 {cny_spent:.2f} 亿元)，海外大宗采购【{sp.name}】+{actual_import:.1f} {sp.unit} 直接入库！当前战备储备恢复至 {sp.reserve_years:.2f} 年。"
        return True, msg

    def customs_import_commodity(self, cid: str, amount: float) -> Tuple[bool, str]:
        """海关报关进口：企业使用国家外汇储备从海外紧急采购关键战略物资"""
        if cid not in self.commodity_hub.commodities:
            return False, f"未知大宗物资编码: {cid}"
            
        usd_cost = self.commodity_hub.calculate_customs_usd(cid, amount)
        if self.state.foreign_reserves_usd < usd_cost:
            return False, f"国家外汇储备不足！进口所需 {usd_cost:.2f} 亿美元，外汇储备仅存 {self.state.foreign_reserves_usd:.2f} 亿美元。"
            
        ok, actual, usd_val, msg = self.commodity_hub.import_customs(cid, amount)
        if not ok:
            return False, msg
            
        # 企业在商业银行办理购汇 (M2 相应湮灭)
        importer_acc = "corporate_sector"
        cny_spent = self.accounting_bus.fx_purchase_import(
            importer_acc_id=importer_acc,
            usd_amount=usd_val,
            description=f"企业海关报关进口大宗物资【{self.commodity_hub.commodities[cid].name}】"
        )
        self.state.foreign_reserves_usd = round(self.accounting_bus.foreign_reserves_usd, 2)
        self.update_state_corporate_cash()
        
        c = self.commodity_hub.commodities[cid]
        self.record_flow(
            source="企业部门",
            target="海关外贸口岸",
            amount=cny_spent,
            category="购汇进口付汇(M2-)",
            description=f"企业向商业银行购汇 {usd_val:.2f} 亿美元进口【{c.name}】{actual:.1f} {c.unit} (货币湮灭)"
        )
        
        if cid == "raw_grain":
            self.state.food_basket_price = max(8.0, round(self.state.food_basket_price * 0.96, 2))
            self.state.cpi_index = round((self.state.food_basket_price / 15.0) * 100.0, 1)
        self.sync_personas_and_ledgers()

        res_msg = f"{msg}\n🚢 实际支付购汇本币 {cny_spent:.2f} 亿元，外汇储备结存 {self.state.foreign_reserves_usd:.2f} 亿美元。"
        return True, res_msg

    def customs_export_commodity(self, cid: str, amount: float) -> Tuple[bool, str]:
        """海关商检外销出口：国内工业企业向海外出口过剩产能制成品创汇并结汇"""
        if cid not in self.commodity_hub.commodities:
            return False, f"未知大宗物资编码: {cid}"
            
        c = self.commodity_hub.commodities[cid]
        avail = c.stock + c.daily_production
        if avail <= 0.1:
            return False, f"国内【{c.name}】商业现货库存告急，无富余物资可供海关出口！"
            
        tariff = self.state.anti_dumping_tariffs.get(cid, 0.0)
        ok, actual, usd_earn, msg = self.commodity_hub.export_customs(cid, amount, tariff=tariff)
        if not ok:
            return False, msg
            
        # 央行按官方汇率办理结汇投放本币到实体出口工厂专户 (M2 派生)
        from engine.factories import COMMODITY_SUPPLIER_MAP
        exporter_acc = COMMODITY_SUPPLIER_MAP.get(cid, ("corporate_sector", "国家实体企业"))[0]
        cny_gained = self.accounting_bus.fx_settle_export(
            exporter_acc_id=exporter_acc,
            usd_amount=usd_earn,
            description=f"企业海关出口制成品【{c.name}】创汇结售汇"
        )
        self.state.foreign_reserves_usd = round(self.accounting_bus.foreign_reserves_usd, 2)
        self.update_state_corporate_cash()

        # 反倾销触发检测与大宗资源出口跟踪
        quota_thr = 4.5 if cid == "coal" else (2.5 if cid == "steel" else 10.0)
        penalty_rate = 0.20 if cid == "coal" else 0.25
        if actual > quota_thr:
            self.state.anti_dumping_tariffs[cid] = penalty_rate

        if cid in ["coal", "crude_oil"]:
            self.state.recent_resource_exports_usd = round(getattr(self.state, "recent_resource_exports_usd", 0.0) + usd_earn, 4)
        self.state.recent_total_exports_usd = round(getattr(self.state, "recent_total_exports_usd", 0.0) + usd_earn, 4)
        
        acc_name = self.accounting_bus.accounts[exporter_acc].name if exporter_acc in self.accounting_bus.accounts else "实体企业专户"
        self.record_flow(
            source="外贸口岸与海外市场",
            target=acc_name,
            amount=cny_gained,
            category="外贸结汇投放(M2+)",
            description=f"企业海关出口【{c.name}】{actual:.1f} {c.unit}，央行结汇投放本币 {cny_gained:.2f} 亿元入【{acc_name}】"
        )
        
        self.sync_personas_and_ledgers()

        res_msg = f"{msg}\n🌐 央行投放外汇占款本币 +{cny_gained:.2f} 亿元入【{acc_name}】！国家外汇储备增至 {self.state.foreign_reserves_usd:.2f} 亿美元。"
        return True, res_msg

    def set_geological_exploration(self, daily_budget: float, focus: str = None) -> Tuple[bool, str]:
        """主动调整国家地质找矿与物探攻坚预算与主攻矿种"""
        ok, msg = self.resource_manager.set_exploration(daily_budget, focus)
        return ok, msg

    def set_strategic_stockpile_target(
        self,
        sid: str,
        target_years: float,
        auto_enabled: bool = None,
        min_market_cover_days: float = None,
        max_market_cover_days: float = None,
        auto_import_reserve_years: float = None
    ) -> Tuple[bool, str]:
        """主动调整国家战略储备库目标年限与自动化方针策略"""
        ok, msg = self.resource_manager.set_stockpile_target(
            sid,
            target_years,
            auto_enabled,
            min_market_cover_days,
            max_market_cover_days,
            auto_import_reserve_years
        )
        return ok, msg

    def set_commodity_auto_trade(
        self,
        cid: str,
        enabled: bool,
        min_cover: float = 12.0,
        max_cover: float = 40.0,
        max_import: float = 0.5,
        max_export: float = 0.5
    ) -> Tuple[bool, str]:
        """主动调整二级制造商品的自动进出口调控方针策略"""
        return self.commodity_hub.set_auto_trade_policy(cid, enabled, min_cover, max_cover, max_import, max_export)

    def run_automated_strategic_buffer_and_replenishment(self) -> List[str]:
        """
        国家战略缓冲储备自动化平准与外汇海外补库中枢 (Buffer Stock Multi-Tier Mechanism)
        1. 市场流动性偏紧 (商业周转天数 < 市场下限): 自动平价抛储救急，防止断工断粮
        2. 市场产能过剩积压 (商业周转天数 > 市场上限): 自动财政托市收储，防止大宗跌穿成本
        3. 战备安全底限告急 (战备储备年限 < 外汇补库线): 自动动用国家外汇储备从海外采购直接充实战略库
        """
        events = []
        stockpile_to_cid = {
            "coal": "coal",
            "grain": "raw_grain",
            "oil": "crude_oil",
            "steel": "steel",
            "iron_ore": "iron_ore",
            "copper": "copper_ore"
        }
        
        for sid, cid in stockpile_to_cid.items():
            sp = self.resource_manager.stockpiles.get(sid)
            c = self.commodity_hub.commodities.get(cid)
            if not sp or not c:
                continue
            if not sp.auto_policy_enabled:
                continue
                
            cover_days = c.inventory_cover_days
            demand = max(0.5, c.last_day_demand)
            
            # 1. 市场流动下限检测：低于 min_market_cover_days 自动平价抛储
            if cover_days < sp.min_market_cover_days and sp.current_stock > 10.0:
                deficit_days = sp.min_market_cover_days - cover_days
                target_release = min(
                    deficit_days * demand,
                    demand * 3.0,
                    sp.current_stock * 0.05
                )
                target_release = max(0.5, round(target_release, 1))
                if target_release > 0.1 and sp.current_stock >= target_release:
                    ok, msg = self.release_strategic_stockpile(sid, target_release)
                    if ok:
                        events.append(f"🏛️ 【战略储备自动抛储】市场【{c.name}】商业周转告急({cover_days:.1f}天 < {sp.min_market_cover_days:.0f}天)，国家战略储备局自动抛储投放 {target_release:.1f} {sp.unit}！回笼国库资金平抑物价。")
            
            # 2. 市场积压上限检测：高于 max_market_cover_days 自动财政托市收储
            elif cover_days > sp.max_market_cover_days and (sp.capacity - sp.current_stock) > 0.5 and self.state.treasury_cash > 30.0:
                surplus_days = cover_days - sp.max_market_cover_days
                target_buy = min(
                    surplus_days * demand,
                    c.stock * 0.05,
                    sp.capacity - sp.current_stock,
                    demand * 0.5
                )
                # 财政支付能力安全阀 (单日最多消耗国库 0.05 亿元或 0.1% 现金，以小者为准，防止吸干国库)
                val_estimate = get_commodity_value_in_yi(cid, target_buy, c.domestic_price)
                max_budget = min(0.05, max(0.005, self.state.treasury_cash * 0.001))
                if val_estimate > max_budget:
                    target_buy = target_buy * (max_budget / max(0.001, val_estimate))
                target_buy = max(0.05, round(target_buy, 2))
                if target_buy > 0.02 and c.stock >= target_buy:
                    ok, msg = self.accumulate_strategic_stockpile(sid, target_buy)
                    if ok:
                        events.append(f"🏛️ 【战略储备自动收储】市场【{c.name}】周转严重积压({cover_days:.1f}天 > {sp.max_market_cover_days:.0f}天)，国家战略储备局自动托市收储 +{target_buy:.2f} {sp.unit}！财政拨付资金托底产业。")
            
            # 3. 战备安全底限检测：战略储备年限低于 auto_import_reserve_years，自动动用外汇海外补库
            if (
                sp.reserve_years < sp.auto_import_reserve_years
                and (sp.capacity - sp.current_stock) > 0.5
                and self.state.foreign_reserves_usd > 10.0
                and self.state.treasury_cash > 30.0
            ):
                # 批次采购量：以弥补战备缺口的 10% 或 2 天消耗量为准
                shortfall_units = (sp.auto_import_reserve_years - sp.reserve_years) * sp.daily_burn_rate * 360.0
                target_import = min(
                    shortfall_units * 0.10,
                    sp.daily_burn_rate * 2.0,
                    sp.capacity - sp.current_stock
                )
                # 外汇安全阀：单日外汇消耗不超过外汇储备的 3%，本币不超过 0.05 亿元
                usd_cost = self.commodity_hub.calculate_customs_usd(cid, target_import)
                cny_cost = usd_cost * self.state.exchange_rate
                max_usd = min(0.15, self.state.foreign_reserves_usd * 0.03)
                max_cny = min(0.05, self.state.treasury_cash * 0.001)
                
                scale = 1.0
                if usd_cost > max_usd:
                    scale = min(scale, max_usd / usd_cost)
                if cny_cost > max_cny:
                    scale = min(scale, max_cny / cny_cost)
                target_import = max(0.05, round(target_import * scale, 2))
                
                if target_import >= 0.05:
                    ok, msg = self.replenish_strategic_stockpile_via_fx(sid, target_import)
                    if ok:
                        events.append(msg)
                        
        return events

    def set_fx_sterilization(self, ratio: float) -> Tuple[bool, str]:
        """
        设置主权外汇平准冲销对冲比例 (0.0 ~ 0.80)
        将顺差外汇划入海外主权财富基金 (SWF) 投资海外长期资产，阻断本币过快升值，防范荷兰病
        """
        ratio = max(0.0, min(0.80, round(float(ratio), 2)))
        self.state.fx_sterilization_ratio = ratio
        if ratio > 0.001:
            msg = f"🏛️ 央行与外管局正式启用法定【主权外汇平准冲销机制】，冲销对冲比例设为 {ratio*100:.0f}%！每日经常账户顺差的 {ratio*100:.0f}% 将直接划拨海外主权财富基金（SWF）进行海外优质资产长期投资，平抑本币升值压力，强力护航本土制造轻工业！"
        else:
            msg = "🏛️ 央行外汇管理局取消外汇冲销机制，经常账户顺差将全额进入国内即期外汇市场结汇为 M2。"
        return True, msg

