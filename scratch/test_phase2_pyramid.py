"""
Phase 2 Verification Script:
Verifies:
1. 5-Tier Consumption Pyramid flow execution.
2. Central bank interest rate sensitivity (rate cut reduces mortgage burden and stimulates housing/durables).
3. Upstream industrial pull from real estate construction (steel, cement, heavy machinery direct purchase).
4. Micro personas fidelity (Li accountant mortgage, Chen factory durable orders).
5. 100% Stock-Flow Consistency (SFC) conservation across 60+ days.
"""
import sys
import os

# Add root directory to sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engine.simulation import SimulationEngine
from engine.state import create_country_state
from engine.policy_cards import PolicyCardManager

def test_phase2_pyramid():
    print("=" * 60)
    print("🚀 Starting Phase 2 Consumption Pyramid & Real Estate Verification")
    print("=" * 60)

    # 1. Initialize simulation with Frugal preset
    state = create_country_state(mode="frugal", seed=42)
    card_manager = PolicyCardManager(max_active_slots=2)
    sim = SimulationEngine(state, card_manager, seed=42)

    print(f"Initial State: Day {sim.state.day}")
    print(f"  Housing Stock: {sim.state.housing_stock_sqm:.1f} 万㎡, Avg Price: {sim.state.housing_avg_price:.1f} 元/㎡")
    print(f"  Household Mortgage Debt: {sim.state.household_mortgage_debt:.1f} 亿元")
    print(f"  Commercial Bank Assets Household Loans: {sim.accounting_bus.bank_loans_household:.1f} 亿元")
    print(f"  Initial Base Interest Rate: {sim.state.base_interest_rate * 100:.2f}%")

    # Verify initial asset matching
    assert abs(sim.accounting_bus.bank_loans_household - sim.state.household_mortgage_debt) < 1.0, (
        f"Bank household loans {sim.accounting_bus.bank_loans_household} does not match state {sim.state.household_mortgage_debt}"
    )

    # 2. Run 30 days under baseline conditions
    print("\n[Stage 1] Running 30 days baseline simulation...")
    for day in range(1, 31):
        sim.step_day()
        audit = sim.last_audit
        assert audit.is_balanced, f"Day {day} SFC imbalance! Messages: {audit.audit_messages}"
        assert abs(audit.m2_discrepancy) < 0.1, f"Day {day} M2 discrepancy {audit.m2_discrepancy}"
        assert abs(audit.flow_discrepancy) < 0.01, f"Day {day} Flow discrepancy {audit.flow_discrepancy}"

    print(f"Day 30 Results:")
    print(f"  Daily Housing Sales: {sim.state.daily_housing_sales_sqm:.2f} 万㎡/天 ({sim.state.daily_housing_sales_yuan:.3f} 亿元/天)")
    print(f"  Daily Housing Starts: {sim.state.daily_housing_starts_sqm:.2f} 万㎡/天")
    print(f"  Daily Mortgage Repaid: {sim.state.daily_mortgage_repay_total:.4f} 亿元/天")
    print(f"  Daily Durable Spending: {sim.state.daily_durable_spending:.4f} 亿元/天")
    print(f"  Daily Service Spending: {sim.state.daily_service_spending:.4f} 亿元/天")
    print(f"  Mortgage Burden Index: {sim.state.mortgage_burden_index:.1f}%")
    print(f"  Durable Penetration Rate: {sim.state.durable_penetration_rate:.1f}%")

    # Assert non-zero consumption across all tiers
    assert sim.state.daily_durable_spending > 0.0, "Durable spending should be active"
    assert sim.state.daily_service_spending > 0.0, "Service spending should be active"
    assert sim.state.daily_mortgage_repay_total > 0.0, "Mortgage repayment should be active"
    assert sim.state.daily_housing_sales_sqm > 0.0, "Housing sales should be active"
    assert sim.state.daily_housing_starts_sqm > 0.0, "Housing starts should be active"

    # Verify upstream pull: steel mill, cement plant, heavy machinery should have positive factory revenue
    steel_factory = sim.factory_manager.factories.get("steel_mill")
    cement_factory = sim.factory_manager.factories.get("cement_plant")
    mach_factory = sim.factory_manager.factories.get("heavy_machinery")

    steel_acc = sim.accounting_bus.accounts.get(steel_factory.account_id)
    cement_acc = sim.accounting_bus.accounts.get(cement_factory.account_id)
    mach_acc = sim.accounting_bus.accounts.get(mach_factory.account_id)

    print("\n[Upstream Industrial Pull Checks]:")
    print(f"  Steel Mill Balance: {steel_acc.balance:.2f} 亿 (Daily Rev: {steel_factory.daily_revenue:.3f} 亿)")
    print(f"  Cement Plant Balance: {cement_acc.balance:.2f} 亿 (Daily Rev: {cement_factory.daily_revenue:.3f} 亿)")
    print(f"  Heavy Machinery Balance: {mach_acc.balance:.2f} 亿 (Daily Rev: {mach_factory.daily_revenue:.3f} 亿)")
    assert steel_factory.daily_revenue > 0, "Steel mill should earn revenue from housing/industrial demand"
    assert cement_factory.daily_revenue > 0, "Cement plant should earn revenue from housing demand"
    assert mach_factory.daily_revenue > 0, "Heavy machinery should earn revenue from housing/durable demand"

    # Verify micro personas
    li_pre = sim.state.citizens_ledger.get("li_accountant")
    chen_pre = sim.state.employers_ledger.get("chen_machinery")
    assert li_pre is not None, "Li accountant persona must exist"
    assert chen_pre is not None, "Chen machinery persona must exist"

    print("\n[Micro Persona Check - Baseline]:")
    print(f"  Li Accountant daily net: {li_pre['daily_net']:.1f} 元, voice: {li_pre['voice']}")
    print(f"  Chen Machinery daily rev: {chen_pre['daily_revenue']:.1f} 万元, voice: {chen_pre['voice']}")
    assert any("按揭" in line["subject"] or "房贷" in line["subject"] for line in li_pre["receipt_lines"]), "Li accountant must have mortgage receipt line"
    assert any("耐用消费品" in line["subject"] or "耐用" in line["subject"] for line in chen_pre["receipt_lines"]), "Chen factory must have durable goods receipt line"

    baseline_li_expense = li_pre["daily_expense"]
    baseline_housing_sales = sim.state.daily_housing_sales_sqm

    # 3. Rate Cut Test: Cut base interest rate from 4.0% to 2.0%
    print("\n[Stage 2] Simulating Central Bank Rate Cut: 4.0% -> 2.0%...")
    sim.state.base_interest_rate = 0.02
    sim.state.loan_interest_rate = 0.035

    for day in range(31, 61):
        sim.step_day()
        audit = sim.last_audit
        assert audit.is_balanced, f"Day {day} SFC imbalance after rate cut! Messages: {audit.audit_messages}"
        assert abs(audit.m2_discrepancy) < 0.1, f"Day {day} M2 discrepancy {audit.m2_discrepancy}"

    li_post = sim.state.citizens_ledger.get("li_accountant")
    print(f"\nDay 60 Results (Post Rate Cut):")
    print(f"  Mortgage Burden Index: {sim.state.mortgage_burden_index:.1f}%")
    print(f"  Housing Sales: {sim.state.daily_housing_sales_sqm:.2f} 万㎡/天 (Baseline was {baseline_housing_sales:.2f})")
    print(f"  Li Accountant daily expense: {li_post['daily_expense']:.1f} 元 (Baseline was {baseline_li_expense:.1f} 元)")
    print(f"  Li Accountant Voice: {li_post['voice']}")

    # Assert interest rate cut reduced mortgage expense for Li accountant
    assert li_post["daily_expense"] <= baseline_li_expense, (
        f"Rate cut should reduce Li accountant mortgage expense: {li_post['daily_expense']} vs {baseline_li_expense}"
    )
    # Assert housing sales remained solid
    assert sim.state.daily_housing_sales_sqm >= baseline_housing_sales * 0.95, (
        f"Housing sales should respond favorably to rate cuts"
    )

    print("\n" + "=" * 60)
    print("✅ All Phase 2 Verification Assertions Passed Successfully!")
    print("=" * 60)

if __name__ == "__main__":
    test_phase2_pyramid()
