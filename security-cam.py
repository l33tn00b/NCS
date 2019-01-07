#!/usr/bin/python3

# ****************************************************************************
# Copyright(c) 2017 Intel Corporation. 
# License: MIT See LICENSE file in root directory.
# ****************************************************************************

# Modifications by l33tn00b

# Detect objects on a LIVE camera feed using
# Intel® Movidius™ Neural Compute Stick (NCS)

import os
import cv2
import sys
import numpy
import ntpath
import argparse

import mvnc.mvncapi as mvnc

from time import localtime, strftime
from utils import visualize_output
from utils import deserialize_output

# "Class of interest" - Display detections only if they match this class ID
CLASS_PERSON         = 15

# Detection threshold: Minimum confidance to tag as valid detection
# now being set by command line argument
#CONFIDANCE_THRESHOLD = 0.60 # 60% confidant

# Variable to store commandline arguments
ARGS                 = None

# ---- Step 1: Open the enumerated device and get a handle to it -------------

def open_ncs_device():

    # Look for enumerated NCS device(s); quit program if none found.
    devices = mvnc.EnumerateDevices()
    if len( devices ) == 0:
        print( "No NCS devices found" )
        sys.exit(3)

    # Get a handle to the first enumerated device and open it
    device = mvnc.Device( devices[0] )
    device.OpenDevice()

    return device

# ---- Step 2: Load a graph file onto the NCS device -------------------------

def load_graph( device ):

    # Read the graph file into a buffer
    with open( ARGS.graph, mode='rb' ) as f:
        blob = f.read()

    # Load the graph buffer into the NCS
    graph = device.AllocateGraph( blob )

    return graph

# ---- Step 3: Pre-process the images ----------------------------------------

def pre_process_image( frame ):

    # Resize image [Image size is defined by choosen network, during training]
    img = cv2.resize( frame, tuple( ARGS.dim ) )

    # Convert RGB to BGR [OpenCV reads image in BGR, some networks may need RGB]
    if( ARGS.colormode == "rgb" ):
        img = img[:, :, ::-1]

    # Mean subtraction & scaling [A common technique used to center the data]
    img = img.astype( numpy.float16 )
    img = ( img - numpy.float16( ARGS.mean ) ) * ARGS.scale

    return img

# ---- Step 4: Read & print inference results from the NCS -------------------

def infer_image( graph, img, frame ):

    # Load the image as a half-precision floating point array
    graph.LoadTensor( img, 'user object' )

    # Get the results from NCS
    output, userobj = graph.GetResult()

    # Get execution time
    inference_time = graph.GetGraphOption( mvnc.GraphOption.TIME_TAKEN )

    # Deserialize the output into a python dictionary
    output_dict = deserialize_output.ssd( 
                      output, 
                      confidence_threshold, 
                      frame.shape )

    # Print the results (each image/frame may have multiple objects)
    exitcode = 0
    for i in range( 0, output_dict['num_detections'] ):
        print( output_dict.get( 'detection_classes_' + str(i) ))
        # Filter a specific class/category
        if( output_dict.get( 'detection_classes_' + str(i) ) == CLASS_PERSON ):

            cur_time = strftime( "%Y_%m_%d_%H_%M_%S", localtime() )
            print( "Person detected on " + cur_time )

            # Extract top-left & bottom-right coordinates of detected objects 
            (y1, x1) = output_dict.get('detection_boxes_' + str(i))[0]
            (y2, x2) = output_dict.get('detection_boxes_' + str(i))[1]

            # Prep string to overlay on the image
            display_str = ( 
                labels[output_dict.get('detection_classes_' + str(i))]
                + ": "
                + str( output_dict.get('detection_scores_' + str(i) ) )
                + "%" )

            # Overlay bounding boxes, detection class and scores
            frame = visualize_output.draw_bounding_box( 
                        y1, x1, y2, x2, 
                        frame,
                        thickness=4,
                        color=(255, 255, 0),
                        display_str=display_str )

            # Capture snapshots
            #photo = ( os.path.dirname(os.path.realpath(__file__))
            # check if our tmp dir exists (it might have been deleted 
            # by os because we're in /var/tmp (which is on purpose)
            # letting this run too long will fill up the user's home pretty fast
            # it doesn't do any harm if older annotations get deleted but
            # we still have some older annotations if we need to look at them.
            if not (os.path.isdir("/var/tmp/captures")):
                 # create directory
                 os.makedirs("/var/tmp/captures")
            photopath = ("/var/tmp/captures/"
                      +os.path.split(ARGS.image)[1])
                      #+ cur_time + ".jpg" )
            cv2.imwrite( photopath, frame )
            # also write output to fixed destination for fhem handling 
            cv2.imwrite("/var/tmp/detection.jpg", frame)
            exitcode = 2
        else:
            exitcode = 0
    return exitcode

