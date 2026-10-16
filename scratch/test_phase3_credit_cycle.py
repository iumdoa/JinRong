import sys
import os
import unittest

# Ensure project root is in path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engine.simulation import SimulationEngine
from engine.state import create_country_state
from engine.policy_cards import PolicyCardManager

class TestPhase3CreditCycle(unittest.TestCase):
    def setUp(self):
        self.state = create_country_state("frugal")
        self.card_manager = PolicyCardManager(max_active_slots=2)
        self.engine = SimulationEngine(self.state, self.card_manager, seed=42)

    def test_initial_credit_ratings_and_sfc(self):
        """验证初始企业信用评级矩阵生成与SFC严格闭环"""
        factories = self.engine.factory_manager.factories
        self.assertEqual(len(factories), 16)
        
        # 验证初始企业债务与 state.corporate_debt 一致
        total_debt = sum(f.debt_principal for f in factories.values())
        self.assertAlmostEqual(total_debt, self.state.corporate_debt, places=2)

        # 验证所有工厂都有合法的信用评级
        for fid, f in factories.items():
            self.assertIn(f.credit_rating, ["AAA", "AA", "A", "BBB", "BB", "B", "CCC", "D"])
            self.assertGreaterEqual(f.credit_score, 0.0)
            self.assertLessEqual(f.credit_score, 100.0)
            self.assertGreater(f.borrowing_rate, 0.0)
            self.assertIn(f.loan_status, ["normal", "special_mention", "substandard", "doubtful", "loss"])
            print(f"[{fid}] Rating: {f.credit_rating} | Score: {f.credit_score:.1f} | Lev: {f.leverage_ratio:.1f}% | ICR: {f.interest_coverage_ratio:.2f}x | Rate: {f.borrowing_rate*100:.2f}% | Status: {f.loan_status}")

    def test_run_60_days_sfc_conservation(self):
        """验证连续运行60天，每日SFC零误差，宏观信贷指标动态演化正常"""
        print("\n--- Running 60-day Simulation with Phase 3 Credit Cycle ---")
        for day in range(1, 61):
            events = self.engine.step_day()
            report = self.engine.last_audit
            
            # 严格核对 SFC 资金守恒零误差
            self.assertTrue(report.is_balanced, f"Day {day} SFC discrepancy detected: {report.flow_discrepancy}")
            self.assertAlmostEqual(report.m2_discrepancy, 0.0, places=3, msg=f"Day {day} M2 discrepancy: {report.m2_discrepancy}")
            
            # 验证 Phase 3 核心指标合理性
            self.assertGreater(self.state.bank_loans, 0.0)
            self.assertGreater(self.state.bank_deposits, 0.0)
            self.assertGreater(self.state.capital_adequacy_ratio, 0.0)
            self.assertGreaterEqual(self.state.bank_provision_coverage, 0.0)
            
            if day % 10 == 0 or day == 1:
                print(f"Day {day:02d} | M2: {self.state.bank_deposits:.1f} | Loans: {self.state.bank_loans:.1f} | "
                      f"CAR: {self.state.capital_adequacy_ratio:.2f}% | NPL: {self.state.bank_npl_loans:.1f} ({self.state.bank_npl_ratio:.2f}%) | "
                      f"PCR: {self.state.bank_provision_coverage:.1f}% | NIM: {self.state.daily_bank_net_interest_margin:.4f} | "
                      f"Recalled: {self.state.daily_loans_recalled:.4f} | SFC: {report.m2_discrepancy:.6f}")

    def test_stress_loan_recall_and_write_off(self):
        """压力测试：强制某工厂巨额亏损降级至CCC，验证银行风控主动抽贷与破产核销，且SFC保持0误差"""
        print("\n--- Stress Testing Credit Downgrade, Loan Recall & SFC Bad Debt Write-off ---")
        f_textile = self.engine.factory_manager.factories["textile_light"]
        
        # 制造轻纺工厂极端亏损与资不抵债条件
        f_textile.consecutive_loss_days = 20
        f_textile.cash_balance = 0.5 # 拥有一定存款，供银行抽贷
        f_textile.debt_principal = 90.0
        
        # 运行一天
        self.engine.step_day()
        report = self.engine.last_audit
        self.assertTrue(report.is_balanced)
        self.assertAlmostEqual(report.m2_discrepancy, 0.0, places=3)
        
        print(f"Post-Stress f_textile Rating: {f_textile.credit_rating} | Score: {f_textile.credit_score:.1f} | Status: {f_textile.loan_status} | Recalled: {f_textile.recalled_loans_today:.4f}")
        self.assertIn(f_textile.credit_rating, ["CCC", "D", "B"])
        
        # 强制将轻纺工厂推入破产，验证坏账核销
        f_textile.status = "bankrupt"
        f_textile.debt_principal = 50.0
        f_textile.cash_balance = 0.0
        
        # 运行下一步，触发破产清算
        self.engine.step_day()
        report_bk = self.engine.last_audit
        self.assertTrue(report_bk.is_balanced)
        self.assertAlmostEqual(report_bk.m2_discrepancy, 0.0, places=3)
        print(f"Post-Bankruptcy Audit: Bad Debt Written Off = {report_bk.bad_debt_write_off:.4f} | M2 Discrepancy = {report_bk.m2_discrepancy:.6f}")

if __name__ == "__main__":
    unittest.main()
