#sudo easy_install ConfigParser
#sudo easy_install PyGreSQL
import ConfigParser
import os
from pg import DB
import subprocess


config = ConfigParser.ConfigParser()
config_file = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'config.ini')
config.read(config_file)
db = DB(dbname=config.get('database', 'dbname'), host='127.0.0.1', port=5432,
         user=config.get('database', 'user'), passwd=config.get('database', 'password'))

print "importing shapefile"

psql_env = dict(PGPASSWORD=config.get('database', 'password'))

db.query("DROP TABLE IF EXISTS "+config.get('summary_stats', 'shp_table_name'))

p1 = subprocess.Popen(['shp2pgsql', '-c', '-t', '2D', '-s', config.get('summary_stats', 'shp_file_srs'),
                       config.get('summary_stats', 'shp_file'), config.get('summary_stats', 'shp_table_name')], stdout=subprocess.PIPE)
p2 = subprocess.Popen(['/usr/bin/psql', '-p', '5432', config.get('database', 'dbname'), '-U',
                       config.get('database', 'user'), '-h', '127.0.0.1'], stdin=p1.stdout, stdout=subprocess.PIPE, env=psql_env)
p1.stdout.close()
output,err = p2.communicate()

db.query("ALTER TABLE "+config.get('summary_stats', 'shp_table_name')+" ADD column attributes TEXT")

print "importing raster"
db.query("DROP TABLE IF EXISTS "+config.get('summary_stats', 'raster_table_name'))
p1 = subprocess.Popen(['raster2pgsql', '-d', '-s', config.get('summary_stats', 'raster_file_srs'), '-t', '50x50',  config.get('summary_stats', 'raster_file'),
                       config.get('summary_stats', 'raster_table_name')], stdout=subprocess.PIPE)
p2 = subprocess.Popen(['/usr/bin/psql', '-p', '5432', config.get('database', 'dbname'), '-U', config.get('database', 'user'), '-h', '127.0.0.1'],
                      stdin=p1.stdout, stdout=subprocess.PIPE, env=psql_env)
p1.stdout.close()  # Allow p1 to receive a SIGPIPE if p2 exits.
output,err = p2.communicate()

db.query('CREATE INDEX dem_st_convexhull_idx ON '+config.get('summary_stats', 'raster_table_name')+' '
                               'USING gist ((st_convexhull(rast)) public.gist_geometry_ops_2d)')

db.query('select raster.updtae_attributes($1, $2)', (config.get('summary_stats', 'shp_table_name'),
                                                     config.get('summary_stats', 'raster_table_name')))
