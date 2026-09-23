import sys
import cv2
import numpy as np
import math




if len(sys.argv) >= 4:

    featureNum=-1;

    img1Filename=sys.argv[1]
    img2Filename=sys.argv[2]

    resultFileName=sys.argv[3]

    mode=1 # 1: ORB 2: SIFT
    if len(sys.argv) >= 5:
       if sys.argv[4]=="SIFT":
           mode=2

    if len(sys.argv) >= 6:
        featureNum=int(sys.argv[5])


    img1 = cv2.imread(img1Filename, cv2.IMREAD_GRAYSCALE)
    img2 = cv2.imread(img2Filename, cv2.IMREAD_GRAYSCALE)

    if img1 is None or img2 is None:
        print("File loading error.")
        exit(10)


    height1,width1 = img1.shape
    height2,width2 = img2.shape

    if (mode==1):
        orb = cv2.ORB_create()
        kp1, des1 = orb.detectAndCompute(img1, None)
        kp2, des2 = orb.detectAndCompute(img2, None)
        bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True) # ORB-hez NORM_HAMMING
    else:
        sift = cv2.SIFT_create()
        kp1, des1 = sift.detectAndCompute(img1, None)
        kp2, des2 = sift.detectAndCompute(img2, None)
        bf = cv2.BFMatcher()


    matches = bf.match(des1, des2)
    matches = sorted(matches, key=lambda x: x.distance)


    numMatches=len(matches)

    if (featureNum!=-1):
        numMatches=featureNum

    affineParameters=np.zeros((numMatches,10))

    print("Found: ",numMatches, "matches.")
    for cnt in range(0,numMatches,1):

        idx1=int(matches[cnt].queryIdx)
        idx2=int(matches[cnt].trainIdx)

        scale=kp2[idx2].size/kp1[idx1].size

        angle=3.1415927*(kp2[idx2].angle-kp1[idx1].angle)/180.0

        pt1=kp1[idx1].pt
        pt2=kp2[idx2].pt


        a1=scale*math.cos(angle)
        a3=-scale*math.sin(angle)
        a2=scale*math.sin(angle)
        a4=scale*math.cos(angle)
        a5=pt2[0]-a1*pt1[0]-a3*pt1[1]
        a6=pt2[1]-a2*pt1[0]-a4*pt1[1]

        affineParameters[cnt,0]=a1
        affineParameters[cnt,1]=a2
        affineParameters[cnt,2]=a3
        affineParameters[cnt,3]=a4
        affineParameters[cnt,4]=a5
        affineParameters[cnt,5]=a6

        affineParameters[cnt,6]=pt1[0]
        affineParameters[cnt,7]=pt1[1]
        affineParameters[cnt,8]=pt2[0]
        affineParameters[cnt,9]=pt2[1]

#        affineParameters[cnt,10]=a1*pt1[0]+a3*pt1[1]+a5
#        affineParameters[cnt,11]=a2*pt1[0]+a4*pt1[1]+a6

#        print("pt1",pt1)
#        print("pt2",pt2)

    np.savetxt(resultFileName,affineParameters)

else:
    print("Usage: python OpenCVAffineMatcher.py imagefile1 imagefile2 resultaffinities")

