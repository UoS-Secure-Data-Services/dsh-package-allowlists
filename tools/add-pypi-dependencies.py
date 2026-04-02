import argparse
import re
import requests


def strip_version(dep):
    dep = dep.strip()
    if not dep or dep.startswith("#"):
        return ""
    # remove inline comment
    dep = dep.split("#", 1)[0].strip()
    # pip syntax allows 'pkg[extra]>=1.2', 'pkg==1.2', 'pkg @ https://...'
    # handle URL-based spec by taking package name before '@'
    if "@" in dep:
        dep = dep.split("@", 1)[0].strip()

    match = re.match(r"([a-zA-Z0-9._-]+(?:\[[^\]]*\])?)", dep)
    if match:
        return match.group(1)
    return dep


def load_requirements(path):
    packages = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            pkg = strip_version(line)
            if pkg:
                packages.append(pkg)
    return packages


def query_pypi_requires(packages):
    deps = set()
    for package in sorted(set(packages)):
        try:
            url = f"https://pypi.python.org/pypi/{package}/json"
            resp = requests.get(url, timeout=30)
            resp.raise_for_status()
            data = resp.json()
            reqs = data.get("info", {}).get("requires_dist")
            if reqs:
                for req in reqs:
                    stripped = strip_version(req)
                    if stripped:
                        deps.add(stripped)
        except Exception as e:
            print(f"Warning: could not get requirements for {package}: {e}")
    return deps


def load_existing(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return set(line.strip() for line in f if line.strip())
    except FileNotFoundError:
        return set()


def main():
    parser = argparse.ArgumentParser(
        description="Fetch dependencies from PyPI and merge with a target file"
    )
    parser.add_argument(
        "--requirements",
        "-r",
        default="requirements.txt",
        help="Input requirements file path",
    )
    parser.add_argument(
        "--output", "-o", default="../nexus/pypi.allowlist", help="Output dependency file path"
    )
    args = parser.parse_args()

    req_packages = load_requirements(args.requirements)
    print(f"Loaded {len(req_packages)} packages from {args.requirements}")
    pypi_deps = query_pypi_requires(req_packages)
    existing = load_existing(args.output)
    all_items = set(req_packages) | pypi_deps | existing

    with open(args.output, "w", encoding="utf-8") as f:
        for item in sorted(all_items, key=str.casefold):
            f.write(item + "\n")

    new_items = all_items - existing
    print(
        f"Added {len(new_items)} new packages to {args.output}"
    )


if __name__ == "__main__":
    main()
