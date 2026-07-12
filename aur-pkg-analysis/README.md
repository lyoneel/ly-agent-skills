# AUR Package Analysis

A skill for cleaning up AUR packages on Arch Linux.

Run it and it will go through every AUR package on your system, one by one, and tell you:

- What the package actually does
- What depends on it
- Whether it has an official alternative (Flatpak, official Arch repo, pip, Go, Cargo)
- Whether the upstream project is still maintained
- Whether the AUR maintainer is reputable
- How to remove it and what to replace it with

It's meant for periodic system cleanup — finding AUR packages you can drop in favor of official alternatives, removing abandoned packages, and consolidating versioned duplicates.
