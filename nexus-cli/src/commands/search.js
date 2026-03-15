import fetch from "node-fetch";
import chalk from "chalk";
import ora from "ora";
import { CONFIG } from "../config.js";

export async function searchCommand(intent, options) {
  const spinner = ora("Searching skill registry...").start();

  try {
    const res = await fetch(`${CONFIG.API_BASE_URL}/api/search`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ problem_statement: intent }),
    });

    if (!res.ok) {
      spinner.fail("Search failed");
      console.error(chalk.red(`API error: ${res.status} ${res.statusText}`));
      process.exit(1);
    }

    const data = await res.json();
    spinner.succeed(`Found ${data.total} skill(s)`);

    if (options.json) {
      console.log(JSON.stringify(data, null, 2));
      return;
    }

    if (data.results.length === 0) {
      console.log(chalk.dim("  No matching skills found."));
      return;
    }

    console.log();
    for (const skill of data.results) {
      const confidence = Math.round(skill.confidence * 100);
      const confColor = confidence > 70 ? chalk.green : confidence > 40 ? chalk.yellow : chalk.dim;
      const riskLabel = skill.risk_score != null
        ? (skill.risk_score < 30 ? chalk.green("LOW") : skill.risk_score < 60 ? chalk.yellow("MED") : chalk.red("HIGH"))
        : chalk.dim("N/A");
      const price = skill.price_per_use ? `$${skill.price_per_use}/use` : chalk.green("FREE");

      console.log(
        `  ${chalk.bold(skill.name)} ${chalk.dim(`(${skill.skill_id})`)}`
      );
      console.log(
        `    Confidence: ${confColor(confidence + "%")}  Risk: ${riskLabel}  Price: ${price}`
      );
      console.log(`    ${chalk.dim(skill.description)}`);
      if (skill.tags.length > 0) {
        console.log(`    Tags: ${skill.tags.map((t) => chalk.cyan(t)).join(", ")}`);
      }
      console.log();
    }
  } catch (err) {
    spinner.fail("Search failed");
    console.error(chalk.red(`Connection error: ${err.message}`));
    console.error(chalk.dim(`Is the Nexus API running at ${CONFIG.API_BASE_URL}?`));
    process.exit(1);
  }
}
