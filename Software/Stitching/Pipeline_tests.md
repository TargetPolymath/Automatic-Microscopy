OpenCL CPU:
real	3m46.764s
user	6m47.671s
sys	0m36.648s

OpenCL GPU:
real	5m15.720s
user	3m22.254s
sys	1m12.964s

CUDA GPU:
real	3m44.102s
user	2m13.699s
sys	1m1.008s

numpy CPU:
real	2m41.654s
user	8m23.436s
sys	1m40.861s


======================================================
Misc Tests:

## OpenCL CPU BS=4
real	3m25.918s
user	10m36.625s
sys	1m17.891s

## OpenCL CPU BS=1024
real	3m51.631s
user	15m37.090s
sys	1m28.876s


## OpenCL CPU BS=512
real	3m20.300s
user	11m24.889s
sys	1m17.344s

^^^
   ncalls  tottime  percall  cumtime  percall filename:lineno(function)
    38975   26.912    0.001   26.912    0.001 {method 'encode' of 'ImagingEncoder' objects}
    65086   25.399    0.000   25.399    0.000 {built-in method occa.c.base.memcpy}
    74425   25.177    0.000   25.177    0.000 {method 'decode' of 'ImagingDecoder' objects}
      136   15.831    0.116   15.831    0.116 {method 'resize' of 'ImagingCore' objects}
   134126   14.527    0.000   14.527    0.000 {built-in method numpy.zeros}
   122954   12.806    0.000   15.095    0.000 {built-in method numpy.core._multiarray_umath.implement_array_function}
      170   10.525    0.062   10.525    0.062 {method 'build_kernel_from_string' of 'occa.c.Device' objects}

---
# Rev 1.1
Fully removed constructing the 'actual' image - only running the error evaluation.
Copied numpy zeros from premade templates.
## OpenCL CPU BS=512
real	2m41.254s
user	10m45.927s
sys	1m18.063s

^^^
   ncalls  tottime  percall  cumtime  percall filename:lineno(function)
    64888   27.249    0.000   27.249    0.000 {built-in method occa.c.base.memcpy}
    48781   17.092    0.000   17.092    0.000 {method 'decode' of 'ImagingDecoder' objects}
      136   15.781    0.116   15.781    0.116 {method 'resize' of 'ImagingCore' objects}
    64948   12.778    0.000   12.778    0.000 {method 'copy' of 'numpy.ndarray' objects}
   122581   10.620    0.000   13.045    0.000 {built-in method numpy.core._multiarray_umath.implement_array_function}
      170    8.618    0.051    8.618    0.051 {method 'build_kernel_from_string' of 'occa.c.Device' objects}
      510    7.879    0.015    7.879    0.015 {method 'astype' of 'numpy.ndarray' objects}
...
    68831    4.763    0.000    4.763    0.000 {built-in method numpy.zeros}

1. NP Zeros approach reduced runtime by 20%. Keeping.
1. Image Decode still takes up ~70% of it's original time
1. Image Resize had no change
1. Image Encode disappeared (~0% time)

# Rev 1.2
O.
Cache image loads between stacks - very high memory usage?
A.
1. Can't cache OCCA mem objects between stacks without a persistant Device (an option)

#### Pre-fill cache of images in Host Memory

## OpenCL CPU BS=512
real	2m54.323s
user	12m52.302s
sys	1m36.944s

^^^
   ncalls  tottime  percall  cumtime  percall filename:lineno(function)
    73006   32.829    0.000   32.829    0.000 {built-in method occa.c.base.memcpy}
   150406   18.938    0.000   18.938    0.000 {built-in method numpy.zeros}
      136   16.086    0.118   16.086    0.118 {method 'resize' of 'ImagingCore' objects}
   137920   13.825    0.000   16.353    0.000 {built-in method numpy.core._multiarray_umath.implement_array_function}
      510    9.533    0.019    9.533    0.019 {method 'astype' of 'numpy.ndarray' objects}
    25644    9.002    0.000    9.002    0.000 {method 'decode' of 'ImagingDecoder' objects}
      170    8.656    0.051    8.656    0.051 {method 'build_kernel_from_string' of 'occa.c.Device' objects}

