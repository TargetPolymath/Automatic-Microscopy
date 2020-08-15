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


One available candidate for vertical movement is a CD/DVD laser head assembly. One example has a 8-step stepper motor driving a threaded rod - one step maps to 0.2mm. Not a good candidate for sub-cellular imaging. Another has a DC motor and gear system - 0.27mm/turn, which is a pretty poor showing as well.

Additionally, the lenses I have for the microscope are 4x, 10x, 40x, and 100x, with working distances of approximately 16, 6.1, 0.65, and 0.18mm. With a 0.2mm vertical resolution, I could take 3 planes at 40x and 30 planes at 10x, giving a steep trade-off between magnification and vertical steps.

It seems like the systems I have for vertical resolution are poorly suited to the precision needed in this task. However, I'll start where I am and build a horizontal translation stage for the moment, and design plans for a very-fine-grained vertical control system later.

### Vertical Range
This largely depends on the actual subjects being examined. In truth, the customer (my curiosity) imagines I'll be depth-stacking images of objects less than 1cm thick, perhaps significantly less, due to the difficulty of imaging objects of that thickness. However, I may be imaging the surfaces of objects significantly more than 1cm tall, perhaps as much as 4 or 5cm; however, this can be set manually on the microscope and left static through the duration of the imaging process.

### Translation Resolution

The 100x objective has a field number of 1.25, meaning the FOV is 0.0125mm. That's less than my fine adjustment with existing hardware, so I'll investigate the rest of the lenses.

| Magnification | Field Number | FOV |
|---|---|---|
| 100x | 1.25 | 0.0125mm |
| 40x | 0.65 | 0.01625mm |
| 10x | 0.25 | 0.025mm |
| 4x | 0.15 | 0.0375mm |

That doesn't make any sense. It's possible the field numbers are incorrect or misunderstood, but it's not possible to get 25x relative magnification and 1/3 the FOV. I own some optical encoder tape and some high precision calipers, so I'll use that to find my own values for FOV directly.

The camera itself will be using an effective 1x eyepiece, but I only own as low as a 5x eyepiece, so these are recorded values for a 5x eyepiece and a conversion to the expected camera FOV.

| Magnification | FOV 5x | FOV Expected |
|---|---|---|
| 100x | 0.19(2)mm | 0.96mm |
| 40x | 0.5mm | 2.5mm |
| 10x | 1.92mm | 9.6mm |
| 4x | 5mm | 25mm |

These are *much* more in line with the behaviors I would expect. 

The camera has a rectangular field which may be inscribed in the FOV, circumscribing the FOV, or something else. However, these FOV values give me order of magnitude estimates for lateral positioning resolution.

Given a series of coliniar circular FOV images with some distance between their centers kr (k times the radius), we can imagine a stripe running along the whole line where every point on that stripe is inside some FOV, or more than one. If we want that stripe to take up some fraction V of the total 'height' of the circles (the diameter, perpendicular to the coliliar centers), we find that k = sqrt(1 - V^2); so, if we wanted to use 80% of the height (just a reasonable example, not a special figure), we would move 0.6 diameters (or FOVs) between images. This tells us we would need a lateral movement resolution as low as around 0.6mm ($(100x FOV) * 0.6 FOVs ~= 0.6mm). This is definitely managable with the CD drivers.

I'll expand these calculations out for each magnification:


| Magnification | FOV Expected | Travel mm per field @ 80% |
|---|---|---|
| 100x | 0.96mm | 0.576mm |
| 40x | 2.5mm | 1.5mm |
| 10x | 9.6mm | 5.76mm |
| 4x | 25mm | 15mm |


### Translation Range

Our goal is to take tens to hundreds of FOVs across an entire sample. At a maximum 25mm FOV, a 10 FOV image set at 4x would be 250mm of travel. The CD driver only supports up to 40mm of travel, just under 2 FOV; however, other drivers around 300mm are available, though at sizes and constructions that made them unfit for consideration as vertical drivers. They will be considered in more detail after simple prototypes are completed.  

At a minimum 0.96mm FOV, 100 FOVs would require 96mm of travel; this also isn't possible on the CD drivers, and the larger drivers might likely struggle to manage the 0.6mm travel. Again, this will be investigated more at a later date.

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
As for the camera, at the highest magnification and 80% height coverage (meaning an image every 0.6mm), this requires an image be taken every 0.4 seconds. A quick test finds that the camera, through the most common configuration of the most common interface, takes a little over 3 seconds between images. That's fairly poor performance for our needs, as it limits our highest-magnification travel speed to 0.2mm/s. I'll complete this calculation for each magnification.

| Magnification | FOV Expected | Travel mm per field @ 80% | 3s / img max travel speed @ 80% |
|---|---|---|---|
| 100x | 0.96mm | 0.576mm | 0.192mm/s |
| 40x | 2.5mm | 1.5mm | 0.5mm/s |
| 10x | 9.6mm | 5.76mm | 1.92mm/s |
| 4x | 25mm | 15mm | 5mm/s |

This suggests the tissue paper could be 'filmed' at 10x. However, it should be noted that I also briefly attempted the same capillary experiment with a sponge and discarded it because it was much slower than I expected, so a material designed to absorb water quickly, given a continuous source of water to draw from, may be an unusually rapid benchmark.

This also suggests that I should find or make available a camera with significantly higher continuous capture speeds. I'll also note that a brief Google search suggests the camera I'm putting to use can be used for *normal* continuous use for around 2 hours, so a picture every 3 seconds (or more often) may limit the run time of experiments significantly. It's seeming more and more likely that, eventually, a totally new image capture solution will be needed.
