"""
System Monitor & Auto-Healing Service
Autonomous system that monitors, reports, and fixes itself
"""

import traceback
import sys
import json
import time
import psutil
from datetime import datetime
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum
import threading
import logging


class ErrorSeverity(Enum):
    LOW = "low"           # Warning, can continue
    MEDIUM = "medium"     # Issue, needs attention
    HIGH = "high"         # Critical, auto-fix attempted
    CRITICAL = "critical" # System halt, manual intervention required


class SystemStatus(Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    ERROR = "error"
    RECOVERING = "recovering"
    HALTED = "halted"


@dataclass
class ErrorReport:
    error_id: str
    timestamp: str
    component: str
    severity: ErrorSeverity
    error_type: str
    message: str
    stack_trace: Optional[str]
    auto_fixed: bool = False
    fix_attempted: Optional[str] = None
    resolved: bool = False


@dataclass
class SystemMetric:
    cpu_percent: float
    memory_percent: float
    disk_percent: float
    api_response_time: float
    active_connections: int
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())


class SystemMonitor:
    """Autonomous system monitor with self-healing capabilities"""
    
    def __init__(self):
        self.status = SystemStatus.HEALTHY
        self.error_log: List[ErrorReport] = []
        self.metrics_history: List[SystemMetric] = []
        self.max_errors = 1000
        self.max_metrics = 500
        self.auto_heal_enabled = True
        self.components: Dict[str, Dict[str, Any]] = {}
        self.last_check = datetime.utcnow()
        self.alert_handlers: List[Callable] = []
        self._lock = threading.Lock()
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(sys.stdout),
                logging.FileHandler('/tmp/ai_earning_system.log')
            ]
        )
        self.logger = logging.getLogger('SystemMonitor')
        
    def register_component(self, name: str, health_check: Callable, heal_func: Optional[Callable] = None):
        """Register a component for monitoring"""
        self.components[name] = {
            "health_check": health_check,
            "heal_func": heal_func,
            "status": "unknown",
            "last_check": None,
            "errors": 0
        }
        self.logger.info(f"Registered component: {name}")
    
    def report_error(self, component: str, error: Exception, severity: ErrorSeverity = ErrorSeverity.MEDIUM) -> ErrorReport:
        """Report an error to the system monitor"""
        error_id = f"err_{int(time.time())}_{hash(str(error)) % 10000}"
        
        report = ErrorReport(
            error_id=error_id,
            timestamp=datetime.utcnow().isoformat(),
            component=component,
            severity=severity,
            error_type=type(error).__name__,
            message=str(error),
            stack_trace=traceback.format_exc() if severity in [ErrorSeverity.HIGH, ErrorSeverity.CRITICAL] else None
        )
        
        with self._lock:
            self.error_log.append(report)
            # Keep only recent errors
            if len(self.error_log) > self.max_errors:
                self.error_log = self.error_log[-self.max_errors:]
        
        self.logger.error(f"[{severity.value.upper()}] {component}: {error}")
        
        # Auto-heal if enabled and severity is high
        if self.auto_heal_enabled and severity in [ErrorSeverity.HIGH, ErrorSeverity.CRITICAL]:
            self._attempt_auto_heal(report)
        
        # Alert handlers
        for handler in self.alert_handlers:
            try:
                handler(report)
            except:
                pass
        
        return report
    
    def _attempt_auto_heal(self, report: ErrorReport):
        """Attempt to auto-heal the system"""
        component = report.component
        
        if component in self.components:
            comp_data = self.components[component]
            heal_func = comp_data.get("heal_func")
            
            if heal_func:
                try:
                    self.logger.info(f"Attempting auto-heal for {component}")
                    heal_func()
                    report.auto_fixed = True
                    report.fix_attempted = "auto_heal_success"
                    self.logger.info(f"Auto-heal successful for {component}")
                except Exception as e:
                    report.fix_attempted = f"auto_heal_failed: {str(e)}"
                    self.logger.error(f"Auto-heal failed for {component}: {e}")
    
    def check_all_components(self) -> Dict[str, str]:
        """Health check all registered components"""
        results = {}
        
        for name, data in self.components.items():
            try:
                health_check = data["health_check"]
                is_healthy = health_check()
                data["status"] = "healthy" if is_healthy else "unhealthy"
                data["last_check"] = datetime.utcnow().isoformat()
                results[name] = data["status"]
                
                if not is_healthy:
                    data["errors"] += 1
                    if data["errors"] > 3:
                        self.report_error(name, Exception(f"Component {name} unhealthy for {data['errors']} checks"), ErrorSeverity.HIGH)
                else:
                    data["errors"] = 0
                    
            except Exception as e:
                data["status"] = "error"
                data["errors"] += 1
                results[name] = "error"
                self.report_error(name, e, ErrorSeverity.MEDIUM)
        
        return results
    
    def collect_metrics(self) -> SystemMetric:
        """Collect system metrics"""
        try:
            metric = SystemMetric(
                cpu_percent=psutil.cpu_percent(interval=1),
                memory_percent=psutil.virtual_memory().percent,
                disk_percent=psutil.disk_usage('/').percent,
                api_response_time=0.0,  # Will be updated by API layer
                active_connections=0    # Will be updated by API layer
            )
            
            with self._lock:
                self.metrics_history.append(metric)
                if len(self.metrics_history) > self.max_metrics:
                    self.metrics_history = self.metrics_history[-self.max_metrics:]
            
            return metric
            
        except Exception as e:
            self.report_error("metrics_collector", e, ErrorSeverity.LOW)
            return SystemMetric(0, 0, 0, 0, 0)
    
    def get_dashboard_data(self) -> Dict[str, Any]:
        """Get data for system dashboard"""
        with self._lock:
            recent_errors = [e for e in self.error_log[-50:] if not e.resolved]
            recent_metrics = self.metrics_history[-24:]  # Last 24 data points
        
        return {
            "system_status": self.status.value,
            "total_errors": len(self.error_log),
            "unresolved_errors": len(recent_errors),
            "critical_errors": len([e for e in recent_errors if e.severity == ErrorSeverity.CRITICAL]),
            "high_errors": len([e for e in recent_errors if e.severity == ErrorSeverity.HIGH]),
            "components": {name: data["status"] for name, data in self.components.items()},
            "recent_errors": [
                {
                    "id": e.error_id,
                    "component": e.component,
                    "severity": e.severity.value,
                    "message": e.message[:100],
                    "timestamp": e.timestamp,
                    "auto_fixed": e.auto_fixed
                }
                for e in recent_errors[-10:]
            ],
            "metrics": {
                "cpu_avg": sum(m.cpu_percent for m in recent_metrics) / len(recent_metrics) if recent_metrics else 0,
                "memory_avg": sum(m.memory_percent for m in recent_metrics) / len(recent_metrics) if recent_metrics else 0,
                "latest": recent_metrics[-1].__dict__ if recent_metrics else None
            },
            "auto_heal_enabled": self.auto_heal_enabled,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def generate_system_report(self) -> str:
        """Generate comprehensive system report for cascade analysis"""
        data = self.get_dashboard_data()
        
        report = f"""
{'='*60}
AI EARNING SYSTEM - AUTONOMOUS REPORT
{'='*60}
Generated: {datetime.utcnow().isoformat()}
System Status: {data['system_status'].upper()}

COMPONENTS:
{'-'*40}
"""
        for comp, status in data['components'].items():
            emoji = "✅" if status == "healthy" else "⚠️" if status == "degraded" else "❌"
            report += f"  {emoji} {comp}: {status}\n"
        
        report += f"""
ERRORS (Last 10):
{'-'*40}
"""
        if data['recent_errors']:
            for err in data['recent_errors']:
                emoji = "🔴" if err['severity'] == 'critical' else "🟠" if err['severity'] == 'high' else "🟡"
                report += f"  {emoji} [{err['severity'].upper()}] {err['component']}: {err['message']}\n"
        else:
            report += "  ✅ No recent errors\n"
        
        report += f"""
METRICS:
{'-'*40}
  CPU: {data['metrics']['cpu_avg']:.1f}%
  Memory: {data['metrics']['memory_avg']:.1f}%
  Auto-Heal: {'ON ✅' if data['auto_heal_enabled'] else 'OFF ❌'}

{'='*60}
"""
        return report


# Global singleton
_monitor: Optional[SystemMonitor] = None

def get_system_monitor() -> SystemMonitor:
    """Get or create system monitor"""
    global _monitor
    if _monitor is None:
        _monitor = SystemMonitor()
    return _monitor
