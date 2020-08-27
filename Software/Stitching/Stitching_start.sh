
sudo -H apt-get -qq install python3 python3-pip python3-tk;

# python3 -m cProfile -o profile_out.txt Stitching_main.py $1;
python3 Stitching_main.py $1;