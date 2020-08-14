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

### With Pre-existing stage:
Max height: 37.4mm

Platform Height: 128.6mm
Platform Depth: 134mm
Platform Width: 114mm

Depth from front of platform to lens: 52.25mm

Light Hole: 26.73mm diameter

Mounting Pin Holes:
2 x 2.98mm diameter holes, 91.5mm from front of platform, 27.3mm from either edge, 59.18mm centers
1 x threaded hole, 109mm from front, centered. Thread OD 3.5mm, 0.61mm thread pitch, ID can't be measured
2 x 2mm diameter holes, 40.7mm fron sides, 29mm from back, 32.5mm centers

### Datums
End of Legs to Lens in Depth: 70mm


## Criteria:
### Vertical Resolution
Existing fine adjustment is 2mm/(8.5 turns) on an 18mm-diameter knob. It feels comfortable to rotate the knob so that the surface of the knob travels 0.5mm.  
At 0.2353mm/turn of lens travel, and 56.549mm/turn of knob travel, we get a 240.33:1 ratio of knob surface travel to lens travel.  
If it's comfortable to turn the knob 0.5mm, then in order to compete with manual resulution (not a required, but a desirable, goal), our vertical control system needs to be able to move to 0.0021mm resolution - 2 micron - accounting for any slop in the rest of the system. This has the potential to pose a challenge.  
Similarly, our vertical movement resolution is also our vertical observation resolution. Animal cells are in the order of 10-30 micron, and plant cells range from 10-100 micron, so a 2-5 micron resolution vertically would be an effective goal.


One available candidate for vertical movement is a CD/DVD laser head assembly. One example has a 8-step stepper motor driving a threaded rod - one step maps to 0.2mm. Not a good candidate for sub-cellular imaging. Another has a DC motor and gear system - 0.27mm/turn, which is a pretty poor showing as well.

Additionally, the lenses I have for the microscope are 4x, 10x, 40x, and 100x, with working distances of approximately 30, 6.1, 0.65, and 0.18mm. With a 0.2mm vertical resolution, I could take 3 planes at 40x and 30 planes at 10x, giving a steep trade-off between magnification and vertical steps.

It seems like the systems I have for vertical resolution are poorly suited to the precision needed in this task. However, I'll start where I am and build a horizontal translation stage for the moment, and design plans for a very-fine-grained vertical control system later.



### Translation Resolution

The 100x objective has a field number of 1.25, meaning the FOV is 0.0125mm. That's less than my fine adjustment with existing hardware, so I'll investigate the rest of the lenses.

| Magnification | Field Number | FOV |
|---|---|---|
| 100x | 1.25 | 0.0125mm |
| 40x | 0.65 | 0.01625mm |
| 10x | 0.25 | 0.025mm |
| 4x | 0.15 | 0.0375mm |

That doesn't make any sense. It's possible the field numbers are incorrect or misunderstood, but it's not possible to get 25x relative magnification and 1/3 the FOV. I own some optical encoder tape, so I'll use that to find my own values for FOV directly.

- [ ] Correct FOV Checkpoint


## Image Capture
Column Bore: 23.22mm
