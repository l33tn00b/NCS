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
