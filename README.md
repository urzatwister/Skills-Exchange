# Nexus M2M Skill Exchange

An autonomous marketplace for AI-to-AI skill discovery, verification, and commerce. Nexus enables AI agents to discover, audit, purchase, and execute specialized skills from other developers in a trustless, automated environment.

## Features

- **Semantic Discovery**: Natural language search powered by vector embeddings to find the most relevant skills
- **Safu Security**: Multi-stage automated code audits that scan for malicious patterns before execution
- **Auto Revenue**: Cryptographic proofs of execution with automated 80/20 developer-platform revenue splits
- **CLI & Web Interface**: Both command-line and web-based interfaces for skill discovery and management

## Project Structure

```
├── app/                    # Next.js frontend application
│   ├── api/               # API routes
│   ├── components/        # React components
│   ├── dashboard/         # Dashboard pages
│   ├── developers/        # Developer pages
│   ├── layout.tsx         # Root layout
│   └── page.tsx          # Home page
├── nexus-cli/             # CLI tool for skill discovery and installation
├── nexus-api/             # Backend API service
├── docs/                  # Documentation
└── package.json           # Project dependencies
```

## Getting Started

### Prerequisites

- Node.js 18+
- npm, yarn, pnpm, or bun

### Installation & Running Locally

This project consists of two parts running concurrently: a **Next.js frontend** and a **Python FastAPI backend**.

#### 1. Start the API Backend
The Next.js frontend relies on the backend API running on `localhost:8000`.

```bash
cd nexus-api
pip install -r requirements.txt
python -m uvicorn main:app --reload --port 8000
```

#### 2. Start the Web Frontend
In a new terminal window, from the root directory:

```bash
npm install
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser to see the application.

## Development

### Available Scripts

- `npm run dev` - Start the development server
- `npm run build` - Build the production bundle
- `npm start` - Start the production server
- `npm run lint` - Run ESLint

### Tech Stack

- **Framework**: [Next.js](https://nextjs.org) 16.1.6
- **UI**: React 19.2.3 with [Tailwind CSS](https://tailwindcss.com)
- **Language**: TypeScript 5
- **CLI**: Commander.js with Chalk and Ora for interactive terminal experience

## CLI Usage

The `nexus-skill` CLI tool provides command-line access to the skill marketplace:

```bash
nexus-skill search "your intent here"
```

For more information, see the [nexus-cli documentation](./nexus-cli/README.md).

## Architecture

### Frontend (Next.js)

The web interface provides:
- Home page with marketplace overview
- Skill search and discovery
- Developer dashboard for skill analytics
- Skill details and installation interface

### Backend (nexus-api)

Handles:
- Skill indexing and search
- Security scanning and verification
- Revenue tracking and splits
- Skill execution proofs

### CLI (nexus-cli)

Enables:
- Skill discovery from terminal
- Skill installation and dependency management
- Skill publishing and updates

## Security

All skills undergo multi-stage automated audits before execution:
- Pattern scanning for malicious code
- Dependency analysis
- Execution environment sandboxing
- Proof-of-execution verification

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](./CONTRIBUTING.md) for guidelines.

## License

See LICENSE file for details.

## Learn More

- [Next.js Documentation](https://nextjs.org/docs)
- [Tailwind CSS Documentation](https://tailwindcss.com/docs)
- Skill specification: [SKILL.md.example](./docs/SKILL.md.example)
