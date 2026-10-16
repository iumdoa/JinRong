"""
政策卡效果对比测试 (Card Comparison Script)
测试三张经典政策卡被激活后，对经济六维指标与资金流向的影响。
"""
from engine.state import create_difficult_country_state
from engine.policy_cards import PolicyCardManager
from engine.simulation import SimulationEngine

def test_card(card_id: str, card_name: str, run_days: int = 360):
    state = create_difficult_country_state(seed=42)
    card_mgr = PolicyCardManager()
    sim = SimulationEngine(state, card_mgr, seed=123)
    
    # 预热90天达到自然稳态
    for _ in range(90):
        sim.step_day()
        
    before_metrics = {
        "gdp": state.gdp_annual_runrate,
        "per_capita": state.gdp_per_capita,
        "engel": state.engel_coefficient,
        "poverty": state.poverty_rate,
        "unemp": state.unemployment_rate,
        "sentiment": state.consumer_sentiment,
        "treasury": state.treasury_cash,
        "debt": state.national_debt
    }
    
    # 激活政策卡
    ok, msg = card_mgr.activate_card(card_id)
    print(f"\n>>> 激活测试：{card_name} (测试生效中 - 运行 {run_days} 天)")
    print(f"    操作结果: {msg}")
    
    # 运行指定天数
    for _ in range(run_days):
        sim.step_day()
        
    print(f"    【实施前后指标对比 (第 {run_days} 天在策状态)】")
    print(f"    - 整体GDP:   {before_metrics['gdp']:.1f}亿 -> {state.gdp_annual_runrate:.1f}亿 (变动: {(state.gdp_annual_runrate - before_metrics['gdp']):+.1f}亿)")
    print(f"    - 恩格尔系数: {before_metrics['engel']*100:.1f}% -> {state.engel_coefficient*100:.1f}% (变动: {(state.engel_coefficient - before_metrics['engel'])*100:+.1f}%)")
    print(f"    - 贫困率:     {before_metrics['poverty']*100:.1f}% -> {state.poverty_rate*100:.1f}% (变动: {(state.poverty_rate - before_metrics['poverty'])*100:+.1f}%)")
    print(f"    - 失业率:     {before_metrics['unemp']*100:.1f}% -> {state.unemployment_rate*100:.1f}% (变动: {(state.unemployment_rate - before_metrics['unemp'])*100:+.1f}%)")
    print(f"    - 消费意向:   {before_metrics['sentiment']:.1f} -> {state.consumer_sentiment:.1f} (变动: {(state.consumer_sentiment - before_metrics['sentiment']):+.1f})")
    print(f"    - 国库结余:   {before_metrics['treasury']:.1f}亿 -> {state.treasury_cash:.1f}亿")
    print(f"    - 国家债务:   {before_metrics['debt']:.1f}亿 -> {state.national_debt:.1f}亿 (新增负债: {(state.national_debt - before_metrics['debt']):+.1f}亿)")
    
    # 打印前三条特征资金流水
    print("    【最近代表性资金流向流水】")
    for rec in state.daily_flows[:3]:
        print(f"      • [{rec.category}] {rec.source} -> {rec.target}: {rec.amount}亿元 ({rec.description})")

if __name__ == "__main__":
    print("=" * 70)
    print("【三张历史名策卡动态对比实测 (生效中期 第180天)】")
    print("=" * 70)
    test_card("roosevelt_new_deal", "【罗斯福新政·以工代赈】", run_days=180)
    test_card("reagan_tax_cut", "【里根大减税·供给学派革命】", run_days=180)
    test_card("helicopter_money", "【直升机撒钱·普惠现金补贴】", run_days=180)
