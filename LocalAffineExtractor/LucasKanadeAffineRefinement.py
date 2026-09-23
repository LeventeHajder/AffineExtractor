import sys
import cv2
import numpy as np
import math
from AffineHelper import *
import threading
#from multiprocessing import Process
import multiprocessing
import os


def LucasKanadeForAffine(patch1,patch2,a1,a2,a3,a4,a5,a6):
    width=patch1.shape[1]
    height=patch1.shape[0]


#    cv2.imwrite("p2.png",patch2)

    A=np.eye(3)
    A[0,0]=a1+1.0
    A[1,0]=a2
    A[0,1]=a3
    A[1,1]=a4+1.0
    A[0,2]=a5
    A[1,2]=a6

    Ainv=np.linalg.inv(A)


    a1inv=Ainv[0,0]-1.0
    a2inv=Ainv[1,0]
    a3inv=Ainv[0,1]
    a4inv=Ainv[1,1]-1.0

    a5inv=Ainv[0,2]
    a6inv=Ainv[1,2]



    newPatch = cv2.warpPerspective(patch1, A, (width,height), cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=(0,0,0))

    errValue,diffPatch = ErrorBetweenImages(newPatch,patch2)


    initError=errValue;

#    cv2.imwrite("diffPatchagain.png",diffPatch)
#    cv2.imwrite("newPatchagain.png",newPatch)



#    patchName='newPatch'
#    fileName = "newPatch/newPatch000.png"
#    cv2.imwrite(fileName,newPatch)





#    scale=1.0
#    angle=0.0

    SZ=int((width-1)/2)


#Initial parameters
#    a5=0.0
#    a6=0.0
#    a1=scale*math.cos(angle)-1.0
#    a3=-scale*math.sin(angle)
#    a2=-1.0*a3
#    a4=a1


#    sobel_u = cv2.Sobel(patch1, cv2.CV_64F, 1, 0, ksize=3)
#    sobel_v = cv2.Sobel(patch1, cv2.CV_64F, 0, 1, ksize=3)

    sobel_u, sobel_v =Sobel(patch1)




#    cv2.imwrite("sobelU.png",sobel_u)
#    cv2.imwrite("sobelV.png",sobel_v)

#    np.savetxt("sobelU.txt",sobel_u)
#    np.savetxt("sobelV.txt",sobel_v)

    contIter=True

    iterNum=0

    while (contIter):
        iterNum=iterNum+1

        A=np.zeros((6,6))
        b=np.zeros((6,1))

#        print('a1:',a1,' a2:',a2,' a3:',a3,' a4:',a4,' a5:',a5,' a6:',a6)

        for du in range(0,width-1):
            for dv in range(0,height-1):
                valid=True

                currU=float(du)
                currV=float(dv)

                newposU=(1.0+a1inv)*currU+a3inv*currV+a5inv
                newposV=(1.0+a4inv)*currV+a2inv*currU+a6inv
#                intensity1=patch1[int(newposV),int(newposV)]

# Hiba: inverz logika??
                intensity1=BilinearInterpolaton(patch1,newposU,newposV,False)
                intensity2=BilinearInterpolaton(patch2,currU,currV,False)

#                print('du',du)
#                print('dv',dv)
#                print('newposU',newposU)
#                print('newposV',newposV)
#                print("Inten1",intensity1)
#                print("Inten2",intensity2)


                sobelU=BilinearInterpolaton(sobel_u,newposU,newposV,True)
                sobelV=BilinearInterpolaton(sobel_v,newposU,newposV,True)

#                print("intensity2",intensity2)
#                print("intensity1",intensity1)

#                print("sobelU",sobelU)
#                print("sobelV",sobelV)


                if ((intensity2==-1000) or (intensity1==-1000) or (sobelU==-1000) or (sobelV==-1000)):
                    valid=False

                if (valid):

                    Cij=intensity1-intensity2
                    NablaJ=np.array([sobelU,sobelV])
                    W=np.array([[newposU,0,newposV,0,1,0],[0,newposU,0,newposV,0,1]])
                    V=(W.transpose())@(NablaJ.reshape(2,1))

                    V=V.reshape(6,1)


                    A=A+(V@V.transpose())

                    b=b+(Cij*V)




        if (abs(np.linalg.det(A))>1e-5):
            res=-1.0*(np.linalg.inv(A))@b
            res=res.reshape(6)
        else:
            res=(0.0,0.0,0.0,0.0,0.0,0.0)
#        print("Res:",res)
#        print("a5: ",a5," a6:",a6 )



#        print("res",res)


        a1inv=a1inv+res[0]
        a2inv=a2inv+res[1]
        a3inv=a3inv+res[2]
        a4inv=a4inv+res[3]
        a5inv=a5inv+res[4]
        a6inv=a6inv+res[5]



        Ainv=np.eye(3)
        Ainv[0,0]=a1inv+1.0
        Ainv[1,0]=a2inv
        Ainv[0,1]=a3inv
        Ainv[1,1]=a4inv+1.0
        Ainv[0,2]=a5inv
        Ainv[1,2]=a6inv

        A=np.linalg.inv(Ainv)


        a1=A[0,0]-1.0
        a2=A[1,0]
        a3=A[0,1]
        a4=A[1,1]-1.0

        a5=A[0,2]
        a6=A[1,2]


#Save images
        H=np.eye((3))

        H[0,0]=1.0+a1
        H[1,0]=a2

        H[0,1]=a3
        H[1,1]=1.0+a4

        H[0,2]=a5
        H[1,2]=a6

        H=np.linalg.inv(H)

        newPatch = cv2.warpPerspective(patch1, A, (width,height), cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=(0,0,0))

        errValue,diffPatch = ErrorBetweenImages(newPatch,patch2)