That's... weird. memcpy shouldn't need to go up 20%. Image.decode went down to 53% of what it was, which is excellent, but with the weird memcpy behavior, I'm worried this isn't a repeatable test. Let's run it again.

## OpenCL CPU BS=512
real	2m46.269s
user	11m42.118s
sys	1m31.171s

   ncalls  tottime  percall  cumtime  percall filename:lineno(function)
    68812   32.777    0.000   32.777    0.000 {built-in method occa.c.base.memcpy}
      136   15.862    0.117   15.862    0.117 {method 'resize' of 'ImagingCore' objects}
   141785   15.715    0.000   15.715    0.000 {built-in method numpy.zeros}
   129995   12.886    0.000   15.492    0.000 {built-in method numpy.core._multiarray_umath.implement_array_function}
      510    9.876    0.019    9.876    0.019 {method 'astype' of 'numpy.ndarray' objects}
    25644    8.930    0.000    8.930    0.000 {method 'decode' of 'ImagingDecoder' objects}
      170    8.703    0.051    8.703    0.051 {method 'build_kernel_from_string' of 'occa.c.Device' objects}

Hmm. That's quite a bit of variation for a largely deterministic program - though there are other processes happening on the server (backups, other uitilities, etc). I could do more short tests for better statistical power, or I could look for big changes. I'm still in the early days for optimization, so I'm willing to bet a significant change will show up appropriately.

# Rev 1.3
MemCopy is taking the largest fraction of our time. Can we cut it down, or multithread around it?

* It should be happening in one of a few places:
  1. \_retrieve\_img
  1. \_new\_OCCA\_mems
  1. \_error\_occa , in calling the kernel or copying back
Let's look at cumulative time for those functions

			       \[S\]
   ncalls  tottime  percall  cumtime  percall filename:lineno(function)
    68812    0.202    0.000   46.192    0.001 /[...]/Auto_Snap.py:92(_retrieve_img)
      170    0.066    0.000   13.768    0.081 /[...]/Auto_Snap.py:162(_new_OCCA_mems)
    34406    3.374    0.000   78.093    0.002 /[...]/Auto_Snap.py:383(_error_occa)

Unsurprisingly, \_error\_occa has the largest cumtime of the three, but new\_occa\_mems has the largest percall cumtime. I'll modify the control flow so that the copy-back behavior is isolated.

    38951    2.454    0.000   86.207    0.002 /[...]/Auto_Snap.py:388(_error_occa)
    38951    0.219    0.000   56.253    0.001 /[...]/Auto_Snap.py:382(_copy_back)

So our total run time and \_error\_occa runtime took longer, but 65% of \_error\_occa is spent waiting for memory to copy back - or is it? As I type this, I realize it'd be pretty obvious that the async execution would appear to halt for memory executions. Let's test.

_Side Note: Calling self.device.finish() during execution limits our abilities to have multiple threads submitting kernels to the device - only waiting on memcpy outcomes could possibly allow the device 'sync up' the relevant kernels and leave the rest to run, while calling finish() would likely force the entire device to sync. That's a question worth more investigation later._

    32462    0.097    0.000   21.113    0.001 /[...]/Auto_Snap.py:382(_device_finish)
    32462    0.184    0.000   26.775    0.001 /[...]/Auto_Snap.py:385(_copy_back)
    32462    2.424    0.000   75.487    0.002 /[...]/Auto_Snap.py:391(_error_occa)

So between \_device\_finish and \_copy\_back we're still seeing ~65% of our \_error\_occa time, but we understand that about half of that time is actually the execution time on the device. In other words, around 12% of our total runtime is spent waiting for the device to complete, and another 16% is waiting for results to copy back to the host. These feel like somewhat small fractions of the total runtime - let's verify by moving back to the time-wide scope.

