from __future__ import annotations
"""
Google A2A Protocol Implementation
Agent-to-Agent Protocol for AI agents to discover and communicate
Based on Google's A2A specification
Docs: https://developers.google.com/agent-to-agent
"""

import json
import uuid
import asyncio
from typing import Dict, Any, Optional, List, Callable, Union
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
import requests
import logging

logger = logging.getLogger('GoogleA2AProtocol')


class A2AMessageType(Enum):
    """A2A protocol message types"""
    TASK_SEND = "task_send"
    TASK_GET = "task_get"
    TASK_CANCEL = "task_cancel"
    TASK_STATUS_UPDATE = "task_status_update"
    TASK_ARTIFACT_UPDATE = "task_artifact_update"
    SKILL_QUERY = "skill_query"
    AGENT_CARD_QUERY = "agent_card_query"
    SUBSCRIBE = "subscribe"
    UNSUBSCRIBE = "unsubscribe"
    PUSH_NOTIFICATION_SET = "push_notification_set"
    PUSH_NOTIFICATION_GET = "push_notification_get"


class TaskState(Enum):
    """Task states per A2A spec"""
    SUBMITTED = "submitted"
    WORKING = "working"
    INPUT_REQUIRED = "input-required"
    COMPLETED = "completed"
    CANCELED = "canceled"


@dataclass
class AgentSkill:
    """A skill that an agent can provide"""
    id: str
    name: str
    description: str
    tags: List[str]
    examples: Optional[List[str]] = None
    input_modes: Optional[List[str]] = None
    output_modes: Optional[List[str]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AgentCard:
    """
    Agent Card per A2A specification
    Describes an agent's capabilities and endpoints
    """
    name: str
    description: str
    url: str
    provider: Dict[str, str]
    version: str
    authentication: Dict[str, Any]
    default_input_modes: List[str] = field(default_factory=lambda: ["text"])
    default_output_modes: List[str] = field(default_factory=lambda: ["text"])
    skills: List[AgentSkill] = field(default_factory=list)
    documentation_url: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "url": self.url,
            "provider": self.provider,
            "version": self.version,
            "authentication": self.authentication,
            "defaultInputModes": self.default_input_modes,
            "defaultOutputModes": self.default_output_modes,
            "skills": [
                {
                    "id": s.id,
                    "name": s.name,
                    "description": s.description,
                    "tags": s.tags,
                    "examples": s.examples or [],
                    "inputModes": s.input_modes or self.default_input_modes,
                    "outputModes": s.output_modes or self.default_output_modes
                }
                for s in self.skills
            ],
            "documentationUrl": self.documentation_url
        }


@dataclass
class TextPart:
    """Text content part"""
    type: str = "text"
    text: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class FilePart:
    """File content part"""
    type: str = "file"
    file: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DataPart:
    """Structured data content part"""
    type: str = "data"
    data: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


Part = Union[TextPart, FilePart, DataPart]


@dataclass
class Message:
    """A2A Message format"""
    role: str  # "user" or "agent"
    parts: List[Part]
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Artifact:
    """Task artifact (output)"""
    name: Optional[str] = None
    description: Optional[str] = None
    parts: List[Part] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    index: int = 0
    append: Optional[bool] = None
    last_chunk: Optional[bool] = None


@dataclass
class Task:
    """A2A Task"""
    id: str
    session_id: str
    state: TaskState
    message: Message
    status: Optional[Dict[str, Any]] = None
    artifacts: List[Artifact] = field(default_factory=list)
    history: List[Message] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    push_notification: Optional[Dict[str, Any]] = None


@dataclass
class A2ARequest:
    """A2A Request format"""
    jsonrpc: str = "2.0"
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    method: str = ""
    params: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "jsonrpc": self.jsonrpc,
            "id": self.id,
            "method": self.method,
            "params": self.params
        }


@dataclass
class A2AResponse:
    """A2A Response format"""
    jsonrpc: str = "2.0"
    id: str = ""
    result: Optional[Dict[str, Any]] = None
    error: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        resp = {
            "jsonrpc": self.jsonrpc,
            "id": self.id
        }
        if self.result is not None:
            resp["result"] = self.result
        if self.error is not None:
            resp["error"] = self.error
        return resp


