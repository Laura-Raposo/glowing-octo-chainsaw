# Program: Image Analytics Assingment 2 
# By: Laura Raposo
# Date: March 3 2024

##########################################################################
##                    Convert DN to Radiance                           ##
#########################################################################
import rasterio 
import numpy 
from rasterio.warp import reproject, Resampling

# Red band image
image_input_red = 'LC09_L1TP_009029_20230922_20230922_02_T1_B4-subset.tif'

# Scale and offset
Rscale = 9.9152E-03
Roffset = -49.57609

with rasterio.open(image_input_red, 'r') as input_red:
    # Read the bands to get the data as an array
    data_red = input_red.read()
    b4_reflectance = data_red[0] * Rscale + Roffset
    
    # Prepare the output profile
    profile_red = input_red.profile
    profile_red['dtype'] = 'float32'  # Change the data type to store radiance values

    # Write the radiance values to a new GeoTIFF file
    with rasterio.open('radiance_red.tif', 'w', **profile_red) as output_red:
        output_red.write(b4_reflectance, 1)

# Green Band Image  
image_input_green = 'LC09_L1TP_009029_20230922_20230922_02_T1_B3-subset.tif'

# Scale and offset
Gscale = 1.2757E-02
Goffset = -63.78403

with rasterio.open(image_input_green, 'r') as input_green:
    # Read the bands to get the data as an array
    data_green = input_green.read()
    b3_reflectance = data_green[0] * Gscale + Goffset
    
    # Prepare the output profile
    profile_green = input_green.profile
    profile_green['dtype'] = 'float32'  # Change the data type to store radiance values

    # Write the radiance values to a new GeoTIFF file
    with rasterio.open('radiance_green.tif', 'w', **profile_green) as output_green:
        output_green.write(b3_reflectance, 1)

# Blue Band Image
image_input_blue = 'LC09_L1TP_009029_20230922_20230922_02_T1_B2-subset.tif'

# Scale and offset
Bscale = 1.1769E-02
Boffset = -58.84429

with rasterio.open(image_input_blue, 'r') as input_blue:
    # Read the bands to get the data as an array
    data_blue = input_blue.read()
    b2_reflectance = data_blue[0] * Bscale + Boffset
    
    # Prepare the output profile
    profile_blue = input_blue.profile
    profile_blue['dtype'] = 'float32'  # Change the data type to store radiance values

    # Write the radiance values to a new GeoTIFF file
    with rasterio.open('radiance_blue.tif', 'w', **profile_blue) as output_blue:
        output_blue.write(b2_reflectance, 1)

# Panchromatic Band Image
image_input_pan = 'LC09_L1TP_009029_20230922_20230922_02_T1_B8-subset.tif'

# Scale and offset
Pscale = 1.1190E-02
Poffset = -55.94908

with rasterio.open(image_input_pan, 'r') as input_pan:
    # Read the bands to get the data as an array
    data_pan = input_pan.read()
    b8_reflectance = data_pan[0] * Pscale + Poffset
    
    # Prepare the output profile
    profile_pan = input_pan.profile
    profile_pan['dtype'] = 'float32'  # Change the data type to store radiance values

    # Write the radiance values to a new GeoTIFF file
    with rasterio.open('radiance_pan.tif', 'w', **profile_pan) as output_pan:
        output_pan.write(b8_reflectance, 1)


##############################################################
##                        Up Scale                          ##
##############################################################
import rasterio 
import numpy 
from rasterio.warp import reproject, Resampling

