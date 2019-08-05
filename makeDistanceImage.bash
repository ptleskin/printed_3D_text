#	$1	input image
#	$2	output for distance transform
#	$3	output for distance transform from image skeleton

#	value for constant CONVERTCOMMAND depends on the os, use the output of console command 'which convert':
CONVERTCOMMAND='/opt/local/bin/convert' # mac os x
# CONVERTCOMMAND='/usr/bin/convert' # ubuntu

#	convert en.png -threshold 60% -morphology Distance Euclidean:4 -function polynomial 8,0 en_dist.png
$CONVERTCOMMAND -define profile:skip=ICC \
	$1 -negate -resize 75% \
	-threshold 60% \
	-morphology Distance Euclidean:8 \
	-blur 0x1 \
	text:- | grep " ([1-9]\d" > $2
	
$CONVERTCOMMAND -define profile:skip=ICC \
	$1 -negate -resize 75% \
	-threshold 60% \
	-morphology Thinning:-1 Skeleton -negate -morphology Distance Euclidean:8 \
	-blur 0x1 \
	$3

	