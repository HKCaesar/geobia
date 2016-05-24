# [GeOBIA - Click&Classify Project](https://github.com/geosynergy/geobia)
Research for approachs to automate the classification of remote sensing images. </br>
Here are the ideas and the currently state of the application.

###Steps:
* [Segmentation Tuning](#segmentation-tuning)
* [Segmentation](#segmentation)
* [Extract Attributes](#extract-attributes)
* [Machine Learning and Complex Networks](#machine-learning-and-complex-networks)
* [UI](#ui)
* [Cloud Processing](#cloud-processing)
* [Parallel Processing](#parallel-processing)
* [Object Detection/Recognition](#object-detection-and-recognition)
* [More ideas](#more-ideas)

--
###Segmentation Tuning
**Ideas:**</br>
- Going to check the idea of [SPT](http://www.lvc.ele.puc-rio.br/wp/?p=1403), mainly the metrics that the program uses for check the quality of segmentation. Need to check too the result provided with tool of [OTB](https://www.orfeo-toolbox.org/), don't think it will be useful. </br>
I'm currently interested on Segmentation Covering metric that SPT uses, as we are going to work with superpixels.</br>
To achieve the parameters, planning to use [Feature Forge](https://github.com/machinalis/featureforge).

###Segmentation
**Currently:**</br>
Using the [gdal-segment](https://github.com/cbalint13/gdal-segment) for produce LSC Superpixels[¹](http://www.cv-foundation.org/openaccess/content_cvpr_2015/papers/Li_Superpixel_Segmentation_Using_2015_CVPR_paper.pdf) with OpenCV and export to shape trought the GDAL Library.</br>
**Ideas:**</br>
- After finish the robust pipeline, we can search to output the resuts of gdal-segment direct to PostGIS. Also we can remove the statistic that the gdal-segment is creating and let it to the extract attributes/machine learning etapa. So it will only extract the attributes that will be use.

###Extract Attributes
**Currently:**</br>
The gdal-segment extract some information like sum, mean and standard deviation.</br>
**Ideas:**</br>
- After search for more information that we can extract for the segments. As the idea of the superpixels is build compact segments we probably going to lose the shape attributes, but with them we gain a lot on object detection. 

### Machine Learning and Complex Networks
**Currently:**</br>
Checking the [MADlib](http://madlib.incubator.apache.org/) with Random Forest</br>.
**Ideas:**</br>
- Check the confusion matrix before run the classifier algorithm, and if have confusions cluster it and create new classes. If have no confusion, run the algorithm, classify all the segments with the output query and after merge the new classes, so they finish as one class.
- I like approaches as the [TWS](http://imagej.net/Trainable_Weka_Segmentation). Currently checking this and the [TBOT](https://github.com/rhiever/tpot) that works with [scikit-learn](http://scikit-learn.org/stable/).

### UI

### Cloud Processing

### Parallel Processing

### Object Detection and Recognition

### More ideas
- Bag-of-Visual-Words