# ---- Step 5: Unload the graph and close the device -------------------------

def close_ncs_device( device, graph ):
    graph.DeallocateGraph()
    device.CloseDevice()

# ---- Main function (entry point for this script ) --------------------------

def main():
    # first thing to do: check if image file exists
    # initializing NCS takes a while,  we may as well skip it
    # if there is notihing to do.
    #print(ARGS.image)
    image_path = os.path.join(os.getcwd(), ARGS.image)
    #print(image_path)
    if os.path.exists(image_path):
        # open NCS device
        device = open_ncs_device()
        # load graph (ssd mobilenet)
        graph = load_graph( device )
        # load image
        frame = cv2.imread(ARGS.image)
        # do preprocessing / scaling
        img = pre_process_image( frame )
        # and finally send the image to the NCS for computation
        result = infer_image( graph, img, frame )
        # release NCS device
        close_ncs_device( device, graph )
        sys.exit(result)
    else:
        # Print error message and  quit
        print("Image not found.")
        sys.exit(1)


# ---- Define 'main' function as the entry point for this script -------------

if __name__ == '__main__':

    parser = argparse.ArgumentParser(
                         description="DIY smart security camera PoC using \
                         Intel® Movidius™ Neural Compute Stick." )

    parser.add_argument( '-g', '--graph', type=str,
                         default='../../caffe/SSD_MobileNet/graph',
                         help="Absolute path to the neural network graph file." )

    parser.add_argument( '-v', '--video', type=int,
                         default=0,
                         help="Index of your computer's V4L2 video device. \
                               ex. 0 for /dev/video0" )

    parser.add_argument( '-l', '--labels', type=str,
                         default='../../caffe/SSD_MobileNet/labels.txt',
                         help="Absolute path to labels file." )

    parser.add_argument( '-M', '--mean', type=float,
                         nargs='+',
                         default=[127.5, 127.5, 127.5],
                         help="',' delimited floating point values for image mean." )

    parser.add_argument( '-S', '--scale', type=float,
                         default=0.00789,
                         help="Factor (float) for image scaling." )

    parser.add_argument( '-D', '--dim', type=int,
                         nargs='+',
                         default=[300, 300],
                         help="Image dimensions. ex. -D 224 224" )

    parser.add_argument( '-c', '--colormode', type=str,
                         default="bgr",
                         help="RGB vs BGR color sequence. This is network dependent." )

    parser.add_argument( '-i', '--image', type=str,
                         default="",
                         help="Image to be processed. File name will be appended to current working directory. Avoid any additional slashes at the beginning." )

    parser.add_argument( '-t', '--threshold', type=int,
                         default=60,
                         help="Confidence threshold for detection in percent. Default is 60.")



    ARGS = parser.parse_args()

    # NCS expects threshold as float, so do conversion
    confidence_threshold = ARGS.threshold / 100
    if confidence_threshold != 0.6:
             print("Confidence threshold modified to "+str(ARGS.threshold)+".")

    # Load the labels file
    labels =[ line.rstrip('\n') for line in
              open( ARGS.labels ) if line != 'classes\n']

    main()

# ==== End of file ===========================================================
