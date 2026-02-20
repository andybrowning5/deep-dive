# Deep Dive

A [Primordial AgentStore](https://github.com/andybrowning5/AgentStore) agent that searches the web for real-time information and synthesizes concise, sourced briefings.

## What it does

Ask about any topic — news, tech, science, people, companies — and Deep Dive will:

1. Search the web via Brave Search API
2. Synthesize results into a well-structured briefing using Claude
3. Include inline citations and a sources section

## Usage

```bash
pip install primordial-agentstore
primordial run https://github.com/andybrowning5/deep-dive
```

## API Keys Required

- **Anthropic** — for Claude inference ([anthropic.com](https://console.anthropic.com))
- **Brave Search** — for web search ([brave.com/search/api](https://brave.com/search/api/))

## Example

```
> What's the latest on quantum computing?

## Quantum Computing: Current State (Feb 2025)

Recent developments in quantum computing show significant progress across
multiple fronts...

[1] Google's Willow chip demonstrated error correction below the threshold...
[2] IBM announced its 1,121-qubit Condor processor...

### Sources
1. [Google Quantum AI Blog](https://blog.google/technology/quantum/)
2. [IBM Quantum Roadmap](https://www.ibm.com/quantum/roadmap)
...
```
