"""
SandboxExecutor — safe execution layer for skill scripts.

Hierarchy:
  SandboxExecutor (abstract)
  ├── SubprocessSandbox   — real implementation, resource-limited subprocess
  ├── DockerSandbox       — Docker-based isolation (requires Docker daemon)
  └── WasmSandbox         — WebAssembly runtime (interface only, not yet implemented)
"""
from __future__ import annotations

import os
import subprocess
import shutil
import tempfile
from abc import ABC, abstractmethod
from dataclasses import dataclass, field


@dataclass
class ExecutionResult:
    stdout: str
    stderr: str
    exit_code: int
    timed_out: bool = False
    sandbox_type: str = "none"

    @property
    def success(self) -> bool:
        return self.exit_code == 0 and not self.timed_out


@dataclass
class ExecutionRequest:
    code: str
    language: str          # "python" | "javascript" | "bash"
    timeout_seconds: int = 10
    env_vars: dict = field(default_factory=dict)
    allow_network: bool = False


class SandboxExecutor(ABC):
    """Abstract base for all sandbox executors."""

    @abstractmethod
    def execute(self, request: ExecutionRequest) -> ExecutionResult:
        """Execute code in a sandboxed environment and return the result."""

    @abstractmethod
    def is_available(self) -> bool:
        """Return True if this sandbox type can run on the current system."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Human-readable name for this executor."""


class SubprocessSandbox(SandboxExecutor):
    """
    Subprocess-based sandbox with timeout and environment isolation.
    Provides basic resource limiting — no network env vars, limited PATH.
    Does NOT prevent all host access; use DockerSandbox for stronger isolation.
    """

    name = "subprocess"

    def is_available(self) -> bool:
        return True  # Always available

    def execute(self, request: ExecutionRequest) -> ExecutionResult:
        with tempfile.TemporaryDirectory() as workdir:
            # Write code to temp file
            ext = {"python": ".py", "javascript": ".js", "bash": ".sh"}.get(request.language, ".txt")
            code_file = os.path.join(workdir, f"skill{ext}")
            with open(code_file, "w") as f:
                f.write(request.code)

            # Build isolated environment
            env = {
                "PATH": "/usr/bin:/bin",
                "HOME": workdir,
                "TMPDIR": workdir,
            }
            if request.allow_network:
                env["ALLOW_NETWORK"] = "1"
            env.update(request.env_vars)

            # Select interpreter
            interpreters = {
                "python": ["python3", code_file],
                "javascript": ["node", code_file],
                "bash": ["bash", code_file],
            }
            cmd = interpreters.get(request.language)
            if cmd is None:
                return ExecutionResult(
                    stdout="", stderr=f"Unsupported language: {request.language}",
                    exit_code=1, sandbox_type=self.name
                )

            try:
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=request.timeout_seconds,
                    env=env,
                    cwd=workdir,
                )
                return ExecutionResult(
                    stdout=result.stdout,
                    stderr=result.stderr,
                    exit_code=result.returncode,
                    sandbox_type=self.name,
                )
            except subprocess.TimeoutExpired:
                return ExecutionResult(
                    stdout="", stderr="Execution timed out",
                    exit_code=1, timed_out=True, sandbox_type=self.name
                )
            except FileNotFoundError as e:
                return ExecutionResult(
                    stdout="", stderr=f"Interpreter not found: {e}",
                    exit_code=1, sandbox_type=self.name
                )


class DockerSandbox(SandboxExecutor):
    """
    Docker-based sandbox using --network none and read-only filesystem.
    Requires Docker daemon to be running.
    """

    name = "docker"

    IMAGES = {
        "python": "python:3.12-slim",
        "javascript": "node:20-slim",
        "bash": "bash:5",
    }

    def is_available(self) -> bool:
        return shutil.which("docker") is not None

    def execute(self, request: ExecutionRequest) -> ExecutionResult:
        if not self.is_available():
            return ExecutionResult(
                stdout="", stderr="Docker not available on this system",
                exit_code=1, sandbox_type=self.name
            )

        image = self.IMAGES.get(request.language)
        if image is None:
            return ExecutionResult(
                stdout="", stderr=f"No Docker image for language: {request.language}",
                exit_code=1, sandbox_type=self.name
            )

        with tempfile.TemporaryDirectory() as workdir:
            ext = {"python": ".py", "javascript": ".js", "bash": ".sh"}.get(request.language, ".txt")
            code_file = os.path.join(workdir, f"skill{ext}")
            with open(code_file, "w") as f:
                f.write(request.code)

            network_flag = "bridge" if request.allow_network else "none"
            entry = {"python": f"python /code/skill{ext}", "javascript": f"node /code/skill{ext}", "bash": f"bash /code/skill{ext}"}[request.language]

            cmd = [
                "docker", "run", "--rm",
                "--network", network_flag,
                "--memory", "128m",
                "--cpus", "0.5",
                "--read-only",
                "--tmpfs", "/tmp",
                "-v", f"{workdir}:/code:ro",
                image,
                "sh", "-c", entry,
            ]

            try:
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=request.timeout_seconds + 10,
                )
                return ExecutionResult(
                    stdout=result.stdout,
                    stderr=result.stderr,
                    exit_code=result.returncode,
                    sandbox_type=self.name,
                )
            except subprocess.TimeoutExpired:
                return ExecutionResult(
                    stdout="", stderr="Docker execution timed out",
                    exit_code=1, timed_out=True, sandbox_type=self.name
                )


class WasmSandbox(SandboxExecutor):
    """
    WebAssembly sandbox — interface defined, runtime not yet integrated.
    Future: integrate wasmtime or wasmer for near-native sandboxed execution.
    """

    name = "wasm"

    def is_available(self) -> bool:
        return shutil.which("wasmtime") is not None or shutil.which("wasmer") is not None

    def execute(self, request: ExecutionRequest) -> ExecutionResult:
        return ExecutionResult(
            stdout="",
            stderr="WasmSandbox is not yet implemented. Use SubprocessSandbox or DockerSandbox.",
            exit_code=1,
            sandbox_type=self.name,
        )


class SandboxFactory:
    """Select the best available sandbox for a given execution scope."""

    @staticmethod
    def get(execution_scope: str = "sandboxed") -> SandboxExecutor:
        """
        execution_scope: "none" | "sandboxed" | "unrestricted"
        Returns the most secure available executor for the given scope.
        """
        if execution_scope == "none":
            raise ValueError("Skill declares execution: none — execution is not permitted.")

        if execution_scope == "unrestricted":
            return SubprocessSandbox()

        # "sandboxed" — prefer Docker > Wasm > Subprocess
        docker = DockerSandbox()
        if docker.is_available():
            return docker

        wasm = WasmSandbox()
        if wasm.is_available():
            return wasm

        return SubprocessSandbox()
