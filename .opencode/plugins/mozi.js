/**
 * Mozi plugin for OpenCode.
 *
 * Registers the root skills directory and injects the using-mozi bootstrap.
 */

import path from 'path';
import fs from 'fs';
import os from 'os';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));

const extractAndStripFrontmatter = (content) => {
  const match = content.match(/^---\n([\s\S]*?)\n---\n([\s\S]*)$/);
  if (!match) return { content };
  return { content: match[2] };
};

const normalizePath = (p, homeDir) => {
  if (!p || typeof p !== 'string') return null;
  let normalized = p.trim();
  if (!normalized) return null;
  if (normalized.startsWith('~/')) {
    normalized = path.join(homeDir, normalized.slice(2));
  } else if (normalized === '~') {
    normalized = homeDir;
  }
  return path.resolve(normalized);
};

let bootstrapCache = undefined;

export const MoziPlugin = async () => {
  const homeDir = os.homedir();
  const moziSkillsDir = path.resolve(__dirname, '../../skills');
  const envConfigDir = normalizePath(process.env.OPENCODE_CONFIG_DIR, homeDir);
  const configDir = envConfigDir || path.join(homeDir, '.config/opencode');
  void configDir;

  const getBootstrapContent = () => {
    if (bootstrapCache !== undefined) return bootstrapCache;

    const skillPath = path.join(moziSkillsDir, 'using-mozi', 'SKILL.md');
    if (!fs.existsSync(skillPath)) {
      bootstrapCache = null;
      return null;
    }

    const fullContent = fs.readFileSync(skillPath, 'utf8');
    const { content } = extractAndStripFrontmatter(fullContent);

    const toolMapping = `**Tool Mapping for OpenCode:**
When Mozi skills reference tools you do not have, substitute OpenCode equivalents:
- \`Skill\` tool -> OpenCode's native \`skill\` tool
- File operations -> your native tools
- Shell commands -> your native shell command tool`;

    bootstrapCache = `<EXTREMELY_IMPORTANT>
You have Mozi.

**IMPORTANT: The using-mozi skill content is included below. It is ALREADY LOADED.**

${content}

${toolMapping}
</EXTREMELY_IMPORTANT>`;

    return bootstrapCache;
  };

  return {
    config: async (config) => {
      config.skills = config.skills || {};
      config.skills.paths = config.skills.paths || [];
      if (!config.skills.paths.includes(moziSkillsDir)) {
        config.skills.paths.push(moziSkillsDir);
      }
    },

    'experimental.chat.messages.transform': async (_input, output) => {
      const bootstrap = getBootstrapContent();
      if (!bootstrap || !output.messages.length) return;
      const firstUser = output.messages.find(m => m.info.role === 'user');
      if (!firstUser || !firstUser.parts.length) return;
      if (firstUser.parts.some(p => p.type === 'text' && p.text.includes('EXTREMELY_IMPORTANT'))) return;

      const ref = firstUser.parts[0];
      firstUser.parts.unshift({ ...ref, type: 'text', text: bootstrap });
    }
  };
};
