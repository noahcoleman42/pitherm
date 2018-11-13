pushd .
cd /home/pi/pitherm
tmux new-session -s pitherm -d -n therm "source env/bin/activate; python pitherm.py"
tmux new-window -t pitherm:1 -n plot "source env/bin/activate; python make_plot.py"
tmux new-window -t pitherm:2 -n web "source env/bin/activate; python webapp.py"
popd
