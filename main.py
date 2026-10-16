"""
国家宏观金融体系模拟器 - 交互式终端 MVP 主程序 (main.py)
"""
import os
import sys
import time
from typing import Optional
from engine.state import create_difficult_country_state, MacroState
from engine.policy_cards import PolicyCardManager
from engine.simulation import SimulationEngine

# ANSI 颜色定义
C_RESET = "\033[0m"
C_BOLD = "\033[1m"
C_RED = "\033[91m"
C_GREEN = "\033[92m"
C_YELLOW = "\033[93m"
C_BLUE = "\033[94m"
C_CYAN = "\033[96m"
C_WHITE = "\033[97m"
C_GRAY = "\033[90m"

def render_bar(value: float, max_val: float = 1.0, length: int = 15, reverse_color: bool = False) -> str:
    """渲染紧凑 ASCII 进度条"""
    ratio = max(0.0, min(1.0, value / max_val))
    filled = int(ratio * length)
    empty = length - filled
    
    # 颜色判断：如果是失业率/贫困/恩格尔，越高越红；反之越绿
    if reverse_color: # 越低越好
        color = C_GREEN if ratio < 0.3 else (C_YELLOW if ratio < 0.55 else C_RED)
    else: # 越高越好
        color = C_RED if ratio < 0.3 else (C_YELLOW if ratio < 0.6 else C_GREEN)
        
    bar = f"{color}[{'█' * filled}{'░' * empty}]{C_RESET}"
    return bar

def clear_screen():
    # 保持跨平台清屏
    os.system('cls' if os.name == 'nt' else 'clear')

def format_delta(val: float, baseline: float, is_pct: bool = False, reverse_good: bool = False) -> str:
    """格式化变动量并着色"""
    diff = val - baseline
    if is_pct:
        text = f"{diff*100:+.1f}%"
    else:
        text = f"{diff:+.1f}"
        
    if abs(diff) < 0.0001:
        return f"{C_GRAY} (持平){C_RESET}"
        
    is_good = (diff < 0) if reverse_good else (diff > 0)
    color = C_GREEN if is_good else C_RED
    return f" {color}({text}){C_RESET}"

