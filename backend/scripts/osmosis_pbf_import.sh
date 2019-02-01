# # createdb osm
# sudo -u postgres createuser osm
# sudo -u postgres psql -c "CREATE DATABASE osm"
# sudo -u postgres psql -c "alter role osm with encrypted password 'HUQPLNTDPCGE';"  
# sudo -u postgres psql -c "grant all privileges on database osm to osm;"
# sudo -u postgres psql -d osm -c 'CREATE EXTENSION postgis; CREATE EXTENSION hstore;'
osmosis=~/Applications/osmosis/bin/osmosis
schema=~/Applications/osmosis/script/pgsnapshot_schema_0.6.sql
# osmosis --read-xml file=~/osm/planbet/planet.osm --write-apidb host="x" database="x" user="x" password="x"
pbf=~/Downloads/Graz.osm.pbf
authfile="authfile_db"

export PGPASSWORD=`cat $authfile | grep -i password| cut -d = -f 2` 

# echo $PGPASSWORD
# sudo -u postgres psql -c "DROP DATABASE osm; "
# sudo -u postgres psql -c "CREATE DATABASE osm;"
# sudo -u postgres psql -c "grant all privileges on database osm to osm;"
# sudo -u postgres psql -d osm -c 'CREATE EXTENSION postgis; CREATE EXTENSION hstore;'
# exit 
psql -h 127.0.0.1 -U osm -d osm -f $schema
##sudo -u postgres psql -d osm -c "GRANT ALL PRIVILEGES ON TABLE * TO osm;"
$osmosis --read-pbf $pbf \
	--tf accept-nodes shop=* amenity=* leisure=* \
	--tf accept-ways shop=* amenity=* leisure=* \
	--tf accept-relations shop=* amenity=* leisure=* \
	--write-pgsql authFile=$authfile

