import fetch from "node-fetch";
import chalk from "chalk";
import ora from "ora";
import fs from "fs";
import path from "path";
import YAML from "yaml";
import { CONFIG } from "../config.js";

export async function publishCommand(skillPath, options) {
  const resolvedPath = path.resolve(skillPath);

  // Read SKILL.md
  const skillMdPath = fs.statSync(resolvedPath).isDirectory()
    ? path.join(resolvedPath, "SKILL.md")
    : resolvedPath;

  if (!fs.existsSync(skillMdPath)) {
    console.error(chalk.red(`SKILL.md not found at ${skillMdPath}`));
    process.exit(1);
  }

  const skillMdContent = fs.readFileSync(skillMdPath, "utf-8");

  // Read nexus.yaml — warn if missing (required for Agent Skills Spec compliance)
  const yamlPath = path.join(path.dirname(skillMdPath), "nexus.yaml");
  let metadata = {};
  if (fs.existsSync(yamlPath)) {
    metadata = YAML.parse(fs.readFileSync(yamlPath, "utf-8")) || {};
  } else {
    // Check for frontmatter inside SKILL.md as alternative
    const hasFrontmatter = skillMdContent.startsWith("---");
    if (!hasFrontmatter) {
      console.warn(
        chalk.yellow(
          "  ⚠ nexus.yaml not found. Add a nexus.yaml or embed YAML frontmatter in SKILL.md\n" +
          "    for full Agent Skills Specification compliance.\n" +
          "    See: docs/SKILL.md.example for the required format.\n"
        )
      );
    }
  }

  // Extract name from SKILL.md first heading
  const nameMatch = skillMdContent.match(/^#\s+(.+)$/m);
  const name = options.name || metadata.name || (nameMatch ? nameMatch[1].trim() : "Unnamed Skill");

  // Extract description from first paragraph after heading
  const descMatch = skillMdContent.match(/^#.+\n+(?:##\s+Description\n+)?(.+)/m);
  const description = options.description || metadata.description || (descMatch ? descMatch[1].trim() : "No description");

  const payload = {
    name,
    version: options.version || metadata.version || "1.0.0",
    description,
    author: options.author || metadata.author || CONFIG.AGENT_ID,
    tags: metadata.tags || [],
    skill_md_content: skillMdContent,
    permissions: {
      network: metadata.network || "none",
      filesystem: metadata.filesystem || "none",
      execution: metadata.execution || "none",
    },
    price_per_use: metadata.price_per_use || null,
    license_fee: metadata.license_fee || null,
  };

  const spinner = ora("Publishing skill to Nexus registry...").start();

  try {
    const res = await fetch(`${CONFIG.API_BASE_URL}/api/skills/publish`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    if (!res.ok) {
      spinner.fail("Publish failed");
      const err = await res.text();
      console.error(chalk.red(`API error: ${err}`));
      process.exit(1);
    }

    const data = await res.json();
    spinner.succeed(`Published: ${name}`);

    console.log(chalk.dim(`  ID: ${data.skill_id}`));
    console.log(chalk.dim(`  Status: ${data.status}`));

    const report = data.security_report;
    const scoreColor = report.risk_score < 30 ? chalk.green : report.risk_score < 60 ? chalk.yellow : chalk.red;
    console.log(`  Risk Score: ${scoreColor(report.risk_score + "/100")}`);

    if (report.static_analysis.length > 0 || report.prompt_injection_flags.length > 0) {
      console.log(chalk.yellow("\n  Security findings:"));
      for (const f of [...report.static_analysis, ...report.prompt_injection_flags]) {
        console.log(chalk.yellow(`    ⚠ ${f}`));
      }
    }
    console.log();
  } catch (err) {
    spinner.fail("Publish failed");
    console.error(chalk.red(`Error: ${err.message}`));
    process.exit(1);
  }
}
