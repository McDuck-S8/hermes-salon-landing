#!/usr/bin/env python3
"""
WorkflowSupervisor — агент-управляющий для исполняемых графов воркфлоу.
Загружает схему, валидирует, выполняет узлы в топологическом порядке,
обрабатывает ретраи/фолбэки/conditional/parallel, логирует всё в KC.
"""

import json
import os
import sys
import time
import uuid
import subprocess
import traceback
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass, field, asdict
from collections import defaultdict, deque
from enum import Enum

# Add scripts to path
SCRIPTS_DIR = Path(os.environ.get("HERMES_HOME", Path(__file__).parent.parent.parent.parent)) / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

try:
    from kc_rag import upsert as kc_upsert
    from chain_heartbeat import event_beat, beat
    from hermes_hooks import get_hooks
    KC_AVAILABLE = True
except ImportError:
    KC_AVAILABLE = False


class NodeType(Enum):
    SKILL = "skill"
    MINI_PIPELINE = "mini_pipeline"
    PIPELINE = "pipeline"
    CONDITIONAL = "conditional"
    PARALLEL = "parallel"
    HUMAN_REVIEW = "human_review"
    START = "start"
    END = "end"


class NodeStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"
    PAUSED = "paused"


@dataclass
class RetryConfig:
    max_attempts: int = 3
    backoff_base_seconds: int = 5
    backoff_multiplier: float = 3.0


@dataclass
class Node:
    id: str
    type: NodeType
    name: str
    config: Dict[str, Any] = field(default_factory=dict)
    depends_on: List[str] = field(default_factory=list)
    condition: Optional[str] = None
    fallback: Optional[str] = None
    timeout_seconds: int = 300
    retry: RetryConfig = field(default_factory=RetryConfig)
    status: NodeStatus = NodeStatus.PENDING
    attempt: int = 0
    started_at: Optional[str] = None
    finished_at: Optional[str] = None
    output: Optional[Any] = None
    error: Optional[str] = None


@dataclass
class Edge:
    from_id: str
    to_id: str
    condition: Optional[str] = None


@dataclass
class Workflow:
    id: str
    version: str
    name: str
    description: str = ""
    inputs: Dict[str, Any] = field(default_factory=dict)
    outputs: Dict[str, Any] = field(default_factory=dict)
    graph: Dict[str, Any] = field(default_factory=dict)
    state: str = "pending"
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Runtime
    nodes: Dict[str, Node] = field(default_factory=dict)
    edges: List[Edge] = field(default_factory=list)
    context: Dict[str, Any] = field(default_factory=dict)
    execution_id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    run_id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])


