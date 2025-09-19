# Fish Configuration
# by Saifullah Balghari 
# -----------------------------------------------------

# Remove the fish greetings
set -g fish_greeting

# Start tmux
tmux list-sessions 2>/dev/null && tmux attach 2>/dev/null || tmux new

# Sets starship as the promt
eval (starship init fish)

# Start atuin
atuin init fish | source

# List Directory
alias l='eza -lha  --icons=auto' # long list
alias ls='eza -1   --icons=auto' # short list
alias ll='eza -lh --icons=auto --sort=name --group-directories-first' # long list all
alias ld='eza -lhD --icons=auto' # long list dirs
alias lt='eza --icons=auto --tree' # list folder as tree
alias v='nvim'
