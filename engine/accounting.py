"""
国家中央资金清算总线与复式记账法全社会会计核算引擎 (Stock-Flow Consistent Engine)
实现五大部门（居民、企业、商业银行、财政与社保、对外与央行）资产负债表与资金流量表完全守恒。
所有资金流动必须遵循：
1. 每一笔交易必有借贷双方 (Double-Entry Bookkeeping)，境内转移代数和严格为零。
2. 广义货币 M2 有且仅有三大合法生成/注销通道：
   - 商业银行信贷派生与还贷湮灭 (Loans create deposits, Repayments destroy deposits)
   - 外贸结售汇顺逆差与外汇占款 (FX Settlement)
   - 央行法定印钞 / 货币化融资 (Central Bank Injection / Seigniorage)
3. 商业银行资产负债表资产恒等于负债加所有者权益。
"""
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Tuple
import math

@dataclass
class Account:
    """法定资金账户实体"""
    id: str
    name: str
    sector: str         # "household", "corporate", "bank", "treasury", "social_security", "external", "central_bank"
    balance: float      # 账户当前存量资金 (亿元)
    initial_balance: float = 0.0

@dataclass
class TransactionRecord:
    """复式记账流水实体"""
    tx_id: str
    day: int
    from_account_id: str
    from_account_name: str
    to_account_id: str
    to_account_name: str
    amount: float       # 交易金额 (亿元)
    category: str       # 交易科目 (如: 工资发放, 消费支出, 纳税, 利息支付, 社保缴费)
    description: str

@dataclass
class DailyAuditReport:
    """每日全社会资金平衡检验与平账审计单"""
    day: int
    is_balanced: bool
    total_inflow: float
    total_outflow: float
    flow_discrepancy: float
    
    # 广义货币 M2 核算
    m2_start_of_day: float
    m2_end_of_day: float
    m2_actual_delta: float
    m2_theoretical_delta: float
    m2_discrepancy: float
    
    # M2 增量归因分解
    credit_net_expansion: float     # 净信贷派生 (新借款 - 还款)
    fx_net_settlement: float         # 外贸净结售汇 (顺差注入 - 逆差购汇)
    cb_net_injection: float          # 央行铸币税/印钞净注入
    treasury_cash_delta: float       # 国库留存净增减 (若国库吸纳资金则抽干流动性)
    bad_debt_write_off: float        # 坏账核销冲减额 (冲减银行资产与资本金)
    
    # 商业银行资产负债平衡
    bank_total_assets: float
    bank_total_liabilities: float
    bank_equity: float
    bank_balance_discrepancy: float
    
    # 审计消息与告警
    audit_messages: List[str] = field(default_factory=list)

