"""
Test Suite: Strategic Reserve Automated Buffer & Foreign Exchange Replenishment
(国家战略储备自动化平准机制与外汇出海补库综合验证测试)
"""
import sys
import os

workspace_dir = "/home/iumdoa/Public/JinRong"
if workspace_dir not in sys.path:
    sys.path.insert(0, workspace_dir)

from engine.state import create_country_state
from engine.simulation import SimulationEngine
from engine.policy_cards import PolicyCardManager
from engine.accounting import AccountingBus

def test_strategic_buffer_automation():
    print("=" * 80)
    print("🚀 开始国家战略缓冲储备自动化平准与外汇出海补库机制综合验证")
    print("=" * 80)

    # 1. 初始化仿真环境
    state = create_country_state(mode="frugal", seed=42)
    card_mgr = PolicyCardManager(max_active_slots=2)
    engine = SimulationEngine(state, card_mgr, seed=42)
    bus = engine.accounting_bus

    # -------------------------------------------------------------------------
    # TEST 1: 市场流动性告急 -> 自动平价抛储救急
    # -------------------------------------------------------------------------
    print("\n--- [测试 1: 市场商业周转告急 -> 战略储备局自动平价抛储] ---")
    c_grain = engine.commodity_hub.commodities["raw_grain"]
    sp_grain = engine.resource_manager.stockpiles["grain"]
    
    # 模拟原粮商业库存骤降，周转跌破 15 天底线
    c_grain.stock = 30.0 # 商业库存仅剩 30 万吨，远低于正常周转
    c_grain.last_day_demand = 80.0 # 日需求 80 万吨，周转仅剩 0.4 天
    initial_sp_stock = sp_grain.current_stock
    initial_treasury = state.treasury_cash
    
    print(f"初始状态: 原粮商业库存={c_grain.stock:.1f}万吨, 周转={c_grain.inventory_cover_days:.1f}天 (阈值<{sp_grain.min_market_cover_days:.0f}天)")
    print(f"战略粮仓存量: {initial_sp_stock:.1f}万吨, 国库现金: {initial_treasury:.2f}亿元")
    
    events = engine.step_day()
    audit = engine.last_audit
    assert audit.is_balanced, f"抛储后 SFC 审计失衡! {audit.audit_messages}"
    
    # 寻找自动抛储事件
    release_events = [e for e in events if "战略储备自动抛储" in e]
    print(f"触发事件: {release_events}")
    assert len(release_events) > 0, "商业周转严重不足时必须自动触发战略储备抛储！"
    assert sp_grain.current_stock < initial_sp_stock, "战略储备库实物存量应扣减"
    assert state.treasury_cash > 0, "抛储款项必须合规结转入中央国库现金"
    print(f"✅ 自动抛储平抑测试通过！粮仓投放物资平抑市场，国库回笼现金，100% SFC 平衡。")

    # -------------------------------------------------------------------------
    # TEST 2: 市场产能过剩积压 -> 自动财政托市收储
    # -------------------------------------------------------------------------
    print("\n--- [测试 2: 实体产能过剩积压 -> 战略储备局自动财政托市收储] ---")
    c_coal = engine.commodity_hub.commodities["coal"]
    sp_coal = engine.resource_manager.stockpiles["coal"]
    
    # 模拟煤炭产能严重过剩，商业堆场周转暴涨至 100 天 (超过上限 45 天)
    c_coal.stock = 4500.0
    c_coal.last_day_demand = 40.0
    initial_sp_coal = sp_coal.current_stock
    
    print(f"初始状态: 原煤商业库存={c_coal.stock:.1f}万吨, 周转={c_coal.inventory_cover_days:.1f}天 (阈值>{sp_coal.max_market_cover_days:.0f}天)")
    print(f"战略电煤库现存: {initial_sp_coal:.1f}万吨, 国库现金: {state.treasury_cash:.2f}亿元")
    
    events = engine.step_day()
    audit = engine.last_audit
    assert audit.is_balanced, f"收储后 SFC 审计失衡! {audit.audit_messages}"
    
    accumulate_events = [e for e in events if "战略储备自动收储" in e]
    print(f"触发事件: {accumulate_events}")
    assert len(accumulate_events) > 0, "商业周转积压严重时必须自动触发财政托市收储！"
    assert sp_coal.current_stock > initial_sp_coal, "战略电煤库实物应增加"
    print(f"✅ 自动托市收储测试通过！财政出资吸纳多余现货，托底坑口物价，100% SFC 平衡。")

    # -------------------------------------------------------------------------
    # TEST 3: 战略战备底线告急 -> 自动动用外汇海外代购补库
    # -------------------------------------------------------------------------
    print("\n--- [测试 3: 战略储备年限告急 -> 自动动用国家外汇储备出海补库] ---")
    sp_oil = engine.resource_manager.stockpiles["oil"]
    
    # 人为压低国家战略石油储备至 0.3 年 (低于设定的 0.5 年补库线)
    sp_oil.current_stock = 100.0 # 约 0.28 年
    initial_res_years = sp_oil.reserve_years
    initial_fx = state.foreign_reserves_usd
    initial_treasury = state.treasury_cash
    
    print(f"初始状态: 战略石油储备={sp_oil.current_stock:.1f}万桶 (战备支撑 {initial_res_years:.2f}年, 告急红线<{sp_oil.auto_import_reserve_years:.1f}年)")
    print(f"国家外汇储备: ${initial_fx:.2f}亿美元, 国库现金: {initial_treasury:.2f}亿元")
    
    events = engine.step_day()
    audit = engine.last_audit
    assert audit.is_balanced, f"外汇海外补库后 SFC 审计失衡! {audit.audit_messages}"
    
    fx_events = [e for e in events if "战略外汇海外补库" in e]
    assert len(fx_events) > 0, "战备储备年限跌破安全底线时必须自动动用外汇出海补库！"
    assert sp_oil.current_stock > 100.0, "战略石油储备必须成功到货入库"
    # 核验国库购汇扣减流水 (TSA 单一账户支付购汇款)
    fx_txs = [t for t in bus.daily_transactions if t.from_account_id == "treasury_cash" and "购汇" in t.category]
    assert len(fx_txs) > 0, "国家外汇储备必须用于支付进口货款并生成国库购汇凭证"
    fx_txs = [t for t in bus.daily_transactions if t.from_account_id == "treasury_cash" and "购汇" in t.category]
    assert len(fx_txs) > 0, "中央国库必须有真实的购汇扣款记账凭证"
    print(f"中央财政购汇记账流水: 扣除国库现金 {fx_txs[0].amount:.2f} 亿元 (注销本币 M2)")
    print(f"更新后战略石油储备: {sp_oil.current_stock:.1f}万桶 (支撑 {sp_oil.reserve_years:.2f}年), 外汇结存: ${state.foreign_reserves_usd:.2f}亿")
    print(f"✅ 战略外汇海外补库全项核验通过！外汇储备作为国家终极生命线顺利打通！")

    # -------------------------------------------------------------------------
    # TEST 4: 自动化策略参数动态调整与一键开关 (QoL)
    # -------------------------------------------------------------------------
    print("\n--- [测试 4: 策略参数调整与纯手动模式切换] ---")
    ok, msg = engine.set_strategic_stockpile_target(
        sid="grain",
        target_years=2.5,
        auto_enabled=False,
        min_market_cover_days=8.0,
        max_market_cover_days=50.0,
        auto_import_reserve_years=0.9
    )
    assert ok, f"调整策略失败: {msg}"
    assert not sp_grain.auto_policy_enabled, "必须成功关闭自动化方针转入纯手动调度"
    assert sp_grain.min_market_cover_days == 8.0
    assert sp_grain.max_market_cover_days == 50.0
    assert sp_grain.auto_import_reserve_years == 0.9
    print(f"调整结果: {msg}")
    print("✅ 策略参数配置与开关控制测试通过！")

    print("\n" + "=" * 80)
    print("🎉 国家战略缓冲储备自动化平准机制全部测试通过！100% SFC 合规！")
    print("=" * 80)

if __name__ == "__main__":
    test_strategic_buffer_automation()