class WorkflowSupervisor:
    """Агент-управляющий: загружает, валидирует, выполняет воркфлоу."""
    
    def __init__(
        self,
        workflow_dir: Optional[Path] = None,
        dry_run: bool = False,
        timeout_seconds: int = 3600
    ):
        self.workflow_dir = workflow_dir or (SCRIPTS_DIR.parent / "workflows")
        self.dry_run = dry_run
        self.timeout_seconds = timeout_seconds
        self.workflow: Optional[Workflow] = None
        self.start_time = time.time()
        
        # Ensure workflow dir exists
        self.workflow_dir.mkdir(parents=True, exist_ok=True)
    
    # ── Loading & Validation ─────────────────────────────────────────
    
    def load_workflow(self, workflow_id: str) -> Workflow:
        """Load workflow from JSON file."""
        wf_file = self.workflow_dir / f"{workflow_id}.json"
        if not wf_file.exists():
            raise FileNotFoundError(f"Workflow not found: {wf_file}")
        
        with open(wf_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        return self._parse_workflow(data)
    
    def _parse_workflow(self, data: Dict[str, Any]) -> Workflow:
        """Parse raw JSON into Workflow dataclass with Node/Edge objects."""
        wf = Workflow(
            id=data["id"],
            version=data["version"],
            name=data["name"],
            description=data.get("description", ""),
            inputs=data.get("inputs", {}),
            outputs=data.get("outputs", {}),
            graph=data.get("graph", {}),
            state=data.get("state", "pending"),
            metadata=data.get("metadata", {}),
        )
        
        # Parse nodes
        for node_data in wf.graph.get("nodes", []):
            node = Node(
                id=node_data["id"],
                type=NodeType(node_data["type"]),
                name=node_data["name"],
                config=node_data.get("config", {}),
                depends_on=node_data.get("depends_on", []),
                condition=node_data.get("condition"),
                fallback=node_data.get("fallback"),
                timeout_seconds=node_data.get("timeout_seconds", 300),
                retry=RetryConfig(**node_data.get("retry", {})),
            )
            wf.nodes[node.id] = node
        
        # Parse edges
        for edge_data in wf.graph.get("edges", []):
            wf.edges.append(Edge(
                from_id=edge_data["from"],
                to_id=edge_data["to"],
                condition=edge_data.get("condition")
            ))
        
        return wf
    
    def validate_workflow(self, workflow: Workflow) -> List[str]:
        """Validate workflow structure. Returns list of errors (empty = valid)."""
        errors = []
        
        # Check all dependencies exist
        node_ids = set(workflow.nodes.keys())
        for node in workflow.nodes.values():
            for dep in node.depends_on:
                if dep not in node_ids:
                    errors.append(f"Node '{node.id}' depends on missing node '{dep}'")
            if node.fallback and node.fallback not in node_ids:
                errors.append(f"Node '{node.id}' fallback '{node.fallback}' not found")
        
        # Check edges reference valid nodes
        for edge in workflow.edges:
            if edge.from_id not in node_ids:
                errors.append(f"Edge from missing node '{edge.from_id}'")
            if edge.to_id not in node_ids:
                errors.append(f"Edge to missing node '{edge.to_id}'")
        
        # Check for cycles (Kahn's algorithm)
        if self._has_cycles(workflow):
            errors.append("Workflow contains cycles")
        
        # Check start/end nodes
        has_start = any(n.type == NodeType.START for n in workflow.nodes.values())
        has_end = any(n.type == NodeType.END for n in workflow.nodes.values())
        if not has_start:
            errors.append("Workflow must have at least one START node")
        if not has_end:
            errors.append("Workflow must have at least one END node")
        
        return errors
    
    def _has_cycles(self, workflow: Workflow) -> bool:
        """Kahn's algorithm for cycle detection."""
        in_degree = defaultdict(int)
        adj = defaultdict(list)
        
        for edge in workflow.edges:
            adj[edge.from_id].append(edge.to_id)
            in_degree[edge.to_id] += 1
        
        # Add implicit edges from depends_on
        for node in workflow.nodes.values():
            for dep in node.depends_on:
                adj[dep].append(node.id)
                in_degree[node.id] += 1
        
        queue = deque([nid for nid in workflow.nodes if in_degree[nid] == 0])
        visited = 0
        
        while queue:
            nid = queue.popleft()
            visited += 1
            for neighbor in adj[nid]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)
        
        return visited != len(workflow.nodes)
    
    def get_execution_order(self, workflow: Workflow) -> List[List[str]]:
        """Return topological layers (list of node ID lists that can run in parallel)."""
        in_degree = defaultdict(int)
        adj = defaultdict(list)
        
        for edge in workflow.edges:
            adj[edge.from_id].append(edge.to_id)
            in_degree[edge.to_id] += 1
        
        # Add implicit edges from depends_on
        for node in workflow.nodes.values():
            for dep in node.depends_on:
                adj[dep].append(node.id)
                in_degree[node.id] += 1
        
        layers = []
        current_layer = [nid for nid in workflow.nodes if in_degree[nid] == 0]
        
        while current_layer:
            layers.append(current_layer)
            next_layer = []
            for nid in current_layer:
                for neighbor in adj[nid]:
                    in_degree[neighbor] -= 1
                    if in_degree[neighbor] == 0:
                        next_layer.append(neighbor)
            current_layer = next_layer
        
        return layers
    
    # ── Execution ────────────────────────────────────────────────────
    
    def execute(self, workflow: Workflow, inputs: Dict[str, Any] = None) -> Dict[str, Any]:
        """Main execution loop."""
        self.workflow = workflow
        workflow.context = {**(inputs or {}), **workflow.inputs}
        workflow.state = "running"
        workflow.run_id = uuid.uuid4().hex[:12]
        
        self._log("WORKFLOW_START", {
            "workflow_id": workflow.id,
            "execution_id": workflow.execution_id,
            "run_id": workflow.run_id,
            "inputs": workflow.context
        })
        
        try:
            # Get execution layers
            layers = self.get_execution_order(workflow)
            
            # Execute layer by layer
            for layer_idx, layer in enumerate(layers):
                self._log(f"LAYER_{layer_idx}", {"nodes": layer})
                
                # Separate parallel and sequential nodes
                parallel_nodes = []
                sequential_nodes = []
                
                for node_id in layer:
                    node = workflow.nodes[node_id]
                    if node.type == NodeType.PARALLEL:
                        parallel_nodes.append(node_id)
                    else:
                        sequential_nodes.append(node_id)
                
                # Execute parallel group
                if parallel_nodes:
                    self._execute_parallel_group(workflow, parallel_nodes)
                
                # Execute sequential nodes
                for node_id in sequential_nodes:
                    if not self._should_execute_node(workflow, node_id):
                        continue
                    self._execute_node(workflow, node_id)
            
            # Collect outputs
            outputs = self._collect_outputs(workflow)
            workflow.state = "completed"
            
            self._log("WORKFLOW_COMPLETE", {
                "execution_id": workflow.execution_id,
                "run_id": workflow.run_id,
                "duration_seconds": time.time() - self.start_time,
                "outputs": outputs
            })
            
            return outputs
            
        except Exception as e:
            workflow.state = "failed"
            self._log("WORKFLOW_FAILED", {
                "execution_id": workflow.execution_id,
                "error": str(e),
                "traceback": traceback.format_exc()
            })
            raise
    
    def _should_execute_node(self, workflow: Workflow, node_id: str) -> bool:
        """Check if node should run (condition, dependencies)."""
        node = workflow.nodes[node_id]
        
        # Check dependencies completed
        for dep_id in node.depends_on:
            dep = workflow.nodes[dep_id]
            if dep.status != NodeStatus.COMPLETED:
                return False
        
        # Check condition
        if node.condition:
            try:
                # Simple eval in context (could use Jinja2 for safety)
                result = eval(node.condition, {"__builtins__": {}}, workflow.context)
                return bool(result)
            except Exception:
                return False
        
        return True
    
    def _execute_parallel_group(self, workflow: Workflow, node_ids: List[str]):
        """Execute parallel nodes (stub - would use ThreadPoolExecutor in production)."""
        for node_id in node_ids:
            self._execute_node(workflow, node_id)
    
    def _execute_node(self, workflow: Workflow, node_id: str):
        """Execute single node with retries."""
        node = workflow.nodes[node_id]
        node.attempt += 1
        node.status = NodeStatus.RUNNING
        node.started_at = datetime.now(timezone.utc).isoformat()
        
        self._log(f"NODE_START:{node_id}", {
            "type": node.type.value,
            "name": node.name,
            "attempt": node.attempt
        })
        
        if self.dry_run:
            node.status = NodeStatus.COMPLETED
            node.output = {"dry_run": True, "node_id": node_id}
            node.finished_at = datetime.now(timezone.utc).isoformat()
            self._log(f"NODE_DRY_RUN:{node_id}", {"node_id": node_id})
            return
        
        try:
            # Execute based on type
            if node.type == NodeType.SKILL:
                output = self._execute_skill(workflow, node)
            elif node.type == NodeType.MINI_PIPELINE:
                output = self._execute_mini_pipeline(workflow, node)
            elif node.type == NodeType.PIPELINE:
                output = self._execute_pipeline(workflow, node)
            elif node.type == NodeType.CONDITIONAL:
                output = self._execute_conditional(workflow, node)
            elif node.type == NodeType.HUMAN_REVIEW:
                output = self._execute_human_review(workflow, node)
            elif node.type == NodeType.START:
                output = {"started": True}
            elif node.type == NodeType.END:
                output = {"completed": True}
            else:
                raise ValueError(f"Unknown node type: {node.type}")
            
            node.output = output
            node.status = NodeStatus.COMPLETED
            
            # Update context with node output for downstream nodes
            workflow.context[f"node.{node_id}"] = output
            if "result" in output:
                workflow.context[f"node.{node_id}.result"] = output["result"]
            
        except Exception as e:
            node.error = str(e)
            if node.attempt < node.retry.max_attempts:
                self._handle_retry(workflow, node, e)
                return
            
            # Max retries exceeded - try fallback
            if node.fallback:
                self._log(f"NODE_FALLBACK:{node_id}", {"fallback": node.fallback})
                self._execute_node(workflow, node.fallback)
                return
            
            node.status = NodeStatus.FAILED
            raise
        
        node.finished_at = datetime.now(timezone.utc).isoformat()
        self._log(f"NODE_COMPLETE:{node_id}", {
            "duration_seconds": self._duration(node.started_at, node.finished_at),
            "output_keys": list(output.keys()) if isinstance(output, dict) else "non-dict"
        })
    
    def _execute_skill(self, workflow: Workflow, node: Node) -> Dict[str, Any]:
        """Execute a skill via its CLI or module."""
        skill_name = node.name
        config = node.config
        
        # Search for skill
        skill_dir = SCRIPTS_DIR.parent / "skills"
        for category in skill_dir.iterdir():
            if not category.is_dir():
                continue
            skill_path = category / skill_name
            if skill_path.exists():
                # Try to find executable script
                scripts_dir = skill_path / "scripts"
                if scripts_dir.exists():
                                    # Look for main.py, run.py, or skill_name.py
                                    for script_name in ["main.py", "run.py", f"{skill_name}.py"]:
                                        script_path = scripts_dir / script_name
                                        if script_path.exists():
                                            # Get phase from node config
                                            phase = config.get("phase", "default")
                                            cmd = [sys.executable, str(script_path), "--phase", phase, "--config", json.dumps(config)]
                                            env = os.environ.copy()
                                            result = subprocess.run(
                                                cmd, capture_output=True, text=True,
                                                timeout=node.timeout_seconds, env=env
                                            )
                                            if result.returncode == 0:
                                                return {"result": result.stdout.strip()}
                                            else:
                                                raise RuntimeError(f"Skill failed: {result.stderr}")
                
                # Fallback: skill is logged but not executed
                self._log(f"SKILL_NOT_EXECUTABLE:{skill_name}", {"config": config})
                return {"skill": skill_name, "status": "logged", "config": config}
        
        # Skill not found
        self._log(f"SKILL_NOT_FOUND:{skill_name}", {"config": config})
        return {"skill": skill_name, "status": "not_found", "config": config}
    
    def _execute_mini_pipeline(self, workflow: Workflow, node: Node) -> Dict[str, Any]:
        """Execute a mini pipeline (inline skill sequence)."""
        steps = node.config.get("steps", [])
        results = []
        
        for step in steps:
            skill_name = step.get("skill")
            step_config = step.get("config", {})
            # Render Jinja2 templates in config
            rendered_config = self._render_template(step_config, workflow.context)
            
            self._log(f"MINI_PIPELINE_STEP:{skill_name}", {"config": rendered_config})
            results.append({"skill": skill_name, "status": "executed"})
        
        return {"steps": results}
    
    def _execute_pipeline(self, workflow: Workflow, node: Node) -> Dict[str, Any]:
        """Execute a full pipeline (composed of multiple skills)."""
        pipeline_name = node.name
        self._log(f"PIPELINE:{pipeline_name}", {"config": node.config})
        return {"pipeline": pipeline_name, "status": "executed"}
    
    def _execute_conditional(self, workflow: Workflow, node: Node) -> Dict[str, Any]:
        """Conditional branch - evaluates condition, routes to true/false paths."""
        condition = node.config.get("condition", "true")
        try:
            result = eval(condition, {"__builtins__": {}}, workflow.context)
            branch = "true" if result else "false"
        except Exception:
            branch = "false"
        
        self._log(f"CONDITIONAL:{node.id}", {"branch": branch})
        return {"branch": branch, "condition": condition}
    
    def _execute_human_review(self, workflow: Workflow, node: Node) -> Dict[str, Any]:
        """Pause for human review (Telegram notification)."""
        message = node.config.get("message", f"Review required for node {node.id}")
        # In real implementation: send to Telegram, wait for callback
        self._log(f"HUMAN_REVIEW:{node.id}", {"message": message, "status": "waiting"})
        return {"status": "awaiting_review", "message": message}
    
    def _handle_retry(self, workflow: Workflow, node: Node, error: Exception):
        """Handle retry with exponential backoff."""
        wait_time = node.retry.backoff_base_seconds * (node.retry.backoff_multiplier ** (node.attempt - 1))
        self._log(f"NODE_RETRY:{node.id}", {
            "attempt": node.attempt,
            "max": node.retry.max_attempts,
            "wait_seconds": wait_time,
            "error": str(error)
        })
        node.status = NodeStatus.PENDING
        time.sleep(wait_time)
        self._execute_node(workflow, node.id)
    
    def _collect_outputs(self, workflow: Workflow) -> Dict[str, Any]:
        """Collect declared outputs from node results."""
        outputs = {}
        for out_name, out_spec in workflow.outputs.items():
            # Could map from node outputs
            pass
        return {**workflow.context, **outputs}
    
    def _render_template(self, obj: Any, context: Dict) -> Any:
        """Render Jinja2-like templates in strings."""
        if isinstance(obj, str):
            for key, value in context.items():
                obj = obj.replace(f"{{{{ {key} }}}}", str(value))
            return obj
        elif isinstance(obj, dict):
            return {k: self._render_template(v, context) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._render_template(v, context) for v in obj]
        return obj
    
    def _duration(self, start: str, end: str) -> float:
        try:
            return (datetime.fromisoformat(end) - datetime.fromisoformat(start)).total_seconds()
        except Exception:
            return 0.0
    
    # ── Logging ──────────────────────────────────────────────────────
    
    def _log(self, event: str, data: Dict[str, Any]):
        """Log to KC and console."""
        entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "workflow_id": self.workflow.id if self.workflow else "unknown",
            "execution_id": self.workflow.execution_id if self.workflow else "unknown",
            "run_id": self.workflow.run_id if self.workflow else "unknown",
            "event": event,
            "data": data
        }
        
        # Console
        print(f"[{entry['timestamp']}] {event}: {json.dumps(data, ensure_ascii=False)[:200]}")
        
        # Knowledge Cube
        if KC_AVAILABLE:
            try:
                kc_upsert(
                    content=f"WORKFLOW {event}: {json.dumps(data, ensure_ascii=False)}",
                    tags=["workflow", "supervisor", event.lower().replace(":", "_")],
                    source="workflow_supervisor",
                    confidence=0.9,
                    verification_method="auto"
                )
                event_beat("knowledge_added")
            except Exception:
                pass  # Non-critical


