import json

import requests
from django.core.management.base import BaseCommand

from software.models import InstallomatorLabel


class Command(BaseCommand):
    help = "Download and load Installomator labels from GitHub"

    def add_arguments(self, parser):
        parser.add_argument(
            "--version",
            type=str,
            default="11.0",
            help="Installomator version to fetch (default: 11.0)",
        )

    def handle(self, *args, **kwargs):
        version = kwargs["version"]

        # Download Labels.txt from GitHub
        url = "https://raw.githubusercontent.com/Installomator/Installomator/main/Labels.txt"

        self.stdout.write(f"Downloading Installomator labels from GitHub...")
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Failed to download: {e}"))
            return

        # Parse labels (one per line)
        label_names = [
            line.strip()
            for line in response.text.split("\n")
            if line.strip() and not line.startswith("#")
        ]

        self.stdout.write(f"Parsing {len(label_names)} labels...")

        # Build label objects with metadata
        labels = []
        for name in label_names:
            labels.append(
                {
                    "name": name,
                    "display_name": self.format_display_name(name),
                    "category": self.categorize_label(name),
                    "bundle_id": None,  # TODO: Parse from Installomator.sh
                    "type": "dmg",  # Default
                    "description": f"Install {self.format_display_name(name)}",
                }
            )

        # Save to database
        if InstallomatorLabel.objects.exists():
            InstallomatorLabel.objects.all().delete()
            self.stdout.write("Removed existing labels")

        InstallomatorLabel(labels=labels, version=version).save()

        self.stdout.write(
            self.style.SUCCESS(
                f"Successfully loaded {len(labels)} Installomator labels (v{version})"
            )
        )

    def format_display_name(self, name):
        """Convert label name to display name"""
        # Remove version numbers
        import re

        clean_name = re.sub(r"\d+$", "", name)
        # Title case and replace underscores
        return clean_name.replace("_", " ").title()

    def categorize_label(self, name):
        """Simple categorization based on name patterns"""
        name_lower = name.lower()

        # Browsers
        if any(
            x in name_lower
            for x in [
                "chrome",
                "firefox",
                "safari",
                "edge",
                "brave",
                "opera",
                "vivaldi",
            ]
        ):
            return "browsers"

        # Development tools
        elif any(
            x in name_lower
            for x in [
                "vscode",
                "sublime",
                "atom",
                "intellij",
                "pycharm",
                "webstorm",
                "phpstorm",
                "goland",
                "rider",
                "clion",
                "datagrip",
                "rubymine",
                "android-studio",
                "xcode",
                "docker",
                "git",
                "sourcetree",
                "postman",
                "insomnia",
                "iterm",
                "termius",
                "terminal",
            ]
        ):
            return "development"

        # Communication
        elif any(
            x in name_lower
            for x in [
                "slack",
                "zoom",
                "teams",
                "discord",
                "skype",
                "telegram",
                "signal",
                "whatsapp",
                "messenger",
                "chime",
            ]
        ):
            return "communication"

        # Design/Creative
        elif any(
            x in name_lower
            for x in [
                "adobe",
                "affinity",
                "sketch",
                "figma",
                "blender",
                "gimp",
                "inkscape",
                "photoshop",
                "illustrator",
                "lightroom",
                "premiere",
                "aftereffects",
            ]
        ):
            return "design"

        # Productivity
        elif any(
            x in name_lower
            for x in [
                "notion",
                "evernote",
                "onenote",
                "todoist",
                "trello",
                "asana",
                "monday",
                "airtable",
                "coda",
                "obsidian",
                "bear",
            ]
        ):
            return "productivity"

        # Media
        elif any(
            x in name_lower
            for x in [
                "spotify",
                "vlc",
                "itunes",
                "plex",
                "kodi",
                "handbrake",
                "audacity",
            ]
        ):
            return "media"

        # Security/VPN
        elif any(
            x in name_lower
            for x in [
                "vpn",
                "nordvpn",
                "expressvpn",
                "tunnelbear",
                "1password",
                "lastpass",
                "bitwarden",
                "keepass",
                "cryptomator",
            ]
        ):
            return "security"

        # Office/Business
        elif any(
            x in name_lower
            for x in [
                "office",
                "microsoft365",
                "word",
                "excel",
                "powerpoint",
                "outlook",
            ]
        ):
            return "office"

        # Utilities
        elif any(
            x in name_lower
            for x in [
                "alfred",
                "bartender",
                "bettertouchtool",
                "cleanmymac",
                "appcleaner",
                "hazel",
                "karabiner",
                "rectangle",
                "magnet",
            ]
        ):
            return "utilities"

        # Default
        else:
            return "general"
