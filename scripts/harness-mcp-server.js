#!/usr/bin/env node
// Harness MCP Server — exposes AIQE skill files as callable tools
// Used by GitHub Copilot and Claude Code via .mcp.json / .vscode/mcp.json

const { Server } = require('@modelcontextprotocol/sdk/server/index.js');
const { StdioServerTransport } = require('@modelcontextprotocol/sdk/server/stdio.js');
const { CallToolRequestSchema, ListToolsRequestSchema } = require('@modelcontextprotocol/sdk/types.js');
const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

const ROOT = path.resolve(__dirname, '..');
const SKILLS_DIR = path.join(ROOT, 'skills');
const SCREEN_MAPS_DIR = path.join(ROOT, 'playwright-automation-framework', 'support', 'screen-maps');
const FLOWS_DIR = path.join(ROOT, 'inputs', 'manual-flows');
const PW_DIR = path.join(ROOT, 'playwright-automation-framework');

const server = new Server(
  { name: 'aiqe-harness', version: '1.0.0' },
  { capabilities: { tools: {} } }
);

server.setRequestHandler(ListToolsRequestSchema, async () => ({
  tools: [
    {
      name: 'list_skills',
      description: 'List all available AIQE harness skills with descriptions.',
      inputSchema: { type: 'object', properties: {} },
    },
    {
      name: 'read_skill',
      description: 'Read a harness SKILL.md to get full workflow instructions. Always call this before starting a skill phase.',
      inputSchema: {
        type: 'object',
        properties: {
          name: {
            type: 'string',
            description: 'Skill name: pipeline-orchestrator | live-execution | automation-framework | test-healer | test-case-design | test-jira-reporter | knowledge-base | project-extension',
          },
        },
        required: ['name'],
      },
    },
    {
      name: 'read_flow',
      description: 'Read a manual flow file from inputs/manual-flows/ for a feature.',
      inputSchema: {
        type: 'object',
        properties: {
          feature: { type: 'string', description: 'Feature slug, e.g. checkout' },
        },
        required: ['feature'],
      },
    },
    {
      name: 'list_screen_maps',
      description: 'List all captured screen maps in support/screen-maps/.',
      inputSchema: { type: 'object', properties: {} },
    },
    {
      name: 'read_screen_map',
      description: 'Read the DOM screen map for a feature. Required before generating page objects.',
      inputSchema: {
        type: 'object',
        properties: {
          feature: { type: 'string', description: 'Feature slug, e.g. checkout' },
        },
        required: ['feature'],
      },
    },
    {
      name: 'run_tests',
      description: 'Run Playwright tests for a feature and return pass/fail output.',
      inputSchema: {
        type: 'object',
        properties: {
          feature: {
            type: 'string',
            description: 'Feature slug to run a specific spec, e.g. checkout. Omit to run all tests.',
          },
        },
      },
    },
  ],
}));

server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name, arguments: args = {} } = request.params;

  try {
    switch (name) {
      case 'list_skills': {
        const entries = fs.readdirSync(SKILLS_DIR, { withFileTypes: true })
          .filter(d => d.isDirectory())
          .map(d => {
            const skillFile = path.join(SKILLS_DIR, d.name, 'SKILL.md');
            const heading = fs.existsSync(skillFile)
              ? fs.readFileSync(skillFile, 'utf8').split('\n').find(l => l.startsWith('# '))?.replace(/^#\s*/, '') ?? d.name
              : d.name;
            return `- **${d.name}**: ${heading}`;
          });
        return { content: [{ type: 'text', text: `Available skills:\n${entries.join('\n')}` }] };
      }

      case 'read_skill': {
        const skillFile = path.join(SKILLS_DIR, args.name, 'SKILL.md');
        if (!fs.existsSync(skillFile)) {
          return {
            content: [{ type: 'text', text: `Skill "${args.name}" not found. Call list_skills to see options.` }],
            isError: true,
          };
        }
        return { content: [{ type: 'text', text: fs.readFileSync(skillFile, 'utf8') }] };
      }

      case 'read_flow': {
        if (!fs.existsSync(FLOWS_DIR)) {
          return { content: [{ type: 'text', text: 'inputs/manual-flows/ not found.' }], isError: true };
        }
        const files = fs.readdirSync(FLOWS_DIR).filter(f => f.includes(args.feature) && f.endsWith('.md'));
        if (files.length === 0) {
          return {
            content: [{ type: 'text', text: `No flow found for "${args.feature}" in inputs/manual-flows/. Create one first.` }],
            isError: true,
          };
        }
        return { content: [{ type: 'text', text: fs.readFileSync(path.join(FLOWS_DIR, files[0]), 'utf8') }] };
      }

      case 'list_screen_maps': {
        if (!fs.existsSync(SCREEN_MAPS_DIR)) {
          return { content: [{ type: 'text', text: 'No screen-maps directory yet. Run live-execution first.' }] };
        }
        const maps = fs.readdirSync(SCREEN_MAPS_DIR).filter(f => f.endsWith('.screen.json'));
        if (maps.length === 0) {
          return { content: [{ type: 'text', text: 'No screen maps captured yet. Run live-execution first.' }] };
        }
        return { content: [{ type: 'text', text: `Captured screen maps:\n${maps.map(f => `- ${f}`).join('\n')}` }] };
      }

      case 'read_screen_map': {
        const mapFile = path.join(SCREEN_MAPS_DIR, `${args.feature}.screen.json`);
        if (!fs.existsSync(mapFile)) {
          return {
            content: [{ type: 'text', text: `No screen map for "${args.feature}". Run live-execution first.` }],
            isError: true,
          };
        }
        return { content: [{ type: 'text', text: fs.readFileSync(mapFile, 'utf8') }] };
      }

      case 'run_tests': {
        const specArg = args.feature ? `tests/e2e/${args.feature}.spec.ts` : '';
        try {
          const out = execSync(`npx playwright test ${specArg} --reporter=line`, {
            cwd: PW_DIR, encoding: 'utf8', timeout: 120000,
          });
          return { content: [{ type: 'text', text: out }] };
        } catch (e) {
          return { content: [{ type: 'text', text: e.stdout || e.message }], isError: true };
        }
      }

      default:
        return { content: [{ type: 'text', text: `Unknown tool: ${name}` }], isError: true };
    }
  } catch (err) {
    return { content: [{ type: 'text', text: `Error: ${err.message}` }], isError: true };
  }
});

async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
}

main().catch(err => {
  process.stderr.write(`Fatal: ${err.message}\n`);
  process.exit(1);
});
