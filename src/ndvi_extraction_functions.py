import rasterio as rio
import numpy as np
from pyproj import Transformer
import rioxarray as rxr
from wkt_functions import load_wkt_as_geodataframe
import geopandas
def get_ndvi_value_from_latlon(latitude, longitude, file_path):
    with rio.open(file_path) as dataset:
        left, bottom, right, top = dataset.bounds
        
        nrows, ncols = dataset.height, dataset.width
        
        pixel_width = (right - left) / ncols
        pixel_height = (top - bottom) / nrows
        
        if not (left <= longitude <= right and bottom <= latitude <= top):
            print(f"Coordinates ({latitude}, {longitude}) are out of bounds for this image.")
            return None
        
        col = int((longitude - left) / pixel_width)
        row = int((top - latitude) / pixel_height)
        
        pixel_value = dataset.read(1)[row, col]
        
        return pixel_value

def get_ndvi_from_range(wkt_string, raster_path='', crs='EPSG:4326'):
    aoi_gdf = load_wkt_as_geodataframe(wkt_string, crs)
    integer_array = []
    
    try:
        ndvi_image = rxr.open_rasterio(raster_path)
        aoi_gdf = aoi_gdf.to_crs(ndvi_image.rio.crs.to_string())
        clipped_band = ndvi_image.rio.clip(aoi_gdf.geometry, from_disk=True)
        masked_band_values = clipped_band.where(clipped_band > 0, np.nan).values

        cleaned_array = masked_band_values[~np.isnan(masked_band_values)]
        integer_array = cleaned_array.astype(int)

    except Exception as e:
        print(f"An error occurred: {e} with file {raster_path}. NOT AN NDVI IMAGE")
        pass

    return integer_array