import sys
import os

workspace_dir = "/home/iumdoa/Public/JinRong"
if workspace_dir not in sys.path:
    sys.path.insert(0, workspace_dir)

from engine.simulation import SimulationEngine
from engine.state import create_country_state
from engine.policy_cards import PolicyCardManager

state = create_country_state(mode="frugal", seed=42)
card_mgr = PolicyCardManager(max_active_slots=2)
sim = SimulationEngine(state, card_mgr, seed=42)

print("=== 30-Day Option A Audit ===")
for d in range(1, 31):
    events = sim.step_day()
    audit = sim.last_audit
    assert audit.is_balanced, f"Day {d} SFC Imbalance: {audit.audit_messages}"
    assert audit.flow_discrepancy < 0.001, f"Day {d} Flow discrepancy: {audit.flow_discrepancy}"

print(f"Day 30 Treasury Cash: {state.treasury_cash:.2f} 亿元 (Initial: 148.35 亿元)")
print(f"Day 30 Foreign Reserves: ${state.foreign_reserves_usd:.2f} 亿美元 (Initial: $25.00 亿美元)")
print(f"Day 30 Exchange Rate: 1 USD = {state.exchange_rate:.2f} CNY")
print(f"Day 30 CPI Index: {state.cpi_index:.1f}, Food Basket: {state.food_basket_price:.2f} 元")
print(f"Day 30 Unemployment Rate: {state.unemployment_rate * 100:.1f}%")

print("\n--- All 16 Factories Status on Day 30 ---")
for fid, f in sim.factory_manager.factories.items():
    cash = sim.accounting_bus.accounts[f.account_id].balance if f.account_id in sim.accounting_bus.accounts else 0.0
    print(f"{fid:24s} | status={f.status:9s} | util={f.utilization_rate:4.1f}% | rev={f.daily_revenue:6.3f}亿 | profit={f.daily_profit:+6.3f}亿 | cash={cash:6.2f}亿 | debt={f.debt_principal:5.1f}亿 | rating={f.credit_rating}")

print("\n--- All 16 Commodities Status on Day 30 ---")
for cid, c in sim.commodity_hub.commodities.items():
    print(f"{cid:16s} | price={c.domestic_price:8.2f} {c.unit:4s} | prod={c.daily_production:5.2f} | demand={c.total_daily_demand:5.2f} | stock={c.stock:6.1f} | cover={c.inventory_cover_days:4.1f}d | status={c.clearance_status}")
