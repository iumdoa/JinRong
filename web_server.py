"""
国家宏观金融体系模拟器 - 轻量内置 Web 服务器 (web_server.py)
基于 Python 标准库 http.server，无需额外安装 pip/npm 依赖，即开即用。
"""
import os
import json
import socket
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse
from engine.state import create_country_state, create_difficult_country_state, MacroState
from engine.policy_cards import PolicyCardManager
from engine.simulation import SimulationEngine
from engine.serializer import serialize_game_state

WEB_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "web")

class GlobalGameManager:
    def __init__(self, seed: int = 42, mode: str = "frugal"):
        self.seed = seed
        self.mode = mode
        self.state: MacroState = create_country_state(mode=mode, seed=seed)
        self.card_manager: PolicyCardManager = PolicyCardManager(max_active_slots=2)
        self.engine: SimulationEngine = SimulationEngine(self.state, self.card_manager, seed=seed)
        self.recent_events = [f"游戏开局：【{self.state.difficulty_name}】{self.state.nation_name}新任内阁就职，等待阁下的宏观治理。"]

    def get_snapshot(self):
        if hasattr(self.engine, "resource_manager"):
            self.state.resources = self.engine.resource_manager.to_dict()
        if hasattr(self.engine, "commodity_hub"):
            self.state.commodities = self.engine.commodity_hub.to_dict()
            if hasattr(self.engine.commodity_hub, "get_macro_clearance_report"):
                self.state.market_clearing_summary = self.engine.commodity_hub.get_macro_clearance_report(getattr(self.engine, "factory_manager", None))
        if hasattr(self.engine, "factory_manager"):
            self.state.factories = self.engine.factory_manager.to_dict(self.engine.accounting_bus)
        if hasattr(self.engine, "labor_manager"):
            self.state.labor_market = self.engine.labor_manager.to_dict(self.engine.factory_manager.factories)
        if hasattr(self.engine, "sync_personas_and_ledgers"):
            self.engine.sync_personas_and_ledgers()
        return serialize_game_state(self.state, self.card_manager, self.engine.infra_manager, self.recent_events, audit=getattr(self.engine, "last_audit", None))

    def reset(self, seed: int = None, mode: str = None):
        if seed is not None:
            self.seed = seed
        if mode is not None:
            self.mode = mode
        self.state = create_country_state(mode=self.mode, seed=self.seed)
        self.card_manager = PolicyCardManager(max_active_slots=2)
        self.engine = SimulationEngine(self.state, self.card_manager, seed=self.seed)
        self.recent_events = [f"国家已重新生成：【{self.state.difficulty_name}】{self.state.nation_name}（种子: {self.seed}），新任内阁正式履职！"]

game_mgr = GlobalGameManager(seed=42, mode="frugal")

class SimulationHttpHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=WEB_DIR, **kwargs)

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == "/api/state":
            self.send_json_response(game_mgr.get_snapshot())
        elif parsed.path == "/" or parsed.path == "/index.html":
            self.path = "/index.html"
            return super().do_GET()
        else:
            return super().do_GET()

    def do_POST(self):
        parsed = urlparse(self.path)
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length).decode("utf-8") if content_length > 0 else "{}"
        try:
            payload = json.loads(body)
        except json.JSONDecodeError:
            payload = {}

        if parsed.path == "/api/step":
            days = int(payload.get("days", 1))
            days = max(1, min(1080, days)) # 限制单次最多推进3年
            collected_events = []
            for _ in range(days):
                evts = game_mgr.engine.step_day()
                if evts:
                    collected_events.extend(evts)
            if collected_events:
                game_mgr.recent_events.extend(collected_events)
                game_mgr.recent_events = game_mgr.recent_events[-30:] # 保留最近30条
            self.send_json_response(game_mgr.get_snapshot())

        elif parsed.path == "/api/policy/activate":
            card_id = payload.get("card_id", "")
            ok, msg = game_mgr.card_manager.activate_card(card_id)
            game_mgr.recent_events.append(msg)
            self.send_json_response({
                "success": ok,
                "message": msg,
                "state": game_mgr.get_snapshot()
            })

        elif parsed.path == "/api/policy/cancel":
            card_id = payload.get("card_id", "")
            ok, msg = game_mgr.card_manager.cancel_card_early(card_id)
            if ok:
                # 朝令夕改重罚
                game_mgr.state.policy_credibility = max(5.0, game_mgr.state.policy_credibility - 15.0)
                punish_msg = f"⚠️【朝令夕改惩罚】中途废除大政方针，市场预期大乱，政策公信力受到严厉惩罚 (-15)！"
                game_mgr.recent_events.append(punish_msg)
            game_mgr.recent_events.append(msg)
            self.send_json_response({
                "success": ok,
                "message": msg,
                "state": game_mgr.get_snapshot()
            })

        elif parsed.path == "/api/project/start":
            template_id = payload.get("template_id", "")
            ok, msg = game_mgr.engine.infra_manager.start_project(
                template_id, 
                current_research_capability=game_mgr.state.research_capability
            )
            game_mgr.state.infra_daily_spending = sum(p.cost_per_day for p in game_mgr.engine.infra_manager.active_projects.values())
            game_mgr.engine.sync_personas_and_ledgers()
            game_mgr.recent_events.append(msg)
            self.send_json_response({
                "success": ok,
                "message": msg,
                "state": game_mgr.get_snapshot()
            })

        elif parsed.path == "/api/project/cancel":
            template_id = payload.get("template_id", "")
            ok, msg = game_mgr.engine.infra_manager.cancel_project(template_id)
            game_mgr.state.infra_daily_spending = sum(p.cost_per_day for p in game_mgr.engine.infra_manager.active_projects.values())
            game_mgr.engine.sync_personas_and_ledgers()
            game_mgr.recent_events.append(msg)
            self.send_json_response({
                "success": ok,
                "message": msg,
                "state": game_mgr.get_snapshot()
            })

        elif parsed.path == "/api/education/grant_research_fund":
            tier_id = payload.get("tier_id", "tier_2")
            tiers_config = {
                "tier_1": {
                    "name": "基础探索性科研专款",
                    "cost": 3.0,
                    "duration_days": 90,
                    "boost": 6.0
                },
                "tier_2": {
                    "name": "国家重点领域科技攻关专项",
                    "cost": 8.0,
                    "duration_days": 180,
                    "boost": 15.0
                },
                "tier_3": {
                    "name": "战略性重大科技工程举国特资",
                    "cost": 18.0,
                    "duration_days": 360,
                    "boost": 30.0
                }
            }
            if tier_id not in tiers_config:
                self.send_json_response({"success": False, "message": "未知的资助额度方案。", "state": game_mgr.get_snapshot()})
            else:
                cfg = tiers_config[tier_id]
                cost = cfg["cost"]
                if game_mgr.state.treasury_cash < cost:
                    self.send_json_response({
                        "success": False,
                        "message": f"国库可用现金不足！审批【{cfg['name']}】需专项划拨 {cost:.1f} 亿元，当前国库仅存 {game_mgr.state.treasury_cash:.1f} 亿元。",
                        "state": game_mgr.get_snapshot()
                    })
                else:
                    game_mgr.engine.execute_flow(
                        from_acc="treasury_cash",
                        to_acc="corporate_sector",
                        amount=cost,
                        category="专项科研经费划拨",
                        description=f"中央财政向科研单位划拨专款 {cost:.1f} 亿元（{cfg['name']}，期限 {cfg['duration_days']} 天）"
                    )
                    game_mgr.state.treasury_cash = round(game_mgr.engine.accounting_bus.accounts["treasury_cash"].balance, 4)
                    ok, msg = game_mgr.engine.infra_manager.grant_research_funds(
                        tier_id=tier_id,
                        tier_name=cfg["name"],
                        cost=cost,
                        boost=cfg["boost"],
                        duration_days=cfg["duration_days"]
                    )
                    # 立即生效科研能力加持
                    buffs = game_mgr.engine.infra_manager.accumulated_buffs
                    game_mgr.state.research_capability = min(100.0, 12.0 + buffs["research_boost"] + cfg["boost"])
                    game_mgr.state.active_research_grant = game_mgr.engine.infra_manager.active_research_grant.copy()
                    game_mgr.recent_events.append(msg)
                    self.send_json_response({
                        "success": True,
                        "message": msg,
                        "state": game_mgr.get_snapshot()
                    })

        elif parsed.path == "/api/debt/issue":
            amount = float(payload.get("amount", 20.0))
            ok, msg = game_mgr.engine.issue_national_debt(amount)
            game_mgr.recent_events.append(msg)
            self.send_json_response({
                "success": ok,
                "message": msg,
                "state": game_mgr.get_snapshot()
            })

        elif parsed.path == "/api/debt/repay":
            amount = float(payload.get("amount", 20.0))
            ok, msg = game_mgr.engine.repay_national_debt(amount)
            game_mgr.recent_events.append(msg)
            self.send_json_response({
                "success": ok,
                "message": msg,
                "state": game_mgr.get_snapshot()
            })

        elif parsed.path == "/api/social/update":
            medicare_rate = payload.get("medicare_reimburse_rate")
            contrib_rate = payload.get("social_contrib_rate")
            ok, msg = game_mgr.engine.change_social_security_policy(
                medicare_rate=float(medicare_rate) if medicare_rate is not None else None,
                social_contrib_rate=float(contrib_rate) if contrib_rate is not None else None
            )
            game_mgr.recent_events.append(msg)
            self.send_json_response({
                "success": ok,
                "message": msg,
                "state": game_mgr.get_snapshot()
            })

        elif parsed.path == "/api/levers":
            base_rate = payload.get("base_rate")
            reserve_ratio = payload.get("reserve_ratio")
            corp_tax = payload.get("corp_tax")
            vat_tax = payload.get("vat_tax")
            income_tax = payload.get("income_tax")
            gov_spending = payload.get("gov_spending")
            welfare_spending = payload.get("welfare_spending")
            min_wage = payload.get("min_wage")
            retirement_age = payload.get("retirement_age")
            fx_sterilization = payload.get("fx_sterilization_ratio")
            
            ok, msg = game_mgr.engine.change_policy_levers(
                base_rate=float(base_rate) if base_rate is not None else None,
                reserve_ratio=float(reserve_ratio) if reserve_ratio is not None else None,
                corp_tax=float(corp_tax) if corp_tax is not None else None,
                vat_tax=float(vat_tax) if vat_tax is not None else None,
                income_tax=float(income_tax) if income_tax is not None else None,
                daily_gov_spending=float(gov_spending) if gov_spending is not None else None,
                welfare_spending=float(welfare_spending) if welfare_spending is not None else None,
                min_wage=float(min_wage) if min_wage is not None else None,
                retirement_age=int(retirement_age) if retirement_age is not None else None,
                fx_sterilization=float(fx_sterilization) if fx_sterilization is not None else None
            )
            game_mgr.recent_events.append(msg)
            self.send_json_response({
                "success": ok,
                "message": msg,
                "state": game_mgr.get_snapshot()
            })

        elif parsed.path == "/api/exploration/set_budget":
            budget = float(payload.get("budget", 0.05))
            focus = payload.get("focus", None)
            ok, msg = game_mgr.engine.set_geological_exploration(daily_budget=budget, focus=focus)
            game_mgr.recent_events.append(msg)
            self.send_json_response({
                "success": ok,
                "message": msg,
                "state": game_mgr.get_snapshot()
            })

        elif parsed.path == "/api/stockpile/action":
            stockpile_id = payload.get("stockpile_id", "")
            action = payload.get("action", "release") # "release" 或 "accumulate"
            amount = float(payload.get("amount", 20.0))
            if action == "release":
                ok, msg = game_mgr.engine.release_strategic_stockpile(stockpile_id, amount)
            elif action == "accumulate":
                ok, msg = game_mgr.engine.accumulate_strategic_stockpile(stockpile_id, amount)
            else:
                ok, msg = False, "未知的战略储备操作指令"
            game_mgr.recent_events.append(msg)
            self.send_json_response({
                "success": ok,
                "message": msg,
                "state": game_mgr.get_snapshot()
            })

        elif parsed.path in ["/api/stockpile/set_target", "/api/stockpile/set_auto_policy"]:
            stockpile_id = payload.get("stockpile_id", "")
            target_years = float(payload.get("target_years", 3.0)) if payload.get("target_years") is not None else None
            auto_enabled = payload.get("auto_enabled", None)
            min_market_cover_days = payload.get("min_market_cover_days", None)
            max_market_cover_days = payload.get("max_market_cover_days", None)
            auto_import_reserve_years = payload.get("auto_import_reserve_years", None)
            ok, msg = game_mgr.engine.set_strategic_stockpile_target(
                stockpile_id,
                target_years,
                auto_enabled,
                min_market_cover_days,
                max_market_cover_days,
                auto_import_reserve_years
            )
            game_mgr.recent_events.append(msg)
            self.send_json_response({
                "success": ok,
                "message": msg,
                "state": game_mgr.get_snapshot()
            })

        elif parsed.path == "/api/customs/trade":
            cid = payload.get("cid", "")
            action = payload.get("action", "import") # "import" 或 "export"
            amount = float(payload.get("amount", 10.0))
            if action == "import":
                ok, msg = game_mgr.engine.customs_import_commodity(cid, amount)
            elif action == "export":
                ok, msg = game_mgr.engine.customs_export_commodity(cid, amount)
            else:
                ok, msg = False, "未知的海关外贸口岸指令"
            game_mgr.recent_events.append(msg)
            self.send_json_response({
                "success": ok,
                "message": msg,
                "state": game_mgr.get_snapshot()
            })

        elif parsed.path == "/api/commodity/set_auto_trade":
            cid = payload.get("cid", "")
            enabled = bool(payload.get("enabled", True))
            min_cover = float(payload.get("min_cover", 12.0))
            max_cover = float(payload.get("max_cover", 40.0))
            max_import = float(payload.get("max_import", 0.5))
            max_export = float(payload.get("max_export", 0.5))
            ok, msg = game_mgr.engine.set_commodity_auto_trade(
                cid=cid,
                enabled=enabled,
                min_cover=min_cover,
                max_cover=max_cover,
                max_import=max_import,
                max_export=max_export
            )
            game_mgr.recent_events.append(msg)
            self.send_json_response({
                "success": ok,
                "message": msg,
                "state": game_mgr.get_snapshot()
            })

        elif parsed.path == "/api/levers/fx_sterilization":
            ratio = float(payload.get("ratio", 0.0))
            ok, msg = game_mgr.engine.set_fx_sterilization(ratio)
            game_mgr.recent_events.append(msg)
            self.send_json_response({
                "success": ok,
                "message": msg,
                "state": game_mgr.get_snapshot()
            })

        elif parsed.path == "/api/reset":
            seed = payload.get("seed")
            mode = payload.get("mode", "frugal")
            game_mgr.reset(seed=int(seed) if seed is not None else None, mode=mode)
            self.send_json_response({
                "success": True,
                "message": f"成功就职【{game_mgr.state.difficulty_name}】！",
                "state": game_mgr.get_snapshot()
            })
        else:
            self.send_error(404, "Endpoint Not Found")

    def send_json_response(self, data: dict, status: int = 200):
        resp = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(resp)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(resp)

def run_server(port: int = 8080):
    os.makedirs(WEB_DIR, exist_ok=True)
    server_address = ("", port)
    httpd = HTTPServer(server_address, SimulationHttpHandler)
    print(f"================================================================")
    print(f"🚀 国家宏观金融模拟器 Web 端已启动！")
    print(f"👉 访问地址: http://localhost:{port} (或 http://127.0.0.1:{port})")
    print(f"================================================================")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nWeb 服务已停止。")
        httpd.server_close()

if __name__ == "__main__":
    import sys
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8080
    run_server(port)
