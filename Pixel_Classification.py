

import fiona
import numpy
import rasterio
from   rasterio.plot import reshape_as_image
from   rasterio.windows import Window
import pystac_client
import planetary_computer
from   sklearn.svm import SVC
from   sklearn.model_selection import train_test_split
from   sklearn.metrics import confusion_matrix, classification_report, accuracy_score
from   rasterio.windows import Window
from   rasterio.windows import from_bounds
from   rasterio.windows import round_window_to_full_blocks 
   

### Import data from Planetary Computer ###

client = pystac_client.Client.open("https://planetarycomputer.microsoft.com/api/stac/v1", modifier=planetary_computer.sign_inplace,)

landsat_id  = 'LC08_L2SP_008029_20201016_02_T1'
search      = client.search(
collections = ['landsat-c2-l2'], 
ids         = [landsat_id])
item        = search.item_collection()[0]

bands      = ['blue', 'green', 'red', 'nir08', 'swir16', 'swir22']
features   = len(bands)

left   = 422400
right  = 472460
top    = 4966160
bottom = 4917440

bbox = (left, bottom, right, top)


### Define the area of interest ####

with rasterio.open(item.assets['blue'].href, 'r') as input:
    # The window is defined using the bounding box and the transform of the input image
    window = rasterio.windows.from_bounds(*bbox, input.transform)
    window = rasterio.windows.round_window_to_full_blocks(
                window,
                [(input.profile['blockysize'], input.profile['blockxsize'])])
    data = input.read(1, window=window)
    profile = input.profile
    ulx, uly = input.xy(int(window.row_off), int(window.col_off), offset='ul')
    profile['transform'] = rasterio.Affine(
        input.transform.a,
        input.transform.b,
        ulx,
        input.transform.d,
        input.transform.e,
        uly)
    
    profile['width'] = int(window.width)
    profile['height'] = int(window.height)
    profile['count'] = 1
    profile['dtype'] = rasterio.uint8
    profile['driver'] = 'COG'
    

### Sampling the Data ###

with fiona.open('training.gpkg') as training:
    # Create the sample labels dataset
    y_labels = numpy.fromiter([l['properties']['code'] for l in training], numpy.uint8)
    # Get the sample coordinates from the training data
    coordinates = [c['geometry']['coordinates'] for c in training]
    # Empty X_samples array
    X_samples = numpy.empty((len(coordinates), features), dtype=numpy.uint16)
 
    for b in bands:
        with rasterio.open(item.assets[b].href) as image:
            # Sample the band
            samples = image.sample(coordinates)
            samples = numpy.fromiter([s[0] for s in samples],
                                     numpy.uint16).reshape(len(y_labels), 1)
            # Put the samples into the X_array at the right location
            numpy.put_along_axis(X_samples,
                                 numpy.full_like(samples, bands.index(b)),
                                 samples, axis=1)


### Accuracy Classification ###

X_train, X_test, y_train, y_test = train_test_split(X_samples, y_labels, test_size=0.5, stratify=y_labels)

# Train the classifier
classification = SVC()
classification.fit(X_train, y_train)

# Test the classifier
classification_test = classification.predict(X_test)

# Calculate and print evaluation metrics
print('== Accuracy Score ================================================')
print(f'{accuracy_score(y_test, classification_test)}')
print('== Classification Report =========================================')
print(classification_report(y_test, classification_test, zero_division=1))
print('== Confusion Matrix ==============================================')
print(confusion_matrix(y_test, classification_test))
    
            

### Pseudo Colour ###

import sqlite3

# Connect to SQLite database and fetch class colors
with sqlite3.connect('training.gpkg') as db:
    colours = {}
    cursor = db.cursor()
    cursor.execute(
        """SELECT code, red, green, blue
        FROM landcover_class
        """)
    
    for r in cursor.fetchall():
        colours[r[0]] = [r[1], r[2], r[3]]
    
# Rasterio Image Processing Operations
file_path = f'C:/NSCC/winter/ImageAnalytics/Assingment3/{landsat_id}_classified_svc_nrcan.tif'

with rasterio.open(file_path, mode='w', **profile) as classified:
    data2 = numpy.empty((window.width * window.height, features), dtype=numpy.uint16)
    
    for b in bands:
        with rasterio.open(item.assets[b].href) as band:
            data_band = reshape_as_image(band.read(window=window)).reshape(-1, 1)
            numpy.put_along_axis(data2, numpy.full_like(data_band, bands.index(b)), data_band, axis=1)
    prediction = classification.predict(data2).reshape(int(window.height), int(window.width))
    classified.write(prediction, indexes=1)
    classified.write_colormap(1,colours)


#### Count pixels ####


with rasterio.open('landcover-2020-classification-subset.tif') as nrcan:
    raster = nrcan.read()    
    values, counts2020 = numpy.unique(raster, return_counts=True)
    print(values)
    print(counts2020)
   
with rasterio.open(f'{landsat_id}_classified_svc_nrcan.tif') as classTC:
    raster2 = classTC.read()
    values2, mycounts = numpy.unique(raster2, return_counts=True)
    print(values2)
    print(mycounts)


