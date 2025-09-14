from logging import fatal
from includes.logger import logger, log_heading
from includes.paths import USER_CONFIGS_DIR, USER_DOTFILES_DIR, HYPRDOTS_DOTFILES_DIR
from includes.library import remove, create_symlink, path_lexists, copy
from includes.tui import print_header, Spinner

from pathlib import Path
from typing import List, Tuple
from time import sleep
from subprocess import run as run_command


class DotfilesInstaller:
    def __init__(self, dry_run: bool = False):
        self.dry_run = dry_run
        self.dotfiles_components = [
            "hypr",
            "waybar",
            "rofi",
            "fish",
            "kitty",
            "neofetch",
            "fastfetch",
            "cava",
            "waypaper",
            "swaync",
            "btop",
            "wlogout",
            "atuin",
            "tmux",
            "starship.toml",
        ]

        self.source_dotfiles_components_paths = [
            HYPRDOTS_DOTFILES_DIR / i for i in self.dotfiles_components
        ]
        self.target_dotfiles_components_paths = [
            USER_DOTFILES_DIR / i for i in self.dotfiles_components
        ]

    def install(self):
        log_heading("Dotfiles installer started")
        print_header("Installing dotfiles.")

        with Spinner("Installing dotfiles...") as spinner:
            # Step 1: Check if source files exists
            if not self._validate_sources(spinner):
                return False
            # Step 2: Copy Dotfiles
            if not self._copy_dotfiles(spinner):
                return False
            # Step 3: Check if Dotfiles copied or not
            if not self._verify_copy(spinner):
                return False
            # Step 4: Remove existing old configs
            if not self._remove_existing_configs(spinner):
                return False
            # Step 5: Link the new Dotfiles
            if not self._create_links(spinner):
                return False

            sleep(1)
            spinner.success("Dotfiles installed successfully!")

        with Spinner("Installing third-party dots...") as spinner:
            if not self._install_tpm(spinner):
                return False
            if not self._install_lazyvim(spinner):
                return False

        print()
        return True

    def _install_lazyvim(self, spinner) -> bool:
        """Install LazyVim"""
        logger.info("Installing LazyVim")
        spinner.update_text("Installing LazyVim...")

        if self.dry_run:
            sleep(2)
            return True

        lazyvim_dir = USER_DOTFILES_DIR / "nvim"

        # Remove existing nvim config if exists
        if lazyvim_dir.exists():
            remove(lazyvim_dir)

        # Backup existing nvim config if it exists
        nvim_config_dir = USER_CONFIGS_DIR / "nvim"
        if nvim_config_dir.exists():
            backup_dir = USER_CONFIGS_DIR / "nvim.backup"
            if backup_dir.exists():
                remove(backup_dir)
            nvim_config_dir.rename(backup_dir)
            logger.info(f"Backed up existing nvim config to {backup_dir}")

        # Clone LazyVim starter template
        try:
            run_command(
                [
                    "git",
                    "clone",
                    "https://github.com/LazyVim/starter",
                    str(lazyvim_dir),
                ],
                check=True,
                capture_output=True,
            )

            # Remove .git directory to avoid conflicts
            git_dir = lazyvim_dir / ".git"
            if git_dir.exists():
                remove(git_dir)

            logger.info("LazyVim installed successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to install LazyVim: {e}")
            spinner.error("Failed to install LazyVim")
            return False

    def _install_tpm(self, spinner) -> bool:
        """Install Tmux Plugin Manager"""
        logger.info("Installing TPM (Tmux Plugin Manager)")
        spinner.update_text("Installing TPM for tmux...")

        if self.dry_run:
            sleep(2)
            return True

        tpm_dir = USER_DOTFILES_DIR / "tmux" / "plugins" / "tpm"

        # Remove existing TPM if exists
        if tpm_dir.exists():
            remove(tpm_dir)

        # Clone TPM repository
        try:
            run_command(
                [
                    "git",
                    "clone",
                    "https://github.com/tmux-plugins/tpm.git",
                    str(tpm_dir),
                ],
                check=True,
                capture_output=True,
            )
            logger.info("TPM installed successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to install TPM: {e}")
            spinner.error("Failed to install TPM for tmux")
            return False

    def _validate_sources(self, spinner) -> bool:
        logger.info("Validating source dotfiles components.")
        spinner.update_text("Validating source dotfiles components...")
        if self.dry_run:
            sleep(2)
            return True
        for i in self.source_dotfiles_components_paths:
            if not path_lexists(i):
                logger.error(f"Missing source: {i}.")
                spinner.error(f"Missing source: {i}, exiting...")
                return False
        return True

    def _copy_dotfiles(self, spinner) -> bool:
        logger.info(f"Copying dotfiles to {USER_DOTFILES_DIR}")
        spinner.update_text("Copying dotfiles...")

        if self.dry_run:
            sleep(2)
            return True

        logger.info("Creating dotfiles dir...")
        if USER_DOTFILES_DIR.exists():
            logger.info("Dotfiles dir already exists, removing it...")
            remove(USER_DOTFILES_DIR)

        logger.info("Copying...")
        try:
            copy(HYPRDOTS_DOTFILES_DIR, USER_DOTFILES_DIR)
        except Exception as e:
            logger.error(f"Failed to copy dotfiles: {e}")
            spinner.error("Failed to copy dotfiles.")
            return False
        return True

    def _verify_copy(self, spinner) -> bool:
        logger.info("Checking if copied successfully or not.")

        if self.dry_run:
            return True

        missing: list = []
        for i in self.target_dotfiles_components_paths:
            if not path_lexists(i):
                logger.error(f"Copied dotfile component {i} is missing.")
                missing.append(i)

        if missing:
            spinner.error(f"Some dotfile components are missing, exiting...")
            return False

        return True

    def _remove_existing_configs(self, spinner) -> bool:
        logger.info("Removing existing configs.")
        spinner.update_text("Removing existing configs...")

        if self.dry_run:
            sleep(2)
            return True

        for i in self.dotfiles_components:
            file: Path = USER_CONFIGS_DIR / i
            if not remove(file):
                spinner.error(f"Failed to remove existing config: {file}.")
                return False
        return True

    def _create_links(self, spinner) -> bool:
        logger.info("Creating system links.")
        spinner.update_text("Linking new dotfiles...")

        if self.dry_run:
            sleep(2)
            return True

        failed_links: List[Tuple[Path, Path]] = []
        for component in self.dotfiles_components:
            source: Path = USER_DOTFILES_DIR / component
            target: Path = USER_CONFIGS_DIR / component
            if not create_symlink(source, target):
                logger.error(f"Failed to link {source} to {target}.")
                failed_links.append((source, target))

        if failed_links:
            spinner.error("Failed to create some links, exiting...")
            return False

        return True
