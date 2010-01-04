net stop sync2winservice
sync2winservice -remove
sync2winservice -auto -install
net start sync2winservice
pause