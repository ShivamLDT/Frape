# Beam - SaaS-Ready Frappe Management Tool

Beam is a wrapper around Frappe Bench that provides all the functionality of bench while adding extensibility for SaaS-specific features. End users interact with `beam` commands without needing to know about the underlying `bench` implementation.

## Features

- ✅ **Full Bench Compatibility**: All bench commands work through beam
- ✅ **SaaS Extensibility**: Easy to add custom SaaS commands
- ✅ **Transparent Wrapper**: Bench functionality is preserved exactly
- ✅ **Cross-Platform**: Works on Linux, macOS, and Windows (via WSL)

## Installation

### Development Installation

```bash
# Clone the repository
git clone <your-repo-url> beam
cd beam

# Install in development mode
pip install -e .
```

This will automatically install `frappe-bench` as a dependency.

### Production Installation

```bash
pip install beam-cli
```

## Usage

### Basic Commands (All Bench Commands Work)

```bash
# Initialize a new beam instance
beam init my-app

# Create a new site
beam new-site example.com

# Start development server
beam start

# Get and install apps
beam get-app erpnext https://github.com/frappe/erpnext
beam --site example.com install-app erpnext

# Update everything
beam update

# Setup production
beam setup production user

# All other bench commands work the same way
```

### SaaS Commands (Extensible)

```bash
# Deploy to cloud
beam deploy production

# Scale resources
beam scale up

# Monitor health
beam monitor

# View logs
beam logs

# Check status
beam status

# Get SaaS help
beam saas --help
```

## Extending Beam with Custom SaaS Commands

The SaaS commands are designed to be easily extensible. Modify the files in `beam/beam/saas/`:

1. **Add a new command**: Create a new file in `beam/beam/saas/`
2. **Register it**: Add it to `is_saas_command()` and `handle_saas_command()` in `beam/cli.py`
3. **Implement logic**: Add your custom SaaS functionality

## Architecture

```
beam/
├── beam/
│   ├── __init__.py          # Package metadata
│   ├── cli.py               # Main CLI entry point
│   ├── install_wsl.py       # WSL auto-install helper
│   └── saas/                # SaaS-specific commands
│       ├── __init__.py
│       ├── deploy.py
│       ├── scale.py
│       ├── monitor.py
│       ├── logs.py
│       ├── status.py
│       └── saas_help.py
├── setup.py                 # Package setup
├── pyproject.toml           # Modern Python packaging
└── README.md
```

## Requirements

- Python 3.10+
- frappe-bench (installed automatically as dependency)

## License

MIT License

## Contributing

Contributions are welcome! Please see CONTRIBUTING.md for guidelines.

