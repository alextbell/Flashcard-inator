import sys
from PyQt5.QtWidgets import (QApplication, QLabel, QWidget, QVBoxLayout, QLineEdit, QFileDialog, QPushButton, QLineEdit)
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import QDir
from imutils.object_detection import non_max_suppression
import numpy as np
import argparse
import time
import cv2
import math
import os
import random
import genanki
import html
import subprocess
global count


class RedactIt(QWidget):
    list_of_pictures = []
    def __init__(self):
        super().__init__()
        self.resize(800,600)
        self.button1 = QPushButton('Upload Image')
        self.button2 = QPushButton('Add image to deck')
        self.button3 = QPushButton('Make My Anki Deck')
        self.labelImage = QLabel()
        self.line = QLineEdit()
        self.button1.clicked.connect(self.get_image_file)
        self.button2.clicked.connect(self.addImageToList)
        self.button3.clicked.connect(self.onPressed)
        self.button3.clicked.connect(self.make_some_cards)
        layout = QVBoxLayout()
        layout.addWidget(self.button1)
        layout.addWidget(self.labelImage)
        layout.addWidget(self.line)
        layout.addWidget(self.button2)
        layout.addWidget(self.button3)
        self.setLayout(layout)
    def get_image_file(self):
        global file_name
        file_name, _ = QFileDialog.getOpenFileName(self, "Open Image File", r"~\\", "Image files (*.jpg *.jpeg *.png)")
        self.labelImage.setPixmap(QPixmap(file_name).scaled(500,500))
    def onPressed(self):
        global deck_name
        deck_name = self.line.text()
    def addImageToList(self):
        try: piclist
        except NameError: self.initializeListOfPictures()
        else: self.addToListOfPictures(piclist)
    def initializeListOfPictures(self):
        self.list_of_pictures = [file_name]
        global piclist
        piclist = self.list_of_pictures.copy()
    def addToListOfPictures(self, x):
        x.append(file_name)
        piclist = x.copy()
    def make_some_cards(self):
        for x in piclist:
            image = cv2.imread(x)
            orig = image.copy()
            orig1 = orig.copy()
            (H, W) = image.shape[:2]

            (newW, newH) = (320, 320)
            rW = W / float(newW)
            rH = H / float(newH)

            image = cv2.resize(image, (newW, newH))
            (H, W) = image.shape[:2]

            layerNames = [
            	"feature_fusion/Conv_7/Sigmoid",
            	"feature_fusion/concat_3"]

            # load the pre-trained EAST text detector
            net = cv2.dnn.readNet('/Users/elissabell/MYVENV/opencv-text-detection/frozen_east_text_detection.pb')

            # construct a blob from the image and then perform a forward pass of
            # the model to obtain the two output layer sets
            blob = cv2.dnn.blobFromImage(image, 1.0, (W, H),
            	(123.68, 116.78, 103.94), swapRB=True, crop=False)
            start = time.time()
            net.setInput(blob)
            (scores, geometry) = net.forward(layerNames)
            end = time.time()
            (numRows, numCols) = scores.shape[2:4]
            rects = []
            confidences = []
            for y in range(0, numRows):
            	# extract the scores (probabilities), followed by the geometrical
            	# data used to derive potential bounding box coordinates that
            	# surround text
            	scoresData = scores[0, 0, y]
            	xData0 = geometry[0, 0, y]
            	xData1 = geometry[0, 1, y]
            	xData2 = geometry[0, 2, y]
            	xData3 = geometry[0, 3, y]
            	anglesData = geometry[0, 4, y]

            	# loop over the number of columns
            	for x in range(0, numCols):
            		# if our score does not have sufficient probability, ignore it
            		if scoresData[x] < 0.5:
            			continue

            		# compute the offset factor as our resulting feature maps will
            		# be 4x smaller than the input image
            		(offsetX, offsetY) = (x * 4.0, y * 4.0)

            		# extract the rotation angle for the prediction and then
            		# compute the sin and cosine
            		angle = anglesData[x]
            		cos = np.cos(angle)
            		sin = np.sin(angle)

            		# use the geometry volume to derive the width and height of
            		# the bounding box
            		h = xData0[x] + xData2[x]
            		w = xData1[x] + xData3[x]

            		# compute both the starting and ending (x, y)-coordinates for
            		# the text prediction bounding box
            		endX = int(offsetX + (cos * xData1[x]) + (sin * xData2[x]))
            		endY = int(offsetY - (sin * xData1[x]) + (cos * xData2[x]))
            		startX = int(endX - w)
            		startY = int(endY - h)

            		# add the bounding box coordinates and probability score to
            		# our respective lists
            		rects.append((startX, startY, endX, endY))
            		confidences.append(scoresData[x])
            boxes = non_max_suppression(np.array(rects), probs=confidences)
            boxeslist = boxes.tolist()
            nboxeslist = len(boxeslist)
            newboxeslist = boxeslist.copy()

            def calculateDistance(x1,y1,x2,y2):
            	dist = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
            	return dist

            def makeBiggerRectangle(rect1, rect2):
                if rect1[0] <= rect2[0]:
                    side1 = rect1[0]
                else:
                    side1 = rect2[0]
                if rect1[1] <= rect2[1]:
                    side2 = rect1[1]
                else:
                    side2 = rect2[1]
                if rect1[2] >= rect2[2]:
                    side3 = rect1[2]
                else:
                    side3 = rect2[2]
                if rect1[3] >= rect2[3]:
                    side4 = rect1[3]
                else:
                    side4 = rect2[3]
                newRectangle = [side1, side2, side3, side4]
                return newRectangle

            rectlist = []
            def distanceBetweenBottomRightandBottomLeftTopRightTopLeft(boxeslist, nboxeslist):
                for rectcore in range(nboxeslist):
                    for rectpair in range(nboxeslist):
                        distanceBottom = calculateDistance(x1 = boxeslist[rectcore][2], y1 = boxeslist[rectcore][3], x2 = boxeslist[rectpair][0], y2 = boxeslist[rectpair][3])
                        distanceTop = calculateDistance(x1 = boxeslist[rectcore][2], y1 = boxeslist[rectcore][1], x2 = boxeslist[rectpair][0], y2 = boxeslist[rectpair][1])
                        distanceSum = distanceBottom + distanceTop
                        if distanceSum < 15:
                            if boxeslist[rectcore] and boxeslist[rectpair] in rectlist:
                                continue
                            elif boxeslist[rectcore] in rectlist and boxeslist[rectpair] not in rectlist:
                                rectlist.append(boxeslist[rectpair])
                            elif boxeslist[rectcore] not in rectlist and boxeslist[rectpair] in rectlist:
                                rectlist.append(boxeslist[rectcore])
                            else:
                                rectlist.append(boxeslist[rectcore])
                                rectlist.append(boxeslist[rectpair])
                        else:
                            continue
            def can_rectangles_be_collapsed(list):
                vector = []
                for x in list:
                    for y in list:
                        if x != y:
                            ystartdist = abs(x[1] - y[1])
                            yenddist = abs(x[3] - y[3])
                            ytotal = ystartdist + yenddist
                            if 0 <= ytotal < 15:
                                vector.append(1)
                            else:
                                vector.append(0)
                        else:
                            continue
                if 1 in vector:
                    return True
                else:
                    return False

            nrectlist = len(rectlist)
            def inner_collapse(i, list, subtractedbiglist):
                for j in list:
                    if j != i:
                        ystartdist = abs(i[1] - j[1])
                        yenddist = abs(i[3] - j[3])
                        ytotal = ystartdist + yenddist
                        if 0 <= ytotal < 15:
                            newRectangle = makeBiggerRectangle(i, j)
                            if newRectangle not in list:
                                list.append(newRectangle)
                                list.remove(i)
                                list.remove(j)
                                if j in subtractedbiglist:
                                    subtractedbiglist.remove(j)
                                if i in subtractedbiglist:
                                    subtractedbiglist.remove(i)
                                return
                            else:
                                continue
            def collapse_rectangles(list, subtractedbiglist):
                for i in list:
                    inner_collapse(i, list, subtractedbiglist)
                return list

            distanceBetweenBottomRightandBottomLeftTopRightTopLeft(boxeslist, nboxeslist)

            while can_rectangles_be_collapsed(list = rectlist) == True:
                collapse_rectangles(list = rectlist, subtractedbiglist = newboxeslist)

            halfcollapsedlist = rectlist + newboxeslist
            nhalfcollapsedlist = len(halfcollapsedlist)
            halfcollapsed_minus_x_collapse = halfcollapsedlist.copy()
            xRectlist = []
            def distanceBetweenBottomRightTopRightandBottomLeftTopLeft(boxeslist, nboxeslist):
                for rectcore in range(nboxeslist):
                    for rectpair in range(nboxeslist):
                        distanceR = calculateDistance(x1 = boxeslist[rectcore][2], y1 = boxeslist[rectcore][1], x2 = boxeslist[rectpair][2], y2 = boxeslist[rectpair][3])
                        distanceL = calculateDistance(x1 = boxeslist[rectcore][0], y1 = boxeslist[rectcore][1], x2 = boxeslist[rectpair][0], y2 = boxeslist[rectpair][3])
                        distanceSum = distanceR + distanceL
                        if distanceSum < 15:
                            if boxeslist[rectcore] and boxeslist[rectpair] in xRectlist:
                                continue
                            elif boxeslist[rectcore] in rectlist and boxeslist[rectpair] not in xRectlist:
                                xRectlist.append(boxeslist[rectpair])
                            elif boxeslist[rectcore] not in rectlist and boxeslist[rectpair] in xRectlist:
                                xRectlist.append(boxeslist[rectcore])
                            else:
                                xRectlist.append(boxeslist[rectcore])
                                xRectlist.append(boxeslist[rectpair])
                        else:
                            continue

            def can_rectangles_from_diff_x_plane_be_collapsed(list):
                vector = []
                for x in list:
                    for y in list:
                        if x != y:
                            xstartdist = abs(x[0] - y[0])
                            xenddist = abs(x[2] - y[2])
                            xtotal = xstartdist + xenddist
                            if 0 <= xtotal < 15:
                                vector.append(1)
                            else:
                                vector.append(0)
                        else:
                            continue
                if 1 in vector:
                    return True
                else:
                    return False
            def inner_x_collapse(i, list, subtractedbiglist):
                for j in list:
                    if j != i:
                        xstartdist = abs(i[0] - j[0])
                        xenddist = abs(i[2] - j[2])
                        xtotal = xstartdist + xenddist
                        if 0 <= xtotal < 15:
                            newRectangle = makeBiggerRectangle(i, j)
                            if newRectangle not in list:
                                list.append(newRectangle)
                                list.remove(i)
                                list.remove(j)
                                if j in subtractedbiglist:
                                    subtractedbiglist.remove(j)
                                if i in subtractedbiglist:
                                    subtractedbiglist.remove(i)
                                return
                            else:
                                continue


            def collapse_rectangles_from_diff_x_planes(list, subtractedbiglist):
                for i in list:
                    inner_x_collapse(i, list, subtractedbiglist)
                return list

            distanceBetweenBottomRightTopRightandBottomLeftTopLeft(halfcollapsedlist, nhalfcollapsedlist)

            while can_rectangles_from_diff_x_plane_be_collapsed(xRectlist):
                collapse_rectangles_from_diff_x_planes(xRectlist, halfcollapsed_minus_x_collapse)

            final_boxes = xRectlist + halfcollapsed_minus_x_collapse
            nfinal_boxes = len(final_boxes)
            ####I CHANGED boxes to final_boxes
            # loop over the bounding boxes
            batch_id = random.randrange(1 << 30, 1 << 31)
            count = 0
            cv2.imwrite("/Users/elissabell/Library/Application Support/Anki2/User 1/collection.media/{}.jpg".format(str(batch_id)), orig)
            for i in final_boxes:
            	orig1 = orig.copy()
            	startX = int(i[0] * rW)
            	startY = int(i[1] * rH)
            	endX = int(i[2] * rW)
            	endY = int(i[3] * rH)
            	count += 1
            	pic = cv2.rectangle(orig1, (startX, startY), (endX, endY), (255, 0, 0), -1)
            	cv2.imwrite('/Users/elissabell/Library/Application Support/Anki2/User 1/collection.media/{}{}.jpg'.format(str(batch_id),str(count)), pic)

            number = random.randrange(1 << 30, 1 << 31)
            my_model = genanki.Model(
            number,
            'Simple Model with Media',
            fields=[
                {'name': 'Question'},
                {'name': 'Answer'},
                {'name': 'MyMedia'},                                  # ADD THIS
                ],
                templates=[
                {
                'name': 'Card 1',
                'qfmt': '{{Question}}<br>{{MyMedia}}',              # AND THIS
                'afmt': '{{FrontSide}}<hr id="answer">{{Answer}}',
                },
                ])
            number = random.randrange(1 << 30, 1 << 31)
            #make each deck have unique ID that corresponds to their given name. convert letters to numbers using ord.sa
            deck_id = int(''.join(str(ord(c)) for c in str(deck_name)))

            try: my_deck
            except NameError: my_deck = genanki.Deck(deck_id,'{}'.format(str(deck_name)))
            else: pass

            counter = 0
            for i in range(nfinal_boxes):
                counter += 1
                my_note = genanki.Note(
                model=my_model,
                fields=['yeet', "<img src='{}.jpg'>".format(str(batch_id)), "<img src='{}{}.jpg'>".format(str(batch_id),str(counter))])
                my_deck.add_note(my_note)

        my_package = genanki.Package(my_deck)
        genanki.Package(my_deck).write_to_file('/Users/elissabell/Documents//Anki_Decks/output.apkg')
        FileName = '/Users/elissabell/Documents//Anki_Decks/output.apkg'
        subprocess.call(['open', FileName])
if __name__ == '__main__':
    app = QApplication(sys.argv)
    demo = RedactIt()
    demo.show()
    sys.exit(app.exec_())
