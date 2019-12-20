# Learn more or give us feedback
# USAGE
# python object_size.py --image images/example_01.png --width 0.955
# python object_size.py --image images/example_02.png --width 0.955
# python object_size.py --image images/example_03.png --width 3.5

# import the necessary packages
from scipy.spatial import distance as dist
from imutils import perspective
from imutils import contours
import numpy as np
import argparse
import imutils
import cv2

def midpoint(ptA, ptB):
    return ((ptA[0] + ptB[0]) * 0.5, (ptA[1] + ptB[1]) * 0.5)

# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-i", "--image", required=True,
    help="path to the input image")
ap.add_argument("-w", "--width", type=float, required=True,
    help="width of the left-most object in the image (in inches)")
args = vars(ap.parse_args())

# load the image, convert it to grayscale, and blur it slightly
image = cv2.imread(args["image"])
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
gray = cv2.GaussianBlur(gray, (7, 7), 0)

# perform edge detection, then perform a dilation + erosion to
# close gaps in between object edges
edged = cv2.Canny(gray, 50, 100)
edged = cv2.dilate(edged, None, iterations=1)
edged = cv2.erode(edged, None, iterations=1)

# find contours in the edge map
cnts = cv2.findContours(edged.copy(), cv2.RETR_EXTERNAL,
    cv2.CHAIN_APPROX_SIMPLE)
cnts = imutils.grab_contours(cnts)

# sort the contours from left-to-right and initialize the
# 'pixels per metric' calibration variable
(cnts, _) = contours.sort_contours(cnts)
pixelsPerMetric = None

# loop over the contours individually
for c in cnts:
    # if the contour is not sufficiently large, ignore it
    if cv2.contourArea(c) < 500:
        continue
    
    ### 넓이가 충분히 크지 않으면 무시
    # compute the rotated bounding box of the contour
    orig = image.copy()
    cv2.drawContours(orig,[c],0,(255,0,0),3)
    box = cv2.minAreaRect(c)
    box = cv2.cv.BoxPoints(box) if imutils.is_cv2() else cv2.boxPoints(box)
    box = np.array(box, dtype="int")
    
    # order the points in the contour such that they appear
    # in top-left, top-right, bottom-right, and bottom-left
    # order, then draw the outline of the rotated bounding
    # box
    box = perspective.order_points(box)
    cv2.drawContours(orig, [box.astype("int")], -1, (0, 255, 0), 2)

    # loop over the original points and draw them
    for (x, y) in box:
        cv2.circle(orig, (int(x), int(y)), 5, (0, 0, 255), -1)

    # unpack the ordered bounding box, then compute the midpoint
    # between the top-left and top-right coordinates, followed by
    # the midpoint between bottom-left and bottom-right coordinates
    (tl, tr, br, bl) = box
    (tltrX, tltrY) = midpoint(tl, tr)
    (blbrX, blbrY) = midpoint(bl, br)

    # compute the midpoint between the top-left and top-right points,
    # followed by the midpoint between the top-righ and bottom-right
    (tlblX, tlblY) = midpoint(tl, bl)
    (trbrX, trbrY) = midpoint(tr, br)

    # draw the midpoints on the image
#     cv2.circle(orig, (int(tltrX), int(tltrY)), 5, (255, 0, 0), -1)
#     cv2.circle(orig, (int(blbrX), int(blbrY)), 5, (255, 0, 0), -1)
#     cv2.circle(orig, (int(tlblX), int(tlblY)), 5, (255, 0, 0), -1)
#     cv2.circle(orig, (int(trbrX), int(trbrY)), 5, (255, 0, 0), -1)

    # draw lines between the midpoints
#     cv2.line(orig, (int(tltrX), int(tltrY)), (int(blbrX), int(blbrY)),
#         (255, 0, 255), 2)
#     cv2.line(orig, (int(tlblX), int(tlblY)), (int(trbrX), int(trbrY)),
#         (255, 0, 255), 2)

    # compute the Euclidean distance between the midpoints
#     dA = dist.euclidean((tltrX, tltrY), (blbrX, blbrY))
#     dB = dist.euclidean((tlblX, tlblY), (trbrX, trbrY))

    # if the pixels per metric has not been initialized, then
    # compute it as the ratio of pixels to supplied metric
    # (in this case, inches)
#     if pixelsPerMetric is None:
#         pixelsPerMetric = dB / args["width"]
# 
#     # compute the size of the object
#     dimA = dA / pixelsPerMetric
#     dimB = dB / pixelsPerMetric
    
    ######################################################
    
    leftmost = tuple(c[c[:, :, 0].argmin()][0])
    rightmost = tuple(c[c[:, :, 0].argmax()][0])
    topmost = tuple(c[c[:, :, 1].argmin()][0])
    bottommost = tuple(c[c[:, :, 1].argmax()][0])
    
    
    cv2.circle(image, leftmost, 5, (0, 0, 255), -1)
    cv2.circle(image, rightmost, 5, (0, 255, 0), -1)
    cv2.circle(image, topmost, 5, (255, 0, 0), -1)
    cv2.circle(image, bottommost, 5, (255, 255, 0), -1)
    
    
    cv2.line(orig,(leftmost[0],leftmost[1]), (rightmost[0],rightmost[1]),(0,0,255),2)
    cv2.line(orig,(topmost[0],topmost[1]), (bottommost[0],bottommost[1]),(0,0,255),2)

    # compute the Euclidean distance between the extreme poi
    dA = dist.euclidean((leftmost[0],leftmost[1]), (rightmost[0],rightmost[1]))
    dB = dist.euclidean((topmost[0],topmost[1]), (bottommost[0],bottommost[1]))

    if pixelsPerMetric is None:
        pixelsPerMetric = dB / args["width"]

    # compute the size of the object
    dimA = dA / pixelsPerMetric
    dimB = dB / pixelsPerMetric
      
#     cv2.line(orig, (int(tltrX), int(tltrY)), (int(blbrX), int(blbrY)),
#     (255, 0, 255), 2)
#     cv2.line(orig, (int(tlblX), int(tlblY)), (int(trbrX), int(trbrY)),
#     (255, 0, 255), 2)

    # draw the object sizes on the image
    cv2.putText(orig, "{:.1f}in".format(dimA),
         (int(leftmost[0] - 15), int(leftmost[1] - 10)), cv2.FONT_HERSHEY_SIMPLEX,
         0.65, (255, 255, 255), 2)
    cv2.putText(orig, "{:.1f}in".format(dimB),
         (int(bottommost[0] + 10), int(bottommost[1])), cv2.FONT_HERSHEY_SIMPLEX,
         0.65, (255, 255, 255), 2)

    # show the output image
    cv2.imshow("Image", orig)
    cv2.waitKey(0)