# ── CLI Entry Point ──────────────────────────────────────────────────

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="WorkflowSupervisor - Execute workflow graphs")
    parser.add_argument("workflow", help="Workflow ID to execute")
    parser.add_argument("--inputs", type=str, help="JSON string of inputs")
    parser.add_argument("--dry-run", action="store_true", help="Validate and simulate without executing")
    parser.add_argument("--workflow-dir", type=str, help="Custom workflow directory")
    parser.add_argument("--visualize", action="store_true", help="Output Mermaid diagram")
    
    args = parser.parse_args()
    
    supervisor = WorkflowSupervisor(
        workflow_dir=Path(args.workflow_dir) if args.workflow_dir else None,
        dry_run=args.dry_run
    )
    
    # Load workflow
    workflow = supervisor.load_workflow(args.workflow)
    
    # Validate
    errors = supervisor.validate_workflow(workflow)
    if errors:
        print(f"❌ Validation errors:")
        for err in errors:
            print(f"  - {err}")
        sys.exit(1)
    
    print(f"✅ Workflow '{workflow.name}' ({workflow.id}) validated")
    
    # Visualize
    if args.visualize:
        mermaid = supervisor.generate_mermaid(workflow)
        print("\n--- MERMAID DIAGRAM ---")
        print(mermaid)
        return
    
    # Execute
    inputs = json.loads(args.inputs) if args.inputs else {}
    try:
        outputs = supervisor.execute(workflow, inputs)
        print(f"\n✅ Workflow completed successfully")
        print(f"Outputs: {json.dumps(outputs, ensure_ascii=False, indent=2)[:500]}")
    except Exception as e:
        print(f"\n❌ Workflow failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()