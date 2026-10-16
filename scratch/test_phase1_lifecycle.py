"""
Phase 1 测试验证脚本：企业生死出清、资产折旧与劳动力联动
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engine.state import create_country_state, MacroState
from engine.policy_cards import PolicyCardManager
from engine.simulation import SimulationEngine
from engine.accounting import AccountingBus
from engine.factories import FactoryManager

def test_phase1_mechanics():
    print("=== 开始 Phase 1 企业生命周期与出清引擎核心验证 ===")
    state = create_country_state(mode="frugal", seed=42)
    card_manager = PolicyCardManager(max_active_slots=2)
    sim = SimulationEngine(state, card_manager, seed=42)
    
    # 1. 验证初始状态
    assert len(sim.factory_manager.factories) == 16, "工厂数量应为16"
    f_textile = sim.factory_manager.factories["textile_light"]
    assert f_textile.equipment_health == 100.0, "初始设备完好率应为100%"
    assert f_textile.status == "operating", "初始状态应为正常经营"
    print(f" Day 1 初始状态正常: {f_textile.name}, 完好率={f_textile.equipment_health}%, 在册工人={f_textile.workers_employed}")

    # 2. 正常运行 30 天，观察资产折旧与 Capex 维保
    print("\n--- 推进 30 天正常仿真 ---")
    for d in range(1, 31):
        events = sim.step_day()
        # 验证 SFC 会计平衡
        assert sim.last_audit.is_balanced, f"Day {d} 资金清算不平衡"
        assert sim.last_audit.m2_discrepancy < 0.05, f"Day {d} M2 不连续，差额: {sim.last_audit.m2_discrepancy}"

    print(f" Day 30: {f_textile.name} 完好率={f_textile.equipment_health}%, 资本存量={f_textile.capital_stock:.2f}亿, 状态={f_textile.status}")
    print(f" 在册产业工人: {f_textile.workers_employed}, 累计裁员={f_textile.total_laid_off}")
    print(f" 全社会宏观失业率: {state.unemployment_rate * 100:.2f}%")

    # 3. 模拟极端严重过剩测试 (轻纺产品无限滞销测试出清与减产)
    print("\n--- 模拟严重滞销冲击：制造 60 天亏损测试出清 ---")
    # 人为模拟严重产能过剩与库存积压 (3.5亿件成衣严重滞销)
    sim.commodity_hub.commodities["textile"].stock = 35000.0
    
    downsizing_triggered = False
    layoffs_occurred = False
    
    for d in range(31, 75):
        # 持续维持库存积压滞销
        sim.commodity_hub.commodities["textile"].stock = max(30000.0, sim.commodity_hub.commodities["textile"].stock)
        events = sim.step_day()
        
        # 检查是否触发 downsizing
        if f_textile.status in ["downsizing", "suspended", "bankrupt"]:
            downsizing_triggered = True
        if f_textile.total_laid_off > 0:
            layoffs_occurred = True
            
        # 检查 SFC
        assert sim.last_audit.is_balanced, f"Day {d} 亏损出清期间资金清算不平衡"
        assert sim.last_audit.m2_discrepancy < 0.05, f"Day {d} 亏损出清期间 M2 出现偏差: {sim.last_audit.m2_discrepancy}"

    print(f" 冲击后 Day 75: {f_textile.name} 状态={f_textile.status}, 状态标签={f_textile.status}")
    print(f" 连续亏损天数: {f_textile.consecutive_loss_days}")
    print(f" 裁员后在册工人数: {f_textile.workers_employed} (额定: {f_textile.workers_baseline})")
    print(f" 累计裁员人数: {f_textile.total_laid_off} 人")
    print(f" 全社会失业率变化: {state.unemployment_rate * 100:.2f}%")
    
    # 验证微观雇主在册数
    zhu_active = state.employer_active_entities.get("zhu_textile", 1800)
    zhu_bankrupt = state.employer_bankrupt_counts.get("zhu_textile", 0)
    print(f" 微观雇主朱老板：在册服装厂={zhu_active} 家, 累计倒闭出清={zhu_bankrupt} 家")
    
    assert downsizing_triggered, "严重亏损与过剩必须触发 downsizing 减产自救"
    assert layoffs_occurred, "减产自救必须发生裁员"
    assert zhu_bankrupt > 0, "微观实体数应体现行业倒闭潮"
    
    print("\n🎉 Phase 1 核心经济机制验证全部通过！100% 遵守 SFC 守恒铁律！")

if __name__ == "__main__":
    test_phase1_mechanics()
