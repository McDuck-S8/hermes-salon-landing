#!/usr/bin/env python3
"""Hermes Agent Architecture — матрёшка: System → Pipelines → Components"""
import os, sys
os.environ["PATH"] += os.pathsep + r"D:\Program Files\Graphviz\bin"

from diagrams import Diagram, Cluster, Edge
from diagrams.onprem.client import User, Client
from diagrams.onprem.queue import Kafka
from diagrams.onprem.database import Postgresql
from diagrams.onprem.monitoring import Grafana, Prometheus
from diagrams.onprem.analytics import Spark
from diagrams.onprem.workflow import Airflow
from diagrams.onprem.compute import Server
from diagrams.onprem.network import Nginx
from diagrams.programming.language import Python, Go, Bash, NodeJS, Rust, Sql, TypeScript
from diagrams.generic.blank import Blank
from diagrams.generic.device import Mobile
from diagrams.generic.database import SQL

OUT = os.path.join(os.path.dirname(__file__), "..", "docs", "hermes_arch")

# ──────────────────────────────────────────────────────
# Level 1: System Context
# ──────────────────────────────────────────────────────
def level1_system_context():
    graph_attr = {
        "label": "Level 1: System Context",
        "labelloc": "t",
        "fontsize": "24",
        "pad": "0.5",
    }
    with Diagram(
        "Hermes Agent — System Context",
        show=False,
        direction="LR",
        filename=f"{OUT}_01_system_context",
        outformat="png",
        graph_attr=graph_attr,
    ):
        with Cluster("External World"):
            user = User("User\n(commands)")
            telegram = Client("Telegram")
            github = Server("GitHub")
            cpa = Server("CPA Networks\n1xBet, 1win")
            browseros = Server("BrowserOS\nAnti-detect")
            feeds = Blank("RSS Feeds")
            youtube = Blank("YouTube\nChannels")
            llm = Rust("LLM APIs")

        hermes = Python("Hermes Agent")

        user >> Edge(color="cyan") >> hermes
        hermes >> Edge(color="cyan") >> user
        hermes >> Edge(color="green", label="deploy") >> github
        feeds >> Edge(color="orange", label="articles") >> hermes
        hermes >> Edge(color="blue", label="posts") >> telegram
        hermes >> Edge(color="red", label="register") >> cpa
        hermes >> Edge(color="purple", label="automate") >> browseros
        youtube >> Edge(color="yellow", label="transcripts") >> hermes
        hermes >> Edge(color="gray", label="API calls") >> llm

# ──────────────────────────────────────────────────────
# Level 2: Containers (Pipelines)
# ──────────────────────────────────────────────────────
def level2_pipelines():
    graph_attr = {
        "label": "Level 2: Pipelines (Containers)",
        "labelloc": "t",
        "fontsize": "24",
        "pad": "0.5",
        "splines": "ortho",
    }
    with Diagram(
        "Hermes Agent — Pipelines",
        show=False,
        direction="LR",
        filename=f"{OUT}_02_pipelines",
        outformat="png",
        graph_attr=graph_attr,
    ):
        # Row 1: Knowledge → Crystal
        with Cluster("Knowledge Pipeline"):
            rss = Blank("RSS Monitor")
            kc = Postgresql("Knowledge Cube")
            rss >> Edge(label="fetch") >> kc

        with Cluster("Crystal Pipeline"):
            obs = Grafana("Observe\n(KC gaps)")
            diag = Prometheus("Diagnose\n(failure patterns)")
            will = Airflow("Will\n(decide action)")
            rec = Postgresql("Record\n(KC write)")
            obs >> diag >> will >> rec

        # Row 2: Self-Improvement → Action
        with Cluster("Self-Improvement Pipeline"):
            hooks = Spark("Event Hooks")
            fixes = Blank("Verified Fixes")
            suggest = Airflow("Suggestions")
            skills = Go("Skill Factory")
            hooks >> fixes >> suggest >> skills

        with Cluster("Action Pipeline"):
            surfer = Blank("Ghost Surfer")
            browser = Server("BrowserOS\nAuto")
            reg = Blank("Registrations")
            post = Blank("Posting")
            surfer >> browser >> reg >> post

        # Heartbeat (vertical connector)
        with Cluster("Heartbeat Chain"):
            scanner = Prometheus("Signal Scanner")
            bus = Kafka("Event Bus")
            improve = Spark("Self Improvement")
            consumer = Airflow("Consumer")
            cruiser = Grafana("Crystal")
            scanner >> bus >> improve >> consumer >> cruiser

        # Cross-pipeline edges
        kc >> Edge(style="dashed", color="orange") >> obs
        skills >> Edge(style="dashed", color="green") >> surfer
        bus >> Edge(style="dashed", color="red") >> hooks
        rec >> Edge(style="dashed", color="purple") >> kc
        post >> Edge(style="dashed", color="blue", label="results") >> kc

