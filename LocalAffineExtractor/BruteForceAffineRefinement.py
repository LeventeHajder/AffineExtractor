import sys
import cv2
import numpy as np
import math
from AffineHelper import *
import threading
#from multiprocessing import Process
import multiprocessing
import os



def BruteForceAffin(patch1,patch2,angle,scaleInit):
    width=patch1.shape[1]
    height=patch1.shape[0]

    ox=int(width/2.0)
    oy=int(height/2.0)

    patch1=NormalizePatch(patch1)
    patch2=NormalizePatch(patch2)
    val, diffPatch =ErrorBetweenImages(patch1,patch2)

#    print("Init Error: ",val)
#    cv2.imwrite("diffPatch.png",diffPatch)


#    print("BruteForceAffin")

#    print("BruteForceAffin",' angle: ',angle,'  scaleinit: ',scaleInit)

    cnt=0



    bestValue=999999999.9


    for alpha in range(-3,4):
        angle2=float(alpha)/40.0+angle

        for dx in range(-2,3):
            for dy in range(-2,3):
                for ds in range(-4,5):

#    for alpha in range(0,1):
#        angle2=float(alpha)/12.0+angle

#        for dx in range(0,1):
#            for dy in range(0,1):
#                for ds in range(20,21):

#    for alpha in range(0,2):
#        angle2=float(alpha)/12.0+angle

#        for dx in range(0,2):
#            for dy in range(0,2):
#                for ds in range(20,22):

                    scale=(1.0+float(ds)/40.0)*scaleInit
                    deltaX=float(dx)/1.0
                    deltaY=float(dy)/1.0


                    H=np.eye((3))

                    c=scale*math.cos(angle2)
                    s=scale*math.sin(angle2)

                    H[0,0]=c
                    H[1,0]=s

                    H[0,1]=-s
                    H[1,1]=c

                    H[0,2]=ox-c*ox+s*oy+deltaX
                    H[1,2]=oy-s*ox-c*oy+deltaY



                    newPatch = cv2.warpPerspective(patch1, H, (width,height), cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=(0,0,0))
                    errorValue, diffPatch=ErrorBetweenImages(newPatch,patch2)

                    if errorValue<bestValue:
                        bestImage=newPatch
                        bestValue=errorValue
                        bestAlpha=angle2
                        bestX=deltaX
                        bestY=deltaY
                        bestScale=scale
                        bestDiff=diffPatch

#                    print('angle:',angle2," deltaX",deltaX,"  deltaY:",deltaY,"  error:",errorValue)

#                    fileName = f"brutePatches/brutePatch{cnt:03d}.png"
#                    fileName2 = f"diffPatches/diffPatch{cnt:03d}.png"



#                    cv2.imwrite(fileName,newPatch)
#                    cv2.imwrite(fileName2,diffPatch)

                    cnt=cnt+1


#    cv2.imwrite("best1.png",bestImage)
#    cv2.imwrite("bestDiff.png",bestDiff)

#    print('bestAlpha',bestAlpha)
#    print('bestX',bestX)
#    print('bestY',bestY)
#    print('bestScale',bestScale)
#    print(bestValue)

    return bestAlpha,bestX,bestY,bestScale


def BruteForceThread(idx,img1,img2,affinities,resultList):

    height1,width1 = img1.shape
    height2,width2 = img2.shape


    print("Processing ...Idx: ",idx,' ...')

    a1=affinities[idx,0]
    a2=affinities[idx,1]
    a3=affinities[idx,2]
    a4=affinities[idx,3]
    a5=affinities[idx,4]
    a6=affinities[idx,5]

    pt1x=affinities[idx,6]
    pt1y=affinities[idx,7]

    pt2x=affinities[idx,8]
    pt2y=affinities[idx,9]

    angle=math.atan2(a2,a1)
    scale=math.sqrt(a1*a1+a2*a2)


#Crop images
    SZ=30

    patch1=np.zeros((2*SZ+1,2*SZ+1),dtype=np.uint8)
    patch2=np.zeros((2*SZ+1,2*SZ+1),dtype=np.uint8)

    for dx in range(-SZ,SZ+1):
        for dy in range(-SZ,SZ+1):

            x1=pt1x+dx
            y1=pt1y+dy

            x2=pt2x+dx
            y2=pt2y+dy

            if ((x1>=0) and (x1<width1) and (y1>=0) and (y1<height1)):
                patch1[dy+SZ,dx+SZ]=img1[int(y1),int(x1)]
            if ((x2>=0) and (x2<width2) and (y2>=0) and (y2<height2)):
                patch2[dy+SZ,dx+SZ]=img2[int(y2),int(x2)]




    bestAlpha,bestX,bestY,bestScale = BruteForceAffin(patch1,patch2,angle,scale)

    ox=int(patch1.shape[1]/2.0)
    oy=int(patch1.shape[0]/2.0)





    sc=bestScale*math.cos(bestAlpha)
    ss=bestScale*math.sin(bestAlpha)

