# Alternative Detection Guide

## Flatpak alternatives

### Search methods
1. Search Flathub: `flathub <app-name>` or visit `https://flathub.org`
2. Search by desktop file name: `<app-name>.desktop flatpak`
3. Check freedesktop wiki for known equivalents

### Verification (MANDATORY for flatpak alternatives)

**Step 1 — Check Flathub API for verification metadata:**
1. Fetch `https://flathub.org/api/v2/appstream/<flatpak-id>?architecture=x86_64&branch=stable`
2. Look for `flathub::verification::verified: true` in `metadata`
3. **If verified=true**: Official flatpak — show "Flatpak alt: yes" + `flatpak install` command
4. **If verified=false or missing**: Check Flathub web page for disclaimer text

**Step 2 — Check Flathub web page (fallback):**
1. Visit `https://flathub.org/apps/<flatpak-id>`
2. Search for disclaimer: "This wrapper is not verified by, affiliated with, or supported by"
3. **Disclaimer present**: Community-maintained — list under "Unofficial Install Methods"
4. **No disclaimer + no API data**: Treat as community-maintained (conservative default)

**Decision table:**

| API `verified` | Disclaimer | Classification | Output location |
|---|---|---|---|
| true | — | Official | "Flatpak alt: yes" + Commands |
| false/missing | Present | Community | "Unofficial Install Methods" |
| false/missing | Absent | Community (conservative) | "Unofficial Install Methods" |

### Common patterns

### Install command format
```
flatpak install flathub <flatpak-id>
```

## pip alternatives

### Search methods
1. Search PyPI: `pypi <tool-name>` or visit `https://pypi.org`
2. Check if the AUR package is a Python `-venv` or `-bin` variant
3. Look for `pip install` in AUR PKGBUILD

### Common patterns
- `*-venv` packages: always have pip equivalent
- `*-bin` packages: check if pip version exists
- CLI tools: search pypi.org directly

### Install command format
```
pip install --user <pip-package-name>
```

## Official Arch repo alternatives

### Search methods
1. Search `site:archlinux.org/packages <pkg-name>`
2. Check if package was recently removed from official repos
3. Check if AUR is orphaned (original maintainer dropped it)

### Common patterns
- Packages moved from official repos to AUR (check forum.endeavouros.com or reddit r/archlinux)
- Downgraded libraries (e.g., `boost1.86`, `gcc13`)
- Orphaned packages waiting for adoption

## When alternatives don't exist

Some packages have no alternatives:
- Custom/patched versions of upstream software
- Hardware-specific drivers (DKMS)
- Niche development tools
- Legacy compatibility libraries

In these cases, note "No flatpak/pip alternative available" and recommend keeping the package or removing if unused.
