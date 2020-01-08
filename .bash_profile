# .bash_profile

# Get the aliases and functions
if [ -f ~/.bashrc ]; then
	. ~/.bashrc
fi

# User specific environment and startup programs

export SECRET_KEY_1=

PATH=$PATH:$HOME/.local/bin:$HOME/bin

export PATH="~/bin:$PATH"