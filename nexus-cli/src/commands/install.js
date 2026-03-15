import fetch from "node-fetch";
import chalk from "chalk";
import ora from "ora";
import fs from "fs";
import path from "path";
import { CONFIG } from "../config.js";
import { scanContent, printReport } from "../scanner.js";

export async function installCommand(skillId, options) {
  const spinner = ora(`Fetching skill ${skillId}...`).start();

  try {
    // 1. Fetch the skill and register usage
    const res = await fetch(
      `${CONFIG.API_BASE_URL}/api/skills/${skillId}/use?agent_id=${CONFIG.AGENT_ID}`,
      { method: "POST" }
    );

    if (!res.ok) {
      spinner.fail("Fetch failed");
      if (res.status === 404) {
        console.error(chalk.red(`Skill '${skillId}' not found in registry.`));
      } else {
        console.error(chalk.red(`API error: ${res.status}`));
      }
      process.exit(1);
    }

    const data = await res.json();
    spinner.succeed(`Fetched: ${data.skill.name}`);

    // 2. Run local security scan
    const findings = scanContent(data.skill.skill_md_content);
    const passed = printReport(findings, data.skill.name);

    if (!passed && !options.force) {
      console.log(chalk.red("\n  ✗ Skill failed security check. Use --force to install anyway.\n"));
      process.exit(1);
    }

    // 3. Mount to skills directory
    const skillsDir = path.resolve(CONFIG.SKILLS_DIR);
    const skillDir = path.join(skillsDir, skillId);
    fs.mkdirSync(skillDir, { recursive: true });

    // Write SKILL.md
    fs.writeFileSync(
      path.join(skillDir, "SKILL.md"),
      data.skill.skill_md_content
    );

    // Write nexus.yaml with permissions
    const permYaml = Object.entries(data.skill.permissions || {})
      .map(([k, v]) => `${k}: ${v}`)
      .join("\n");
    fs.writeFileSync(path.join(skillDir, "nexus.yaml"), permYaml + "\n");

    console.log(chalk.green(`\n  ✓ Installed to ${skillDir}`));

    // 4. Show payment info
    if (data.usage.status === "paid") {
      console.log(chalk.dim(`  Payment: $${data.usage.payment.developer_payout} → developer, $${data.usage.payment.platform_fee} → platform`));
      console.log(chalk.dim(`  Proof: ${data.usage.proof_of_execution}`));
    } else {
      console.log(chalk.dim(`  Proof: ${data.usage.proof_of_execution}`));
    }
    console.log();
  } catch (err) {
    spinner.fail("Install failed");
    console.error(chalk.red(`Error: ${err.message}`));
    process.exit(1);
  }
}
