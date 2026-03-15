import fetch from "node-fetch";
import chalk from "chalk";
import ora from "ora";
import { CONFIG } from "../config.js";

export async function syncCommand(options) {
  const max = parseInt(options.max || "20", 10);
  const spinner = ora(
    `Syncing registry from awesome-agent-skills (max ${max} skills)...`
  ).start();

  try {
    const res = await fetch(
      `${CONFIG.API_BASE_URL}/api/sync?max_skills=${max}`,
      { method: "POST" }
    );

    if (!res.ok) {
      spinner.fail("Sync failed");
      console.error(chalk.red(`API error: ${res.status} ${res.statusText}`));
      process.exit(1);
    }

    const data = await res.json();
    spinner.succeed(
      `Sync complete [source: ${chalk.cyan(data.source)}]`
    );

    console.log();
    console.log(
      `  ${chalk.green("+")} ${data.added} added   ` +
      `${chalk.dim("~")} ${data.skipped} skipped   ` +
      `${data.errors > 0 ? chalk.red("✗") : chalk.dim("✗")} ${data.errors} errors`
    );

    if (options.verbose && data.details?.length) {
      console.log();
      for (const line of data.details) {
        const icon = line.startsWith("Added") ? chalk.green("+") :
                     line.startsWith("Already") ? chalk.dim("~") : chalk.red("!");
        console.log(`  ${icon} ${line}`);
      }
    }
    console.log();
  } catch (err) {
    spinner.fail("Sync failed");
    console.error(chalk.red(`Connection error: ${err.message}`));
    console.error(chalk.dim(`Is the Nexus API running at ${CONFIG.API_BASE_URL}?`));
    process.exit(1);
  }
}
