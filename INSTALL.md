# Installation

Installation is manual but trivial. To avoid the need to install system-wide Python packages, creating a virtual environment is recommended.

apt-get update
cd /opt
git clone https://github.com/mi0xzz/wsjtx-dx-alert
cd /opt/wsjtx-dx-alert
virtualenv venv --python=/usr/bin/python3
source venv/bin/activate
pip install -r requirements.txt
sudo cp systemd/wsjtx-dx-alert.service /etc/systemd/system/
sudo systemctl enable wsjtx-dx-alert.service
sudo systemctl start wsjtx-dx-alert.service

Upon doing this, the module is now running as a service and should _hopefully_ continue as normal.

If you make any changes to the _settings.yaml_ file then you'll need to restart the service which can be done with the following command:

sudo systemctl restart wsjtx-dx-alert.service
