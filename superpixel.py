import sys
import os
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))

import postgis_helper
from osgeo import gdal
import argparse
import subprocess
import shutil

class Classifier:
    """classifies raster"""

    gdal_translate = "/usr/bin/gdal_translate"
    gdal_segment = "/usr/local/projects/gdal-segment/bin/gdal-segment"
    shp2pgsql = "/usr/bin/shp2pgsql"

    tmp_path = "/tmp/superpixel/"
    shp_output = "/tmp/superpixel_segment.shp"

    db_file_id = 0


    def __init__(self):
        """"""

    def create_source_entry(self, source_file_path):
        """"""
        ph = postgis_helper.postgis_helper()
        sqlstring = "INSERT INTO geobia.source_files (filepath) VALUES (%s) RETURNING id"
        ret = ph.query(sqlstring, [str(source_file_path)])
        self.db_file_id = ret[0][0]

    def process(self, source_file_path, should_slice):
        """"""
        if not os.path.exists(self.tmp_path):
            os.makedirs(self.tmp_path)
        else:
            shutil.rmtree(self.tmp_path)
            os.makedirs(self.tmp_path)

        self.create_source_entry(source_file_path)

        if os.path.isfile(source_file_path):
            """"""
            self.process_file(source_file_path, should_slice)
        else:
            """"""
            for f in os.listdir(source_file_path):
                if f.lower().endswith(".tif") or f.lower().endswith(".tiff"):
                    self.process_file(os.path.join(source_file_path,f), should_slice)

        self.clusterise_superpixels()


    def process_file(self, raster_file_path, should_slice):
        """"""
        source_files = []
        ph = postgis_helper.postgis_helper()
        if should_slice and self.need_slice(raster_file_path):
            """"""
            source_files = self.slice(raster_file_path)
        else:
            """"""
            source_files.append(raster_file_path)

        for sf in source_files:
            """"""
            p = subprocess.Popen([self.gdal_segment, sf, "-out", self.shp_output, "-algo", "LSC"])
            p.communicate()
            psql_env = dict(PGPASSWORD='oHk785V8jG5_')
            p = subprocess.Popen([self.shp2pgsql, "-a", "-S", "-t", "2D","-g","geo", self.shp_output, "geobia.superpixel_rgb"], stdout=subprocess.PIPE)
            p2 = subprocess.Popen(['/usr/bin/psql', '-p', '5432',"-d", 'v4', '-U', 'v4', '-h', '127.0.0.1'], stdin=p.stdout, stdout=subprocess.PIPE, env=psql_env)
            p.stdout.close()  # Allow p1 to receive a SIGPIPE if p2 exits.
            output,err = p2.communicate()
            ph.execute("UPDATE geobia.superpixel_rgb set source_file_id = %s WHERE source_file_id is NULL", [self.db_file_id])





    def clusterise_superpixels(self):
        ph = postgis_helper.postgis_helper()
        table_name = "geobia_kmeans_"+str(self.db_file_id)
        ph.execute("CREATE TABLE "+table_name+" AS select kmeans(ARRAY[\"1_average\", \"2_average\", \"3_average\"], 7) OVER (), "
                                              "gid FROM geobia.superpixel_rgb WHERE source_file_id = %s", [self.db_file_id])
        ph.execute("UPDATE geobia.superpixel_rgb as sp SET kmeans = t.kmeans FROM "+table_name+" t WHERE sp.gid = t.gid")
        ph.execute("DROP TABLE "+table_name)

    def slice(self, raster_file_path):
        """"""
        gtif = gdal.Open(raster_file_path)
        step = 4000
        w = gtif.RasterXSize
        h = gtif.RasterYSize
        source_files = []

        for x in range(0, w, step):
            for y in range(0, h, step):
                tile_path = os.path.join(self.tmp_path, "tile_"+str(x)+"_"+str(y)+".tif")
                p = subprocess.Popen([self.gdal_translate, "-srcwin", str(x), str(y), str(step), str(step), raster_file_path, tile_path])
                p.communicate()
                source_files.append(tile_path)

        return source_files


    def need_slice(self, raster_file_path):
        """"""
        gtif = gdal.Open(raster_file_path)
        return gtif.RasterXSize * gtif.RasterYSize > 16100000

    def classify(self, files):
        """"""



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Parameters')

    parser.add_argument('--source_file',
                        type=str,
                        help='Source raster file', required=True)
    parser.add_argument('--should_slice', action='store_true', default=False)

    args = parser.parse_args()

    classifier = Classifier()
    classifier.process(args.source_file, args.should_slice)

