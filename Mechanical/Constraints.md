# Microscope Physical Constraints

## Build Volume:
The 'front plane' of these measurements will be the vertical plane of the front of the legs. The 'Center plane' of these measurements is the middle of these two legs.

### Center Volume:
Depth: 120 mm  
Width (between legs): 75mm  
Height (to the lens): 175mm  

### Over-legs volume
Bottom: 40mm up  
Depth: 130mm (from legs to mounting pins)  

End of Legs to Lens in Depth: 70mm

### With Pre-existing stage:
Max height: 37.4mm

Platform Height: 128.6mm
Platform Depth: 134mm
Platform Width: 114mm

Depth from front of platform to lens: 52.25mm centered

Light Hole: 26.73mm diameter, centered under the lens

#### Mounting Pin Holes:  
- 2 x 2.98mm diameter holes, 91.5mm from front of platform, 27.3mm from either edge, 59.18mm between centers  
- 1 x threaded hole, 109mm from front, centered. Thread OD 3.5mm, 0.61mm thread pitch, ID not measured (calipers' blades not sharp enough). Appears to be standard M3.5x0.6 metric threads.  
- 2 x 2mm diameter holes, 40.7mm from sides, 29mm from back, 32.5mm between centers  


## Criteria:
### Vertical Resolution
Existing fine adjustment is 2mm/(8.5 turns) on an 18mm-diameter knob. It feels comfortable to rotate the knob so that the surface of the knob travels 0.5mm.  
At 0.2353mm/turn of lens travel, and 56.549mm/turn of knob travel, we get a 240.33:1 ratio of knob surface travel to lens travel.  
If it's comfortable to turn the knob 0.5mm, then in order to compete with manual resulution (not a required, but a desirable, goal), our vertical control system needs to be able to move to 0.0021mm resolution - 2 micron - accounting for any slop in the rest of the system. This has the potential to pose a challenge.  
Similarly, our vertical movement resolution is also our vertical observation resolution. Animal cells are in the order of 10-30 micron, and plant cells range from 10-100 micron, so a 2-5 micron resolution vertically would be an effective goal.


One available candidate for vertical movement is a CD/DVD laser head assembly. One example has a 8-step stepper motor driving a threaded rod - one step maps to 0.1235mm. Not a good candidate for sub-cellular imaging. Another has a DC motor and gear system - 0.27mm/turn, which is a pretty poor showing as well.

Additionally, the lenses I have for the microscope are 4x, 10x, 40x, and 100x, with working distances of approximately 16, 6.1, 0.65, and 0.18mm. With a 0.1235mm vertical resolution, I could take ~5 planes at 40x and ~50 planes at 10x, giving a steep but potentially usable trade-off between magnification and vertical steps.

It seems like the systems I have for vertical resolution are barely - but acceptably - suited for the tasks at hand. However, I'll start where I am and build a horizontal translation stage for the moment, and design plans for a very-fine-grained vertical control system later.

### Vertical Range
This largely depends on the actual subjects being examined. In truth, the customer (my curiosity) imagines I'll be depth-stacking images of objects less than 1cm thick, perhaps significantly less, due to the difficulty of imaging objects of that thickness. However, I may be imaging the surfaces of objects significantly more than 1cm tall, perhaps as much as 4 or 5cm; however, this can be set manually on the microscope and left static through the duration of the imaging process.

### Translation Resolution

I previously found that the values stamped on the objective lenses are not accurate field numbers. I own some optical encoder tape and some high precision calipers, so I'll use that to find my own values for FOV directly. Note these are along the wide view of the camera, fully crossing the width - these would be shrunk some in order to have a fully inscribed rectangle.

| Magnification | FOV |
|---|---|
| 100x | 0.168mm |
| 40x | 0.42mm |
| 10x | 1.68mm |
| 4x | 4.2mm |

The approximated travel resolution for the CD drivers - 0.2mm - sits in the ballpark of the 100x magnification FOV, especially given how rough those estimates are.

### Translation Range

Our goal is to take tens to hundreds of FOVs across an entire sample. At a maximum 4.2mm FOV, a 10 FOV image set at 4x would be 42mm of travel. The CD driver only supports up to 40mm of travel, just under the 10 FOV target. Additionally, other drivers around 300mm are available, though at sizes and constructions that made them unfit for consideration as vertical drivers. They will be considered in more detail after simple prototypes are completed.  

At a minimum 0.168mm FOV, 100 FOVs would require 16.8mm of travel; this is possible on the CD drivers, though the larger drivers might likely struggle to manage the 0.16mm travel. Again, this will be investigated more at a later date.

### Third axis?

It would be lovely to have a second horizontal motion axis, to take images of wide flat objects. It would be pretty reasonable to modify the vision, especially so early in the process; however, there's a huge amount that can be learned with a more simple prototype, so a 2-axis table will stay off the vision for now.

## Image Capture

Eyepiece Column Bore: 23.22mm

Camera Hardware: EF mounting Canon Rebel T3

I happen to already know that the Rebel T3 has computer-controlled capture functionality; otherwise the decision of what mounting hardware to purchase would also involve the software constraints.

General research has found that there is an intermediate standard for microscope mounting hardware - M42x1mm threads. Generally, this means an eyepiece-to-M42 column and an M42-to-camera plate are purchased.

The performance of this camera is good in general; a proper investigation into the aperture, dynamic range, resolution, sensor size, and other metrics would be appropriate were new camera hardware expected to be purchased. However, that will not be done at this time, primarily because this is the best camera available to me, and secondarily because the microscope has an inbuilt light source and control scheme which I trust can be flexible enough to ensure the camera is capable of tuning to the settings needed.

## Timing
The travel speed and capture frequency of the system is largely unknown, along with any reasonable target speeds. Generally, CD drivers can move very quickly while under zero load; this may not be the case while carrying potentially a microscope slide and sample. 
The vision ought to be improved with some more specific target speeds. However, any particular speed listed would be the outcome of pure guesswork. So, I'll pick some physical phenomenon and use that as an order-of-magnitude estimate. 

One experiment demonstrating the flow of dye through the stem and flower of a Carnation; the lower average length of a carnation stem is ~500mm (the experiment lists shorter as better), and the experiment suggests the dye reaches the flower after around 24 hours. This pace is incredibly slow, a little under 6 micron per second, but it does suggest that (with a horizontal travel maxing out around 300mm) that these capture sessions could last 15 hours or more.

A preliminary test I can perform at home is the rate of capillary spread of water over tissue paper - around 1.5 mm/second. The motor drivers should be able to handle this easily. 
As for the camera, at the highest magnification (meaning an image every 0.168mm), this requires an image be taken every 0.112 seconds. A quick test finds that the camera, through the most common configuration of the most common interface, takes a little over 3 seconds between images. That's fairly poor performance for our needs, as it limits our highest-magnification travel speed to 0.056mm/s. I'll complete this calculation for each magnification.

| Magnification | FOV | 3s/img travel speed |
|---|---|---|
| 100x | 0.168mm | 0.056 mm/s |
| 40x | 0.42mm | 0.14 mm/s |
| 10x | 1.68mm | 0.56 mm/s |
| 4x | 4.2mm | 1.4 mm/s |


This suggests the tissue paper could barely be 'filmed' at 4x. However, it should be noted that I also briefly attempted the same capillary experiment with a sponge and discarded it because it was much slower than I expected, so a material designed to absorb water quickly, given a continuous source of water to draw from, may be an unusually rapid benchmark.

This also suggests that I should find or make available a camera with significantly higher continuous capture speeds. I'll also note that a brief Google search suggests the battery of the camera I'm putting to use can be used for *normal* continuous use for around 2 hours, so a picture every 3 seconds (or more often) may limit the run time of experiments significantly. It's seeming more and more likely that, eventually, a totally new image capture solution will be needed.