#        print("errValue:",errValue)



#        patchName='newPatch'
#        fileName = f"newPatch/newPatch{iterNum:03d}.png"
#        cv2.imwrite(fileName,newPatch)
#        print(fileName)

#        fileName2 = f"diffLucasKanade/diffPatch{iterNum:03d}.png"
#        cv2.imwrite(fileName2,diffPatch)


        if (iterNum>200):
            contIter=False

        if (np.linalg.norm(res)<1e-5):
            contIter=False


    if (errValue>1.1*initError) or (iterNum>100):
        print('Hello')
        a1=0.0
        a2=0.0
        a3=0.0
        a4=0.0
        a5=0.0
        a6=0.0



    return a1,a2,a3,a4,a5,a6







def LucasKanadeThread(idx,img1,img2,affinities,resultList):

    height1,width1 = img1.shape
    height2,width2 = img2.shape


    print("Processing ...Idx: ",idx,' ...')

    a1=affinities[idx,0]
    a2=affinities[idx,1]
    a3=affinities[idx,2]
    a4=affinities[idx,3]
    a5=affinities[idx,4]
    a6=affinities[idx,5]

    a1init=a1
    a2init=a2
    a3init=a3
    a4init=a4
    a5init=a5
    a6init=a6

    pt1x=affinities[idx,6]
    pt1y=affinities[idx,7]

    pt2x=affinities[idx,8]
    pt2y=affinities[idx,9]

    angle=math.atan2(a2,a1)
    scale=math.sqrt(a1*a1+a2*a2)

#    print('angle',angle)
#    print('scale',scale)




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


#Normalizálás?
#és a brute force-nál?

    patch1=NormalizePatch(patch1)
    patch2=NormalizePatch(patch2)


#    cv2.imwrite('patch1.png',patch1)
#    cv2.imwrite('patch2.png',patch2)


#    print('pt2xbecs: ',a1*pt1x+a3*pt1y+a5)
#    print('pt2ybecs: ',a2*pt1x+a4*pt1y+a6)


#    print('pt2xbecsNew: ',a1*pt1x+a3*pt1y+a5)
#    print('pt2ybecsNew: ',a2*pt1x+a4*pt1y+a6)


    a5=a5+a1*(pt1x-SZ)+a3*(pt1y-SZ)+SZ-pt2x
    a6=a6+a2*(pt1x-SZ)+a4*(pt1y-SZ)+SZ-pt2y

#    print('pt2xbecsNew: ',a1*pt1x+a3*pt1y+a5)
#    print('pt2ybecsNew: ',a2*pt1x+a4*pt1y+a6)



#    print('a5 new: ',a5)
#    print('a6 new: ',a6)


#    print('pt2xbecsLegNew: ',a1*SZ+a3*SZ+a5)
#    print('pt2ybecsLegNew: ',a2*SZ+a4*SZ+a6)


    a1=a1-1.0
    a4=a4-1.0


    a1,a2,a3,a4,a5,a6 = LucasKanadeForAffine(patch1,patch2,a1,a2,a3,a4,a5,a6)
    print('Idx: ',idx,' a1:',a1,' a2:',a2,' a3:',a3,' a4:',a4,' a5:',a5,' a6:',a6)


    if ((a1!=0.0) or (a2!=0.0) or (a3!=0.0) or (a4!=0.0) or (a5!=0.0) or (a6!=0.0) ):

        a1=a1+1.0
        a4=a4+1.0

    #Biztos?

        a5=a5-a1*(pt1x-SZ)-a3*(pt1y-SZ)-SZ+pt2x
        a6=a6-a2*(pt1x-SZ)-a4*(pt1y-SZ)-SZ+pt2y

    else:
        print("Brute Force parameters applied for \#",idx)

        a1=a1init
        a2=a2init
        a3=a3init
        a4=a4init
        a5=a5init
        a6=a6init
        print('Idx: ',idx,' a1:',a1,' a2:',a2,' a3:',a3,' a4:',a4,' a5:',a5,' a6:',a6, '--- coming from Brute force')


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


#delete later!!!
#    affinities[0,:]=affinities[1,:]

    num=affinities.shape[0]




#    for idx in range(num):
#        thread = BruteForceThread(idx,img1,img2,affinities,newAffinities)


    num_processes = os.cpu_count() if os.cpu_count() else 4 # Használjuk az elérhető magokat

    num_processes=multiprocessing.cpu_count()


    iternum=math.ceil(num/num_processes)
    print("Iternum ", iternum)


    newAffinities=np.zeros((num,10))



#    for iterIdx in range(iternum-6,iternum):
    for iterIdx in range(iternum):

        with multiprocessing.Manager() as manager:
            threads=[]
            shared_list = manager.list() # Létrehozunk egy megosztott listát
            for procIdx in range(num_processes):
                idx=iterIdx*num_processes+procIdx
                if idx<num:
                    thread = multiprocessing.Process(target=LucasKanadeThread, args=(idx,img1,img2,affinities,shared_list))
                    print("Thread #",idx,'  started.')
                    thread.start()
                    threads.append(thread)

            for procIdx in range(num_processes):
                idx=iterIdx*num_processes+procIdx
                if idx<num:
                    threads[procIdx].join()
                    print("Thread #",idx,'  finished.')

            results_array = list(shared_list) # Konvertáljuk a Manager.list-et normál listává
            print(shared_list)


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
