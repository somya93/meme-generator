#!/usr/bin/env python

# Copyright 2015 Google, Inc
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Overlays meme glasses on detected faces in the given image."""

import argparse
import math
import requests
from google.cloud import vision
from PIL import Image, ImageDraw
from io import BytesIO


# [START vision_face_detection_tutorial_send_request]
def detect_face(face_file, max_results):
    """Uses the Vision API to detect faces in the given file.

    Args:
        face_file: A file-like object containing an image with faces.
        max_results: Maximum number of faces to be detected

    Returns:
        An array of Face objects with information about the picture.
    """
    client = vision.ImageAnnotatorClient()

    # content = face_file.read()
    # image = vision.Image(content=content)

    image = vision.Image()
    image.source.image_uri = face_file
    return client.face_detection(
        image=image, max_results=max_results).face_annotations


# [END vision_face_detection_tutorial_send_request]


# [START vision_face_detection_tutorial_process_response]
def highlight_eyes(im, faces, output_filename):
    """Gets the landmarks on the faces, returns them in a variable called box

    Args:
        im: a file containing the image with the faces.
        faces: a list of faces found in the file. This should be in the format returned by the Vision API.
        output_filename: saves the output to location output_filename
    Returns:
        A list of coordinates of left eyes corner, right eye corner and midpoint between the eyes
    """
    # im = Image.open(image)
    draw = ImageDraw.Draw(im)

    for face in faces:
        for landmark in face.landmarks:
            if landmark.type_ == vision.FaceAnnotation.Landmark.Type.LEFT_EYE_LEFT_CORNER:
                verticesLeftLeftEyebrow = landmark.position
            if landmark.type_ == vision.FaceAnnotation.Landmark.Type.RIGHT_EYE_RIGHT_CORNER:
                verticesRightRightEyebrow = landmark.position
            if landmark.type_ == vision.FaceAnnotation.Landmark.Type.MIDPOINT_BETWEEN_EYES:
                verticesMidpointEyes = landmark.position

        box = [(verticesLeftLeftEyebrow.x, verticesLeftLeftEyebrow.y),
               (verticesRightRightEyebrow.x, verticesRightRightEyebrow.y),
               (verticesMidpointEyes.x, verticesMidpointEyes.y)]

        # draw line to show the distance between farthest corners of the eyes
        # draw.line(box + [box[0]], width=5, fill='#00ff00')

        # draw a point to show the midpoint between the two eyes
        # leftUpPoint = (box[2][0] - 3, box[2][1] - 3)
        # rightDownPoint = (box[2][0] + 3, box[2][1] + 3)
        # twoPointList = [leftUpPoint, rightDownPoint]
        # draw.ellipse(twoPointList, 'red')
    im.save(output_filename)
    return box


# [END vision_face_detection_tutorial_process_response]

# [START]
def add_prop(face_image, prop_image, output_file, box):
    background = Image.open(face_image)
    foreground = Image.open(prop_image)

    # we want to align the centre point of the prop_image to the midpoint between the eyes
    # draw a point to show the centre of the prop_image
    # cx = foreground.size[0] / 2
    # cy = foreground.size[1] / 2
    # leftUpPoint = (cx - 3, cy - 3)
    # rightDownPoint = (cx + 3, cy + 3)
    # twoPointList = [leftUpPoint, rightDownPoint]
    # draw = ImageDraw.Draw(foreground)
    # draw.ellipse(twoPointList, 'red')

    # calculate the slope of the line from corner to corner of the eyes, to get the orientation of the glasses
    # adjusted the y-coordinates of the background image since the top-left corner of the image is (0,0) instead of
    # the bottom-left
    # slope formula: m = (y2 - y1)/(x2 - x1)
    slope = ((-box[1][1]) - (-box[0][1])) / (box[1][0] - box[0][0])
    angle = math.degrees(math.atan(slope))

    # if the face is inverted, i.e., left eye is to the right of the right eye, then rotate the mem glasses by
    # an additional 180 deg.
    if box[0][0] > box[1][0]:
        foreground = foreground.rotate(angle + 180)
    else:
        foreground = foreground.rotate(angle)

    # resize the prop_image as a function of the distance between the corners of the eyes
    size = math.ceil(math.dist(box[1], box[0]))
    size = int(size + 0.7 * size)
    lengthpercent = foreground.size[0] / size
    foreground = foreground.resize((size, int(foreground.size[1] / lengthpercent)))

    # finally paste the prop_image onto the face
    # specify the exact coordinates where you the prop_image to be pasted/ In this case, we want the centre point of
    # the prop_image to align with the midpoint between the eyes
    background.paste(foreground, (int(box[2][0] - (foreground.size[0] / 2)), int(box[2][1] - (foreground.size[1] / 2))),
                     foreground)
    background.show()
    background.save(output_file)


# [END]

# [START vision_face_detection_tutorial_run_application]
def main(input_filename, output_filename, max_results):
    # with open(input_filename, 'rb') as image:
    faces = detect_face(input_filename, max_results)
    print('Found {} face{}'.format(
        len(faces), '' if len(faces) == 1 else 's'))
    print('Writing to file {}'.format(output_filename))
    # Reset the file pointer, so we can read the file again
    # image.seek(0)

    # get the eyes' landmarks
    response = requests.get(input_filename)
    image = Image.open(BytesIO(response.content))
    box = highlight_eyes(image, faces, output_filename)

    # overlay the meme glasses image onto the face
    with open("resources\meme_glasses.png", 'rb') as image2:
        add_prop(output_filename, image2, output_filename, box)


# [END vision_face_detection_tutorial_run_application]


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Detects faces in the given image.')
    parser.add_argument(
        'input_image', help='the image you\'d like to detect faces in.')
    parser.add_argument(
        '--out', dest='output', default='out.jpg',
        help='the name of the output file.')
    parser.add_argument(
        '--max-results', dest='max_results', default=4,
        help='the max results of face detection.')
    args = parser.parse_args()

    main(args.input_image, args.output, args.max_results)
