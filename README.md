# TDX-SelfBalancingBot

This repo contains the extra helper files so Toradex partners can have access to the client and server mockups and the Dockerfiles

## Introduction 

Hi! Well, unfortunately, the robot needs more than a good old firmware to work. But don't worry, this `/extras` folder is here to help you set up the firmware to run alongside the applications on Linux.

## Torizon OS 6.6.0 image customization

We had a problem! We chose to share data between the A and M cores using shared memory (visit: [Cortex-M Shared Memory Guide](https://developer.toradex.com/software/cortex-m/cortex-m-shared-memory-guide)). However, the pre-built Torizon OS with Docker Containers has a kernel configuration enabled ([`CONFIG_STRICT_DEVMEM`](https://www.man7.org/linux/man-pages/man4/mem.4.html)) that prevents you from reading and writing data on the `/dev/mem`. To overcome this hurdle, follow these steps:

1. Follow the instructions on [Build Torizon OS from Source With Yocto Project/OpenEmbedded](https://developer.toradex.com/torizon/in-depth/build-torizoncore-from-source-with-yocto-projectopenembedded/) and set up your oe-core build environment for Torizon.

2. Bitbake the menuconfig and change disable the `CONFIG_STRICT_DEVMEM`.

```
$ bitbake -c menuconfig virtual/kernel
```

3. Bitbake the `torizon-core-docker` image:

```
$ bitbake torizon-core-docker
```

4. Or if you are lazy or do not have time, just use the `torizon-core-docker-verdin-imx8mp-Tezi_6.6.0-devel-20240326143502+build.0.tar` that is in this folder.

## Devicetree Overlay

Toradex already offer an overlay that allows you to use the Remoteproc and RPMsg, but because we are roots and reationary people, we want go another way and use the shared memory approach. No, it's not because of that.
RPMsg using the NXP SDK needs to be used with FreeRTOS tasks, and our code, the way it was designed, it's not prepared for that. So the shared memory is the way to go!

We modified a bit the `verdin-imx8mp_hmp_overlay.dts` file to reserve a portion of the memory on the Linux side so we can access from the Cortex M7 side.

```
m7_shm: cm7@40000000 {
	reg = <0x40000000 0x10000000>;
	no-map;
};
```

You can follow the steps in the [Build Device Tree Overlays from Source Code](https://developer.toradex.com/linux-bsp/os-development/build-u-boot-and-linux-kernel-from-source-code/build-device-tree-overlays-from-source-code) to compile your binary or, if you are lazy and do not have time to worry about this, just use the compiled binary (`verdin-imx8mp_hmp_overlay.dtbo`) in this directory.

Don't forget to update the `overlays.txt` file once you boot your OS:

```
$ sudo echo "fdt_overlays=verdin-imx8mp_hmp_overlay.dtbo" > overlays.txt
$ sync
$ sudo reboot now
```

## U-boot changes to load and run the firmware

1. Copy the compiled `robot_fw.bin` and `robot_fw.elf` binaries to your Torizon OS `/var`.

2. Stop the boot process and access the U-boot terminal. 

2. Follow the steps below (visit: [How to Load Compiled Binaries into Cortex-M](https://developer.toradex.com/software/cortex-m/how-to-load-binaries#verdinimx8mm/verdinimx8mm))

```
# setenv load_cmd "ext4load mmc 2:1"
# setenv m7image "/ostree/deploy/torizon/var/hello_world.bin"
# setenv m7image_size 20000
# setenv loadm7image "${load_cmd} ${loadaddr} ${m7image}"
# setenv m7boot "${loadm7image}; cp.b ${loadaddr} 0x7e0000 ${m7image_size}; dcache flush; bootaux 0x7e0000"
# saveenv
# run m7boot
# setenv bootcmd "run m7boot; ${bootcmd}"
# saveenv
# reset
```

## Container

We came up with a container to run the Linux application to exchange data between the cores. 

### Docker build

The `Dockerfile` is in this directory and you can copy it to you Torizon OS and build it as:

```
# scp Dockerfile torizon@<ip-adress>:/home/torizon
# docker build -t selfbalancingbot .
```

Or...

```
# docker pull gabs28/selfbalancingbot:latest
```

Yes, it's in my Docker hub and you can use it.

### Docker run

- If you build it on your device:

```
# docker run --privileged --cap-add=SYS_RAWIO -it -v /dev:/dev --device /dev/mem --rm --name selfbalancingbot selfbalancingbot
```

- If you want to use the prebuilt container

```
# docker run --privileged --cap-add=SYS_RAWIO -it -v /dev:/dev --device /dev/mem --rm --name selfbalancingbot gabs28/selfbalancingbot
```

## Configuring the Access Point Mode (optional)

Follow the instruction on the Toradex developer article: [Wi-Fi Access Point Mode](https://developer.toradex.com/torizon/application-development/use-cases/networking-connectivity/networking-with-torizoncore/#method-2-hostapd)

1. Copy the `hostapd.conf` file in this directory to `/etc/hostapd.conf` on your device

2. Copy the `hostapd.service` file in this directory to `/etc/systemd/system/hostapd.service`

3. Enable and start the service:

```
# sudo systemctl enable hostapd
# sudo systemctl start hostapd
```
