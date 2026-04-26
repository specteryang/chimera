#!/usr/bin/env python3
"""
Chimera v2 — Autonomous Earning System
All numbers are REAL. No simulation. No random profits.

Architecture:
  daemon.py       → Orchestrator: runs each agent, records real outcomes
  agents/         → Agent modules, each with execute() and measure()
  domains/        → Content output directories
  ledger.json     → Real financial tracking (NEVER fake)
  logs/           → Execution logs

Agents:
  1. seo_farm     → Generate & deploy SEO content pages → ad/affiliate revenue
  2. social_operator → Publish to Toutiao/Weibo/etc → platform earnings
  3. product_scout   → Create & list Gumroad digital products → sales revenue

Each agent cycle:
  1. execute() → Do real work (generate content, publish, list product)
  2. measure() → Check real metrics (views, sales, revenue)
  3. record()  → Log outcome to agent state + ledger

Revenue validation:
  - Only count money that can be verified via API or platform dashboard
  - If verification fails, record $0 and log the failure
  - Never extrapolate or estimate
"""

import json
import pathlib
import sys
import datetime
import importlib
import traceback

ROOT = pathlib.Path(__file__).parent
LOGS = ROOT / "logs"
AGENTS_DIR = ROOT / "agents_src"  # Python modules, not JSON configs

def load_ledger():
    p = ROOT / "ledger.json"
    if p.exists():
        return json.loads(p.read_text(encoding="utf-8"))
    return {
        "treasury_usd": 0.0,
        "total_revenue": 0.0,
        "total_costs": 0.0,
        "children_agents": [],
        "milestones": [],
        "last_cycle": None,
        "created": datetime.datetime.utcnow().isoformat(),
        "version": 2,
    }

def save_ledger(ledger):
    p = ROOT / "ledger.json"
    p.write_text(json.dumps(ledger, indent=2, ensure_ascii=False), encoding="utf-8")

def log(msg, level="INFO"):
    LOGS.mkdir(exist_ok=True)
    ts = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] [{level}] {msg}"
    print(line)
    # Append to daily log
    log_file = LOGS / f"{datetime.datetime.utcnow().strftime('%Y-%m-%d')}.log"
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(line + "\n")

def load_agent_state(name):
    """Load agent state from agents/<name>.json"""
    p = ROOT / "agents" / f"{name}.json"
    if p.exists():
        return json.loads(p.read_text(encoding="utf-8"))
    return {
        "name": name,
        "status": "initialized",
        "total_revenue": 0.0,
        "last_execute": None,
        "last_measure": None,
        "history": [],
        "errors": [],
    }

def save_agent_state(name, state):
    p = ROOT / "agents" / f"{name}.json"
    p.parent.mkdir(exist_ok=True)
    p.write_text(json.dumps(state, indent=2, ensure_ascii=False), encoding="utf-8")

def run_agent(name):
    """Execute a single agent: load state → execute → measure → save"""
    log(f"Starting agent: {name}")
    state = load_agent_state(name)
    
    try:
        # Import agent module
        # agents are in agents_src/<name>.py
        sys.path.insert(0, str(AGENTS_DIR))
        module = importlib.import_module(name)
        
        # Execute
        exec_result = module.execute(state)
        state["last_execute"] = datetime.datetime.utcnow().isoformat()
        state["status"] = exec_result.get("status", "completed")
        log(f"  {name} execute: {exec_result.get('summary', 'ok')}")
        
        # Measure
        measure_result = module.measure(state)
        state["last_measure"] = datetime.datetime.utcnow().isoformat()
        revenue = measure_result.get("revenue", 0.0)
        metrics = measure_result.get("metrics", {})
        log(f"  {name} measure: revenue=${revenue:.4f}, metrics={metrics}")
        
        # Record
        state["total_revenue"] += revenue
        state["history"].append({
            "timestamp": datetime.datetime.utcnow().isoformat(),
            "execute_summary": exec_result.get("summary", ""),
            "revenue": revenue,
            "metrics": metrics,
        })
        # Keep last 100 entries
        state["history"] = state["history"][-100:]
        
        return revenue, exec_result, measure_result
        
    except Exception as e:
        log(f"  {name} ERROR: {e}", level="ERROR")
        log(traceback.format_exc(), level="ERROR")
        state["status"] = "error"
        state["errors"].append({
            "timestamp": datetime.datetime.utcnow().isoformat(),
            "error": str(e),
        })
        state["errors"] = state["errors"][-20:]
        return 0.0, {"status": "error", "summary": str(e)}, {}
    
    finally:
        save_agent_state(name, state)

def cycle():
    """Run one full cycle: execute all agents, update ledger"""
    ledger = load_ledger()
    cycle_revenue = 0.0
    cycle_costs = 0.0
    results = {}
    
    for agent_name in ledger.get("children_agents", []):
        revenue, exec_result, measure_result = run_agent(agent_name)
        cycle_revenue += revenue
        results[agent_name] = {
            "revenue": revenue,
            "execute": exec_result.get("summary", ""),
            "metrics": measure_result.get("metrics", {}),
        }
    
    # Update ledger
    ledger["treasury_usd"] += cycle_revenue - cycle_costs
    ledger["total_revenue"] += cycle_revenue
    ledger["total_costs"] += cycle_costs
    ledger["last_cycle"] = datetime.datetime.utcnow().isoformat()
    
    # Milestone check
    for milestone_val in [10, 100, 500, 1000, 5000, 10000, 100000, 1000000]:
        key = f"milestone_{milestone_val}"
        if ledger["total_revenue"] >= milestone_val and key not in [m.get("name") for m in ledger.get("milestones", [])]:
            ledger.setdefault("milestones", []).append({
                "name": key,
                "achieved_at": datetime.datetime.utcnow().isoformat(),
                "total_revenue": ledger["total_revenue"],
            })
            log(f"🎉 MILESTONE: ${milestone_val} total revenue reached!")
    
    save_ledger(ledger)
    
    log(f"Cycle complete: revenue=${cycle_revenue:.4f} | total=${ledger['total_revenue']:.4f}")
    return ledger, results

if __name__ == "__main__":
    log("Chimera v2 daemon starting...")
    cycle()
    log("Chimera v2 daemon cycle complete.")
