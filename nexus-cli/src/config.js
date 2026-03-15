export const CONFIG = {
  API_BASE_URL: process.env.NEXUS_API_URL || "http://localhost:8000",
  SKILLS_DIR: process.env.NEXUS_SKILLS_DIR || ".agents/skills",
  AGENT_ID: process.env.NEXUS_AGENT_ID || `agent-${Date.now().toString(36)}`,
};