real	2m46.267s
user	10m59.199s
sys	1m39.823s
			       \[S\]
   ncalls  tottime  percall  cumtime  percall filename:lineno(function)
    64941   21.205    0.000   21.205    0.000 {method 'finish' of 'occa.c.Device' objects}
    64984   16.840    0.000   16.840    0.000 {method 'copy' of 'numpy.ndarray' objects}
      136   15.980    0.117   15.980    0.117 {method 'resize' of 'ImagingCore' objects}
   122647   12.131    0.000   15.768    0.000 {built-in method numpy.core._multiarray_umath.implement_array_function}
      510    9.161    0.018    9.161    0.018 {method 'astype' of 'numpy.ndarray' objects}
    25644    9.118    0.000    9.118    0.000 {method 'decode' of 'ImagingDecoder' objects}
      170    8.573    0.050    8.573    0.050 {method 'build_kernel_from_string' of 'occa.c.Device' objects}
    64924    8.535    0.000    8.535    0.000 {built-in method occa.c.base.memcpy}
        1    8.413    8.413  153.521  153.521 /mnt/Shelves/LiveProjects/Automatic_Microscopy/Automatic-Microscopy/Software/Stitching/Post_Processing.py:43(align)
      510    6.544    0.013    6.544    0.013 {method 'malloc' of 'occa.c.Device' objects}

Interestingly, by calling out 'finish' specifically, we get a much much better view of our execution timing. On-device execution is the largest fraction of our execution time, followed by on-host memory allocation, Image resizing, and numpy array math. In fact, the first grouping we see that isn't directly attached to execution is the align function, which contains operations on the error masks of each image - operations which could certainly be parallelized, though with a peak benefit of taking 7% off the run time.  
The only stand-out opportunities for improvement would be avoiding the Image class as much as possible and writing a resize kernel on the device; doing further digging into the np.copy vs np.zeros choice; and/or optimizing the existing kernel. I'm largely here to learn about high-performance kernel design, so I'll start there with trying to determine the best device and block size.

## CUDA GPU BS=4
real	2m51.365s
user	1m56.687s
sys	1m2.185s

			       \[S\]
   ncalls  tottime  percall  cumtime  percall filename:lineno(function)
      136   15.756    0.116   15.756    0.116 {method 'resize' of 'ImagingCore' objects}
       17   14.290    0.841   14.291    0.841 /home/[...]/python3.6/site-packages/occa/device.py:10(__init__)
        1   13.384   13.384  138.224  138.224 /[...]/Post_Processing.py:43(align)
   122001   13.062    0.000   16.071    0.000 {built-in method numpy.core._multiarray_umath.implement_array_function}
    64582   12.677    0.000   12.677    0.000 {built-in method occa.c.base.memcpy}
    64642   12.537    0.000   12.537    0.000 {method 'copy' of 'numpy.ndarray' objects}
    25644    8.983    0.000    8.983    0.000 {method 'decode' of 'ImagingDecoder' objects}
      510    6.296    0.012    6.296    0.012 {method 'astype' of 'numpy.ndarray' objects}
      170    3.956    0.023    3.956    0.023 {method 'build_kernel_from_string' of 'occa.c.Device' objects}
    68508    3.933    0.000    3.933    0.000 {built-in method numpy.zeros}
...
    32291    0.117    0.000   31.404    0.001 /[...]/Auto_Snap.py:385(_copy_back)
...
    32291    0.036    0.000    3.134    0.000 /[...]/Auto_Snap.py:382(_device_finish)


Despite a slower overall execution, this spent less time waiting for the device to finish and less time waiting for the device to copy its information back. However - _lots_ of time was spent initializing devices, around 8% of total run time. Interestingly, np.copy() took a little less time - clearly something is happening that I don't explicitely understand.