#    a1=scale*math.cos(angle)
#    a3=-scale*math.sin(angle)
#    a2=scale*math.sin(angle)
#    a4=scale*math.cos(angle)
#    a5=pt2[0]-a1*pt1[0]-a3*pt1[1]
#    a6=pt2[1]-a2*pt1[0]-a4*pt1[1]


    a1=sc
    a2=ss
    a3=-1.0*ss
    a4=sc
    a5=pt2x-a1*pt1x-a3*pt1y+bestX
    a6=pt2y-a2*pt1x-a4*pt1y+bestY

    a7=affinities[idx,6]
    a8=affinities[idx,7]
    a9=affinities[idx,8]
    a10=affinities[idx,9]


    processed_data=[idx,a1,a2,a3,a4,a5,a6,a7,a8,a9,a10]
    resultList.extend(processed_data)


#    newAffinities[idx,0]=a1
#    newAffinities[idx,1]=a2
#    newAffinities[idx,2]=a3
#    newAffinities[idx,3]=a4
#    newAffinities[idx,4]=a5
#    newAffinities[idx,5]=a6
#    newAffinities[idx,6]=affinities[idx,6]
#    newAffinities[idx,7]=affinities[idx,7]
#    newAffinities[idx,8]=affinities[idx,8]
#    newAffinities[idx,9]=affinities[idx,9]


#    print(newAffinities)


# ---- main starts here ----

if len(sys.argv) >= 5:
    affinities=np.loadtxt(sys.argv[3])

    img1Filename=sys.argv[1]
    img2Filename=sys.argv[2]

    img1 = cv2.imread(img1Filename, cv2.IMREAD_GRAYSCALE)
    img2 = cv2.imread(img2Filename, cv2.IMREAD_GRAYSCALE)

    if img1 is None or img2 is None:
        print("File loading error.")
        exit(10)


    num=affinities.shape[0]




#    for idx in range(num):
#        thread = BruteForceThread(idx,img1,img2,affinities,newAffinities)


    num_processes = os.cpu_count() if os.cpu_count() else 4 # Használjuk az elérhető magokat

    num_processes=multiprocessing.cpu_count()


    iternum=math.ceil(num/num_processes)
    print("Iternum ", iternum)


    newAffinities=np.zeros((num,10))



    for iterIdx in range(iternum):

        with multiprocessing.Manager() as manager:
            threads=[]
            shared_list = manager.list() # Létrehozunk egy megosztott listát
            for procIdx in range(num_processes):
                idx=iterIdx*num_processes+procIdx
                if idx<num:
                    thread = multiprocessing.Process(target=BruteForceThread, args=(idx,img1,img2,affinities,shared_list))
                    print("Thread #",idx,'  started.')
                    thread.start()
                    threads.append(thread)

            for procIdx in range(num_processes):
                idx=iterIdx*num_processes+procIdx
                if idx<num:
                    threads[procIdx].join()
                    print("Thread #",idx,'  finished.')

            results_array = list(shared_list) # Konvertáljuk a Manager.list-et normál listává

            for procIdx in range(num_processes):
                idx=iterIdx*num_processes+procIdx
                if idx<num:
                    idxRes=shared_list[11*procIdx]
                    newAffinities[idxRes,0]=results_array[11*procIdx+1]
                    newAffinities[idxRes,1]=results_array[11*procIdx+2]
                    newAffinities[idxRes,2]=results_array[11*procIdx+3]
                    newAffinities[idxRes,3]=results_array[11*procIdx+4]
                    newAffinities[idxRes,4]=results_array[11*procIdx+5]
                    newAffinities[idxRes,5]=results_array[11*procIdx+6]
                    newAffinities[idxRes,6]=results_array[11*procIdx+7]
                    newAffinities[idxRes,7]=results_array[11*procIdx+8]
                    newAffinities[idxRes,8]=results_array[11*procIdx+9]
                    newAffinities[idxRes,9]=results_array[11*procIdx+10]


    np.savetxt(sys.argv[4],newAffinities)







#    for idx in range(num):
#        thread = threading.Thread(target=BruteForceThread, args=(idx,img1,img2,affinities,newAffinities))
#        thread.start()
#        threads.append(thread)

#    for idx in range(num):
#        threads[idx].join()
#        print("Thread #",idx,'  finished.')


else:
    print("Usage: python OpenCVAffineMatcher.py imagefile1 imagefile2 inputaffinities refinedaffinities")
