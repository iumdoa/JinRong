"""
模拟用户输入测试交互主程序流程
"""
import sys
from io import StringIO
from main import GameSession

def test_full_session_flow():
    session = GameSession(seed=42)
    print("1. 测试时间推进一步...")
    session.advance_time(1)
    assert session.state.day == 2
    
    print("2. 测试推进一季度(90天)...")
    session.advance_time(90)
    assert session.state.quarter == 2
    assert len(session.state.quarterly_history) == 1
    
    print("3. 测试签署政策卡（罗斯福新政）...")
    ok, msg = session.card_manager.activate_card("roosevelt_new_deal")
    assert ok is True
    assert "roosevelt_new_deal" in session.card_manager.active_card_ids
    
    print("4. 测试政策卡生效运行 90 天...")
    session.advance_time(90)
    assert session.state.households[0].employed > session.engine.baseline_employed[0]
    
    print("5. 测试调整政策把手并触发公信力检测...")
    ok, msg = session.engine.change_policy_levers(base_rate=0.035)
    assert ok is True
    assert session.state.base_interest_rate == 0.035
    
    print("6. 测试资金流记录...")
    assert len(session.state.daily_flows) > 0
    assert any("政府国库" in f.source for f in session.state.daily_flows)
    
    print("\n✅ 所有交互功能核心流程自动化测试全部通过！")

if __name__ == "__main__":
    test_full_session_flow()