class GameSession:
    def __init__(self, seed: int = 42):
        self.state: MacroState = create_difficult_country_state(seed=seed)
        self.card_manager: PolicyCardManager = PolicyCardManager(max_active_slots=2)
        self.engine: SimulationEngine = SimulationEngine(self.state, self.card_manager, seed=seed)
        self.event_log = ["游戏开局：你接管了一个深陷泥潭的困难国家，请利用金融与政策工具引导国家走出困境！"]

    def render_dashboard(self):
        state = self.state
        init = state.initial_metrics
        
        print(f"\n{C_BOLD}{C_CYAN}╔══════════════════════════════════════════════════════════════════════════════════════╗{C_RESET}")
        print(f"{C_BOLD}{C_CYAN}║  🏛️  国家宏观金融模拟器 (MVP)  |  {state.nation_name:<20}              ║{C_RESET}")
        print(f"{C_BOLD}{C_CYAN}║  📅 当前时间：第 {state.year:2d} 年 第 {state.quarter:1d} 季度 第 {state.day:4d} 天  |  政策公信力：{state.policy_credibility:5.1f}/100           ║{C_RESET}")
        print(f"{C_BOLD}{C_CYAN}╚══════════════════════════════════════════════════════════════════════════════════════╝{C_RESET}")
        
        # 六维民生与宏观雷达指标
        print(f"\n{C_BOLD}【📊 六维核心宏观指标 (六维雷达数据)】{C_RESET}")
        
        # 1. 整体 GDP
        gdp_bar = render_bar(state.gdp_annual_runrate, max_val=4000.0, length=14, reverse_color=False)
        gdp_delta = format_delta(state.gdp_annual_runrate, init["annual_gdp"], is_pct=False, reverse_good=False)
        print(f"  1. 整体年化GDP:  {state.gdp_annual_runrate:7.1f} 亿元  {gdp_bar}{gdp_delta}")
        
        # 2. 人均 GDP
        cap_bar = render_bar(state.gdp_per_capita, max_val=40000.0, length=14, reverse_color=False)
        cap_delta = format_delta(state.gdp_per_capita, init["gdp_per_capita"], is_pct=False, reverse_good=False)
        print(f"  2. 人均年化GDP:  {state.gdp_per_capita:7.0f} 元/年   {cap_bar}{cap_delta}")
        
        # 3. 恩格尔系数
        engel_bar = render_bar(state.engel_coefficient, max_val=1.0, length=14, reverse_color=True)
        engel_delta = format_delta(state.engel_coefficient, init["engel_coefficient"], is_pct=True, reverse_good=True)
        print(f"  3. 恩格尔系数:   {state.engel_coefficient*100:6.1f}%       {engel_bar}{engel_delta} (基准: 困难国 >55%)")
        
        # 4. 贫困占比
        pov_bar = render_bar(state.poverty_rate, max_val=1.0, length=14, reverse_color=True)
        pov_delta = format_delta(state.poverty_rate, init["poverty_rate"], is_pct=True, reverse_good=True)
        print(f"  4. 贫困人口占比: {state.poverty_rate*100:6.1f}%       {pov_bar}{pov_delta} (基准线: 20元/人/天)")
        
        # 5. 失业率
        unemp_bar = render_bar(state.unemployment_rate, max_val=0.5, length=14, reverse_color=True)
        unemp_delta = format_delta(state.unemployment_rate, init["unemployment_rate"], is_pct=True, reverse_good=True)
        print(f"  5. 社会失业率:   {state.unemployment_rate*100:6.1f}%       {unemp_bar}{unemp_delta}")
        
        # 6. 消费意向
        sent_bar = render_bar(state.consumer_sentiment, max_val=100.0, length=14, reverse_color=False)
        sent_delta = format_delta(state.consumer_sentiment, init["consumer_sentiment"], is_pct=False, reverse_good=False)
        print(f"  6. 居民消费意向: {state.consumer_sentiment:6.1f} / 100   {sent_bar}{sent_delta}")
        
        # 财政与金融账户简报
        print(f"\n{C_BOLD}【💰 金融与财政核心底账】{C_RESET}")
        print(f"  🏛️ 国库现金储备: {state.treasury_cash:7.1f} 亿元   |  📜 国家存量国债: {state.national_debt:7.1f} 亿元")
        print(f"  🏦 银行信贷资产: {state.bank_loans:7.1f} 亿元   |  🛡️ 银行自有资本: {state.bank_capital:7.1f} 亿元 (不良率: {state.bad_debt_rate*100:.1f}%)")
        print(f"  🏭 企业营运现金: {state.corporate_cash:7.1f} 亿元   |  💳 企业银行负债: {state.corporate_debt:7.1f} 亿元")
        print(f"  ⚙️ 当前调控杠杆: 基准利率 {state.base_interest_rate*100:.1f}% | 企业税率 {state.corp_tax_rate*100:.1f}% | 日常政府开支 {state.gov_daily_spending:.2f}亿/天")
        
        # 激活中的政策卡
        active_ids = self.card_manager.active_card_ids
        print(f"\n{C_BOLD}【📜 战略政策卡生效槽位 ({len(active_ids)}/2)】{C_RESET}")
        if not active_ids:
            print(f"  {C_GRAY}(当前暂无生效政策卡，可在主菜单签署推行){C_RESET}")
        else:
            for cid in active_ids:
                c = self.card_manager.cards[cid]
                remain_days = c.duration_days - c.days_active
                print(f"  • {C_GREEN}{c.name}{C_RESET} [流派: {c.tag}] 剩余有效时间: {remain_days} 天 (约 {remain_days//90} 季度)")
                print(f"    ↳ 资金链路: {c.money_source} ➔ {c.money_target}")

        # 最新事件日志 (最多显示2条)
        if self.event_log:
            print(f"\n{C_BOLD}【📢 最新动态】{C_RESET}")
            for msg in self.event_log[-2:]:
                print(f"  {C_YELLOW}• {msg}{C_RESET}")
        print("-" * 88)

    def advance_time(self, days: int):
        """推进时间"""
        print(f"\n⏳ 正在推进 {days} 天...")
        for _ in range(days):
            events = self.engine.step_day()
            if events:
                self.event_log.extend(events)
        print(f"✅ 时间已推进至：第 {self.state.year} 年 第 {self.state.quarter} 季度 第 {self.state.day} 天。")

    def show_money_flow_details(self):
        """展示资金流穿透流水账本"""
        print(f"\n{C_BOLD}==================== 🔍 【资金流穿透全景账本 (钱从哪来，到哪去)】 ===================={C_RESET}")
        print(f"今日共记录结算 {len(self.state.daily_flows)} 笔宏观资金流动：\n")
        print(f"{'来源部门':<12} {'去向部门':<16} {'流转金额':<12} {'收支类目':<18} {'说明'}")
        print("-" * 88)
        for rec in self.state.daily_flows:
            print(f"{rec.source:<12} {rec.target:<16} {rec.amount:6.4f} 亿元   {rec.category:<18} {rec.description}")
            
        print("-" * 88)
        print(f"\n{C_BOLD}【本季度累计特征资金流总览】{C_RESET}")
        for key, val in sorted(self.state.quarterly_flow_summary.items(), key=lambda x: x[1], reverse=True)[:8]:
            print(f"  • {key:<38}: 累计 {val:8.2f} 亿元")
            
        input(f"\n{C_WHITE}按回车键返回主菜单...{C_RESET}")

    def show_policy_cards_menu(self):
        """政策卡菜单"""
        while True:
            clear_screen()
            print(f"\n{C_BOLD}==================== 📜 【国家战略政策卡牌库】 ===================={C_RESET}")
            print(f"当前可用槽位: {len(self.card_manager.active_card_ids)} / {self.card_manager.max_active_slots}")
            print(f"政策公信力: {self.state.policy_credibility:.1f} (提前强行废除会遭受严厉信用惩罚)\n")
            
            card_list = list(self.card_manager.cards.values())
            for idx, c in enumerate(card_list, 1):
                status_str = f"{C_GREEN}[生效中 - 剩余 {c.duration_days - c.days_active} 天]{C_RESET}" if c.is_active else (
                    f"{C_RED}[冷却中 - 剩余 {c.days_cooldown_left} 天]{C_RESET}" if c.days_cooldown_left > 0 else f"{C_CYAN}[可随时签署]{C_RESET}"
                )
                print(f"[{idx}] {C_BOLD}{c.name}{C_RESET} {status_str}")
                print(f"    流派标签: {c.tag} | 持续时长: {c.duration_days} 天 ({c.duration_days//90} 季度)")
                print(f"    历史背景: {c.history_intro}")
                print(f"    {C_YELLOW}钱从哪来: {c.money_source}{C_RESET}")
                print(f"    {C_YELLOW}钱到哪去: {c.money_target}{C_RESET}")
                print("-" * 80)
                
            print("\n操作选项:")
            print("  [1~3] 签署/启用对应的政策卡")
            print("  [4]   强行废除正在生效的政策卡 (朝令夕改惩罚)")
            print("  [0]   返回主菜单")
            
            choice = input(f"\n{C_BOLD}请输入指令代号: {C_RESET}").strip()
            if choice == "0":
                break
            elif choice in ["1", "2", "3"]:
                target_card = card_list[int(choice) - 1]
                ok, msg = self.card_manager.activate_card(target_card.id)
                print(f"\n{msg}")
                self.event_log.append(msg)
                input(f"\n{C_WHITE}按回车键继续...{C_RESET}")
            elif choice == "4":
                if not self.card_manager.active_card_ids:
                    print("\n当前没有正在生效的政策卡，无需废除。")
                    input(f"\n{C_WHITE}按回车键继续...{C_RESET}")
                    continue
                print("\n请选择要废除的生效政策卡：")
                for i, cid in enumerate(self.card_manager.active_card_ids, 1):
                    print(f"  [{i}] {self.card_manager.cards[cid].name}")
                sub_choice = input("请输入序号 (0取消): ").strip()
                if sub_choice.isdigit() and 1 <= int(sub_choice) <= len(self.card_manager.active_card_ids):
                    target_cid = self.card_manager.active_card_ids[int(sub_choice) - 1]
                    ok, msg = self.card_manager.cancel_card_early(target_cid)
                    # 朝令夕改重罚公信力
                    self.state.policy_credibility = max(5.0, self.state.policy_credibility - 15.0)
                    print(f"\n{msg}")
                    self.event_log.append(msg)
                    input(f"\n{C_WHITE}按回车键继续...{C_RESET}")

    def adjust_policy_levers_menu(self):
        """调整宏观把手菜单"""
        state = self.state
        days_since_last = state.day - state.last_policy_change_day
        print(f"\n{C_BOLD}==================== ⚙️ 【调整日常宏观政策杠杆】 ===================={C_RESET}")
        print(f"当前政策公信力：{state.policy_credibility:.1f} / 100")
        print(f"距上次调整天数：{days_since_last} 天")
        if days_since_last < 30:
            print(f"{C_RED}⚠️ 警告：当前处于30天极速变动机敏期，修改政策将导致市场严厉抗议朝令夕改 (公信力 -12)！{C_RESET}")
        elif days_since_last < 90:
            print(f"{C_YELLOW}⚠️ 注意：调整不足一个季度，会有轻微公信力惩罚 (公信力 -5)。{C_RESET}")
        else:
            print(f"{C_GREEN}✅ 距离上次调整已充分消化预期，正常调控不会产生额外惩罚。{C_RESET}")
            
        print(f"\n当前数值：")
        print(f"  [1] 央行基准利率: {state.base_interest_rate*100:.1f}%")
        print(f"  [2] 企业综合税率: {state.corp_tax_rate*100:.1f}%")
        print(f"  [3] 政府日常公共支出: {state.gov_daily_spending:.2f} 亿元/天")
        print(f"  [0] 取消返回")
        
        choice = input(f"\n{C_BOLD}请选择要修改的杠杆 (0~3): {C_RESET}").strip()
        if choice == "1":
            raw = input(f"请输入新的基准利率 (如 0.03 代表 3.0%, 当前为 {state.base_interest_rate}): ").strip()
            try:
                val = float(raw)
                if 0.005 <= val <= 0.25:
                    ok, msg = self.engine.change_policy_levers(base_rate=val)
                    print(f"\n{msg}")
                    self.event_log.append(msg)
                else:
                    print("利率范围应在 0.005 (0.5%) 到 0.25 (25%) 之间。")
            except ValueError:
                print("无效输入！")
            input(f"\n{C_WHITE}按回车键继续...{C_RESET}")
        elif choice == "2":
            raw = input(f"请输入新的企业综合税率 (如 0.15 代表 15%, 当前为 {state.corp_tax_rate}): ").strip()
            try:
                val = float(raw)
                if 0.05 <= val <= 0.40:
                    ok, msg = self.engine.change_policy_levers(corp_tax=val)
                    print(f"\n{msg}")
                    self.event_log.append(msg)
                else:
                    print("税率范围应在 0.05 (5%) 到 0.40 (40%) 之间。")
            except ValueError:
                print("无效输入！")
            input(f"\n{C_WHITE}按回车键继续...{C_RESET}")
        elif choice == "3":
            raw = input(f"请输入每日政府日常公共支出 (亿元/天, 当前为 {state.gov_daily_spending}): ").strip()
            try:
                val = float(raw)
                if 0.2 <= val <= 5.0:
                    ok, msg = self.engine.change_policy_levers(daily_gov_spending=val)
                    print(f"\n{msg}")
                    self.event_log.append(msg)
                else:
                    print("支出范围应在 0.2 到 5.0 亿元/天之间。")
            except ValueError:
                print("无效输入！")
            input(f"\n{C_WHITE}按回车键继续...{C_RESET}")

    def show_history_reports(self):
        """查看季度与年度决算历史"""
        print(f"\n{C_BOLD}==================== 📈 【历史财务与六维审计报告】 ===================={C_RESET}")
        if not self.state.quarterly_history:
            print("当前尚无已结案的季度报告，时间推进至第90天后自动生成首季财报。")
        else:
            print(f"{'周期':<12} {'当季GDP':<10} {'年化人均GDP':<12} {'恩格尔':<8} {'贫困率':<8} {'失业率':<8} {'消费意向':<8} {'国债总额'}")
            print("-" * 88)
            for h in self.state.quarterly_history:
                period_str = f"Y{h['year']} Q{h['quarter']}"
                print(f"{period_str:<12} {h['quarter_gdp']:6.1f}亿    {h['gdp_per_capita']:6.0f}元        {h['engel']*100:4.1f}%    {h['poverty']*100:4.1f}%    {h['unemployment']*100:4.1f}%    {h['sentiment']:5.1f}     {h['debt']:6.1f}亿")
        input(f"\n{C_WHITE}按回车键返回主菜单...{C_RESET}")

    def main_loop(self):
        while True:
            clear_screen()
            self.render_dashboard()
            
            print(f"{C_BOLD}【🕹️ 治国理政决策菜单】{C_RESET}")
            print("  [1] 推进时间 (1天 / 30天 / 1个季度90天 / 1个年度360天)")
            print("  [2] 政策卡牌库 (查看3张历史名策、签署推行、废除惩罚)")
            print("  [3] 调整宏观杠杆 (央行基准利率、宏观企业税率、日常财政支出)")
            print("  [4] 查看穿透账本 (钱从哪来、到哪去、每日流转全景)")
            print("  [5] 查看历史财报 (季度运行数据与六维审计决算)")
            print("  [0] 退出模拟器")
            
            choice = input(f"\n{C_BOLD}请输入指令代号 [0~5]: {C_RESET}").strip()
            
            if choice == "0":
                print("\n感谢体验国家宏观金融模拟器！再见。")
                break
            elif choice == "1":
                print("\n选择推进时长：")
                print("  [A] 推进 1 天 (精细观察单日资金流)")
                print("  [B] 推进 30 天 (推进 1 个月)")
                print("  [C] 推进 90 天 (推进 1 个季度，生成季度财报)")
                print("  [D] 推进 360 天 (推进 1 个年度，生成年度决算)")
                sub = input("请选择 [A/B/C/D] (回车默认90天): ").strip().upper()
                if sub == "A":
                    self.advance_time(1)
                elif sub == "B":
                    self.advance_time(30)
                elif sub == "D":
                    self.advance_time(360)
                else:
                    self.advance_time(90)
                time.sleep(0.5)
            elif choice == "2":
                self.show_policy_cards_menu()
            elif choice == "3":
                self.adjust_policy_levers_menu()
            elif choice == "4":
                self.show_money_flow_details()
            elif choice == "5":
                self.show_history_reports()

if __name__ == "__main__":
    session = GameSession(seed=42)
    session.main_loop()
