# EventEase — Modules 1 & 2: Virtualization & VM Automation Guide

Part of the **BCA Cloud Computing and Virtualization** curriculum portfolio.

---

## 1. Module 1: Virtualization Fundamentals

### 1.1 Physical Machines vs. Virtual Machines

```
┌──────────────────────────────────────┐     ┌──────────────────────────────────────────────────┐
│ Traditional Physical Architecture    │     │ Virtualized Architecture (Type-2 Hypervisor)     │
├──────────────────────────────────────┤     ├──────────────────────────────────────────────────┤
│ Single Operating System              │     │ VM 1 (Ubuntu)    │ VM 2 (Debian)  │ VM 3 (Alpine)│
│ Single Hardware Set                  │     │ App: EventEase   │ App: Database  │ App: Cache   │
│ Inflexible Resource Allocation       │     ├──────────────────┴────────────────┴──────────────┤
│ Low Server Utilization (10% - 15%)   │     │ Hypervisor (e.g. Oracle VirtualBox / VMware)     │
├──────────────────────────────────────┤     ├──────────────────────────────────────────────────┤
│ Bare-Metal Server Hardware           │     │ Host Operating System (Windows 11 / 10)          │
│ (CPU, RAM, NIC, Physical Disks)      │     ├──────────────────────────────────────────────────┤
│                                      │     │ Physical Host Hardware (CPU with VT-x/AMD-V)     │
└──────────────────────────────────────┘     └──────────────────────────────────────────────────┘
```

- **Physical Machine (Bare Metal)**: Direct execution of a single operating system on physical hardware. Difficult to partition, slow to provision (days to weeks), and disaster recovery requires purchasing identical hardware.
- **Virtual Machine (VM)**: A software emulation of a complete physical computer, including virtual CPU, memory, network interfaces, and storage controllers, managed by a hypervisor.

---

### 1.2 Type 1 vs. Type 2 Hypervisors

| Feature | Type 1 Hypervisor (Bare-Metal) | Type 2 Hypervisor (Hosted) |
| :--- | :--- | :--- |
| **Architecture** | Runs directly on bare hardware without a host OS. | Runs as an application inside a standard host OS (e.g., Windows). |
| **Examples** | VMware ESXi, Microsoft Hyper-V Server, KVM, Xen. | Oracle VirtualBox, VMware Workstation, Parallels Desktop. |
| **Performance** | Maximum efficiency; lowest latency; zero host OS overhead. | Slight overhead caused by host OS scheduling and translation. |
| **Use Cases** | Enterprise datacenters, AWS EC2 Nitro, Azure Cloud. | Student labs, development testing, desktop virtualization. |

---

### 1.3 Key Virtualization Technologies: VirtualBox vs. KVM

- **Oracle VirtualBox (Type-2)**:
  - Cross-platform hypervisor running seamlessly on Windows, macOS, and Linux.
  - Ideal for student microprojects because it provides a friendly graphical interface and CLI (`VBoxManage`).
- **Kernel-based Virtual Machine / KVM (Type-1 / Kernel Module)**:
  - Built directly into the Linux kernel (`kvm.ko`).
  - Turns the Linux kernel itself into a bare-metal hypervisor using hardware virtualization extensions (Intel VT-x or AMD-V).
  - Managed via `libvirt` and the `virsh` command-line utility in production enterprise Linux environments.

---

### 1.4 Virtual Machine Resource Allocation

1. **vCPU Allocation**:
   - Hypervisors time-slice host physical cores to virtual CPUs (vCPUs).
   - Overcommitment allows provisioning more vCPUs than physical cores, but exceeding a 3:1 ratio causes CPU contention.
2. **RAM Allocation**:
   - Fixed allocation vs. Dynamic Memory / Ballooning.
   - Host reserving: Leave at least 4 GB RAM for the Windows host OS to avoid thrashing.
3. **Virtual Disk Formats**:
   - **VDI (VirtualBox Disk Image)**: Native format for VirtualBox.
   - **VMDK (Virtual Machine Disk)**: VMware standard format.
   - **QCOW2 (QEMU Copy-On-Write)**: Native Linux KVM format supporting efficient snapshots and sparse allocation.
   - **Fixed vs. Dynamically Allocated**: Dynamically allocated disks grow on demand up to the maximum size limit, saving host drive space.

---

### 1.5 VM Snapshots and Cloning

- **Snapshots**:
  - Captures the exact state, disk contents, and memory of a VM at a specific point in time.
  - Allows instant rollback before testing system upgrades or configuration changes.
  - *Mechanism*: The base virtual disk is marked read-only, and a delta/differencing disk records subsequent writes.
- **Full Clone vs. Linked Clone**:
  - **Full Clone**: An entirely independent copy of the VM disk. Consumes full disk space but operates without dependencies.
  - **Linked Clone**: References the parent snapshot disk. Created in seconds with minimal disk consumption, but depends on the master VM remaining intact.

---

### 1.6 Virtualization in Application Deployment

