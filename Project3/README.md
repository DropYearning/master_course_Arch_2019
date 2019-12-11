

# project3

## 说明
使用 Xilinx Nexys 4 ddr 开发版， 选择适当的SoC 实现，并在此基础上移植一个任意操作系统。需要提供完整的技术方案，包括 RTL 实现、操作系统源码及实现的完整技术方案。

## 教程

- [Installing Vivado 2018.3 on Ubuntu 18.04 for the PYNQ-Z1 board](https://gist.github.com/sgherbst/f73c31938d3483e6c72e3baf3443f66a)
- [Build your own RISC-V architecture on FPGA – ModernHackers.com](http://modernhackers.com/build-your-own-risc-v-architecture-on-fpga/)
- [Architectures/RISC-V/FPGA - Fedora Project Wiki](https://fedoraproject.org/wiki/Architectures/RISC-V/FPGA)

## 步骤记录
1. 串口输出

   - `screen /dev/ttyUSB1 115200`
   - `microcom -s 115200 /dev/ttyUSB1`
   - `sudo picocom -b 115200 /dev/ttyUSB1`

2. `sudo fdisk -l`

   ```
   [sudo] mastlab-zl 的密码： 
   Disk /dev/loop0：54.5 MiB，57151488 字节，111624 个扇区
   单元：扇区 / 1 * 512 = 512 字节
   扇区大小(逻辑/物理)：512 字节 / 512 字节
   I/O 大小(最小/最佳)：512 字节 / 512 字节
   
   
   Disk /dev/loop1：956 KiB，978944 字节，1912 个扇区
   单元：扇区 / 1 * 512 = 512 字节
   扇区大小(逻辑/物理)：512 字节 / 512 字节
   I/O 大小(最小/最佳)：512 字节 / 512 字节
   
   
   Disk /dev/loop2：54.6 MiB，57274368 字节，111864 个扇区
   单元：扇区 / 1 * 512 = 512 字节
   扇区大小(逻辑/物理)：512 字节 / 512 字节
   I/O 大小(最小/最佳)：512 字节 / 512 字节
   
   
   Disk /dev/loop3：44.2 MiB，46325760 字节，90480 个扇区
   单元：扇区 / 1 * 512 = 512 字节
   扇区大小(逻辑/物理)：512 字节 / 512 字节
   I/O 大小(最小/最佳)：512 字节 / 512 字节
   
   
   Disk /dev/loop4：67 MiB，70262784 字节，137232 个扇区
   单元：扇区 / 1 * 512 = 512 字节
   扇区大小(逻辑/物理)：512 字节 / 512 字节
   I/O 大小(最小/最佳)：512 字节 / 512 字节
   
   
   Disk /dev/loop5：42.8 MiB，44879872 字节，87656 个扇区
   单元：扇区 / 1 * 512 = 512 字节
   扇区大小(逻辑/物理)：512 字节 / 512 字节
   I/O 大小(最小/最佳)：512 字节 / 512 字节
   
   
   Disk /dev/loop6：14.8 MiB，15458304 字节，30192 个扇区
   单元：扇区 / 1 * 512 = 512 字节
   扇区大小(逻辑/物理)：512 字节 / 512 字节
   I/O 大小(最小/最佳)：512 字节 / 512 字节
   
   
   Disk /dev/loop7：4.2 MiB，4403200 字节，8600 个扇区
   单元：扇区 / 1 * 512 = 512 字节
   扇区大小(逻辑/物理)：512 字节 / 512 字节
   I/O 大小(最小/最佳)：512 字节 / 512 字节
   
   
   Disk /dev/nvme0n1：477 GiB，512110190592 字节，1000215216 个扇区
   单元：扇区 / 1 * 512 = 512 字节
   扇区大小(逻辑/物理)：512 字节 / 512 字节
   I/O 大小(最小/最佳)：512 字节 / 512 字节
   磁盘标签类型：gpt
   磁盘标识符：C3D574C4-F1CC-45CD-B5E4-D2CF5575C363
   
   设备                起点       末尾      扇区   大小 类型
   /dev/nvme0n1p1      2048     534527    532480   260M EFI 系统
   /dev/nvme0n1p2    534528     567295     32768    16M Microsoft 保留
   /dev/nvme0n1p3    567296  159082495 158515200  75.6G Microsoft 基本数据
   /dev/nvme0n1p4 159082496  255942966  96860471  46.2G Microsoft 基本数据
   /dev/nvme0n1p5 998166528 1000214527   2048000  1000M Windows 恢复环境
   /dev/nvme0n1p6 255944704  998166527 742221824 353.9G Linux 文件系统
   
   分区表记录没有按磁盘顺序。
   
   
   Disk /dev/loop8：14.8 MiB，15462400 字节，30200 个扇区
   单元：扇区 / 1 * 512 = 512 字节
   扇区大小(逻辑/物理)：512 字节 / 512 字节
   I/O 大小(最小/最佳)：512 字节 / 512 字节
   
   
   Disk /dev/loop9：3.7 MiB，3821568 字节，7464 个扇区
   单元：扇区 / 1 * 512 = 512 字节
   扇区大小(逻辑/物理)：512 字节 / 512 字节
   I/O 大小(最小/最佳)：512 字节 / 512 字节
   
   
   Disk /dev/loop10：1008 KiB，1032192 字节，2016 个扇区
   单元：扇区 / 1 * 512 = 512 字节
   扇区大小(逻辑/物理)：512 字节 / 512 字节
   I/O 大小(最小/最佳)：512 字节 / 512 字节
   
   
   Disk /dev/loop11：156.7 MiB，164290560 字节，320880 个扇区
   单元：扇区 / 1 * 512 = 512 字节
   扇区大小(逻辑/物理)：512 字节 / 512 字节
   I/O 大小(最小/最佳)：512 字节 / 512 字节
   
   
   Disk /dev/loop12：3.7 MiB，3825664 字节，7472 个扇区
   单元：扇区 / 1 * 512 = 512 字节
   扇区大小(逻辑/物理)：512 字节 / 512 字节
   I/O 大小(最小/最佳)：512 字节 / 512 字节
   
   
   Disk /dev/loop13：89.1 MiB，93429760 字节，182480 个扇区
   单元：扇区 / 1 * 512 = 512 字节
   扇区大小(逻辑/物理)：512 字节 / 512 字节
   I/O 大小(最小/最佳)：512 字节 / 512 字节
   
   
   Disk /dev/loop14：4 MiB，4218880 字节，8240 个扇区
   单元：扇区 / 1 * 512 = 512 字节
   扇区大小(逻辑/物理)：512 字节 / 512 字节
   I/O 大小(最小/最佳)：512 字节 / 512 字节
   
   
   Disk /dev/loop15：149.9 MiB，157184000 字节，307000 个扇区
   单元：扇区 / 1 * 512 = 512 字节
   扇区大小(逻辑/物理)：512 字节 / 512 字节
   I/O 大小(最小/最佳)：512 字节 / 512 字节
   
   
   Disk /dev/loop16：89.1 MiB，93429760 字节，182480 个扇区
   单元：扇区 / 1 * 512 = 512 字节
   扇区大小(逻辑/物理)：512 字节 / 512 字节
   I/O 大小(最小/最佳)：512 字节 / 512 字节
   
   
   Disk /dev/loop17：499 MiB，523288576 字节，1022048 个扇区
   单元：扇区 / 1 * 512 = 512 字节
   扇区大小(逻辑/物理)：512 字节 / 512 字节
   I/O 大小(最小/最佳)：512 字节 / 512 字节
   
   
   Disk /dev/sda：29.5 GiB，31633440768 字节，61784064 个扇区
   单元：扇区 / 1 * 512 = 512 字节
   扇区大小(逻辑/物理)：512 字节 / 512 字节
   I/O 大小(最小/最佳)：512 字节 / 512 字节
   磁盘标签类型：dos
   磁盘标识符：0xe01c0f72
   
   设备       启动  起点     末尾     扇区  大小 Id 类型
   /dev/sda1        2048 61784063 61782016 29.5G  c W95 FAT32 (LBA)
   
   ```

 2. `make USB=sda cleandisk partition`

   ```
   rm -f cardmem.log
   Checking /dev/sda
   for i in `lsblk -P -o NAME,MOUNTPOINT | grep sda | grep 'MOUNTPOINT="/' | cut -d\" -f4`; do umount $i; done
   Checking /dev/sda
   lsblk -P -o NAME|grep sda | grep [1-9] && sudo partx -d /dev/sda
   NAME="sda1"
   sudo sh cardmem.sh /dev/sda
   cardmem.sh: 1: cardmem.sh: source: not found
   请检查现在是不是有人在使用此磁盘... 好的
   
   Disk /dev/sda：29.5 GiB，31633440768 字节，61784064 个扇区
   单元：扇区 / 1 * 512 = 512 字节
   扇区大小(逻辑/物理)：512 字节 / 512 字节
   I/O 大小(最小/最佳)：512 字节 / 512 字节
   磁盘标签类型：dos
   磁盘标识符：0xe01c0f72
   
   旧状况：
   
   设备       启动  起点     末尾     扇区  大小 Id 类型
   /dev/sda1        2048 61784063 61782016 29.5G  c W95 FAT32 (LBA)
   
   >>> 已接受脚本标头(header)。
   >>> 已接受脚本标头(header)。
   >>> 已接受脚本标头(header)。
   >>> 创建了一个磁盘标识符为 0xdeadbeef 的新 DOS 磁盘标签。
   /dev/sda1: 创建了一个新分区 1，类型为“W95 FAT32 (LBA)”，大小为 32 MiB。
   分区 #1 包含一个 vfat 签名。
   /dev/sda2: 创建了一个新分区 2，类型为“Linux”，大小为 2 GiB。
   /dev/sda3: 创建了一个新分区 3，类型为“Linux swap / Solaris”，大小为 512 MiB。
   /dev/sda4: 创建了一个新分区 4，类型为“Linux”，大小为 512 MiB。
   所有分区均已使用。
   
   新状况：
   磁盘标签类型：dos
   磁盘标识符：0xdeadbeef
   
   设备       启动    起点    末尾    扇区  大小 Id 类型
   /dev/sda1  *       2048   67582   65535   32M  c W95 FAT32 (LBA)
   /dev/sda2         67584 4261887 4194304    2G 83 Linux
   /dev/sda3       4261888 5310463 1048576  512M 82 Linux swap / Solaris
   /dev/sda4       5310464 6359039 1048576  512M 83 Linux
   
   分区表已调整。
   将调用 ioctl() 来重新读分区表。
   正在同步磁盘。
   请检查现在是不是有人在使用此磁盘... 好的
   
   Disk /dev/sda：29.5 GiB，31633440768 字节，61784064 个扇区
   单元：扇区 / 1 * 512 = 512 字节
   扇区大小(逻辑/物理)：512 字节 / 512 字节
   I/O 大小(最小/最佳)：512 字节 / 512 字节
   磁盘标签类型：dos
   磁盘标识符：0xdeadbeef
   
   旧状况：
   
   设备       启动    起点    末尾    扇区  大小 Id 类型
   /dev/sda1  *       2048   67582   65535   32M  c W95 FAT32 (LBA)
   /dev/sda2         67584 4261887 4194304    2G 83 Linux
   /dev/sda3       4261888 5310463 1048576  512M 82 Linux swap / Solaris
   /dev/sda4       5310464 6359039 1048576  512M 83 Linux
   
   /dev/sda4: 
   新状况：
   磁盘标签类型：dos
   磁盘标识符：0xdeadbeef
   
   设备       启动    起点     末尾     扇区  大小 Id 类型
   /dev/sda1  *       2048    67582    65535   32M  c W95 FAT32 (LBA)
   /dev/sda2         67584  4261887  4194304    2G 83 Linux
   /dev/sda3       4261888  5310463  1048576  512M 82 Linux swap / Solaris
   /dev/sda4       5310464 61784063 56473600   27G 83 Linux
   
   分区表已调整。
   将调用 ioctl() 来重新读分区表。
   正在同步磁盘。
   sleep 2
   lsblk -P -o NAME,PARTUUID | grep sda | grep sda | tail -4 > cardmem.log
   ```

3. `make USB=sda mkfs fatdisk extdisk`

   ```
   sudo mkfs -t msdos /dev/sda1
   mkfs.fat 4.1 (2017-01-24)
   sudo mkfs -t ext4 /dev/sda2
   mke2fs 1.44.1 (24-Mar-2018)
   创建含有 524288 个块（每块 4k）和 131072 个inode的文件系统
   文件系统UUID：39b9ff13-4a38-41bb-b1e5-8be6cb8a7ccb
   超级块的备份存储于下列块： 
   	32768, 98304, 163840, 229376, 294912
   
   正在分配组表： 完成                            
   正在写入inode表： 完成                            
   创建日志（16384 个块） 完成
   写入超级块和文件系统账户统计信息： 已完成
   
   sudo mkswap /dev/sda3
   正在设置交换空间版本 1，大小 = 512 MiB (536866816  个字节)
   无标签， UUID=917734ae-cedb-40a0-a954-bd850761a584
   sudo mkfs -t ext4 /dev/sda4
   mke2fs 1.44.1 (24-Mar-2018)
   创建含有 7059200 个块（每块 4k）和 1766016 个inode的文件系统
   文件系统UUID：77dd25d2-4665-4081-99e8-3e5fe549efa2
   超级块的备份存储于下列块： 
   	32768, 98304, 163840, 229376, 294912, 819200, 884736, 1605632, 2654208, 
   	4096000
   
   正在分配组表： 完成                            
   正在写入inode表： 完成                            
   创建日志（32768 个块） 完成
   写入超级块和文件系统账户统计信息： 已完成 
   
   sudo mkdir -p /mnt/sda1
   sudo mount /dev/sda1 /mnt/sda1
   sudo cp boot.bin /mnt/sda1
   sudo umount /mnt/sda1
   sudo mkdir -p /mnt/sda2
   sudo mount -t ext4 /dev/sda2 /mnt/sda2
   sudo tar xJf rootfs.tar.xz -C /mnt/sda2
   sudo mkdir -p /mnt/sda2/mnt/dos
   sudo cp fstab.riscv /mnt/sda2/etc/fstab
   sudo sed s=@=mastlab-zl= < firstboot.riscv | sudo tee /mnt/sda2/etc/profile.d/firstboot.sh
   echo 'This is the firstboot script. It will display only once'
   echo 'Set the superuser (root) password below'
   passwd root
   echo 'Creating normal user mastlab-zl ...'
   adduser mastlab-zl
   usermod -a -G sudo mastlab-zl
   exec rm /etc/profile.d/firstboot.sh
   sudo umount /mnt/sda2
   ```

4. `make program-cfgmem`

      ```
      git clone -b refresh-v0.6 https://github.com/lowrisc/lowrisc-fpga.git
      正克隆到 'lowrisc-fpga'...
      remote: Enumerating objects: 3, done.
      remote: Counting objects: 100% (3/3), done.
      remote: Compressing objects: 100% (2/2), done.
      remote: Total 4202 (delta 0), reused 2 (delta 0), pack-reused 4199
      接收对象中: 100% (4202/4202), 3.34 MiB | 118.00 KiB/s, 完成.
      处理 delta 中: 100% (1530/1530), 完成.
      make -C lowrisc-fpga/common/script
      make[1]: 进入目录“/home/mastlab-zl/Git/lowrisc-quickstart-modernhackers.com/lowrisc-fpga/common/script”
      cc -g   -c -o recvRawEth.o recvRawEth.c
      cc -g   -c -o hash-md5.o hash-md5.c
      cc recvRawEth.o hash-md5.o -o recvRawEth -g
      make[1]: 离开目录“/home/mastlab-zl/Git/lowrisc-quickstart-modernhackers.com/lowrisc-fpga/common/script”
      touch lowrisc-fpga/STAMP.fpga
      vivado -mode batch -source lowrisc-fpga/common/script/cfgmem.tcl -tclargs "xc7a100t_0" chip_top.bit
      
      ****** Vivado v2018.3 (64-bit)
        **** SW Build 2405991 on Thu Dec  6 23:36:41 MST 2018
        **** IP Build 2404404 on Fri Dec  7 01:43:56 MST 2018
          ** Copyright 1986-2018 Xilinx, Inc. All Rights Reserved.
      
      source lowrisc-fpga/common/script/cfgmem.tcl
      # set bit [lindex $argv 1]
      # set device [lindex $argv 0]
      # puts "BITSTREAM: $bit"
      BITSTREAM: chip_top.bit
      # puts "DEVICE: $device"
      DEVICE: xc7a100t_0
      # write_cfgmem -force -format mcs -interface spix4 -size 128 -loadbit "up 0x0 $bit" -file "$bit.mcs"
      Command: write_cfgmem -force -format mcs -interface spix4 -size 128 -loadbit {up 0x0 chip_top.bit} -file chip_top.bit.mcs
      Creating config memory files...
      Creating bitstream load up from address 0x00000000
      Loading bitfile chip_top.bit
      Writing file ./chip_top.bit.mcs
      Writing log file ./chip_top.bit.prm
      ===================================
      Configuration Memory information
      ===================================
      File Format        MCS
      Interface          SPIX4
      Size               128M
      Start Address      0x00000000
      End Address        0x07FFFFFF
      
      Addr1         Addr2         Date                    File(s)
      0x00000000    0x003A607B    Dec  7 10:18:18 2019    chip_top.bit
      0 Infos, 0 Warnings, 0 Critical Warnings and 0 Errors encountered.
      write_cfgmem completed successfully
      INFO: [Common 17-206] Exiting Vivado at Sat Dec  7 11:45:34 2019...
      vivado -mode batch -source lowrisc-fpga/common/script/program_cfgmem.tcl -tclargs "xc7a100t_0" chip_top.bit.mcs
      
      ****** Vivado v2018.3 (64-bit)
        **** SW Build 2405991 on Thu Dec  6 23:36:41 MST 2018
        **** IP Build 2404404 on Fri Dec  7 01:43:56 MST 2018
          ** Copyright 1986-2018 Xilinx, Inc. All Rights Reserved.
      
      source lowrisc-fpga/common/script/program_cfgmem.tcl
      # set mcs [lindex $argv 1]
      # set device [lindex $argv 0]
      # puts "CFGMEM: $mcs"
      CFGMEM: chip_top.bit.mcs
      # puts "DEVICE: $device"
      DEVICE: xc7a100t_0
      # open_hw
      # connect_hw_server
      INFO: [Labtools 27-2285] Connecting to hw_server url TCP:localhost:3121
      INFO: [Labtools 27-2222] Launching hw_server...
      INFO: [Labtools 27-2221] Launch Output:
      
      ****** Xilinx hw_server v2018.3
        **** Build date : Dec  6 2018-23:53:53
          ** Copyright 1986-2018 Xilinx, Inc. All Rights Reserved.
      
      
      # open_hw_target
      INFO: [Labtoolstcl 44-466] Opening hw_target localhost:3121/xilinx_tcf/Digilent/210292A6EAB4A
      # current_hw_device [lindex [get_hw_devices] 0]
      # refresh_hw_device -update_hw_probes false [lindex [get_hw_devices] 0]
      INFO: [Labtools 27-1435] Device xc7a100t (JTAG device index = 0) is not programmed (DONE status = 0).
      # create_hw_cfgmem -hw_device [lindex [get_hw_devices] 0] -mem_dev  [lindex [get_cfgmem_parts {s25fl128sxxxxxx0-spi-x1_x2_x4}] 0]
      # set_property PROGRAM.BLANK_CHECK  0 [ get_property PROGRAM.HW_CFGMEM [lindex [get_hw_devices] 0 ]]
      # set_property PROGRAM.ERASE  1 [ get_property PROGRAM.HW_CFGMEM [lindex [get_hw_devices] 0 ]]
      # set_property PROGRAM.CFG_PROGRAM  1 [ get_property PROGRAM.HW_CFGMEM [lindex [get_hw_devices] 0 ]]
      # set_property PROGRAM.VERIFY  1 [ get_property PROGRAM.HW_CFGMEM [lindex [get_hw_devices] 0 ]]
      # set_property PROGRAM.CHECKSUM  0 [ get_property PROGRAM.HW_CFGMEM [lindex [get_hw_devices] 0 ]]
      # refresh_hw_device [lindex [get_hw_devices] 0]
      INFO: [Labtools 27-1435] Device xc7a100t (JTAG device index = 0) is not programmed (DONE status = 0).
      # set_property PROGRAM.ADDRESS_RANGE  {use_file} [ get_property PROGRAM.HW_CFGMEM [lindex [get_hw_devices] 0 ]]
      # set_property PROGRAM.FILES [list $mcs] [ get_property PROGRAM.HW_CFGMEM [lindex [get_hw_devices] 0]]
      # set_property PROGRAM.UNUSED_PIN_TERMINATION {pull-none} [ get_property PROGRAM.HW_CFGMEM [lindex [get_hw_devices] 0 ]]
      # startgroup 
      # if {![string equal [get_property PROGRAM.HW_CFGMEM_TYPE  [lindex [get_hw_devices] 0]] [get_property MEM_TYPE [get_property CFGMEM_PART [get_property PROGRAM.HW_CFGMEM [lindex [get_hw_devices] 0 ]]]]] }  { create_hw_bitstream -hw_device [lindex [get_hw_devices] 0] [get_property PROGRAM.HW_CFGMEM_BITFILE [ lindex [get_hw_devices] 0]]; program_hw_devices [lindex [get_hw_devices] 0]; };
      INFO: [Labtools 27-3164] End of startup status: HIGH
      # program_hw_cfgmem -hw_cfgmem [get_property PROGRAM.HW_CFGMEM [lindex [get_hw_devices] 0 ]]
      Mfg ID : 1   Memory Type : 20   Memory Capacity : 18   Device ID 1 : 0   Device ID 2 : 0
      Performing Erase Operation...
      Erase Operation successful.
      Performing Program and Verify Operations...
      Program/Verify Operation successful.
      INFO: [Labtoolstcl 44-377] Flash programming completed successfully
      program_hw_cfgmem: Time (s): cpu = 00:00:00.17 ; elapsed = 00:01:22 . Memory (MB): peak = 2179.691 ; gain = 9.656 ; free physical = 5573 ; free virtual = 11207
      # endgroup
      INFO: [Common 17-206] Exiting Vivado at Sat Dec  7 11:47:05 2019..
      ```

 5. 启动（见视频）

