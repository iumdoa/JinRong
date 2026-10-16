import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from engine.state import create_difficult_country_state
from engine.policy_cards import PolicyCardManager
from engine.simulation import SimulationEngine

def main():
    state = create_difficult_country_state(seed=42)
    card_mgr = PolicyCardManager()
    sim = SimulationEngine(state, card_mgr, seed=123)
    print("=== INITIAL STATE (Day 0) ===")
    print(f"Research capability: {sim.state.research_capability}")
    print(f"Bank loans: {sim.state.bank_loans} 亿 | Bank deposits: {sim.state.bank_deposits} 亿 | Bad debt rate: {sim.state.bad_debt_rate}%")
    print(f"Treasury cash: {sim.state.treasury_cash} 亿 | National debt: {sim.state.national_debt} 亿")
    print(f"Food basket price: {sim.state.food_basket_price} 元 | CPI: {sim.state.cpi_index}")
    
    # Check persona initial savings
    c_aqiang = sim.state.citizens_ledger["aqiang_unemployed"]
    c_zhang = sim.state.citizens_ledger["zhang_miner"]
    e_qian = sim.state.employers_ledger["qian_farm"]
    print(f"Aqiang savings: {c_aqiang['accumulated_funds']} 元 (daily net: {c_aqiang['daily_net']})")
    print(f"Zhang miner savings: {c_zhang['accumulated_funds']} 元 (daily net: {c_zhang['daily_net']})")
    print(f"Qian farm capital: {e_qian['accumulated_funds']} 万元 (daily net: {e_qian['daily_net']})")
    
    print("\n--- Running 360 days (1 full year) ---")
    for d in range(1, 361):
        events = sim.step_day()
        
    print("\n=== STATE AFTER 90 DAYS (Day 90) ===")
    print(f"Research capability: {sim.state.research_capability} (baseline: {getattr(sim.state, 'base_research_capability', 45.0)})")
    print(f"Bank loans: {sim.state.bank_loans} 亿 | Bank deposits: {sim.state.bank_deposits} 亿 | Bad debt rate: {sim.state.bad_debt_rate:.2f}%")
    print(f"Treasury cash: {sim.state.treasury_cash} 亿 | National debt: {sim.state.national_debt} 亿")
    print(f"Food basket price: {sim.state.food_basket_price:.2f} 元 | CPI: {sim.state.cpi_index:.1f}")
    print(f"Exchange rate: {sim.state.exchange_rate:.2f}")
    
    print("\n=== COMMODITY COVER & STOCK CHECK ===")
    hub = sim.commodity_hub
    for cid, c in hub.commodities.items():
        total_d = c.total_daily_demand
        print(f"  [{c.name:12s}] 库存: {c.stock:8.1f} {c.unit:4s} | 日产: {c.daily_production:6.1f} | 日耗: {total_d:6.1f} | 库容天数: {c.inventory_cover_days:5.1f} 天 | 现货价: {c.domestic_price:8.1f} 元 (基准 {c.base_price:.1f})")
        
    print("\n=== CITIZEN SAVINGS CHECK (Day 90) ===")
    c_aqiang = sim.state.citizens_ledger["aqiang_unemployed"]
    c_zhang = sim.state.citizens_ledger["zhang_miner"]
    c_li = sim.state.citizens_ledger["li_accountant"]
    c_expert = sim.state.citizens_ledger["lin_expert"]
    print(f"  Aqiang savings: {c_aqiang['accumulated_funds']} 元 | 日收: {c_aqiang['daily_revenue']} | 日支: {c_aqiang['daily_expense']} | 日净: {c_aqiang['daily_net']} | 状态: {c_aqiang['financial_status']}")
    print(f"  Zhang miner savings: {c_zhang['accumulated_funds']} 元 | 日收: {c_zhang['daily_revenue']} | 日支: {c_zhang['daily_expense']} | 日净: {c_zhang['daily_net']} | 状态: {c_zhang['financial_status']}")
    print(f"  Li accountant savings: {c_li['accumulated_funds']} 元 | 日净: {c_li['daily_net']} | 状态: {c_li['financial_status']}")
    print(f"  Lin expert savings: {c_expert['accumulated_funds']} 元 | 日净: {c_expert['daily_net']} | 状态: {c_expert['financial_status']}")
    
    print("\n=== EMPLOYER CAPITAL CHECK (Day 90) ===")
    e_qian = sim.state.employers_ledger["qian_farm"]
    e_sun = sim.state.employers_ledger["sun_coal"]
    e_chen = sim.state.employers_ledger["chen_machinery"]
    print(f"  Qian farm: {e_qian['accumulated_funds']} 万元 | 日净: {e_qian['daily_net']} 元 | 状态: {e_qian['financial_status']}")
    print(f"  Sun coal: {e_sun['accumulated_funds']} 万元 | 日净: {e_sun['daily_net']} 元 | 状态: {e_sun['financial_status']}")
    print(f"  Chen machinery: {e_chen['accumulated_funds']} 万元 | 日净: {e_chen['daily_net']} 元 | 状态: {e_chen['financial_status']}")
    
    print("\n=== STRATEGIC STOCKPILES (Day 90) ===")
    for sid, sp in sim.resource_manager.stockpiles.items():
        print(f"  {sp.name}: {sp.current_stock:.1f} / {sp.capacity:.0f} {sp.unit} (daily flow: {sp.daily_flow})")

    print("\n=== AUDIT BALANCED? ===")
    print(f"SFC is_balanced: {sim.last_audit.is_balanced} (flow discrepancy: {sim.last_audit.flow_discrepancy})")

if __name__ == "__main__":
    main()
