"""
国家宏观金融体系模拟器 - 状态序列化与 API 适配 (State Serializer)
"""
from typing import Dict, Any
from engine.state import MacroState
from engine.policy_cards import PolicyCardManager
from engine.infrastructure import compute_research_success_rate

def serialize_game_state(state: MacroState, card_manager: PolicyCardManager, infra_manager: Any = None, events: list = None, audit: Any = None) -> Dict[str, Any]:
    """将整个游戏运行状态转换为前端 JSON 格式"""
    households_data = []
    for h in state.households:
        households_data.append({
            "id": getattr(h, "id", ""),
            "name": h.name,
            "population": h.population,
            "labor_force": h.labor_force,
            "employed": h.employed,
            "unemployed": h.labor_force - h.employed,
            "base_wage": round(h.base_wage, 1),
            "savings": round(h.savings, 1),
            "daily_income": round(h.daily_income, 4),
            "daily_food_cost": round(h.daily_food_cost, 4),
            "daily_other_cost": round(h.daily_other_cost, 4),
            "daily_savings_delta": round(h.daily_savings_delta, 4),
            "mortgage_debt": round(getattr(h, "mortgage_debt", 0.0), 1),
            "daily_mortgage_cost": round(getattr(h, "daily_mortgage_cost", 0.0), 4),
            "daily_durable_cost": round(getattr(h, "daily_durable_cost", 0.0), 4),
            "daily_service_cost": round(getattr(h, "daily_service_cost", 0.0), 4),
            "housing_sqm_owned": round(getattr(h, "housing_sqm_owned", 0.0), 1)
        })
        
    flows_data = []
    for f in state.daily_flows:
        flows_data.append({
            "source": f.source,
            "target": f.target,
            "amount": f.amount,
            "category": f.category,
            "description": f.description
        })
        
    cards_data = []
    for c in card_manager.cards.values():
        cards_data.append({
            "id": c.id,
            "name": c.name,
            "tag": c.tag,
            "history_intro": c.history_intro,
            "duration_days": c.duration_days,
            "cooldown_days": c.cooldown_days,
            "money_source": c.money_source,
            "money_target": c.money_target,
            "daily_cost_type": c.daily_cost_type,
            "daily_cost_amount": c.daily_cost_amount,
            "is_active": c.is_active,
            "days_active": c.days_active,
            "days_cooldown_left": c.days_cooldown_left,
            "remaining_days": max(0, c.duration_days - c.days_active) if c.is_active else 0
        })
        
    return {
        "meta": {
            "nation_name": state.nation_name,
            "difficulty_mode": getattr(state, "difficulty_mode", "frugal"),
            "difficulty_name": getattr(state, "difficulty_name", "艰难求生 (孟加拉型 · 量入为出)"),
            "day": state.day,
            "quarter": state.quarter,
            "year": state.year,
            "total_population": state.total_population,
            "policy_credibility": round(state.policy_credibility, 1),
            "days_since_policy_change": state.day - state.last_policy_change_day,
            "policy_change_count": state.policy_change_count
        },
        "metrics": {
            "gdp_annual": round(state.gdp_annual_runrate, 1),
            "gdp_quarterly": round(state.gdp_quarterly, 1),
            "gdp_per_capita": round(state.gdp_per_capita, 0),
            "engel_coefficient": round(state.engel_coefficient, 4),
            "poverty_rate": round(state.poverty_rate, 4),
            "unemployment_rate": round(state.unemployment_rate, 4),
            "consumer_sentiment": round(state.consumer_sentiment, 1),
            "initial": state.initial_metrics
        },
        "fiscal": {
            "daily_revenue": round(state.fiscal_daily_revenue, 4),
            "daily_expense": round(state.fiscal_daily_expense, 4),
            "daily_deficit": round(state.fiscal_daily_deficit, 4),
            "annual_deficit": round(state.fiscal_daily_deficit * 360.0, 1),
            "deficit_rate": round(state.deficit_to_gdp_rate, 2),
            "debt_rate": round(state.debt_to_gdp_rate, 1),
            "treasury_cash": round(state.treasury_cash, 1),
            "national_debt": round(state.national_debt, 1),
            "debt_interest_rate": round(state.national_debt_rate * 100, 2),
            "sovereign_credit_rating": getattr(state, "sovereign_credit_rating", "AAA"),
            "sovereign_risk_spread": round(getattr(state, "sovereign_risk_spread", 0.0) * 10000, 1),
            "sovereign_bond_yield": round(getattr(state, "sovereign_bond_yield", 0.035) * 100, 2),
            "national_debt_limit": round(getattr(state, "national_debt_limit", 2500.0), 1),
            "corp_tax_loss_carry_forward": round(getattr(state, "corp_tax_loss_carry_forward", 0.0), 2),
            "progressive_tax_stats": getattr(state, "progressive_tax_stats", {}),
            "counter_cyclical_boost_active": getattr(state, "counter_cyclical_boost_active", False),
            "unemployment_relief_standard": getattr(state, "unemployment_relief_standard", 28.0),
            "tax_breakdown": state.tax_breakdown,
            "expense_breakdown": state.expense_breakdown
        },
        "balances": {
            "treasury_cash": round(state.treasury_cash, 1),
            "national_debt": round(state.national_debt, 1),
            "national_debt_rate": round(state.national_debt_rate * 100, 2),
            "bank_loans": round(state.bank_loans, 1),
            "bank_deposits": round(state.bank_deposits, 1),
            "bank_capital": round(state.bank_capital, 1),
            "bad_debt_rate": round(state.bad_debt_rate * 100, 2),
            "deposit_rate": round(state.deposit_interest_rate * 100, 2),
            "loan_rate": round(state.loan_interest_rate * 100, 2),
            "bank_reserve_cash": round(state.bank_reserve_cash, 1),
            "loan_to_deposit_ratio": round(state.loan_to_deposit_ratio, 1),
            "capital_adequacy_ratio": round(state.capital_adequacy_ratio, 1),
            "corporate_cash": round(state.corporate_cash, 1),
            "corporate_debt": round(state.corporate_debt, 1),
            "corporate_capacity": round(state.corporate_capacity, 1),
            "capacity_utilization": round(state.capacity_utilization_rate, 1),
            "firm_profit": round(state.firm_daily_profit, 2)
        },
        "levers": {
            "base_interest_rate": round(state.base_interest_rate, 4),
            "reserve_ratio": round(state.reserve_ratio, 4),
            "corp_tax_rate": round(state.corp_tax_rate, 4),
            "vat_tax_rate": round(state.vat_tax_rate, 4),
            "income_tax_rate": round(state.income_tax_rate, 4),
            "gov_daily_spending": round(state.gov_daily_spending, 2),
            "welfare_spending": round(state.welfare_spending, 2),
            "min_wage_daily": round(state.min_wage_daily, 1),
            "retirement_age": getattr(state, "retirement_age", 60),
            "fx_sterilization_ratio": round(getattr(state, "fx_sterilization_ratio", 0.0), 2)
        },
        "demographics": {
            "total_population": state.total_population,
            "child_population": getattr(state, "child_population", 1_800_000),
            "child_ratio": round(getattr(state, "child_population", 1_800_000) / max(1, state.total_population) * 100.0, 1),
            "working_population": getattr(state, "working_population", 6_500_000),
            "working_ratio": round(getattr(state, "working_population", 6_500_000) / max(1, state.total_population) * 100.0, 1),
            "retired_population": getattr(state, "retired_population", 1_700_000),
            "retired_ratio": round(getattr(state, "retired_population", 1_700_000) / max(1, state.total_population) * 100.0, 1),
            "retirement_age": getattr(state, "retirement_age", 60),
            "fertility_rate": round(getattr(state, "fertility_rate", 1.65), 2),
            "elderly_dependency_ratio": round(getattr(state, "elderly_dependency_ratio", 26.2), 1),
            "total_dependency_ratio": round(getattr(state, "total_dependency_ratio", 53.8), 1),
            "birth_rate_annual": round(getattr(state, "birth_rate_annual", 10.8), 1),
            "death_rate_annual": round(getattr(state, "death_rate_annual", 7.2), 1),
            "child_survival_rate": round(getattr(state, "child_survival_rate", 0.965) * 100.0, 1),
            "infant_mortality_rate": round(getattr(state, "infant_mortality_rate", 35.0), 1)
        },
        "micro": {
            "food_basket_price": round(state.food_basket_price, 2),
            "cpi_index": round(state.cpi_index, 1),
            "loan_cost_per_10k_month": round(state.loan_cost_per_10k_month, 1),
            "deposit_yield_per_10k_year": round(state.deposit_yield_per_10k_year, 1)
        },
        "personas": {
            "worker": state.persona_worker,
            "middle": state.persona_middle,
            "boss": state.persona_boss,
            "employers": getattr(state, "employers_ledger", {}),
            "citizens": getattr(state, "citizens_ledger", {})
        },
        "social": {
            "medicare_rate": round(state.medicare_reimburse_rate * 100, 1),
            "contrib_rate": round(state.social_contrib_rate * 100, 1),
            "fund_pool": round(state.social_fund_pool, 1),
            "daily_revenue": round(state.social_daily_revenue, 4),
            "daily_payout": round(state.social_daily_payout, 4),
            "daily_balance": round(state.social_daily_balance, 4),
            "daily_gov_subsidy": round(state.social_daily_gov_subsidy, 4)
        },
        "infra": {
            "daily_spending": round(state.infra_daily_spending, 4),
            "maintenance_spending": round(state.infra_maintenance_spending, 4),
            "research_capability": round(state.research_capability, 1),
            "school_count": state.school_count,
            "max_research_success_rate": 30.0,
            "active_research_grant": state.active_research_grant,
            "active_projects": [
                {
                    "template_id": p.template_id,
                    "name": p.name,
                    "category": p.category,
                    "category_name": p.category_name,
                    "total_cost": p.total_cost,
                    "cost_per_day": round(p.cost_per_day, 4),
                    "daily_maintenance_cost": round(p.daily_maintenance_cost, 4),
                    "duration_quarters": p.duration_quarters,
                    "quarters_elapsed": p.quarters_elapsed,
                    "days_elapsed": p.days_elapsed,
                    "progress_pct": round(min(100.0, (p.days_elapsed / (p.duration_quarters * 90)) * 100.0), 1),
                    "funds_spent": round(p.funds_spent, 2),
                    "status_text": p.status_text,
                    "success_rate": round(p.success_rate * 100, 1),
                    "attempt": p.attempt,
                    "returns_desc": p.returns_desc,
                    "materials_required_daily": getattr(p, "materials_required_daily", {}),
                    "materials_shortage": getattr(p, "materials_shortage", False)
                }
                for p in infra_manager.active_projects.values()
            ] if infra_manager else [],
            "templates": [
                {
                    "id": t.id,
                    "name": t.name,
                    "category": t.category,
                    "category_name": t.category_name,
                    "total_cost": t.total_cost,
                    "cost_per_quarter": t.cost_per_quarter,
                    "cost_per_day": t.cost_per_day,
                    "daily_maintenance_cost": round(t.daily_maintenance_cost, 4),
                    "duration_quarters": t.duration_quarters,
                    "ramp_up_quarters": t.ramp_up_quarters,
                    "schools_granted": t.schools_granted,
                    "research_boost": t.research_boost,
                    "base_success_rate": round(t.base_success_rate * 100, 1),
                    "success_rate": round(
                        (compute_research_success_rate(t.base_success_rate, state.research_capability, t.experience_bonus) * 100)
                        if t.category == "science" else 100.0, 1
                    ),
                    "attempt": t.attempt,
                    "failed_attempts": t.failed_attempts,
                    "experience_bonus": round(t.experience_bonus * 100, 1),
                    "intro": t.intro,
                    "returns_desc": t.returns_desc,
                    "materials_required_daily": getattr(t, "materials_required_daily", {}),
                    "is_active": t.id in infra_manager.active_projects if infra_manager else False,
                    "is_completed": any(c["template_id"] == t.id for c in infra_manager.completed_projects) if infra_manager else False
                }
                for t in (infra_manager.templates.values() if infra_manager else [])
            ],
            "completed_projects": infra_manager.completed_projects if infra_manager else [],
            "failed_projects": infra_manager.failed_projects if infra_manager else []
        },
        "resources": state.resources,
        "commodities": state.commodities,
        "market_clearing_summary": getattr(state, "market_clearing_summary", {}),
        "factories": state.factories,
        "labor_market": state.labor_market,
        "foreign_exchange": {
            "reserves_usd": round(state.foreign_reserves_usd, 2),
            "exchange_rate": round(state.exchange_rate, 2),
            "reserves_cny_equivalent": round(state.foreign_reserves_usd * state.exchange_rate, 2),
            "exchange_rate_baseline": round(getattr(state, "exchange_rate_baseline", 7.20), 2),
            "bop_current_account_usd": round(getattr(state, "bop_current_account_usd", 0.0), 3),
            "bop_exports_usd": round(getattr(state, "bop_exports_usd", 0.0), 3),
            "bop_imports_usd": round(getattr(state, "bop_imports_usd", 0.0), 3),
            "bop_trade_surplus_cny": round(getattr(state, "bop_trade_surplus_cny", 0.0), 3),
            "fx_sterilization_ratio": round(getattr(state, "fx_sterilization_ratio", 0.0), 2),
            "sovereign_wealth_fund_usd": round(getattr(state, "sovereign_wealth_fund_usd", 0.0), 2),
            "swf_daily_yield_usd": round(getattr(state, "swf_daily_yield_usd", 0.0), 4),
            "manufacturing_competitiveness_index": round(getattr(state, "manufacturing_competitiveness_index", 100.0), 1),
            "dutch_disease_active": getattr(state, "dutch_disease_active", False),
            "anti_dumping_tariffs": {k: round(v, 2) for k, v in getattr(state, "anti_dumping_tariffs", {}).items()},
            "commodity_export_quotas": getattr(state, "commodity_export_quotas", {})
        },
        "theories": state.active_theory_insights,
        "citizen_voices": state.citizen_voices,
        "households": households_data,
        "daily_flows": flows_data,
        "quarterly_flow_summary": {k: round(v, 2) for k, v in state.quarterly_flow_summary.items()},
        "cards": cards_data,
        "active_card_ids": card_manager.active_card_ids,
        "history": state.quarterly_history,
        "consumption_pyramid": {
            "housing_stock_sqm": round(getattr(state, "housing_stock_sqm", 32000.0), 1),
            "housing_avg_price": round(getattr(state, "housing_avg_price", 5200.0), 1),
            "daily_housing_sales_sqm": round(getattr(state, "daily_housing_sales_sqm", 0.0), 2),
            "daily_housing_starts_sqm": round(getattr(state, "daily_housing_starts_sqm", 0.0), 2),
            "daily_housing_sales_yuan": round(getattr(state, "daily_housing_sales_yuan", 0.0), 4),
            "daily_housing_downpayment": round(getattr(state, "daily_housing_downpayment", 0.0), 4),
            "daily_mortgage_issued": round(getattr(state, "daily_mortgage_issued", 0.0), 4),
            "household_mortgage_debt": round(getattr(state, "household_mortgage_debt", 1600.0), 1),
            "daily_mortgage_repay_total": round(getattr(state, "daily_mortgage_repay_total", 0.0), 4),
            "daily_durable_spending": round(getattr(state, "daily_durable_spending", 0.0), 4),
            "daily_service_spending": round(getattr(state, "daily_service_spending", 0.0), 4),
            "mortgage_burden_index": round(getattr(state, "mortgage_burden_index", 32.5), 1),
            "durable_penetration_rate": round(getattr(state, "durable_penetration_rate", 68.0), 1),
            "engel_coefficient": round(state.engel_coefficient * 100.0, 1)
        },
        "credit_cycle": {
            "capital_adequacy_ratio": round(getattr(state, "capital_adequacy_ratio", 10.0), 2),
            "risk_weighted_assets": round(getattr(state, "risk_weighted_assets", 2200.0), 2),
            "credit_crunch_active": getattr(state, "credit_crunch_active", False),
            "bank_npl_loans": round(getattr(state, "bank_npl_loans", 135.0), 2),
            "bank_npl_ratio": round(getattr(state, "bank_npl_ratio", 4.5), 2),
            "bank_provisions_pool": round(getattr(state, "bank_provisions_pool", 200.0), 2),
            "bank_provision_coverage": round(getattr(state, "bank_provision_coverage", 148.0), 1),
            "daily_bank_loan_interest_rev": round(getattr(state, "daily_bank_loan_interest_rev", 0.0), 4),
            "daily_bank_deposit_interest_cost": round(getattr(state, "daily_bank_deposit_interest_cost", 0.0), 4),
            "daily_bank_net_interest_margin": round(getattr(state, "daily_bank_net_interest_margin", 0.0), 4),
            "daily_bank_provision_deduction": round(getattr(state, "daily_bank_provision_deduction", 0.0), 4),
            "daily_bank_write_offs": round(getattr(state, "daily_bank_write_offs", 0.0), 4),
            "daily_corporate_loans_issued": round(getattr(state, "daily_corporate_loans_issued", 0.0), 4),
            "daily_corporate_loans_repaid": round(getattr(state, "daily_corporate_loans_repaid", 0.0), 4),
            "daily_loans_recalled": round(getattr(state, "daily_loans_recalled", 0.0), 4),
            "corporate_ratings": list(state.corporate_credit_ratings.values()) if isinstance(getattr(state, "corporate_credit_ratings", []), dict) else list(getattr(state, "corporate_credit_ratings", []) or [])
        },
        "audit": {
            "is_balanced": getattr(audit, "is_balanced", True) if audit else True,
            "flow_discrepancy": round(getattr(audit, "flow_discrepancy", 0.0), 6) if audit else 0.0,
            "m2_discrepancy": round(getattr(audit, "m2_discrepancy", 0.0), 6) if audit else 0.0,
            "m2_start": round(getattr(audit, "m2_start_of_day", 0.0), 2) if audit else round(state.bank_deposits, 2),
            "m2_end": round(getattr(audit, "m2_end_of_day", 0.0), 2) if audit else round(state.bank_deposits, 2),
            "m2_delta": round(getattr(audit, "m2_actual_delta", 0.0), 4) if audit else 0.0,
            "messages": getattr(audit, "audit_messages", []) if audit else ["✅ 宏观资金借贷严格零和守恒 (SFC)，分文不差。"]
        },
        "events": events or []
    }
