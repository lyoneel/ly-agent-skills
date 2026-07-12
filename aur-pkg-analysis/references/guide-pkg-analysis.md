# Package Analysis Guide

## Reading the package list

When reading the input file:
- Skip lines starting with `#` (already analyzed/done)
- Skip empty lines
- Process each remaining line as one package

## Tracking progress

After each package is analyzed:
- Add `# ` prefix to the package line in the input file
- Example: `accounts-qml-module` becomes `# accounts-qml-module`
- This allows resuming across sessions without re-processing

## Step-by-step workflow for analyzing one AUR package

### Step 1: Get package info

Search the AUR for the package:
- Query: `site:aur.archlinux.org <pkg-name>`
- Extract: description, dependencies, reverse dependencies (Required-By)

### Step 2: Check official repos

Search Arch Linux official packages:
- Query: `site:archlinux.org/packages <pkg-name>`
- If found in `[core]`, `[extra]`, or `[community]`, note it as official alternative

### Step 3: Check flatpak alternatives

Search for flatpak equivalents:
- Query: `flathub <app-name>` or `<app-name> flatpak`
- Check `https://flathub.org` for matching flatpak ID
- Note the flatpak install ID if found

### Step 4: Check pip alternatives

For Python tools:
- Query: `pypi <tool-name>` or `<tool-name> pip install`
- Check `https://pypi.org` for matching package
- Note the pip install command if found

### Step 5: Determine reverse dependencies

From AUR page or web search:
- Check "Required-By" section on AUR page
- Search for packages that list it as a dependency
- Note if it's a standalone app with no dependents

### Step 6: Output results

Present results in the standard format defined in SKILL.md. Always include:
- Package description
- Reverse dependencies
- Alternative availability (flatpak/pip/official)
- Removal command: `sudo pacman -Rns <pkg-name>`
- Alternative install commands when applicable
