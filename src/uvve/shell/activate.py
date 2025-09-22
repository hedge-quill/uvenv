"""Shell activation script generation for uvve."""

import os
from pathlib import Path

from uvve.core.paths import PathManager


class ActivationManager:
    """Manages shell activation scripts for virtual environments."""

    def __init__(self, base_dir: str | None = None) -> None:
        """Initialize the activation manager.

        Args:
            base_dir: Base directory for environments
        """
        self.path_manager = PathManager(base_dir)

    def get_activation_script(self, name: str, shell: str | None = None) -> str:
        """Generate activation script for a given environment and shell.

        Args:
            name: Environment name
            shell: Shell type (bash, zsh, fish, etc.). Auto-detected if None

        Returns:
            Shell activation script

        Raises:
            RuntimeError: If environment doesn't exist
        """
        if not self.path_manager.environment_exists(name):
            raise RuntimeError(f"Environment '{name}' does not exist")

        if shell is None:
            shell = self._detect_shell()

        bin_path = self.path_manager.get_env_bin_path(name)

        if shell in ("bash", "zsh"):
            return self._generate_bash_script(bin_path)
        if shell == "fish":
            return self._generate_fish_script(bin_path)
        if shell == "powershell":
            return self._generate_powershell_script(bin_path)
        # Default to bash-compatible
        return self._generate_bash_script(bin_path)

    def get_deactivation_script(self, shell: str | None = None) -> str:
        """Generate deactivation script.

        Args:
            shell: Shell type. Auto-detected if None

        Returns:
            Shell deactivation script
        """
        if shell is None:
            shell = self._detect_shell()

        if shell in ("bash", "zsh"):
            return "deactivate"
        if shell == "fish":
            return "deactivate"
        if shell == "powershell":
            return "deactivate"
        return "deactivate"

    def _detect_shell(self) -> str:
        """Detect the current shell.

        Returns:
            Shell name
        """
        shell_env = os.environ.get("SHELL", "")

        if "bash" in shell_env:
            return "bash"
        if "zsh" in shell_env:
            return "zsh"
        if "fish" in shell_env:
            return "fish"
        if os.name == "nt":
            return "powershell"
        return "bash"  # Default

    def _generate_bash_script(self, bin_path: Path) -> str:
        """Generate bash/zsh activation script.

        Args:
            bin_path: Path to environment bin directory

        Returns:
            Bash activation script
        """
        activate_script = bin_path / "activate"
        return f"source {activate_script}"

    def _generate_fish_script(self, bin_path: Path) -> str:
        """Generate fish activation script.

        Args:
            bin_path: Path to environment bin directory

        Returns:
            Fish activation script
        """
        activate_script = bin_path / "activate.fish"
        return f"source {activate_script}"

    def _generate_powershell_script(self, bin_path: Path) -> str:
        """Generate PowerShell activation script.

        Args:
            bin_path: Path to environment Scripts directory

        Returns:
            PowerShell activation script
        """
        activate_script = bin_path / "Activate.ps1"
        return f"& {activate_script}"

    def generate_shell_integration(self, shell: str | None = None) -> str:
        """Generate shell integration script for uvve.

        This creates a shell function that wraps the uvve command to handle
        activation automatically without requiring eval.

        Args:
            shell: Shell type. Auto-detected if None

        Returns:
            Shell integration script to be added to shell config
        """
        if shell is None:
            shell = self._detect_shell()

        if shell in ("bash", "zsh"):
            return self._generate_bash_integration()
        if shell == "fish":
            return self._generate_fish_integration()
        if shell == "powershell":
            return self._generate_powershell_integration()
        # Default to bash-compatible
        return self._generate_bash_integration()

    def _generate_bash_integration(self) -> str:
        """Generate bash/zsh shell integration script."""
        return """# uvve shell integration
uvve() {
    local command="$1"

    if [[ "$command" == "activate" ]]; then
        if [[ -z "$2" ]]; then
            echo "Usage: uvve activate <environment_name>"
            return 1
        fi
        # Use eval to actually activate the environment
        eval "$(command uvve activate "$2")"
    else
        # For all other commands, just call uvve normally
        command uvve "$@"
    fi
}

# Auto-activate uvve environment when changing directories
uvve_auto_activate() {
    if [[ -f ".uvve-version" ]]; then
        local env_name
        env_name=$(cat .uvve-version 2>/dev/null | head -n1 | tr -d '\\n\\r')
        if [[ -n "$env_name" ]]; then
            # Check if we're not already in this environment
            local current_env
            current_env=$(command uvve status --current 2>/dev/null || echo "")
            if [[ "$current_env" != "$env_name" ]]; then
                echo "Auto-activating uvve environment: $env_name"
                eval "$(command uvve activate "$env_name" 2>/dev/null)" || {
                    echo "Warning: Failed to activate environment '$env_name' from .uvve-version"
                    echo "Run 'uvve list' to see available environments"
                }
            fi
        fi
    fi
}

# Hook into cd command for bash/zsh
if [[ -n "$BASH_VERSION" ]] || [[ -n "$ZSH_VERSION" ]]; then
    if [[ -n "$ZSH_VERSION" ]]; then
        # ZSH hook
        autoload -U add-zsh-hook
        add-zsh-hook chpwd uvve_auto_activate
    else
        # Bash hook using PROMPT_COMMAND
        if [[ "$PROMPT_COMMAND" != *"uvve_auto_activate"* ]]; then
            PROMPT_COMMAND="uvve_auto_activate; ${PROMPT_COMMAND}"
        fi
    fi
fi

# Also check on initial load
uvve_auto_activate"""

    def _generate_fish_integration(self) -> str:
        """Generate fish shell integration script."""
        return """# uvve shell integration
function uvve
    set command $argv[1]

    if test "$command" = "activate"
        if test (count $argv) -lt 2
            echo "Usage: uvve activate <environment_name>"
            return 1
        end
        # Use eval to actually activate the environment
        eval (command uvve activate $argv[2])
    else
        # For all other commands, just call uvve normally
        command uvve $argv
    end
end

# Auto-activate uvve environment when changing directories
function uvve_auto_activate
    if test -f ".uvve-version"
        set env_name (cat .uvve-version 2>/dev/null | head -n1 | tr -d '\\n\\r')
        if test -n "$env_name"
            # Check if we're not already in this environment
            set current_env (command uvve status --current 2>/dev/null; or echo "")
            if test "$current_env" != "$env_name"
                echo "Auto-activating uvve environment: $env_name"
                eval (command uvve activate "$env_name" 2>/dev/null; or begin
                    echo "Warning: Failed to activate environment '$env_name' from .uvve-version"
                    echo "Run 'uvve list' to see available environments"
                end)
            end
        end
    end
end

# Hook into directory changes for fish
function __uvve_on_pwd --on-variable PWD
    uvve_auto_activate
end

# Also check on initial load
uvve_auto_activate"""

    def _generate_powershell_integration(self) -> str:
        """Generate PowerShell integration script."""
        return """# uvve shell integration
function uvve {
    param([string]$Command, [string[]]$Args)

    if ($Command -eq "activate") {
        if (-not $Args -or $Args.Length -eq 0) {
            Write-Host "Usage: uvve activate <environment_name>"
            return
        }
        # Execute the activation script directly
        $activationScript = & uvve.exe activate $Args[0]
        Invoke-Expression $activationScript
    }
    else {
        # For all other commands, just call uvve normally
        & uvve.exe $Command @Args
    }
}"""
