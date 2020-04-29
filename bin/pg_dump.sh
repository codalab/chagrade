#!/usr/bin/env bash

export dump_name="`date +"%F_%H%M%S"`.dump"

docker-compose exec postgres bash -c "
export DUMP_PATH=/backups/$dump_name
echo 'Making dump: $dump_name'
PGPASSWORD=\$DB_PASSWORD pg_dump -Fc -U \$DB_USER \$DB_NAME > \$DUMP_PATH
";

docker-compose exec django ./manage.py upload_backup $dump_name
