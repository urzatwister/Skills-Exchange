import chalk from "chalk";

const DANGEROUS_PATTERNS = [
  { pattern: /\bcurl\b/gi, desc: "Network access via curl" },
  { pattern: /\bwget\b/gi, desc: "Network access via wget" },
  { pattern: /\beval\b/gi, desc: "Dynamic code execution via eval" },
  { pattern: /\bexec\b/gi, desc: "Dynamic code execution via exec" },
  { pattern: /\bchmod\b/gi, desc: "File permission modification" },
  { pattern: /\brm\s+-rf\b/gi, desc: "Recursive file deletion" },
  { pattern: /child_process/gi, desc: "Node.js child process execution" },
  { pattern: /(api[_-]?key|secret|password|token)\s*[=:]\s*["'][^"']{8,}/gi, desc: "Hardcoded secret" },
  { pattern: /(AKIA|ASIA)[A-Z0-9]{16}/g, desc: "AWS access key" },
  { pattern: /sk-[a-zA-Z0-9]{20,}/g, desc: "API key pattern" },
];

const INJECTION_PATTERNS = [
  { pattern: /ignore\s+(all\s+)?previous\s+instructions/gi, desc: "Prompt override attempt" },
  { pattern: /you\s+are\s+now\s+/gi, desc: "Role reassignment attempt" },
  { pattern: /forget\s+(all\s+)?(your\s+)?instructions/gi, desc: "Instruction erasure attempt" },
  { pattern: /disregard\s+(any|all|the)\s+(previous|above)/gi, desc: "Instruction override attempt" },
  { pattern: /override\s+(security|safety|permissions)/gi, desc: "Security bypass attempt" },
];

export function scanContent(content) {
  const findings = { static: [], injection: [], riskScore: 0 };

  for (const { pattern, desc } of DANGEROUS_PATTERNS) {
    const matches = content.match(pattern);
    if (matches) {
      findings.static.push(`${desc} (${matches.length}x)`);
    }
  }

  for (const { pattern, desc } of INJECTION_PATTERNS) {
    if (pattern.test(content)) {
      findings.injection.push(desc);
    }
  }

  findings.riskScore = Math.min(
    100,
    findings.static.length * 10 + findings.injection.length * 25
  );

  return findings;
}

export function printReport(findings, skillName) {
  console.log(chalk.bold(`\n  Security Scan: ${skillName}`));
  console.log("  " + "─".repeat(40));

  if (findings.static.length === 0 && findings.injection.length === 0) {
    console.log(chalk.green("  ✓ No security issues detected"));
  }

  for (const issue of findings.static) {
    console.log(chalk.yellow(`  ⚠ [STATIC] ${issue}`));
  }
  for (const issue of findings.injection) {
    console.log(chalk.red(`  ✗ [INJECTION] ${issue}`));
  }

  const scoreColor = findings.riskScore < 30 ? chalk.green : findings.riskScore < 60 ? chalk.yellow : chalk.red;
  console.log(`\n  Risk Score: ${scoreColor(findings.riskScore + "/100")}`);
  console.log("  " + "─".repeat(40));

  return findings.riskScore < 50;
}
