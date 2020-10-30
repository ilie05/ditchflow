sudo chgrp -R www-data /var/www/ditchflow
sudo find /var/www/ditchflow -type d -exec chmod g+rx {} +
sudo find /var/www/ditchflow -type f -exec chmod g+r {} +

sudo chmod g+w /var/www/ditchflow/settings.json
sudo chgrp www-data db.sqlite
sudo chmod g+w db.sqlite
sudo chmod g+w .
