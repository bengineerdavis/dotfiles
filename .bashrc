# Source global definitions
if [ -f /etc/bashrc ]; then
	. /etc/bashrc
fi

export PIP_REQUIRE_VIRTUALENV=false

PS1='[\u@\h \W$(__docker_machine_ps1)]\$ '

# Uncomment the following line if you don't like systemctl's auto-paging feature:
# export SYSTEMD_PAGER=

# User specific aliases and functions
export PATH="$HOME/.rbenv/bin:$PATH"
eval "$(rbenv init -)"
export PATH="$HOME/.rbenv/plugins/ruby-build/bin:$PATH"

alias todo='~/bin/todo.txt-cli/todo.sh -d /bin/todo.txt-cli/todo.cfg'
alias upgrade='sudo dnf update && sudo dnf upgrade && flatpak update'
alias activate='source venv/bin/activate'
alias newvenv='python3 -m venv venv'
alias bashup='source .bashrc'
alias pipgradeuser='pip3 install --upgrade --user pip' # Universial pip upgrade for my user namespace
alias pipgradevenv='pip install --upgrade pip' # I don't need user permissions within virtual env

# >>> conda initialize >>>
# !! Contents within this block are managed by 'conda init' !!
__conda_setup="$('/home/bd/miniconda3/bin/conda' 'shell.bash' 'hook' 2> /dev/null)"
if [ $? -eq 0 ]; then
    eval "$__conda_setup"
else
    if [ -f "/home/bd/miniconda3/etc/profile.d/conda.sh" ]; then
        . "/home/bd/miniconda3/etc/profile.d/conda.sh"
    else
        export PATH="/home/bd/miniconda3/bin:$PATH"
    fi
fi
unset __conda_setup
# <<< conda initialize <<<