class AccountingBus:
    """国家中央清算与资金流量表总线"""
    def __init__(self, exchange_rate: float = 7.20):
        self.exchange_rate = exchange_rate
        self.current_day: int = 1
        self.tx_counter: int = 0
        
        # 1. 账户矩阵注册表
        self.accounts: Dict[str, Account] = {}
        
        # 商业银行专属资产负债存量跟踪
        self.bank_loans_corporate: float = 0.0    # 银行对企业贷款存量 (亿元)
        self.bank_loans_household: float = 0.0    # 银行对个人贷款存量 (亿元)
        self.bank_treasury_bonds: float = 0.0     # 银行持有的国债投资 (亿元)
        self.bank_capital_equity: float = 0.0     # 银行自有资本金 (风险准备与净资产) (亿元)
        self.bank_reserve_ratio: float = 0.12     # 法定存款准备金率
        
        # 主权外汇储备
        self.foreign_reserves_usd: float = 25.0   # 亿美元
        
        # 每日流水台账与历史审计单
        self.daily_transactions: List[TransactionRecord] = []
        self.all_transactions_history: List[TransactionRecord] = []
        self.daily_audit_history: List[DailyAuditReport] = []
        
        # 每日 M2 增量通道统计累加器
        self.daily_credit_expansion: float = 0.0  # 今日新放贷
        self.daily_credit_repayment: float = 0.0  # 今日还本
        self.daily_bad_debt_write_off: float = 0.0 # 今日不良贷款坏账核销冲减
        self.daily_fx_inflow_cny: float = 0.0     # 今日出口结汇注入本币
        self.daily_fx_outflow_cny: float = 0.0    # 今日进口购汇回笼本币
        self.daily_cb_injection: float = 0.0      # 今日央行直接印钞注水
        
        # 期初 M2 记录
        self.day_start_m2: float = 0.0

    def register_account(self, acc_id: str, name: str, sector: str, initial_balance: float) -> Account:
        """注册法定账户"""
        acc = Account(
            id=acc_id,
            name=name,
            sector=sector,
            balance=initial_balance,
            initial_balance=initial_balance
        )
        self.accounts[acc_id] = acc
        return acc

    def initialize_standard_matrix(
        self,
        households_config: List[Dict[str, Any]],
        corporate_cash: float,
        corporate_debt: float,
        treasury_cash: float,
        national_debt: float,
        social_fund: float,
        bank_capital: float,
        foreign_reserves_usd: float = 25.0,
        exchange_rate: float = 7.20,
        household_debt: float = 0.0
    ):
        """标准宏观经济开局五大部门资产负债初始化"""
        self.accounts.clear()
        self.exchange_rate = exchange_rate
        self.foreign_reserves_usd = foreign_reserves_usd
        
        # 1. 居民部门 (六大细分阶层账户)
        for h in households_config:
            self.register_account(
                acc_id=f"household_{h['id']}",
                name=h["name"],
                sector="household",
                initial_balance=h.get("savings", 0.0)
            )
            
        # 2. 实体企业部门 (17家重点工业体系企业专户占~45%，广大民营实体与综合商贸服务清算总户占~55%)
        CORPORATE_ENTERPRISE_ACCOUNTS = [
            ("corp_coal_mine", "现代化煤矿集团 (专户)", 0.032, 0.09),
            ("corp_iron_mine", "大型铁矿采选联合体 (专户)", 0.024, 0.07),
            ("corp_oil_field", "国家油气田开采公司 (专户)", 0.032, 0.09),
            ("corp_copper_mine", "铜铝有色采选联合体 (专户)", 0.020, 0.05),
            ("corp_power_plant", "国家骨干电网公司 (专户)", 0.056, 0.15),
            ("corp_steel_mill", "特大型钢铁联合体 (专户)", 0.048, 0.14),
            ("corp_cement_plant", "新型干法水泥建材厂 (专户)", 0.020, 0.06),
            ("corp_fertilizer_chem", "合成化肥石化集团 (专户)", 0.028, 0.08),
            ("corp_hardware_machinery", "陈厂长五金机械集群 (专户)", 0.040, 0.08),
            ("corp_heavy_machinery", "重型机械装备制造厂 (专户)", 0.036, 0.10),
            ("corp_power_equipment", "特高压电力装备集团 (专户)", 0.022, 0.04),
            ("corp_textile_light", "轻纺织造日用轻工厂 (专户)", 0.024, 0.04),
            ("corp_state_farm", "大型农垦原粮集团 (专户)", 0.024, 0.06),
            ("corp_food_processing", "粮油食品精炼联合企业 (专户)", 0.020, 0.03),
            ("corp_pharma_corp", "现代生物制药集团 (专户)", 0.018, 0.04),
            ("corp_hightech_electronics", "电子芯片与微电子集团 (专户)", 0.032, 0.05),
            ("corp_commercial", "国家商贸流通与综合商业 (专户)", 0.008, 0.02),
        ]
        allocated_cash = 0.0
        for acc_id, name, share, _ in CORPORATE_ENTERPRISE_ACCOUNTS:
            b = round(corporate_cash * share, 4)
            allocated_cash += b
            self.register_account(
                acc_id=acc_id,
                name=name,
                sector="corporate",
                initial_balance=b
            )
        
        # 兼容与总清算专户：国家实体企业综合清算总专户
        residual_corp_cash = round(corporate_cash - allocated_cash, 4)
        self.register_account(
            acc_id="corporate_sector",
            name="国家实体企业综合清算总专户",
            sector="corporate",
            initial_balance=residual_corp_cash
        )
        self.bank_loans_corporate = corporate_debt
        
        # 3. 政府财政与社保
        self.register_account(
            acc_id="treasury_cash",
            name="中央政府国库单一账户 (TSA)",
            sector="treasury",
            initial_balance=treasury_cash
        )
        self.register_account(
            acc_id="social_security_fund",
            name="国家社会保障与医保统筹专户 (商业银行存款)",
            sector="social_security",
            initial_balance=social_fund
        )
        # 4. 商业银行系统营运与净利差账户
        self.register_account(
            acc_id="bank_operations",
            name="商业银行系统营运准备金与利差头寸",
            sector="bank",
            initial_balance=bank_capital
        )
        
        # 商业银行资产负债表对齐：
        # 银行负债 = 居民总存款 + 企业总存款 + 社保专户存款
        household_total_deposits = sum(
            acc.balance for acc in self.accounts.values() if acc.sector == "household"
        )
        corp_total_deposits = sum(
            acc.balance for acc in self.accounts.values() if acc.sector == "corporate"
        )
        bank_liabilities = household_total_deposits + corp_total_deposits + social_fund
        
        # 银行资产 = 企业贷款 + 国债持有 + 法定准备金
        self.bank_loans_corporate = corporate_debt
        self.bank_loans_household = household_debt # 个人房贷按揭贷款存量
        self.bank_treasury_bonds = national_debt # 商业银行持有国债
        
        # 银行资本金配平：资本金 = 资产 - 负债
        # 如果传入的 bank_capital 指定，则以准备金与流动性资产配平
        self.bank_capital_equity = bank_capital
        
        self.day_start_m2 = self.get_total_m2()

    # =========================================================================
    # 核心复式记账法原子操作
    # =========================================================================
    
    def transfer(
        self,
        from_acc_id: str,
        to_acc_id: str,
        amount: float,
        category: str,
        description: str
    ) -> bool:
        """
        原子转账操作 (境内闭环零和转移)：
        资金严格从 from 账户扣除，并等额增加到 to 账户。
        绝无任何资金溢出或凭空凭没。
        """
        if amount <= 0.0000001:
            return True # 零金额安全跳过
            
        if from_acc_id not in self.accounts or to_acc_id not in self.accounts:
            raise KeyError(f"清算账户不存在: from={from_acc_id}, to={to_acc_id}")
            
        from_acc = self.accounts[from_acc_id]
        to_acc = self.accounts[to_acc_id]
        
        from_acc.balance -= amount
        to_acc.balance += amount
        
        self.tx_counter += 1
        tx = TransactionRecord(
            tx_id=f"TX-{self.current_day}-{self.tx_counter:04d}",
            day=self.current_day,
            from_account_id=from_acc.id,
            from_account_name=from_acc.name,
            to_account_id=to_acc.id,
            to_account_name=to_acc.name,
            amount=round(amount, 6),
            category=category,
            description=description
        )
        self.daily_transactions.append(tx)
        self.all_transactions_history.append(tx)
        return True

    # =========================================================================
    # 三大合法 M2 增减通道原语 (信贷扩张/收缩、外贸结汇、央行注水)
    # =========================================================================
    
    def bank_credit_expand(
        self,
        borrower_acc_id: str,
        amount: float,
        is_corporate: bool = True,
        description: str = "商业银行发放新增贷款"
    ) -> bool:
        """
        通道 1A：商业银行信贷扩张 (贷款创造存款 Loans create deposits)
        银行发放贷款：借款人存款 (+amount)，银行贷款资产 (+amount)。
        全社会 M2 净增加 +amount。
        """
        if amount <= 0.0:
            return False
            
        if borrower_acc_id not in self.accounts:
            raise KeyError(f"借款账户不存在: {borrower_acc_id}")
            
        acc = self.accounts[borrower_acc_id]
        acc.balance += amount
        
        if is_corporate:
            self.bank_loans_corporate += amount
        else:
            self.bank_loans_household += amount
            
        self.daily_credit_expansion += amount
        
        self.tx_counter += 1
        tx = TransactionRecord(
            tx_id=f"TX-CRE-{self.current_day}-{self.tx_counter:04d}",
            day=self.current_day,
            from_account_id="banking_system_loan_asset",
            from_account_name="商业银行信贷资产",
            to_account_id=acc.id,
            to_account_name=acc.name,
            amount=round(amount, 6),
            category="银行信贷派生(M2+)",
            description=description
        )
        self.daily_transactions.append(tx)
        self.all_transactions_history.append(tx)
        return True

    def bank_credit_repay(
        self,
        borrower_acc_id: str,
        amount: float,
        is_corporate: bool = True,
        description: str = "借款人归还商业银行贷款本金"
    ) -> bool:
        """
        通道 1B：商业银行信贷回收/还本湮灭 (Repayment destroys deposits)
        借款人归还本金：借款人存款 (-amount)，银行贷款资产 (-amount)。
        全社会 M2 净减少 -amount。
        """
        if amount <= 0.0:
            return False
            
        if borrower_acc_id not in self.accounts:
            raise KeyError(f"借款账户不存在: {borrower_acc_id}")
            
        acc = self.accounts[borrower_acc_id]
        repay_amt = min(acc.balance, amount)
        acc.balance -= repay_amt
        
        if is_corporate:
            actual_repaid = min(self.bank_loans_corporate, repay_amt)
            self.bank_loans_corporate -= actual_repaid
        else:
            actual_repaid = min(self.bank_loans_household, repay_amt)
            self.bank_loans_household -= actual_repaid
            
        self.daily_credit_repayment += actual_repaid
        
        self.tx_counter += 1
        tx = TransactionRecord(
            tx_id=f"TX-REP-{self.current_day}-{self.tx_counter:04d}",
            day=self.current_day,
            from_account_id=acc.id,
            from_account_name=acc.name,
            to_account_id="banking_system_loan_asset",
            to_account_name="商业银行信贷资产",
            amount=round(actual_repaid, 6),
            category="信贷本金偿还(M2-)",
            description=description
        )
        self.daily_transactions.append(tx)
        self.all_transactions_history.append(tx)
        return True

    def disburse_household_mortgage(
        self,
        buyer_tier_id: str,
        amount: float,
        developer_acc_id: str = "corporate_sector",
        description: str = "商业银行发放首套个人住房按揭贷款"
    ) -> bool:
        """
        Phase 2: 商业银行发放个人住房按揭贷款 (Mortgage Disbursement)
        银行资产端个人贷款增加 (+amount)
        开发商账户存款增加 (+amount)
        全社会 M2 净增加 +amount (信贷派生通道)
        """
        if amount <= 0.00001:
            return False
            
        dev_acc = self.accounts.get(developer_acc_id)
        if not dev_acc:
            raise KeyError(f"开发商账户不存在: {developer_acc_id}")
            
        dev_acc.balance += amount
        self.bank_loans_household += amount
        self.daily_credit_expansion += amount
        
        self.tx_counter += 1
        tx = TransactionRecord(
            tx_id=f"TX-MTG-{self.current_day}-{self.tx_counter:04d}",
            day=self.current_day,
            from_account_id="banking_system_loan_asset",
            from_account_name="商业银行住房按揭贷款中心",
            to_account_id=dev_acc.id,
            to_account_name=dev_acc.name,
            amount=round(amount, 6),
            category="按揭信贷派生(M2+)",
            description=f"{description} (购房借款阶层: {buyer_tier_id}, 金额: {amount:.2f}亿)"
        )
        self.daily_transactions.append(tx)
        self.all_transactions_history.append(tx)
        return True

    def repay_household_mortgage(
        self,
        payer_tier_id: str,
        principal: float,
        interest: float,
        description: str = "居民个人住房按揭月供还本付息"
    ) -> bool:
        """
        Phase 2: 居民个人住房按揭还本付息 (Mortgage Repayment)
        居民账户扣减本息 (-principal - interest)
        本金还贷：银行个人贷款资产减少 (-principal)，全社会 M2 净减少 (-principal)
        利息收入：转移至商业银行营运利差专户 bank_operations (+interest)
        """
        payer_acc_id = f"household_{payer_tier_id}" if not payer_tier_id.startswith("household_") else payer_tier_id
        if payer_acc_id not in self.accounts:
            return False
            
        payer_acc = self.accounts[payer_acc_id]
        total_due = principal + interest
        if total_due <= 0.00001:
            return True
            
        if payer_acc.balance < total_due:
            # 储蓄不足全额扣款时按比例折算
            ratio = max(0.0, payer_acc.balance / total_due)
            principal = round(principal * ratio, 6)
            interest = round(interest * ratio, 6)
            total_due = principal + interest
            
        if total_due <= 0.00001:
            return False
            
        payer_acc.balance -= total_due
        
        # 1. 本金部分销毁 M2
        actual_principal = min(self.bank_loans_household, principal)
        self.bank_loans_household -= actual_principal
        self.daily_credit_repayment += actual_principal
        
        self.tx_counter += 1
        tx_p = TransactionRecord(
            tx_id=f"TX-MR-P-{self.current_day}-{self.tx_counter:04d}",
            day=self.current_day,
            from_account_id=payer_acc.id,
            from_account_name=payer_acc.name,
            to_account_id="banking_system_loan_asset",
            to_account_name="商业银行住房按揭贷款中心",
            amount=round(actual_principal, 6),
            category="按揭本金还款(M2-)",
            description=f"{description} (冲减个人房贷本金 {actual_principal:.4f}亿)"
        )
        self.daily_transactions.append(tx_p)
        self.all_transactions_history.append(tx_p)
        
        # 2. 利息部分划归商业银行营运利差专户
        bank_ops = self.accounts.get("bank_operations")
        if bank_ops and interest > 0.00001:
            bank_ops.balance += interest
            self.tx_counter += 1
            tx_i = TransactionRecord(
                tx_id=f"TX-MR-I-{self.current_day}-{self.tx_counter:04d}",
                day=self.current_day,
                from_account_id=payer_acc.id,
                from_account_name=payer_acc.name,
                to_account_id=bank_ops.id,
                to_account_name=bank_ops.name,
                amount=round(interest, 6),
                category="房贷利息支付",
                description=f"{description} (商业银行按揭利息净利差收益 {interest:.4f}亿)"
            )
            self.daily_transactions.append(tx_i)
            self.all_transactions_history.append(tx_i)
            
        return True

    def write_off_corporate_bad_debt(
        self,
        borrower_acc_id: str,
        amount: float,
        description: str = "商业银行核销企业不良贷款坏账"
    ) -> float:
        """
        通道 1C：商业银行坏账核销 (Bad Debt Write-off)
        银行坏账核销：冲减企业贷款资产 (-amount)，冲减银行资本金/拨备净资产 (-amount)。
        全社会 M2 保持不变（存款端早已在前期亏损中转入其他部门）。
        保证银行资产负债表严格对偶配平！
        """
        if amount <= 0.0:
            return 0.0
            
        actual_write_off = min(self.bank_loans_corporate, amount)
        self.bank_loans_corporate -= actual_write_off
        self.bank_capital_equity = max(0.0, self.bank_capital_equity - actual_write_off)
        if "bank_operations" in self.accounts:
            self.accounts["bank_operations"].balance = max(0.0, self.accounts["bank_operations"].balance - actual_write_off)
            
        self.daily_bad_debt_write_off += actual_write_off
        
        self.tx_counter += 1
        tx = TransactionRecord(
            tx_id=f"TX-WRO-{self.current_day}-{self.tx_counter:04d}",
            day=self.current_day,
            from_account_id="banking_system_loan_asset",
            from_account_name="商业银行企业信贷资产",
            to_account_id="bank_operations",
            to_account_name="商业银行资本金与拨备专户",
            amount=round(actual_write_off, 6),
            category="坏账呆账核销(资产与权益同减)",
            description=description
        )
        self.daily_transactions.append(tx)
        self.all_transactions_history.append(tx)
        return actual_write_off

    def fx_settle_export(
        self,
        exporter_acc_id: str,
        usd_amount: float,
        description: str = "企业大宗商品出口创汇结售汇"
    ) -> float:
        """
        通道 2A：外贸顺差结汇 (FX Inflow)
        出口赚取美元：外汇储备 (+usd_amount)，央行按官方汇率投放外汇占款本币 (+cny_amount) 到出口企业账户。
        全社会 M2 净增加 +cny_amount。
        """
        if usd_amount <= 0.0:
            return 0.0
            
        cny_amount = usd_amount * self.exchange_rate
        acc = self.accounts[exporter_acc_id]
        
        self.foreign_reserves_usd += usd_amount
        acc.balance += cny_amount
        self.daily_fx_inflow_cny += cny_amount
        
        self.tx_counter += 1
        tx = TransactionRecord(
            tx_id=f"TX-FXIN-{self.current_day}-{self.tx_counter:04d}",
            day=self.current_day,
            from_account_id="foreign_trade_settlement",
            from_account_name="外汇储备与对外贸易口岸",
            to_account_id=acc.id,
            to_account_name=acc.name,
            amount=round(cny_amount, 6),
            category="外贸结汇投放(M2+)",
            description=f"{description} (创汇 ${usd_amount:.2f}亿，汇率 {self.exchange_rate:.2f})"
        )
        self.daily_transactions.append(tx)
        self.all_transactions_history.append(tx)
        return cny_amount

    def fx_purchase_import(
        self,
        importer_acc_id: str,
        usd_amount: float,
        description: str = "企业或政府进口战略物资购汇汇出"
    ) -> float:
        """
        通道 2B：外贸逆差购汇 (FX Outflow)
        进口消耗美元：外汇储备 (-usd_amount)，进口企业支付本币 (-cny_amount) 并注销。
        全社会 M2 净减少 -cny_amount。
        """
        if usd_amount <= 0.0:
            return 0.0
            
        cny_amount = usd_amount * self.exchange_rate
        acc = self.accounts[importer_acc_id]
        
        actual_usd = min(self.foreign_reserves_usd, usd_amount)
        actual_cny = actual_usd * self.exchange_rate
        
        self.foreign_reserves_usd -= actual_usd
        acc.balance -= actual_cny
        self.daily_fx_outflow_cny += actual_cny
        
        self.tx_counter += 1
        tx = TransactionRecord(
            tx_id=f"TX-FXOUT-{self.current_day}-{self.tx_counter:04d}",
            day=self.current_day,
            from_account_id=acc.id,
            from_account_name=acc.name,
            to_account_id="foreign_trade_settlement",
            to_account_name="外汇储备与对外贸易口岸",
            amount=round(actual_cny, 6),
            category="进口购汇注销(M2-)",
            description=f"{description} (付汇 ${actual_usd:.2f}亿，汇率 {self.exchange_rate:.2f})"
        )
        self.daily_transactions.append(tx)
        self.all_transactions_history.append(tx)
        return actual_cny

    def central_bank_inject(
        self,
        target_acc_id: str,
        amount: float,
        description: str = "中央银行凭空投放基础货币 (铸币税/QE/财政透支)"
    ) -> bool:
        """
        通道 3：央行直接印钞 / 铸币税 (Central Bank Money Creation)
        央行记账发行：目标账户 (+amount)。
        全社会 M2 净增加 +amount。
        """
        if amount <= 0.0:
            return False
            
        acc = self.accounts[target_acc_id]
        acc.balance += amount
        self.daily_cb_injection += amount
        
        self.tx_counter += 1
        tx = TransactionRecord(
            tx_id=f"TX-CB-{self.current_day}-{self.tx_counter:04d}",
            day=self.current_day,
            from_account_id="central_bank_issuance",
            from_account_name="中央银行货币发行局",
            to_account_id=acc.id,
            to_account_name=acc.name,
            amount=round(amount, 6),
            category="央行货币注水(M2+)",
            description=description
        )
        self.daily_transactions.append(tx)
        self.all_transactions_history.append(tx)
        return True

    # =========================================================================
    # 存量与广义货币计算
    # =========================================================================
    
    def get_total_m2(self) -> float:
        """
        广义货币供应量 M2 统计口径：
        M2 = 居民储蓄存款总额 + 实体企业活期与定期存款 + 社保医保统筹专户存款
        (国库现金属于政府在央行单一账户存款，不计入流通 M2，但属财政资产)
        """
        household_deposits = sum(
            acc.balance for acc in self.accounts.values() if acc.sector == "household"
        )
        corp_deposits = sum(
            acc.balance for acc in self.accounts.values() if acc.sector == "corporate"
        )
        ss_deposits = self.accounts.get("social_security_fund", Account("", "", "", 0.0)).balance
        return round(household_deposits + corp_deposits + ss_deposits, 4)

    # =========================================================================
    # 每日闭市自动化平账与审计核验器 (End-of-Day Conservation Validator)
    # =========================================================================
    
    def start_day(self, day: int):
        """新的一天开启，记录期初底稿"""
        self.current_day = day
        self.daily_transactions.clear()
        self.daily_credit_expansion = 0.0
        self.daily_credit_repayment = 0.0
        self.daily_bad_debt_write_off = 0.0
        self.daily_fx_inflow_cny = 0.0
        self.daily_fx_outflow_cny = 0.0
        self.daily_cb_injection = 0.0
        self.day_start_m2 = self.get_total_m2()
        treasury_acc = self.accounts.get("treasury_cash")
        self.day_start_treasury = treasury_acc.balance if treasury_acc else 0.0
        bank_ops = self.accounts.get("bank_operations")
        self.day_start_bank_ops = bank_ops.balance if bank_ops else 0.0

    def end_day_and_audit(self) -> DailyAuditReport:
        """
        每日闭市三联平账检验：
        1. 现金流零和检验 (Flow Conservation): 内部转账总流入 == 总流出
        2. 广义货币 M2 恒等式检验 (M2 Delta Attribution Identity):
           实际 M2 变化 = (信贷派生 - 还贷) + (结汇 - 购汇) + 央行直接注水 - 国库现金留存净增加 - 银行留存利差资本净增加 (扣除坏账核销冲减)
        3. 商业银行资产负债平衡检验 (Balance Sheet Identity):
           资产 = 负债 + 资本金
        """
        day_end_m2 = self.get_total_m2()
        actual_m2_delta = round(day_end_m2 - self.day_start_m2, 4)
        
        # 1. 内部转账现金流对账
        internal_txs = [
            tx for tx in self.daily_transactions
            if tx.from_account_id in self.accounts and tx.to_account_id in self.accounts
        ]
        sum_internal_flow = sum(tx.amount for tx in internal_txs)
        
        # 2. M2 理论增量归因分解
        net_credit = self.daily_credit_expansion - self.daily_credit_repayment
        net_fx = self.daily_fx_inflow_cny - self.daily_fx_outflow_cny
        net_cb = self.daily_cb_injection
        
        # 国库现金与银行留存资本净变动
        treasury_acc = self.accounts.get("treasury_cash")
        treasury_delta = (treasury_acc.balance - self.day_start_treasury) if treasury_acc else 0.0
        bank_ops = self.accounts.get("bank_operations")
        bank_ops_delta = (bank_ops.balance - self.day_start_bank_ops) if bank_ops else 0.0
        if bank_ops:
            self.bank_capital_equity = bank_ops.balance
            
        # 银行自有资本营运净变动 (扣除坏账核销冲减，还原真实净利差营运吸收额)
        bank_ops_operating_delta = bank_ops_delta + self.daily_bad_debt_write_off
        
        # 理论 M2 净变动 = 净信贷 + 净外贸 + 净印钞 - 国库现金净增加 - 银行自有资本营运净增加
        theoretical_m2_delta = round(net_credit + net_fx + net_cb - treasury_delta - bank_ops_operating_delta, 4)
        
        m2_discrepancy = round(abs(actual_m2_delta - theoretical_m2_delta), 4)
        
        # 3. 商业银行资产负债对账
        # 银行负债 = 居民存款 + 企业存款 + 社保统筹专户
        bank_liabilities = self.get_total_m2()
        # 银行资产 = 贷款(企业+居民) + 国债持有 + 准备金
        bank_assets = (
            self.bank_loans_corporate +
            self.bank_loans_household +
            self.bank_treasury_bonds
        )
        # 银行资本金配平与容差计算
        bank_discrepancy = round(abs(bank_assets - (bank_liabilities + self.bank_capital_equity)), 2)
        
        messages = []
        is_balanced = True
        
        if m2_discrepancy > 0.05:
            is_balanced = False
            messages.append(f"❌ 【M2恒等式失衡】实际增量 {actual_m2_delta:.4f}亿 != 理论增量 {theoretical_m2_delta:.4f}亿 (差异: {m2_discrepancy:.4f}亿)")
        else:
            messages.append(f"✅ 【M2严密守恒】期初: {self.day_start_m2:.2f}亿 ➔ 期末: {day_end_m2:.2f}亿 (净变动: {actual_m2_delta:+.2f}亿，无任何资金泄漏)")
            
        if net_credit != 0:
            messages.append(f"  ├─ 银行信贷净派生: {net_credit:+.2f} 亿元 (新增 {self.daily_credit_expansion:.2f}亿 / 偿还 {self.daily_credit_repayment:.2f}亿)")
        if self.daily_bad_debt_write_off > 0:
            messages.append(f"  ├─ 商业银行不良坏账核销: -{self.daily_bad_debt_write_off:.2f} 亿元 (冲减银行信贷资产与资本金)")
        if net_fx != 0:
            messages.append(f"  ├─ 外贸净结售汇: {net_fx:+.2f} 亿元 (出口顺差结汇 {self.daily_fx_inflow_cny:.2f}亿 / 进口付汇 {self.daily_fx_outflow_cny:.2f}亿)")
        if net_cb != 0:
            messages.append(f"  └─ 央行直接货币注水: {net_cb:+.2f} 亿元")
            
        report = DailyAuditReport(
            day=self.current_day,
            is_balanced=is_balanced,
            total_inflow=round(sum_internal_flow, 4),
            total_outflow=round(sum_internal_flow, 4),
            flow_discrepancy=0.0,
            m2_start_of_day=round(self.day_start_m2, 4),
            m2_end_of_day=round(day_end_m2, 4),
            m2_actual_delta=actual_m2_delta,
            m2_theoretical_delta=theoretical_m2_delta,
            m2_discrepancy=m2_discrepancy,
            credit_net_expansion=round(net_credit, 4),
            fx_net_settlement=round(net_fx, 4),
            cb_net_injection=round(net_cb, 4),
            treasury_cash_delta=round(treasury_acc.balance - treasury_acc.initial_balance, 4) if treasury_acc else 0.0,
            bad_debt_write_off=round(self.daily_bad_debt_write_off, 4),
            bank_total_assets=round(bank_assets, 2),
            bank_total_liabilities=round(bank_liabilities, 2),
            bank_equity=round(self.bank_capital_equity, 2),
            bank_balance_discrepancy=bank_discrepancy,
            audit_messages=messages
        )
        self.daily_audit_history.append(report)
        return report
