# NCS
Movidius Neural Compute Stick Stuff

In case you've been wondering (like me) how e.g. Netatmo does all that clever processing stuff in their cameras (Welcome, Presence): Wonder no more.

I recently learned of the Intel Movidius Neural Compute Stick. It is a neat USB device that you plug into your Raspberry Pi (or another supported device, see https://software.intel.com/en-us/movidius-ncs). 

Basically, it contains a specialized chip for performing neural net computations.

You may take pre-trained models (e.g. Tensorflow models like MobileNet) and convert them for usage with the Neural Compute Stick.

Machine vision on a Raspberry Pi has never been easier.

Since I run a couple of security cameras I always wanted these to be as "smart" as the Netatmo devices. I previously thought about sending videos and images to Microsoft's Azure Cloud for classification. Luckily I never completed the project. I now do it at home.

There are some sites/articles that got me started:

https://www.bouvet.no/bouvet-deler/adding-ai-to-edge-devices-with-the-movidius-neural-compute-stick

https://movidius.github.io/ncsdk/install.html (official documentation for the SDK)

https://movidius.github.io/blog/ncs-apps-on-rpi/ (Step-by-step installation on Raspberry Pi)

Don't be suprised if you encounter some obstacles. These steps pretty much apply to "clean" systems. I had to manually add packages and resolve conflicts during installation. Google is your friend...

And yes, if you have the Windows Subsystem for Linux installed: The SDK works. I have Ubuntu running in there. Setup takes a while and finally fails wwhen trying to set up udev rules. But since I don't run the NCS on my Windows machine there is no problem with that.

The original NCS SDK is located in /opt/movidius/NCSDK/ncsdk-x86_64/tk/.

To make our life easier, Intel decided to discard the original NCS API (but only after having had an incompatible version 2 of it) and transition to something called openVINO. Guess what, NCS and openVINO models are incompatible. Migration was to be found at https://software.intel.com/en-us/articles/neural-compute-stick-ncsdk-to-openvino. But no longer. Now, it can be found at https://software.intel.com/en-us/articles/transitioning-from-intel-movidius-neural-compute-sdk-to-openvino-toolkit. Haha. 

Models I tried:

https://github.com/chuanqi305/MobileNet-SSD
https://github.com/opencv/open_model_zoo/tree/2018/intel_models (openVINO models (.bin + .xml))
https://github.com/intel/Edge-optimized-models

For downloading models from the Open Model Zoo at openCV one has to use the model downloader to be found at:
https://github.com/opencv/open_model_zoo/blob/2018/model_downloader/README.md



Regarding https://github.com/opencv/open_model_zoo/blob/2018/intel_models/pedestrian-detection-adas-0002/description/pedestrian-detection-adas-0002.md:
It expects images with a dimension of 384x672. This translates to an original size of 768 x 1344.
