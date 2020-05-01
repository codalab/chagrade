#!/usr/bin/env bash

dump_path=/backups/$1

docker-compose exec postgres bash -c "
echo 'dropping existing db and restoring from $dump_path..'
dropdb --if-exists -U \$DB_USER \$DB_NAME
createdb -U \$DB_USER \$DB_NAME
pg_restore -U \$DB_USER -d \$DB_NAME -1 $dump_path

echo '
..restore successful!
'
"
