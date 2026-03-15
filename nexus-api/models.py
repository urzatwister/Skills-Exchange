from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum


class NetworkScope(str, Enum):
    NONE = "none"
    INTERNAL_ONLY = "internal-only"
    EXTERNAL = "external"


class FilesystemScope(str, Enum):
    NONE = "none"
    READ_ONLY = "read-only"
    READ_WRITE = "read-write"


class ExecutionScope(str, Enum):
    NONE = "none"
    SANDBOXED = "sandboxed"
    UNRESTRICTED = "unrestricted"


class PermissionManifest(BaseModel):
    network: NetworkScope = NetworkScope.NONE
    filesystem: FilesystemScope = FilesystemScope.NONE
    execution: ExecutionScope = ExecutionScope.NONE


class SkillMetadata(BaseModel):
    skill_id: str
    name: str
    version: str = "1.0.0"
    description: str
    author: str
    tags: list[str] = []
    skill_md_content: str
    permissions: PermissionManifest = PermissionManifest()
    price_per_use: Optional[float] = None
    license_fee: Optional[float] = None
    risk_score: Optional[int] = None


class SearchRequest(BaseModel):
    problem_statement: str
    offset: int = 0
    limit: int = 12


class SearchResult(BaseModel):
    skill_id: str
    name: str
    description: str
    confidence: float = Field(ge=0.0, le=1.0)
    risk_score: Optional[int] = None
    price_per_use: Optional[float] = None
    author: str
    tags: list[str] = []


class SearchResponse(BaseModel):
    results: list[SearchResult]
    query: str
    total: int
    offset: int = 0
    limit: int = 12


class PublishRequest(BaseModel):
    name: str
    version: str = "1.0.0"
    description: str
    author: str
    tags: list[str] = []
    skill_md_content: str
    permissions: PermissionManifest = PermissionManifest()
    price_per_use: Optional[float] = None
    license_fee: Optional[float] = None


class UsageRecord(BaseModel):
    skill_id: str
    agent_id: str
    action: str  # "install" | "execute"
    timestamp: str
    proof_hash: str


class TransactionRecord(BaseModel):
    transaction_id: str
    skill_id: str
    agent_id: str
    total_amount: float
    developer_share: float  # 80%
    platform_share: float   # 20%
    proof_hash: str
    timestamp: str


class LLMInjectionVerdict(BaseModel):
    verdict: str = "skipped"   # safe | suspicious | malicious | skipped | error
    confidence: float = 0.0
    explanation: str = ""
    flags: list[str] = []
    source: str = "llm"


class SecurityReport(BaseModel):
    skill_id: str
    risk_score: int = Field(ge=0, le=100)
    static_analysis: list[str]
    prompt_injection_flags: list[str]
    permission_issues: list[str]
    llm_injection_verdict: Optional[LLMInjectionVerdict] = None
    passed: bool


class DeveloperStats(BaseModel):
    author: str
    skill_count: int
    total_uses: int
    unique_agents: int
    total_revenue: float
    skills: list[dict] = []
