"""
无干预稳态基准测试 (Verification Script)
验证在完全不干预的情况下，整个国家财政和6大指标是否能在困难国家标准下平稳运转 10 年（3600天 / 40个季度）而不发生系统性崩盘。
"""
from engine.state import create_difficult_country_state
from engine.policy_cards import PolicyCardManager
from engine.simulation import SimulationEngine

def run_test():
    state = create_difficult_country_state(seed=42)
    card_mgr = PolicyCardManager()
    sim = SimulationEngine(state, card_mgr, seed=123)
    
    print("=" * 70)
    print("【索拉尼亚共和国 - 10年（3600天）无干预基准稳态测试】")
    print("=" * 70)
    
    print(f"初始开局数据：")
    print(f"  整体GDP (年化): {state.gdp_annual_runrate:.1f} 亿元")
    print(f"  人均GDP: {state.gdp_per_capita:.0f} 元/年")
    print(f"  恩格尔系数: {state.engel_coefficient * 100:.1f}%")
    print(f"  贫困人口占比: {state.poverty_rate * 100:.1f}%")
    print(f"  失业率: {state.unemployment_rate * 100:.1f}%")
    print(f"  消费意向: {state.consumer_sentiment:.1f} / 100")
    print(f"  国库现金: {state.treasury_cash:.1f} 亿元 | 国债总额: {state.national_debt:.1f} 亿元")
    print(f"  银行资本金: {state.bank_capital:.1f} 亿元")
    print("-" * 70)
    
    checkpoints = [90, 360, 720, 1800, 3600] # Q1, 第1年末, 第2年末, 第5年末, 第10年末
    
    for day in range(1, 3601):
        events = sim.step_day()
        if day in checkpoints:
            year = (day - 1) // 360 + 1
            quarter = ((day - 1) % 360) // 90 + 1
            print(f"--- 进度：第 {day:4d} 天 (第 {year} 年 第 {quarter} 季度) ---")
            print(f"  整体GDP (年化): {state.gdp_annual_runrate:.1f} 亿元")
            print(f"  人均GDP: {state.gdp_per_capita:.0f} 元/年")
            print(f"  恩格尔系数: {state.engel_coefficient * 100:.1f}%")
            print(f"  贫困人口占比: {state.poverty_rate * 100:.1f}%")
            print(f"  失业率: {state.unemployment_rate * 100:.1f}%")
            print(f"  消费意向: {state.consumer_sentiment:.1f} / 100")
            print(f"  国库现金: {state.treasury_cash:.1f} 亿元 | 国债总额: {state.national_debt:.1f} 亿元")
            print(f"  银行资本金: {state.bank_capital:.1f} 亿元")
            print("-" * 70)

    # 统计偏离度
    init_gdp = state.initial_metrics["annual_gdp"]
    end_gdp = state.gdp_annual_runrate
    gdp_diff_pct = (end_gdp - init_gdp) / init_gdp * 100.0
    
    print("【10年测试结论】")
    print(f"GDP 10年累计偏离度: {gdp_diff_pct:+.2f}%")
    print(f"国库维持健康: {'是' if state.treasury_cash > 50 else '否'} (结余 {state.treasury_cash:.1f} 亿元)")
    print(f"金融体系稳定: {'是' if state.bank_capital > 100 else '否'} (资本金 {state.bank_capital:.1f} 亿元)")
    print(f"民生体系未崩盘: {'是' if state.poverty_rate < 0.50 and state.unemployment_rate < 0.30 else '否'}")

if __name__ == "__main__":
    run_test()
