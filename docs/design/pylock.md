# PEP 751 pylock.toml Support

## Problem

Hermeto currently supports `requirements.txt` for Python dependencies. However,
users increasingly generate lockfiles with tools like poetry, pipenv, and uv,
which produce incompatible formats (`poetry.lock`, `Pipfile.lock`, `uv.lock`).

This forces hermeto users to:

- Generate `requirements.txt` from their tool's lockfile as an intermediate
  step
- Lose attestation/provenance information in the conversion
- Manually maintain two files (lockfile + requirements.txt)

Additionally, using `requirements.txt` as a pseudo-lockfile has limitations:

- No format versioning (hermeto cannot detect schema changes)
- Hashes are line-based, not per-artifact (cannot distinguish wheel vs sdist
  hashes)
- No native attestation support (PEP 740)

## Goals

Support a standardized lockfile format that tools can generate directly,
preserving all metadata.

## PEP 751 Standard

[PEP 751](https://peps.python.org/pep-0751/) defines `pylock.toml`, a
standardized lockfile format. Key features hermeto needs:

1. Format versioning: `lock-version` field enables hermeto to handle
   schema evolution
2. Per-artifact hashes: Hashes nested in distribution objects (wheel,
   sdist, archive)
3. Attestation support: `attestation-identities` field (PEP 740)
4. Multiple package sources: PyPI, VCS, direct URLs, local directories
5. TOML structure: Easy to parse, better than line-based text

### Lockfile Structure

```toml
lock-version = "1.0"

[[packages]]
name = "foo"
version = "1.0.0"
sdist = { url = "https://...", hashes = { "sha256" = "..." } }
wheels = [
    { url = "https://...", hashes = { "sha256" = "..." } }
]
```

### Package Kinds Hermeto Must Support

#### PyPI Packages

```toml
[[packages]]
name = "foo"
version = "1.0.0"
index = "https://pypi.org/simple/"  # Optional, defaults to PyPI
sdist = { url = "...", hashes = { "sha256" = "..." } }
wheels = [{ url = "...", hashes = { "sha256" = "..." } }]
```

#### VCS Packages

```toml
[[packages]]
name = "foo"
vcs = { url = "https://github.com/user/repo.git", rev = "abc123" }
```

#### URL Packages

```toml
[[packages]]
name = "foo"
archive = { url = "https://example.com/pkg.tar.gz", hashes = { ... } }
```

#### Directory Packages

```toml
[[packages]]
name = "foo"
directory = { path = "./local-pkg" }
```

#### Attestation Support

```toml
[[packages]]
name = "foo"
attestation-identities = [
    { kind = "..." }
]
```

Hermeto should add these to SBOM output.

## Design Considerations

### Parser Architecture

#### Option 1: Extend requirements.txt parser

- Pro: Less code
- Con: TOML vs line-based are fundamentally different
- Con: Nested hash extraction becomes awkward
- Con: Attestations would be bolted on

#### Option 2: Separate pylock parser

- Pro: Clean separation, follows PEP 751 spec naturally
- Pro: Attestations are built into the TOML format
- Con: More code to maintain

#### Option 3: Hybrid approach (preferred)

- Pro: Reuses download/processing logic from PipRequirement
- Pro: Clean separation for TOML parsing
- Pro: Attestations are built into the TOML format
- Con: More code than extending requirements.txt parser

### Key Design Decisions

#### 1. Lockfile Priority

Question: When both pylock.toml and requirements.txt exist, which to use?

Options:

- A. Error out
  - Con: Annoying during migration
- B. Pylock takes precedence (preferred)
  - Pro: Clear migration path
  - Con: Silent behavior change
- C. Merge both
  - Con: Defeats lockfile purpose
  - Con: Complex semantics

Preferred approach: B. Pylock takes precedence

Rationale:

- Users adding pylock.toml want hermeto to use it
- Clear migration: add pylock.toml - hermeto auto-detects it

#### 2. Version Tolerance

Per PEP 751:

- Unknown major version -> error (incompatible)
- Unknown minor version -> warning, continue (forward compatible)

Implementation:

```python
SUPPORTED_LOCK_MAJOR = 1
SUPPORTED_LOCK_MINOR = 0

if version.major != SUPPORTED_LOCK_MAJOR:
    raise InvalidLockfileFormat(...)
if version.minor != SUPPORTED_LOCK_MINOR:
    log.warning("Unknown minor version, continuing...")
```

#### 3. Hash Extraction

Challenge: Pylock nests hashes in distribution objects (wheels, sdist,
archive), unlike requirements.txt where hashes are top-level.

Approach:

- Extract hashes from all distribution types
- Flatten into `PipRequirement.hashes` list
- Format as `algorithm:digest`
- Reuse existing hash validation infrastructure

## Implementation Overview

### Architecture

- `PipRequirement`: Base class providing download, hash validation, and
  processing logic. Has a `from_line()` method for parsing requirements.txt
  format.
- `PyLockPackage`: Extends PipRequirement with a `from_dict()` method for
  parsing pylock.toml TOML format.

This design allows pylock to reuse existing pip infrastructure (download
handling, hash verification, Rust extension detection) while providing a
separate parser for the TOML-based format.

### Components

1. `PyLockFile` - Parses pylock.toml, validates version, extracts packages
2. `PyLockPackage` - Extends PipRequirement with pylock-specific parsing
3. `_download_pylock_dependencies()` - Entry point for pylock processing

### Integration

- Input: Add `pylock_files` and `pylock_build_files` to `PipPackageInput`
- Resolution: Check pylock files before requirements.txt
- Downloads: Route packages by kind (pypi, vcs, url, directory)
- SBOM: Preserve attestation-identities

### Processing Flow

1. `fetch_pip_source()` checks for pylock files
2. If pylock files exist:
   - Call `_download_from_pylock_files()`
   - Route packages by kind to appropriate processors:
     - PyPI packages -> `_process_pypi_req()`
     - VCS packages -> `_process_vcs_req()`
     - URL packages -> `_process_url_req()`
     - Directory packages -> `_process_directory_req()`
3. If no pylock files, call `_download_from_requirement_files()`
4. Both paths converge at `filter_packages_with_rust_code()`
5. Return `RequestOutput`

## Security Considerations

1. Path traversal: Validate directory package paths stay within repo
2. Hash verification: All downloads verified against lockfile hashes
3. Attestation preservation: Store in SBOM (verification is future work)
4. Trusted sources: VCS/directory are trusted; URL requires hashes

## References

- [PEP 751](https://peps.python.org/pep-0751/) - Lockfile specification
- [PEP 740](https://peps.python.org/pep-0740/) - Attestation identities
- [uv documentation](https://docs.astral.sh/uv/) - Reference implementation
