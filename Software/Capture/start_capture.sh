# Arg 1: Image Count
# Arg 2: Steps per image (positive or negative)
# Arg 3: Time between images (Limited by camera response speed)


sudo apt-get install -y python3.7 python3-pip pkg-config libgphoto2-dev ufraw-batch;

sudo -H pip3 install gphoto2;
sudo -H pip3 install pyserial;

python3 Capture_Orchestration.py $1 $2 $3