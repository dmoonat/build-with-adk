# AI Context Files

This folder contains context files optimized for AI coding assistants. Use the file that matches your preferred tool.

## Quick Reference

| Your Tool | File | To Activate |
|-----------|------|-------------|
| **Claude Code** | `CLAUDE.md` | Copy to project root |
| **Gemini CLI** | `GEMINI.md` | Copy to project root |
| **Cursor** | `.cursor/rules/` | Copy to project root |
| **GitHub Copilot** | `.github/` | Copy to project root |
| **OpenAI Codex / Jules** | `AGENTS.md` | Copy to project root |
| **Any LLM** | `llms.txt` | Use directly |

**All context files are in this `.ai/` folder.** Copy the ones you need to your project root to activate them.

## Files in This Folder

### Main Context Files

- **`CLAUDE.md`** - Claude Code context with quick start, architecture, and common tasks
- **`GEMINI.md`** - Gemini CLI context with @import references to shared modules
- **`AGENTS.md`** - Universal format for OpenAI Codex, Copilot, Cursor, Jules
- **`llms.txt`** - Minimal LLM-optimized summary for any AI assistant

### Shared Context Modules (`context/`)

- **`architecture.md`** - Pipeline flow diagram and file structure
- **`commands.md`** - All Makefile commands with descriptions
- **`agents.md`** - Detailed reference for each agent
- **`tools.md`** - Custom tools documentation
- **`state-keys.md`** - Session state key reference
- **`common-tasks.md`** - Step-by-step guides for adding agents, tools, callbacks
- **`troubleshooting.md`** - Common errors and fixes

## Learning Resources

### Tutorial Series

The `blog/` directory contains a 9-part progressive tutorial:

1. **Part 1**: Setup and First Agent
2. **Part 2**: IntakeAgent - Request parsing
3. **Part 3**: MarketResearchAgent - Google Search
4. **Part 4**: CompetitorMappingAgent - Google Maps API
5. **Part 5**: GapAnalysisAgent - Code execution
6. **Part 6**: StrategyAdvisorAgent - Extended reasoning
7. **Part 7**: ArtifactGenerationPipeline - Multimodal outputs
8. **Part 8**: Testing your agent
9. **Part 9**: Production deployment
10. **Bonus**: AG-UI interactive frontend

### Documentation

- **`DEVELOPER_GUIDE.md`** - Deep architecture documentation
- **ADK Docs**: https://google.github.io/adk-docs/

## Quick Start

```bash
# Install dependencies
make install

# Run agent at localhost:8501
make dev

# Run tests
make test-unit
```

## Claude Code Slash Commands

The `.claude/commands/` folder contains slash commands for Claude Code:

- `/add-agent` - Guide for adding a new agent
- `/add-tool` - Guide for adding a new tool
- `/run-tests` - Run the test suite
- `/explain-pipeline` - Explain the agent pipeline

To use: copy `.ai/.claude/` to your project's root `.claude/` folder, or symlink it.

## How to Use These Files

All AI context files are stored in this `.ai/` folder. To use them:

### Claude Code
```bash
cp .ai/CLAUDE.md ./CLAUDE.md
cp -r .ai/.claude ./.claude
```
Claude Code automatically reads `CLAUDE.md` at project root.

### Gemini CLI
```bash
cp .ai/GEMINI.md ./GEMINI.md
```
Run `/memory add file:GEMINI.md` to add to memory.

### Cursor
```bash
cp -r .ai/.cursor ./.cursor
```
Cursor reads `.cursor/rules/*.mdc` files automatically.

### GitHub Copilot
```bash
cp -r .ai/.github ./.github
```
Copilot reads `.github/copilot-instructions.md` automatically.

### OpenAI Codex / Jules
```bash
cp .ai/AGENTS.md ./AGENTS.md
```
Follows the universal AGENTS.md specification.

## Contributing

When updating agent architecture:
1. Update `context/architecture.md` with new pipeline flow
2. Update `context/agents.md` with agent details
3. Update `context/state-keys.md` if new state keys added
4. Update main context files (CLAUDE.md, GEMINI.md, AGENTS.md)
