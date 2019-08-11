#### 3D printed text
This repository contains Python and ImageMagick codes for creating a stl-model from a bitmap. The code was used in my personal project to create a 3D-model and then 3D print my family name to decorate my front door.

The process of extruding the bitmap into a 3D shape uses morphological operations [Distance Transform](http://www.imagemagick.org/Usage/morphology/#distance) and [Skeleton Information](http://www.imagemagick.org/Usage/morphology/#skeleton_info) from which the local shape radius at each point is estimated. 

![3D process](https://raw.githubusercontent.com/ptleskin/printed_3D_text/master/images/3DProcess.png)

![Final 3D print](https://raw.githubusercontent.com/ptleskin/printed_3D_text/master/images/IMG_0749.png)
