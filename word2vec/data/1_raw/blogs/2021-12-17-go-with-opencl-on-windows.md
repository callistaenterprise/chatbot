---
categories: blogg teknik
layout: "details-blog"
published: true
heading: OpenCL with Go on Windows 10
authors: 
  - eriklupander
tags: "go golang opencl windows nvidia cl cgo_cflags cgo_ldflags"
topstory: true
comments: true
---
This is a prelude to an upcoming blog post about Path Tracing with Go and OpenCL, which can be seen as a spiritual sequel to my 2020 ramblings on [go ray-tracer optimization](https://callistaenterprise.se/blogg/teknik/2020/07/04/a-go-ray-tracer/).

If you want some tidbits on Golang, OpenCL and CGO on Windows 10 - read on!

-[readmore]-

# 1. Introduction
I typically use OS X in my software development endeavours. However, while developing a new piece of hobbyist software with Go and OpenCL, I found myself in need of running the application on Microsoft Windows 10.

OpenCL with Golang is based on using some wrapper around the core C library, which requires CGO. I've been using [jgillich/go-opencl](https://github.com/jgillich/go-opencl), which seems to be a now abandoned fork of [samuel/go-opencl](https://github.com/samuel/go-opencl). Seems there are a few more recently updated forks, but for my purposes it works alright.

On both Macs I tried this with - one with an Nvidida GPU and one with an AMD GPU - compiling with OpenCL support through CGO has worked out of the box. Windows, on the other hand, turned out to be much trickier. Therefore, I wrote this little blog post if someone else stumbles into the same wall I did. 

# 2. Example program
The objective of this blog post is NOT to teach OpenCL, so I'll keep the sample program as simple as possible, split into two files:

* main.go
* kernel.cl

The full source can be found here: [https://github.com/eriklupander/go-opencl-example](https://github.com/eriklupander/go-opencl-example)

### 2.1 main.go
OpenCL requires quite a bit of boilerplate to read and set up platforms, devices, command queues, memory buffers etc.

Feel free to browse over the ~100 LoC required for a "Hello world" OpenCL program with Go. The actual point where the OpenCL code in `kernel.cl` execute is when `queue.EnqueueNDRangeKernel` is called, which invokes the .cl kernel with the enqueued buffers. 
```go
package main

import (
	_ "embed"
	"fmt"
	"github.com/jgillich/go-opencl/cl"
	"unsafe"
)

//go:embed kernel.cl
var kernelSource string

func main() {

	// 1. Set up some input to pass into the OpenCL kernel
	input := make([]int64, 0)
	for i := 0; i < 16; i++ {
		input = append(input, int64(i))
	}
	// size in bytes for each input element. 8, in this case but doing it dynamically looks cooler.
	inputElemSize := int(unsafe.Sizeof(input[0]))

	// 2. Get hold of OpenCL platform and device
	platforms, err := cl.GetPlatforms()
	check("Failed to get platforms", err)

	devices, err := platforms[0].GetDevices(cl.DeviceTypeAll)
	check("Failed to get devices", err)
	if len(devices) == 0 {
		panic("GetDevices returned 0 devices")
	}
	fmt.Println("Using: " + devices[0].Name())
	
	// 3. Select a device to use. On my mac: 0 == CPU, 1 == Iris GPU, 2 == GeForce 750M GPU
	context, err := cl.CreateContext([]*cl.Device{devices[0]})
	check("CreateContext failed", err)

	// 4. Create a "Command Queue" bound to the first device
	queue, err := context.CreateCommandQueue(devices[0], 0)
	check("CreateCommandQueue failed", err)

	// 5. Create an OpenCL "program" from the source code.
	program, err := context.CreateProgramWithSource([]string{kernelSource})
	check("CreateProgramWithSource failed", err)

	// 5.1 Build the OpenCL program, i.e. compile it.
	err = program.BuildProgram(nil, "")
	check("BuildProgram failed", err)

	// 5.2 Create the actual Kernel with a name, the Kernel is the "function"
	//     we call when we want to execute something.
	kernel, err := program.CreateKernel("square")
	check("CreateKernel failed", err)

	// 6.1 Create OpenCL buffers (memory) for the input. Note that we're allocating 8 bytes per input element, each int64 is 8 bytes in length.
	inputBuffer, err := context.CreateEmptyBuffer(cl.MemReadOnly, inputElemSize*len(input))
	check("CreateBuffer failed for vectors input", err)
	defer inputBuffer.Release()

	// 6.2 Create OpenCL buffer (memory) for the output data, which in our case is identical in length to the input.
	outputBuffer, err := context.CreateEmptyBuffer(cl.MemReadOnly, inputElemSize*len(input))
	check("CreateBuffer failed for output", err)
	defer outputBuffer.Release()

	// 6.3 Connect our input to the command queue and upload the data into device (GPU/CPU) memory. The inputDataPtr is
	// a pointer to the first element of the input slice, while inputDataTotalSizeBytes is the total length of the input data, in bytes
	inputDataPtr := unsafe.Pointer(&input[0])
	inputDataTotalSizeBytes := inputElemSize * len(input)
	_, err = queue.EnqueueWriteBuffer(inputBuffer, true, 0, inputDataTotalSizeBytes, inputDataPtr, nil)
	check("EnqueueWriteBuffer failed", err)

	// 6.4 Kernel is our program and here we explicitly bind our 4 parameters to it
	err = kernel.SetArgs(inputBuffer, outputBuffer)
	check("SetKernelArgs failed", err)

	// 7. Finally, start work! Enqueue executes the loaded args on the specified kernel.
	_, err = queue.EnqueueNDRangeKernel(kernel, nil, []int{len(input)}, []int{16}, nil)
	check("EnqueueNDRangeKernel failed", err)

	// 8. Finish() blocks the main goroutine until the OpenCL queue is empty, i.e. all calculations are done
	err = queue.Finish()
	check("Finish failed", err)

	// 9. Allocate go-side storage for loading the output from the OpenCL program
	results := make([]int64, len(input))

	// 10. EnqueueReadBuffer copies the data in the OpenCL "output" buffer into the "results" slice.
	dataPtrOut := unsafe.Pointer(&results[0])
	sizePerEntry := int(unsafe.Sizeof(results[0]))
	dataSizeOut := sizePerEntry * len(results)

	_, err = queue.EnqueueReadBuffer(outputBuffer, true, 0, dataSizeOut, dataPtrOut, nil)
	check("EnqueueReadBuffer failed", err)

	// 11. We're done! Just dump the results to stdout
	fmt.Printf("%+v\n", results)
}

func check(msg string, err error) {
	if err != nil {
		panic(msg + ": " + err.Error())
	}
}
```

### 2.2 kernel.cl

The kernel (i.e. OpenCL function that can do stuff in parallel) is very simple. It takes the current index `i` being processed from the built-in `get_global_id(0)` function and squares `input[i]`, storing the result in `output[i]`:
```c
__kernel void square(__global long *input, __global long *output) {
    int i = get_global_id(0);
    output[i] = input[i]*input[i];
}
```

# 3. Setting up our build env on Windows
First off - I'm running Microsoft Windows 10 on an AMD Ryzen 2600X with an Nvidia RTX2080 graphics card. This guide does not deal with AMD graphics cards, but I guess installing the OpenCL headers and drivers should be similar to how it's done for Nvidia.

### 3.1 Download the drivers and headers
It seems as the standard Nvidia driver software does not include the necessary OpenCL .h files nor the nvopencl.dll. To obtain these, one needs to download and install the [Nvidida CUDA](https://developer.nvidia.com/cuda-downloads) software suite, which includes the OpenCL resources we need.

After installation, you should find the CUDA installation under `C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v11.5\`.

Take note of this folder, we'll need it shortly.

### 3.2 Download and install GCC
We'll need GCC with 64-bit support in order to build our Go program. When writing this, downloading and installing [TDM64-GCC-10.3.0](https://jmeubank.github.io/tdm-gcc/download/) seems to be perhaps the easiest way to obtain a GCC capable environment that works well with CGO.

### 3.3 Download and install Go
Perhaps this step is superfluous for Gophers reading this blog post. Nevertheless - head over to the official [downloads page](https://go.dev/dl/) and fetch the Windows installer. This blog post was written with Go 1.17.5. 

# 4. Building
Open a command shell (`cmd`) and head over to a suitable directory where you'll clone the example app source later, such as `c:\projects`.

We need to do three things:
1. Enable CGO
2. Let the Go toolchain know where it can find the OpenCL header (.h) files.
3. let the Go toolchain know where it can find the Nvidia OpenCL driver .dll.

### 4.1 Enable CGO
This is the easiest part:
```shell
set CGO_ENABLED=1
```

### 4.2 Set CGO_CFLAGS
We'll use the slightly magical `CGO_CFLAGS` environment variable to tell the Go toolchain where to find the OpenCL header files. They are located inside the CUDA installation we downloaded and installed earlier. 

It was quite tricky to locate the actual documentation for that `-I` flag we use when passing a file system path, but intense use of a well-known online search engine came up with [the GCC Directory-Options](https://gcc.gnu.org/onlinedocs/gcc/Directory-Options.html#Directory-Options) which tells us that `-I` is used to specify a directory to search for C includes.

However, we're not quite done yet, since the Windows cmd prompt with GCC can't handle the spaces in `C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v11.5\`. After a lot of frustration with futile attempts to quote the full path or parts of the path, as well as trying various methods to escape the whitespace, it turned out we have to use those [8.3 files names](https://en.wikipedia.org/wiki/8.3_filename) such as `C:\PROGRA~1\` we havn't really seen since the 90:s...

In order to figure out the 8.3 equivalent of `C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v11.5\include` which contains the `CL/opencl.h` header, we'll have to use a little "DOS-script" or whatever it's called.

Enter the `include` directory of the CUDA installation and then run the `for` statement from the example below:

```shell
$ cd C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v11.5\include
$ for %I in (.) do @echo %~sI
C:\PROGRA~1\NVIDIA~2\CUDA\v11.5\include
```

Then set the `CGO_CFLAGS` environment variable with the 8.3 representation.
```shell
set CGO_CFLAGS=-I C:\PROGRA~1\NVIDIA~2\CUDA\v11.5\include
```

### 4.3 Set CGO_LDFLAGS
Following the same pattern as above, we need to tell Go where it can find library files for OpenCL. However, here we'll use the `-L` flag instead. The same 8.3 trick is needed here, but for the `lib/x64` folder inside the CUDA installation:
```shell
$ cd C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v11.5\lib\x64
$ for %I in (.) do @echo %~sI
C:\PROGRA~1\NVIDIA~2\CUDA\v11.5\lib\x64
```
Set the environment variable:
```shell
set CGO_LDFLAGS=-L C:\PROGRA~1\NVIDIA~2\CUDA\v11.5\lib\x64
```

Observant readers may notice that these env vars differs slightly from how they're used on Linux and/or OS X, the space between `-I C:\...` and `-L C:\...` as well as no wrapping `"`:s. Took me a while to get these right, which is the primary reason for taking the time to write this blog post.

### 4.4 Clone and build the application
Let's take our env vars for a spin. In the **same** cmd windows you set those env vars, clone the example app:

```shell
git clone https://github.com/eriklupander/go-opencl-example.git
cd go-opencl-example
```
With the ENV vars set properly, we should be able to build using normal `go build`:
```shell
go build main.go
```
If you get any errors, you probably didn't get the path(s) in the CGO_CFLAGS or CGO_LDFLAGS quite right, or you missed some step. Or you're running Windows 8/11 which may work differently... 

# 5. Running
If the build step above worked, there should be a `main.exe` file in the folder of your cmd window. 

As a little reminder, the example program is very very silly:

It passes a slice of 16 `int64`, `[0,1,2,3 ... 15]` to a OpenCL kernel named `square` which - surprisingly enough - **squares** - each `int64` (`long` in OpenCL) passed in each index with itself, and stores the result in the corresponding result index. 

```c
__kernel void square(__global long *input, __global long *output) {
    int i = get_global_id(0);
    output[i] = input[i]*input[i];
}
```
Let's run it!

```shell
main.exe
Using: Intel(R) Core(TM) i7-4870HQ CPU @ 2.50GHz
[0 1 4 9 16 25 36 49 64 81 100 121 144 169 196 225]
```
As you can see, the output buffer consists of 16 integers, where each one is the square of its corresponding input 0-15 values.

# 6. Final words
This simple guide hopefully can help someone that struggles to locate OpenCL headers/drivers or having problems setting those mysterious CGO_CFLAGS/CGO_LDFLAGS env vars correctly.

In a follow-up to this blog post, I'll get to the reason for me writing this - my very own little Golang/OpenCL based path tracer!

Until next time,

// Erik Lupander
