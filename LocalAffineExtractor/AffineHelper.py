import cv2
import numpy as np
import math


def Sobel(image):

    height,width = image.shape

    sobelHor=np.zeros((height,width),dtype=np.float32)
    sobelVer=np.zeros((height,width),dtype=np.float32)


#SobelHor
    for x in range(width-1):
        for y in range(height):
#            print("Val:",image[y,x+1],' prev',image[y,x])
            sobelHor[y,x]=float(image[y,x+1])-float(image[y,x])

#SobelVer
    for y in range(height-1):
        for x in range(width):
            sobelVer[y,x]=float(image[y+1,x])-float(image[y,x])

#    np.savetxt("sobelVer.mat",sobelVer)
#    np.savetxt("sobelHor.mat",sobelHor)

#    np.savetxt("image.mat",image)

    return sobelHor,sobelVer


def BilinearInterpolaton(image,u,v,modeNegative):
    height,width=image.shape

    u1=math.floor(u)
    u2=u1+1

    fractionU=u-u1

    v1=math.floor(v)
    v2=v1+1

    fractionV=v-v1



#Error handling!

    if ((v1<0.0) or (u1<0.0) or (u2>(width-1)) or (v2>(height-1))):
        intensityF=-1000.0
    else:


#        topleft=image[v1,u1]
#        topright=image[v1,u2]

#        bottomleft=image[v2,u1]
#        bottomright=image[v2,u2]

        topleftF=float(image[v1,u1])
        toprightF=float(image[v1,u2])

        bottomleftF=float(image[v2,u1])
        bottomrightF=float(image[v2,u2])


        if modeNegative:
            intensityF=fractionU*fractionV*bottomrightF+(1.0-fractionU)*fractionV*bottomleftF+fractionU*(1.0-fractionV)*toprightF+(1.0-fractionU)*(1.0-fractionV)*topleftF
        else:

            if ((topleftF>0.0) and (toprightF>0.0) and (bottomleftF>0.0) and (bottomrightF>0.0)):
                intensityF=fractionU*fractionV*bottomrightF+(1.0-fractionU)*fractionV*bottomleftF+fractionU*(1.0-fractionV)*toprightF+(1.0-fractionU)*(1.0-fractionV)*topleftF
            else:
                intensityF=-1000.0


    return intensityF


def NormalizePatch(image):
    image2=image.astype(np.float32)
    medianIntensity=np.median(image2)
    image2=image2-medianIntensity
#Why 30?
    image2=25.0*image2/image2.std()+127.5
    image3=image2.astype(np.uint8)


###Check: mi van, ha kilóg a tartományból egy pixel?
###Kézzel meg kellene írni rendesen!
    return image3


def ErrorBetweenImages(patch1,patch2):
    height,width=patch1.shape


    diffPatch=abs(patch2.astype(np.float32)-patch1.astype(np.float32))
    val=0.0
    cnt=0
    for x in range(width):
        for y in range(height):
            pixel1=patch1[y,x]
            pixel2=patch2[y,x]


            if ((pixel1>0) and (pixel2>0)):

                val=val+diffPatch[y,x]
                cnt=cnt+1

    if (cnt>0):

        errorValue=float(val)/cnt
    else:
        errorValue=999999999999.9
#    print("Init Error: ",errorValue)
    return errorValue, diffPatch