Virtualization revolutionized application deployment by:
- Enabling infrastructure-as-code and automated server provisioning.
- Providing consistent, reproducible environments identical to production.
- Allowing legacy applications requiring older operating systems to run on modern physical hardware.
- Serving as the foundational substrate for Cloud IaaS (Amazon EC2, Google Compute Engine, Microsoft Azure VMs).

---

## 2. Module 2: VM Management & Automation

### 2.1 Managing VirtualBox VMs via Windows PowerShell (`VBoxManage`)

Oracle VirtualBox includes a robust CLI utility called `VBoxManage.exe`, typically located at `C:\Program Files\Oracle\VirtualBox\VBoxManage.exe`.

#### Listing VMs:
```powershell
& "C:\Program Files\Oracle\VirtualBox\VBoxManage.exe" list vms
& "C:\Program Files\Oracle\VirtualBox\VBoxManage.exe" list runningvms
```

#### Starting a VM:
```powershell
# Start in headless (background) mode
& "C:\Program Files\Oracle\VirtualBox\VBoxManage.exe" startvm "Ubuntu-Server" --type headless

# Start with graphical display
& "C:\Program Files\Oracle\VirtualBox\VBoxManage.exe" startvm "Ubuntu-Server" --type gui
```

#### Stopping and Pausing a VM:
```powershell
# Graceful ACPI shutdown (like pressing power button)
& "C:\Program Files\Oracle\VirtualBox\VBoxManage.exe" controlvm "Ubuntu-Server" acpipowerbutton

# Force power off
& "C:\Program Files\Oracle\VirtualBox\VBoxManage.exe" controlvm "Ubuntu-Server" poweroff

# Pause and resume execution
& "C:\Program Files\Oracle\VirtualBox\VBoxManage.exe" controlvm "Ubuntu-Server" pause
& "C:\Program Files\Oracle\VirtualBox\VBoxManage.exe" controlvm "Ubuntu-Server" resume
```

#### Inspecting VM Hardware & Statistics:
```powershell
& "C:\Program Files\Oracle\VirtualBox\VBoxManage.exe" showvminfo "Ubuntu-Server"
```

#### Creating and Restoring Snapshots:
```powershell
# Take snapshot before updating
& "C:\Program Files\Oracle\VirtualBox\VBoxManage.exe" snapshot "Ubuntu-Server" take "Pre-Update-State"

# Restore snapshot
& "C:\Program Files\Oracle\VirtualBox\VBoxManage.exe" snapshot "Ubuntu-Server" restore "Pre-Update-State"
```

---

### 2.2 Enterprise Linux KVM & `virsh` Management

> **Environment Note**: These commands run on a Linux host (e.g., Ubuntu Server, RHEL, or Fedora) with hardware virtualization enabled (`kvm-ok`). On Windows, students who do not run Linux bare-metal can demonstrate these concepts conceptually or inside Windows Subsystem for Linux (WSL2).

#### Verifying Hardware Virtualization Support on Linux:
```bash
egrep -c '(vmx|svm)' /proc/cpuinfo
kvm-ok
```

#### Common `virsh` Commands:
```bash
# List all active virtual machines
virsh list

# List all defined virtual machines (running and shut off)
virsh list --all

# Start a virtual machine
virsh start eventease-vm

# Gracefully reboot a virtual machine
virsh reboot eventease-vm

# Gracefully shut down a virtual machine
virsh shutdown eventease-vm

# Force power off a frozen virtual machine
virsh destroy eventease-vm

# View VM CPU and memory configuration
virsh dominfo eventease-vm

# Manage KVM snapshots
virsh snapshot-create-as --domain eventease-vm --name "Clean-Install" --description "Fresh OS with EventEase dependencies"
virsh snapshot-list eventease-vm
virsh snapshot-revert eventease-vm --snapshotname "Clean-Install"
```

---

### 2.3 Troubleshooting Common VM Issues

1. **Hardware Virtualization (VT-x / AMD-V) Disabled in BIOS/UEFI**:
   - *Symptom*: Hypervisor fails to start 64-bit guest OS with error *"VT-x is not available"*.
   - *Resolution*: Reboot host PC, enter BIOS/UEFI firmware settings (F2/Del), locate *Virtualization Technology* or *SVM Mode*, enable it, and save.
2. **Hyper-V / VirtualBox Conflict on Windows**:
   - *Symptom*: VirtualBox VMs fail to boot or run extremely slowly when Windows Hyper-V or WSL2 is active.
   - *Resolution*: Use modern VirtualBox 7.x which supports Hyper-V co-existence (NEM - Native Execution Mode), or disable Windows Hyper-V via `bcdedit /set hypervisorlaunchtype off`.
3. **Insufficient Disk Space on Virtual Drive**:
   - *Symptom*: Guest OS throws `No space left on device` during database writes or package installation.
   - *Resolution*: Resize virtual disk using `VBoxManage modifymedium disk <uuid> --resize <megabytes>`, then extend the partition in guest OS using `resize2fs` or `growpart`.
