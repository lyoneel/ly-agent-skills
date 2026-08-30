# AUR Package Analysis

A skill for cleaning up AUR packages on Arch Linux. It walks every installed AUR package one by one and reports what each one does, what depends on it, whether an official alternative exists, and how to remove it. It is meant for periodic system cleanup.

## Features

- Reports what each package does and what depends on it
- Finds official alternatives (official Arch repo, Flatpak, pip, Go, Cargo)
- Checks whether upstream is still maintained and the AUR maintainer is reputable
- Detects versioned duplicates and plugin packages that have pre-built binaries
- Produces removal commands and replacement install commands

## Prerequisites

- Arch Linux with `pacman` available

## License

See the project root LICENSE.