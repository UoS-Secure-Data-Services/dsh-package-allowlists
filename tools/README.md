# add-pypi-dependencies.py

A Python script to fetch and merge PyPI dependencies for packages listed in a requirements file.

## Description

This script reads a `requirements.txt` style PyPI file, queries the PyPI API for each package's dependencies, and merges them with any existing dependencies in a target output file.

## Usage

```bash
python add-pypi-dependencies.py [options]
```

- `-r, --requirements FILE`: Input requirements file path (default: `requirements.txt`)
- `-o, --output FILE`: Output dependency file path (default: `../nexus/pypi.allowlist`)
