net stop sync2service
sync2service -remove
sync2service -auto -install
net start sync2service
pause