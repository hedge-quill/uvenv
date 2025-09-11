"""Shell completion support for uvenv."""

from typing import List


class CompletionManager:
    """Manages shell completion for uvenv commands."""

    def get_bash_completion(self) -> str:
        """Generate bash completion script.

        Returns:
            Bash completion script
        """
        return """
# Bash completion for uvenv
_uvenv_completion() {
    local cur prev commands
    
    cur="${COMP_WORDS[COMP_CWORD]}"
    prev="${COMP_WORDS[COMP_CWORD-1]}"
    commands="create activate list remove lock thaw python-install"
    
    case "${prev}" in
        uvenv)
            COMPREPLY=($(compgen -W "${commands}" -- ${cur}))
            return 0
            ;;
        activate|remove|lock|thaw)
            # Complete with environment names
            local envs=$(uvenv list --quiet 2>/dev/null | awk '{print $1}')
            COMPREPLY=($(compgen -W "${envs}" -- ${cur}))
            return 0
            ;;
        create)
            # No specific completion for create
            return 0
            ;;
        python-install)
            # Could add Python version completion here
            return 0
            ;;
    esac
}

complete -F _uvenv_completion uvenv
"""

    def get_zsh_completion(self) -> str:
        """Generate zsh completion script.

        Returns:
            Zsh completion script
        """
        return """
# Zsh completion for uvenv
#compdef uvenv

_uvenv() {
    local context state line
    typeset -A opt_args

    _arguments \\
        '1: :->command' \\
        '*: :->args'

    case $state in
        command)
            _values 'commands' \\
                'create[Create a new virtual environment]' \\
                'activate[Print activation script for environment]' \\
                'list[List all virtual environments]' \\
                'remove[Remove a virtual environment]' \\
                'lock[Generate lockfile for environment]' \\
                'thaw[Rebuild environment from lockfile]' \\
                'python-install[Install Python version]'
            ;;
        args)
            case ${words[2]} in
                activate|remove|lock|thaw)
                    _values 'environments' ${(f)"$(uvenv list --quiet 2>/dev/null | awk '{print $1}')"}
                    ;;
            esac
            ;;
    esac
}

_uvenv "$@"
"""

    def get_fish_completion(self) -> str:
        """Generate fish completion script.

        Returns:
            Fish completion script
        """
        return """
# Fish completion for uvenv

# Main commands
complete -c uvenv -f -n '__fish_use_subcommand' -a 'create' -d 'Create a new virtual environment'
complete -c uvenv -f -n '__fish_use_subcommand' -a 'activate' -d 'Print activation script for environment'
complete -c uvenv -f -n '__fish_use_subcommand' -a 'list' -d 'List all virtual environments'
complete -c uvenv -f -n '__fish_use_subcommand' -a 'remove' -d 'Remove a virtual environment'
complete -c uvenv -f -n '__fish_use_subcommand' -a 'lock' -d 'Generate lockfile for environment'
complete -c uvenv -f -n '__fish_use_subcommand' -a 'thaw' -d 'Rebuild environment from lockfile'
complete -c uvenv -f -n '__fish_use_subcommand' -a 'python-install' -d 'Install Python version'

# Environment name completion for relevant commands
complete -c uvenv -f -n '__fish_seen_subcommand_from activate remove lock thaw' -a '(uvenv list --quiet 2>/dev/null | awk \'{print $1}\')'

# Options
complete -c uvenv -f -n '__fish_seen_subcommand_from remove' -l force -s f -d 'Force removal without confirmation'
"""

    def get_environment_names(self) -> List[str]:
        """Get list of environment names for completion.

        Returns:
            List of environment names
        """
        # This would be implemented to return actual environment names
        # For now, return empty list as placeholder
        return []

    def install_completion(self, shell: str, install_path: str = None) -> str:
        """Get installation instructions for shell completion.

        Args:
            shell: Shell type (bash, zsh, fish)
            install_path: Optional custom installation path

        Returns:
            Installation instructions
        """
        if shell == "bash":
            path = install_path or "~/.bashrc"
            return f"Add the following to {path}:\\n\\n{self.get_bash_completion()}"
        elif shell == "zsh":
            path = install_path or "~/.zshrc"
            return f"Add the following to {path}:\\n\\n{self.get_zsh_completion()}"
        elif shell == "fish":
            path = install_path or "~/.config/fish/completions/uvenv.fish"
            return f"Save the following to {path}:\\n\\n{self.get_fish_completion()}"
        else:
            return f"Shell '{shell}' is not supported for completion"
