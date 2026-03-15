#!/usr/bin/env node

import { Command } from "commander";
import { searchCommand } from "../src/commands/search.js";
import { installCommand } from "../src/commands/install.js";
import { publishCommand } from "../src/commands/publish.js";
import { syncCommand } from "../src/commands/sync.js";

const program = new Command();

program
  .name("nexus-skill")
  .description("Nexus M2M Skill Exchange CLI — autonomous AI skill discovery and installation")
  .version("0.1.0");

program
  .command("search <intent>")
  .description("Search for skills by describing what you need")
  .option("--json", "Output raw JSON")
  .action(searchCommand);

program
  .command("use <skill_id>")
  .description("Fetch, scan, and install a skill to .agents/skills/")
  .option("--force", "Install even if security scan fails")
  .action(installCommand);

program
  .command("publish <path>")
  .description("Publish a SKILL.md to the Nexus registry")
  .option("--name <name>", "Override skill name")
  .option("--description <desc>", "Override skill description")
  .option("--author <author>", "Override author")
  .option("--version <ver>", "Override version")
  .action(publishCommand);

program
  .command("sync")
  .description("Sync the registry with awesome-agent-skills (scrape new skills)")
  .option("--max <n>", "Maximum number of skills to import", "20")
  .option("--verbose", "Show per-skill details")
  .action(syncCommand);

program.parse();