# ──────────────────────────────────────────────────────
# Level 3: Core Components
# ──────────────────────────────────────────────────────
def level3_components():
    graph_attr = {
        "label": "Level 3: Core Components",
        "labelloc": "t",
        "fontsize": "24",
        "pad": "0.5",
        "splines": "ortho",
    }
    with Diagram(
        "Hermes Agent — Core Components",
        show=False,
        direction="TB",
        filename=f"{OUT}_03_components",
        outformat="png",
        graph_attr=graph_attr,
    ):
        with Cluster("Event Layer"):
            ev = Python("event_evolution.py")
            hk = Python("hermes_hooks.py")
            ev - Edge(style="dashed") >> hk

        with Cluster("Knowledge Layer"):
            rc = Python("auto_recall.py")
            kc = Postgresql("knowledge_cube.db")
            enr = Python("on_task_complete\n→ KC write")
            rc >> Edge(label="query") >> kc
            enr >> Edge(label="write") >> kc

        with Cluster("Agent Layer"):
            cron = Python("cron_manager.py")
            sk = Python("skill_manager\n_tool.py")
            mem = SQL("memories/")
            cron >> sk
            cron - Edge(style="dashed") >> mem

        with Cluster("Plugin / IO Layer"):
            ws = Python("plugins/\nweb_search/")
            bh = Go("Browser\nHarness")
            gw = Rust("Gateway\nService")
            tg = TypeScript("Telegram\nBridge")

        # Cross links
        hk >> Edge(color="red") >> rc
        sk >> enr
        mem >> kc

# ──────────────────────────────────────────────────────
# Level 4: File map (text-based, one combined diagram)
# ──────────────────────────────────────────────────────
def level4_file_map():
    """Level 4 is too granular for diagrams lib — emit as Mermaid text instead"""
    mermaid = """# Level 4: File Map (Hermes)
```mermaid
mindmap
  root((Hermes))
    ::id root
    scripts
      ::id scripts
      core_engine.py
      event_evolution.py
      hermes_hooks.py
      auto_recall.py
      autonomous_agent.py
      proactive_executor.py
      knowledge_cube.py
      cron_manager.py
      posting/
        ::id posting
        telegram_poster.py
        web_poster.py
      utilities/
    tools
      ::id tools
      skill_manager_tool.py
      approval_policies.py
    skills/
      ::id skills
      web-development/
      software-development/
      self-improvement/
      devops/
      creative/
      automation/
    cron/
      jobs.json
    plugins/
      web_search/
      self_evolution/
    config/
      config.yaml
    protocols/
      planning/
      review/
    docs/
      architecture/
```
"""
    return mermaid

if __name__ == "__main__":
    d = os.path.dirname(OUT)
    os.makedirs(d, exist_ok=True)
    
    print("Level 1: System Context...")
    level1_system_context()
    
    print("Level 2: Pipelines...")
    level2_pipelines()
    
    print("Level 3: Components...")
    level3_components()
    
    print(f"\nAll PNGs saved to {OUT}_*.png")
    print("\nLevel 4 (file map):")
    print(level4_file_map())
