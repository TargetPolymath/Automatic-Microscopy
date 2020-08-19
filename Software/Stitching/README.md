# Goals

- [ ] Low computational power needed
- [ ] Ease of use (to some extent)
- [ ] Effective at performing stitching operations

# Inputs

1. Folder full of timestamp-ordered .png images, where each image in the sequence *must* overlap in some way with the proceeding image
1. Some user input to reduce computational load

# Plan

- [ ] Display the first and second image (A and B)
- [ ] Gather user input to get the general transform from A to B
- [ ] Use some method to 'snap' to close solutions
- [ ] User confirms a 'snap' is good, or confirms their manual movement is good
- [ ] Extrapolate transform through image series, asking for confirm/deny

- Deny Options:
	- [ ] The extrapolation is wrong for a single image
	- [ ] A new extrapolation needs to occur and continue
	- [ ] There is another 'starting' image