with rasterio.open('radiance_green.tif') as Green, \
        rasterio.open('radiance_pan.tif') as Pan, \
        rasterio.open('radiance_red.tif') as Red, \
        rasterio.open('radiance_blue.tif') as Blue:

    Pan_band = Pan.read(1)
    Red_band = Red.read(1)
    Green_band = Green.read(1)
    Blue_band = Blue.read(1)

    # Create an empty NumPy array for the output. The empty array needs to be the same shape as 
    # the panchromatic band. Its data type should be the same as the near infrared band.
    # This is where values will come from.
    resample_red = numpy.empty(Pan_band.shape, dtype=Red_band.dtype)
    resample_blue = numpy.empty(Pan_band.shape, dtype=Blue_band.dtype)
    resample_green = numpy.empty(Pan_band.shape, dtype=Green_band.dtype)

    # Use the reproject function from rasterio. The function
    # returns the resampled values and its transform. So the
    # result is assigned to two variables as below.
    resampled_red, transform_red = reproject(
        Red_band,
        resample_red,
        src_transform=Red.transform,  # Use Pan's transform instead of Red_band's transform
        src_crs=Red.crs,
        dst_transform=Pan.transform,
        dst_crs=Pan.crs,
        resampling=Resampling.nearest
    )

    resampled_blue, transform_blue = reproject(
        Blue_band,
        resample_blue,
        src_transform=Blue.transform,  # Use Pan's transform instead of Blue_band's transform
        src_crs=Blue.crs,
        dst_transform=Pan.transform,
        dst_crs=Pan.crs,
        resampling=Resampling.nearest
    )

    resampled_green, transform_green = reproject(
        Green_band,
        resample_green,
        src_transform=Green.transform,  # Use Pan's transform instead of Green_band's transform
        src_crs=Green.crs,
        dst_transform=Pan.transform,
        dst_crs=Pan.crs,
        resampling=Resampling.nearest
    )


    profile_red = Red.profile 
    profile_red['transform'] = transform_red
    profile_red['width'] = Pan.width 
    profile_red['height'] = Pan.height
    with rasterio.open('upscaled_red.tif', mode='w', **profile_red) as output_red:
        output_red.write(resampled_red, indexes=1)

    profile_blue = Blue.profile 
    profile_blue['transform'] = transform_blue
    profile_blue['width'] = Pan.width 
    profile_blue['height'] = Pan.height
    with rasterio.open('upscaled_blue.tif', mode='w', **profile_blue) as output_blue:
        output_blue.write(resampled_blue, indexes=1)

    profile_green = Green.profile 
    profile_green['transform'] = transform_green
    profile_green['width'] = Pan.width 
    profile_green['height'] = Pan.height
    with rasterio.open('upscaled_green.tif', mode='w', **profile_green) as output_green:
        output_green.write(resampled_green, indexes=1)


#########################################################
##             Brovey transformation                   ##
#########################################################

import rasterio
import numpy as np

# Read the red band
with rasterio.open('upscaled_red.tif') as red_band:
    red = red_band.read(1)
    # Prepare the output profile
    profile_red = red_band.profile.copy()
    profile_red['dtype'] = 'float32'  # Change the data type to store the transformed values

# Read the green band
with rasterio.open('upscaled_green.tif') as green_band:
    green = green_band.read(1)
    # Prepare the output profile
    profile_green = green_band.profile.copy()
    profile_green['dtype'] = 'float32'  # Change the data type to store the transformed values

# Read the blue band
with rasterio.open('upscaled_blue.tif') as blue_band:
    blue = blue_band.read(1)
    # Prepare the output profile
    profile_blue = blue_band.profile.copy()
    profile_blue['dtype'] = 'float32'  # Change the data type to store the transformed values

# Read the pan band
with rasterio.open('radiance_pan.tif') as pan_band:
    pan = pan_band.read(1)

# Calculate Brovey transformation for each band
pan_sharpened_red = red * (pan / (red + green + blue))
pan_sharpened_green = green * (pan / (red + green + blue))
pan_sharpened_blue = blue * (pan / (red + green + blue))

# Write the transformed data into new GeoTIFF files
with rasterio.open('pan_sharpened_red.tif', 'w', **profile_red) as red_output:
    red_output.write(pan_sharpened_red, 1)

with rasterio.open('pan_sharpened_green.tif', 'w', **profile_green) as green_output:
    green_output.write(pan_sharpened_green, 1)

with rasterio.open('pan_sharpened_blue.tif', 'w', **profile_blue) as blue_output:
    blue_output.write(pan_sharpened_blue, 1)


######################################################################
##                  Stack Bands to RGB                              ##
######################################################################
import rasterio
from rasterio.enums import ColorInterp

# Filenames
red_filename = 'pan_sharpened_red.tif'
green_filename = 'pan_sharpened_green.tif'
blue_filename = 'pan_sharpened_blue.tif'

# Form these filenames into a list so that each can
# easily be opened in turn and processed. Note the order
# is RGB. This order will follow through into the image.
filenames = [
    red_filename,
    green_filename,
    blue_filename
]

# An image profile for the output must be created. We can open just
# one file and extract its profile as the basis.
with rasterio.open(red_filename) as red:
    profile_red = red.profile.copy()

# Open the green band to extract its profile
with rasterio.open(green_filename) as green:
    profile_green = green.profile.copy()

# Open the blue band to extract its profile
with rasterio.open(blue_filename) as blue:
    profile_blue = blue.profile.copy()

# Each input dataset has one band while the output must have 3
# so this profile does need to be changed in this regard. But
# otherwise it can be left as is.
profile_red['count'] = 3

# Open the file that will be written to
with rasterio.open('final_stacked.tif', mode='w', **profile_red) as output:
    # Iterate over the filenames 
    for f in filenames:
        with rasterio.open(f) as input:
            # We must say the index (band position) at which the data will be written. And rescale
            output.write(input.read(1), indexes=filenames.index(f)+1)
    # Set the colour interpretation. This just labels the band
    # so that we know what it is.
    output.colorinterp = [ ColorInterp.red, ColorInterp.green, ColorInterp.blue]
