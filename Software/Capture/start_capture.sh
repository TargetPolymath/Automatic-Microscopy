# Copyright 2020 Zachary J. Allen

# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at

#    http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.


# Arg 1: Image Count
# Arg 2: Steps per image (positive or negative)
# Arg 3: Time between images (Limited by camera response speed)


sudo apt-get install -y python3.7 python3-pip pkg-config libgphoto2-dev ufraw-batch;

sudo -H pip3 install gphoto2;
sudo -H pip3 install pyserial;

python3 Capture_Orchestration.py $1 $2 $3
