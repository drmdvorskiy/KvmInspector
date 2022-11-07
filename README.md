# kvm-inventory
Inventory for KVM hosts with web interface

## Installation
***ATTENTION !!! You need to make sure that the `kvm node` is available via `ssh` from the virtual machine (node) where the containers with the application work.***
* Copy `.ssh` directory with `ssh keys` to the project directory
* Rename `example.env` to `.env` and edit settings:
    * LISTOFNODES - Comma delimited KVM nodes to be inspected. (string)
    * MemoryForOs - The amount of memory required by the OS on the KVM node. (integer number)
    * CpuForOs - The amount of cpu required by the OS on the KVM node. (integer number)
    * BASIC_USER - Username for basic auth to `KVM Inspector`. (string)
    * BASIC_PASS - Password for basic auth to `KVM Inspector`. (string)

* Run KVM Inspector: `docker compose up -d`.

## Change settings
To change the app's settings:
* `cd` to app's directory
* Fill `.env` with your new values
* Stop containers: `docker compose down`
* Rebuild app's image: `docker compose build flask`
* Rebuild nginx's image: `docker compose build nginx` (if change the `basic authentication` credits)
* Run app again: `docker compose up -d`

### Credits
* Bootstrap 5 Dark theme https://mdbootstrap.com/