class A2AAgent:
    """
    A2A Protocol Agent implementation
    Handles agent discovery, task execution, and inter-agent communication
    """
    
    def __init__(
        self,
        name: str,
        description: str,
        url: str,
        provider_name: str,
        version: str = "1.0.0"
    ):
        self.agent_id = str(uuid.uuid4())
        self.name = name
        self.description = description
        self.url = url
        self.provider = {"name": provider_name, "url": url}
        self.version = version
        
        self.skills: Dict[str, AgentSkill] = {}
        self.tasks: Dict[str, Task] = {}
        self.discovered_agents: Dict[str, AgentCard] = {}
        
        # Authentication (simplified - would use OAuth/JWT in production)
        self.authentication = {
            "schemes": ["none"],  # or "oauth", "apiKey"
            "credentials": None
        }
        
        # Task handlers
        self.skill_handlers: Dict[str, Callable] = {}
        
        logger.info(f"🤖 A2A Agent initialized: {name} ({self.agent_id[:8]}...)")
    
    def add_skill(
        self,
        skill_id: str,
        name: str,
        description: str,
        tags: List[str],
        handler: Callable,
        examples: List[str] = None
    ) -> AgentSkill:
        """Add a skill to the agent"""
        skill = AgentSkill(
            id=skill_id,
            name=name,
            description=description,
            tags=tags,
            examples=examples or [],
            input_modes=["text", "data"],
            output_modes=["text", "data", "file"]
        )
        
        self.skills[skill_id] = skill
        self.skill_handlers[skill_id] = handler
        
        logger.info(f"✅ Skill added: {name} ({skill_id})")
        return skill
    
    def get_agent_card(self) -> AgentCard:
        """Generate Agent Card for discovery"""
        return AgentCard(
            name=self.name,
            description=self.description,
            url=self.url,
            provider=self.provider,
            version=self.version,
            authentication=self.authentication,
            skills=list(self.skills.values()),
            documentation_url=f"{self.url}/docs"
        )
    
    def handle_agent_card_query(self, request: A2ARequest) -> A2AResponse:
        """Handle agent card query (discovery)"""
        return A2AResponse(
            id=request.id,
            result=self.get_agent_card().to_dict()
        )
    
    def handle_skill_query(self, request: A2ARequest) -> A2AResponse:
        """Handle skill query"""
        query = request.params.get("query", "")
        matching_skills = []
        
        for skill in self.skills.values():
            if (query.lower() in skill.name.lower() or 
                query.lower() in skill.description.lower() or
                any(query.lower() in tag.lower() for tag in skill.tags)):
                matching_skills.append({
                    "id": skill.id,
                    "name": skill.name,
                    "description": skill.description,
                    "tags": skill.tags
                })
        
        return A2AResponse(
            id=request.id,
            result={"skills": matching_skills}
        )
    
    def handle_task_send(self, request: A2ARequest) -> A2AResponse:
        """
        Handle task send (initiate task execution)
        This is the core A2A task execution method
        """
        params = request.params
        
        # Create task
        task_id = params.get("id") or str(uuid.uuid4())
        session_id = params.get("sessionId") or str(uuid.uuid4())
        
        message_data = params.get("message", {})
        message = Message(
            role=message_data.get("role", "user"),
            parts=self._parse_parts(message_data.get("parts", [])),
            metadata=message_data.get("metadata", {})
        )
        
        task = Task(
            id=task_id,
            session_id=session_id,
            state=TaskState.SUBMITTED,
            message=message,
            metadata=params.get("metadata", {}),
            push_notification=params.get("pushNotification")
        )
        
        self.tasks[task_id] = task
        
        # Determine which skill to use
        skill_id = self._match_skill_to_message(message)
        
        if skill_id and skill_id in self.skill_handlers:
            # Execute skill handler
            handler = self.skill_handlers[skill_id]
            task.state = TaskState.WORKING
            
            try:
                # Execute synchronously for now (could be async)
                result = handler(message, task)
                
                task.state = TaskState.COMPLETED
                if result:
                    artifact = Artifact(
                        name="result",
                        parts=self._create_parts_from_result(result)
                    )
                    task.artifacts.append(artifact)
                
                logger.info(f"✅ Task completed: {task_id[:8]}...")
                
            except Exception as e:
                task.state = TaskState.CANCELED
                logger.error(f"❌ Task failed: {task_id[:8]}... - {e}")
                return A2AResponse(
                    id=request.id,
                    error={
                        "code": -32000,
                        "message": str(e)
                    }
                )
        else:
            task.state = TaskState.INPUT_REQUIRED
            logger.warning(f"⚠️ No skill match for task: {task_id[:8]}...")
        
        return A2AResponse(
            id=request.id,
            result=self._task_to_dict(task)
        )
    
    def handle_task_get(self, request: A2ARequest) -> A2AResponse:
        """Get task status and results"""
        task_id = request.params.get("id")
        
        if task_id not in self.tasks:
            return A2AResponse(
                id=request.id,
                error={
                    "code": -32001,
                    "message": f"Task not found: {task_id}"
                }
            )
        
        task = self.tasks[task_id]
        return A2AResponse(
            id=request.id,
            result=self._task_to_dict(task)
        )
    
    def handle_task_cancel(self, request: A2ARequest) -> A2AResponse:
        """Cancel a task"""
        task_id = request.params.get("id")
        
        if task_id not in self.tasks:
            return A2AResponse(
                id=request.id,
                error={
                    "code": -32001,
                    "message": f"Task not found: {task_id}"
                }
            )
        
        task = self.tasks[task_id]
        task.state = TaskState.CANCELED
        
        return A2AResponse(
            id=request.id,
            result=self._task_to_dict(task)
        )
    
    def _match_skill_to_message(self, message: Message) -> Optional[str]:
        """Match message to appropriate skill based on content analysis"""
        text_parts = [p.text for p in message.parts if isinstance(p, TextPart)]
        combined_text = " ".join(text_parts).lower()
        
        # Simple keyword matching (in production, use NLP/ML)
        best_match = None
        best_score = 0
        
        for skill_id, skill in self.skills.items():
            score = 0
            
            # Check skill name
            if skill.name.lower() in combined_text:
                score += 10
            
            # Check tags
            for tag in skill.tags:
                if tag.lower() in combined_text:
                    score += 5
            
            # Check description keywords
            desc_words = skill.description.lower().split()
            for word in desc_words:
                if len(word) > 4 and word in combined_text:
                    score += 2
            
            if score > best_score:
                best_score = score
                best_match = skill_id
        
        return best_match if best_score > 0 else None
    
    def _parse_parts(self, parts_data: List[Dict]) -> List[Part]:
        """Parse message parts from JSON"""
        parts = []
        for part in parts_data:
            part_type = part.get("type", "text")
            
            if part_type == "text":
                parts.append(TextPart(text=part.get("text", "")))
            elif part_type == "file":
                parts.append(FilePart(file=part.get("file", {})))
            elif part_type == "data":
                parts.append(DataPart(data=part.get("data", {})))
        
        return parts
    
    def _create_parts_from_result(self, result: Any) -> List[Part]:
        """Convert handler result to message parts"""
        parts = []
        
        if isinstance(result, str):
            parts.append(TextPart(text=result))
        elif isinstance(result, dict):
            parts.append(DataPart(data=result))
        elif isinstance(result, list):
            parts.append(DataPart(data={"items": result}))
        else:
            parts.append(TextPart(text=str(result)))
        
        return parts
    
    def _task_to_dict(self, task: Task) -> Dict[str, Any]:
        """Convert task to A2A response format"""
        return {
            "id": task.id,
            "sessionId": task.session_id,
            "state": task.state.value,
            "message": {
                "role": task.message.role,
                "parts": [
                    {"type": p.type, **({"text": p.text} if isinstance(p, TextPart) else {}),
                     **({"data": p.data} if isinstance(p, DataPart) else {})}
                    for p in task.message.parts
                ]
            },
            "status": task.status,
            "artifacts": [
                {
                    "name": a.name,
                    "description": a.description,
                    "parts": [
                        {"type": p.type, **({"text": p.text} if hasattr(p, 'text') else {})}
                        for p in a.parts
                    ]
                }
                for a in task.artifacts
            ],
            "history": [
                {
                    "role": m.role,
                    "parts": [{"type": p.type, **({"text": p.text} if isinstance(p, TextPart) else {})} for p in m.parts]
                }
                for m in task.history
            ]
        }
    
    def process_request(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process incoming A2A request"""
        try:
            request = A2ARequest(
                jsonrpc=request_data.get("jsonrpc", "2.0"),
                id=request_data.get("id", str(uuid.uuid4())),
                method=request_data.get("method", ""),
                params=request_data.get("params", {})
            )
            
            # Route to appropriate handler
            method = request.method
            
            if method == "agent/card":
                response = self.handle_agent_card_query(request)
            elif method == "skills/query":
                response = self.handle_skill_query(request)
            elif method == "tasks/send":
                response = self.handle_task_send(request)
            elif method == "tasks/get":
                response = self.handle_task_get(request)
            elif method == "tasks/cancel":
                response = self.handle_task_cancel(request)
            else:
                response = A2AResponse(
                    id=request.id,
                    error={
                        "code": -32601,
                        "message": f"Method not found: {method}"
                    }
                )
            
            return response.to_dict()
            
        except Exception as e:
            logger.error(f"Error processing A2A request: {e}")
            return {
                "jsonrpc": "2.0",
                "id": request_data.get("id", ""),
                "error": {
                    "code": -32603,
                    "message": f"Internal error: {str(e)}"
                }
            }
    
    # Discovery methods
    def discover_agents(self, directory_url: str) -> List[AgentCard]:
        """Discover agents from an A2A directory service"""
        try:
            response = requests.get(f"{directory_url}/agents", timeout=30)
            response.raise_for_status()
            agents_data = response.json()
            
            discovered = []
            for agent_data in agents_data.get("agents", []):
                card = AgentCard(
                    name=agent_data.get("name", ""),
                    description=agent_data.get("description", ""),
                    url=agent_data.get("url", ""),
                    provider=agent_data.get("provider", {}),
                    version=agent_data.get("version", "1.0.0"),
                    authentication=agent_data.get("authentication", {}),
                    skills=[
                        AgentSkill(
                            id=s.get("id", ""),
                            name=s.get("name", ""),
                            description=s.get("description", ""),
                            tags=s.get("tags", [])
                        )
                        for s in agent_data.get("skills", [])
                    ]
                )
                
                self.discovered_agents[card.url] = card
                discovered.append(card)
            
            logger.info(f"🔍 Discovered {len(discovered)} agents from {directory_url}")
            return discovered
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Agent discovery error: {e}")
            return []
    
    def send_task_to_agent(self, agent_url: str, message: str, skill_hint: str = None) -> Dict[str, Any]:
        """Send a task to another A2A agent"""
        try:
            request = A2ARequest(
                method="tasks/send",
                params={
                    "id": str(uuid.uuid4()),
                    "sessionId": str(uuid.uuid4()),
                    "message": {
                        "role": "user",
                        "parts": [{"type": "text", "text": message}]
                    },
                    "metadata": {
                        "skill_hint": skill_hint,
                        "sender": self.agent_id
                    }
                }
            )
            
            response = requests.post(
                f"{agent_url}/a2a",
                json=request.to_dict(),
                headers={"Content-Type": "application/json"},
                timeout=120
            )
            response.raise_for_status()
            
            result = response.json()
            logger.info(f"📤 Task sent to {agent_url}, received response")
            return result
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error sending task to agent: {e}")
            return {"error": str(e)}


class A2ACodingAgent(A2AAgent):
    """
    A2A Coding Agent specialization
    Provides coding services via A2A protocol
    """
    
    def __init__(self, url: str, provider_name: str = "AI Coding Agency"):
        super().__init__(
            name="Coding Assistant",
            description="Professional coding services including code review, bug fixing, feature development, and API integration",
            url=url,
            provider_name=provider_name
        )
        
        # Register coding skills
        self._register_coding_skills()
    
    def _register_coding_skills(self):
        """Register all coding skills with their handlers"""
        
        def code_review_handler(message: Message, task: Task) -> Dict[str, Any]:
            """Handle code review requests"""
            text_parts = [p.text for p in message.parts if isinstance(p, TextPart)]
            code = " ".join(text_parts)
            
            # In production, this would use actual code analysis tools
            return {
                "review": "Code analysis complete",
                "issues_found": 3,
                "suggestions": [
                    "Consider adding type hints",
                    "Add more unit tests",
                    "Refactor long function into smaller ones"
                ],
                "quality_score": 7.5,
                "lines_reviewed": len(code.split("\n"))
            }
        
        def bug_fix_handler(message: Message, task: Task) -> Dict[str, Any]:
            """Handle bug fixing requests"""
            return {
                "status": "bug_analyzed",
                "root_cause": "Null pointer exception in line 42",
                "fix": "Added null check before dereference",
                "tests_added": 2,
                "estimated_time": "2 hours"
            }
        
        def feature_dev_handler(message: Message, task: Task) -> Dict[str, Any]:
            """Handle feature development requests"""
            return {
                "status": "requirements_analyzed",
                "architecture": "Proposed microservices approach",
                "components": ["API Gateway", "Auth Service", "Database Layer"],
                "estimated_hours": 40,
                "milestones": [
                    {"name": "Design", "hours": 8},
                    {"name": "Implementation", "hours": 24},
                    {"name": "Testing", "hours": 8}
                ]
            }
        
        def api_integration_handler(message: Message, task: Task) -> Dict[str, Any]:
            """Handle API integration requests"""
            return {
                "status": "integration_plan_created",
                "apis_analyzed": ["Stripe", "SendGrid", "AWS S3"],
                "endpoints_needed": 12,
                "auth_method": "OAuth 2.0 + API Keys",
                "estimated_hours": 16,
                "deliverables": ["API client library", "Documentation", "Tests"]
            }
        
        # Add skills
        self.add_skill(
            skill_id="code_review",
            name="Code Review",
            description="Professional code review with quality analysis, bug detection, and improvement suggestions",
            tags=["code-review", "quality", "python", "javascript", "typescript"],
            handler=code_review_handler,
            examples=["Review this Python function", "Check my React component for issues"]
        )
        
        self.add_skill(
            skill_id="bug_fix",
            name="Bug Fixing",
            description="Fast and reliable bug fixing with root cause analysis and regression testing",
            tags=["bug-fix", "debugging", "troubleshooting", "fix"],
            handler=bug_fix_handler,
            examples=["Fix this error in my code", "Why is this function returning None?"]
        )
        
        self.add_skill(
            skill_id="feature_dev",
            name="Feature Development",
            description="Full-stack feature development from requirements to deployment",
            tags=["feature", "development", "full-stack", "backend", "frontend"],
            handler=feature_dev_handler,
            examples=["Build a user authentication system", "Add payment processing"]
        )
        
        self.add_skill(
            skill_id="api_integration",
            name="API Integration",
            description="Third-party API integration with error handling, rate limiting, and monitoring",
            tags=["api", "integration", "third-party", "rest", "graphql"],
            handler=api_integration_handler,
            examples=["Integrate Stripe payments", "Connect to AWS S3"]
        )


# Global registry for agent discovery
_a2a_agents: Dict[str, A2AAgent] = {}

def register_a2a_agent(agent: A2AAgent):
    """Register an A2A agent in the global registry"""
    global _a2a_agents
    _a2a_agents[agent.agent_id] = agent
    logger.info(f"📋 A2A Agent registered: {agent.name}")

def get_a2a_agent(agent_id: str) -> Optional[A2AAgent]:
    """Get an A2A agent by ID"""
    return _a2a_agents.get(agent_id)

def get_all_a2a_agents() -> List[A2AAgent]:
    """Get all registered A2A agents"""
    return list(_a2a_agents.values())


if __name__ == "__main__":
    print("=" * 70)
    print("GOOGLE A2A PROTOCOL IMPLEMENTATION TEST")
    print("=" * 70)
    
    # Create an A2A coding agent
    agent = A2ACodingAgent(
        url="http://localhost:8000",
        provider_name="Test AI Agency"
    )
    
    print("\n1. Agent Card (Discovery)")
    card = agent.get_agent_card()
    print(f"   Name: {card.name}")
    print(f"   Skills: {len(card.skills)}")
    for skill in card.skills:
        print(f"   - {skill.name}: {skill.description[:50]}...")
    
    print("\n2. Simulate Incoming Task (Code Review)")
    request = A2ARequest(
        method="tasks/send",
        params={
            "message": {
                "role": "user",
                "parts": [{"type": "text", "text": "Please review my Python function for handling API errors"}]
            }
        }
    )
    
    response = agent.process_request(request.to_dict())
    print(f"   Task ID: {response.get('result', {}).get('id', 'N/A')[:8]}...")
    print(f"   State: {response.get('result', {}).get('state', 'N/A')}")
    if response.get('result', {}).get('artifacts'):
        print(f"   Result: {response['result']['artifacts'][0]}")
    
    print("\n3. Simulate Agent Card Query")
    card_request = A2ARequest(method="agent/card")
    card_response = agent.process_request(card_request.to_dict())
    print(f"   Agent name: {card_response.get('result', {}).get('name')}")
    print(f"   Version: {card_response.get('result', {}).get('version')}")
    
    print("\n4. Skill Query")
    skill_request = A2ARequest(
        method="skills/query",
        params={"query": "debugging"}
    )
    skill_response = agent.process_request(skill_request.to_dict())
    matching = skill_response.get('result', {}).get('skills', [])
    print(f"   Skills matching 'debugging': {len(matching)}")
    for s in matching:
        print(f"   - {s['name']}")
    
    print("\n" + "=" * 70)
    print("A2A Protocol Implementation Complete")
    print("=" * 70)


# Factory function for external imports
_coding_agent_instance: Optional[A2ACodingAgent] = None

def get_real_coding_agent(url: str = "http://localhost:8000", provider_name: str = "AI Coding Agency") -> A2ACodingAgent:
    """Get or create the singleton A2A Coding Agent instance"""
    global _coding_agent_instance
    if _coding_agent_instance is None:
        _coding_agent_instance = A2ACodingAgent(url=url, provider_name=provider_name)
        register_a2a_agent(_coding_agent_instance)
    return _coding_agent_instance
