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