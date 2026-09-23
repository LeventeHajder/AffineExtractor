import sys
import cv2
import numpy as np
import math
import random


# -- main ---

if len(sys.argv) >= 4:

    affinities=np.loadtxt(sys.argv[3])

    img1Filename=sys.argv[1]
    img2Filename=sys.argv[2]

    img1 = cv2.imread(img1Filename)
    img2 = cv2.imread(img2Filename)

    if img1 is None or img2 is None:
        print("File loading error.")
        exit(10)


    height1,width1,_=img1.shape
    height2,width2,_=img2.shape


    imageRes=np.full((height1, width1+width2, 3), 255, dtype=np.uint8)
    imageRes[0:height1,0:width1,:]=img1[0:height1,0:width1,:]
    imageRes[0:height1,width1:(width1+width2),:]=img2[0:height1,0:width2,:]


    num=affinities.shape[0]

    SZ=30


    for idx in range(num):

        print('Drawing affine feature #',idx,'/',num)

        # Start coordinate, here (0, 0)
        # represents the top left corner of image
        x1=int(round(affinities[idx,6]))
        y1=int(round(affinities[idx,7]))

        x2=affinities[idx,8]
        y2=affinities[idx,9]

        x2Draw=int(round(x2))
        y2Draw=int(round(y2))


        colorDraw =   (random.randrange(255),random.randrange(255), random.randrange(255))



        drawPt1=(x1,y1)
        drawPt2=(x2Draw+width1,y2Draw)

        cv2.line(imageRes, drawPt1,drawPt2, colorDraw, 3)

        # Green color in BGR
        color = (0, 255, 0)

        # Line thickness of 9 px
        thickness = 1

        i1p1=(x1-SZ,y1-SZ)
        i1p2=(x1-SZ,y1+SZ)
        i1p3=(x1+SZ,y1+SZ)
        i1p4=(x1+SZ,y1-SZ)

        # Using cv2.line() method
        # Draw a diagonal green line with thickness of 9 px
        cv2.line(img1, i1p1,i1p2, color, thickness)
        cv2.line(img1, i1p2,i1p3, color, thickness)
        cv2.line(img1, i1p3,i1p4, color, thickness)
        cv2.line(img1, i1p4,i1p1, color, thickness)

        A=np.array([affinities[idx,0],affinities[idx,2],affinities[idx,1],affinities[idx,3]]).reshape(2,2)


        vec1=A@np.array([-SZ,-SZ])
        vec2=A@np.array([-SZ,SZ])
        vec3=A@np.array([SZ,SZ])
        vec4=A@np.array([SZ,-SZ])



        i2p1=(int(round(vec1[0]+x2)),int(round(vec1[1]+y2)))
        i2p2=(int(round(vec2[0]+x2)),int(round(vec2[1]+y2)))
        i2p3=(int(round(vec3[0]+x2)),int(round(vec3[1]+y2)))
        i2p4=(int(round(vec4[0]+x2)),int(round(vec4[1]+y2)))

#        cv2.line(img2, i2p1,i2p2, color, thickness)
#        cv2.line(img2, i2p2,i2p3, color, thickness)
#        cv2.line(img2, i2p3,i2p4, color, thickness)
#        cv2.line(img2, i2p4,i2p1, color, thickness)



        # Green color in BGR
        color = (0, 0, 255)


        x1=affinities[idx,6]
        y1=affinities[idx,7]

        A2=np.array([affinities[idx,0],affinities[idx,2],affinities[idx,4],affinities[idx,1],affinities[idx,3],affinities[idx,5]]).reshape(2,3)

        pt1=A2@(np.array([x1-SZ,y1-SZ,1.0]).reshape(3,1))
        pt2=A2@(np.array([x1-SZ,y1+SZ,1.0]).reshape(3,1))
        pt3=A2@(np.array([x1+SZ,y1+SZ,1.0]).reshape(3,1))
        pt4=A2@(np.array([x1+SZ,y1-SZ,1.0]).reshape(3,1))


        pt1=(int(np.round(pt1[0,0])),int(np.round(pt1[1,0])))
        pt2=(int(np.round(pt2[0,0])),int(np.round(pt2[1,0])))
        pt3=(int(np.round(pt3[0,0])),int(np.round(pt3[1,0])))
        pt4=(int(np.round(pt4[0,0])),int(np.round(pt4[1,0])))

        cv2.line(img2, pt1,pt2, color, thickness)
        cv2.line(img2, pt2,pt3, color, thickness)
        cv2.line(img2, pt3,pt4, color, thickness)
        cv2.line(img2, pt4,pt1, color, thickness)


        if len(sys.argv)==7:
            affinities2=np.loadtxt(sys.argv[6])
            # Green color in BGR
            color = (0, 255, 0)
            A3=np.array([affinities2[idx,0],affinities2[idx,2],affinities2[idx,4],affinities2[idx,1],affinities2[idx,3],affinities2[idx,5]]).reshape(2,3)

            pt1=A3@(np.array([x1-SZ,y1-SZ,1.0]).reshape(3,1))
            pt2=A3@(np.array([x1-SZ,y1+SZ,1.0]).reshape(3,1))
            pt3=A3@(np.array([x1+SZ,y1+SZ,1.0]).reshape(3,1))
            pt4=A3@(np.array([x1+SZ,y1-SZ,1.0]).reshape(3,1))

            pt1=(int(np.round(pt1[0,0])),int(np.round(pt1[1,0])))
            pt2=(int(np.round(pt2[0,0])),int(np.round(pt2[1,0])))
            pt3=(int(np.round(pt3[0,0])),int(np.round(pt3[1,0])))
            pt4=(int(np.round(pt4[0,0])),int(np.round(pt4[1,0])))

            cv2.line(img2, pt1,pt2, color, thickness)
            cv2.line(img2, pt2,pt3, color, thickness)
            cv2.line(img2, pt3,pt4, color, thickness)
            cv2.line(img2, pt4,pt1, color, thickness)





    cv2.imwrite(sys.argv[4],img1)
    cv2.imwrite(sys.argv[5],img2)

    cv2.imwrite("result.png",imageRes)

