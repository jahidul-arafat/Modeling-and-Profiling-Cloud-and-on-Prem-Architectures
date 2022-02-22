# An Interesting Bug in Oracle Cloud Infrastructure Console UI
### By Jahidul Arafat

---
### Bug Name: CONSOLE UI is failing to get the call from instance terminal for Compute Instance State Transition

https://youtu.be/pcdhK4DvgwY
[![Watch the video](https://img.youtube.com/vi/T-D1KVIuvjA/maxresdefault.jpg)](https://youtu.be/pcdhK4DvgwY)



---

### @OCI
- [x] create a new compute instance. You will see the instance in provisioning stage. Once ready, it will be in running state.
- [x] if you stop (through **CONSOLE UI**) the instance, then it transitioned to "**STOP**" state
- [x] if you reboot (through **CONSOLE UI**) the instance transitioned from **rebooting** to **running** state

#### Let's Debug the Bug
- [x] ssh to the instance 
- [x] then shutdown the instance from terminal using
  >sudo shutdown now
- [x] SSH connection will be closed as instance is shutdown from terminal.

### So We are expecting?
- We are expecting that, the instance state will be updated to **STOPPED** in the CONSOLE UI.
- But **this never happens**, as the CONSOLE UI can't even identify this call from terminal and dont transition 
the instance state (doesn't matter how many times you refresh the CONSOLE UI, that transition not gonna show
and it's still showing Instance in (FALSE) RUNNING state )


## @AWS

Let's simulate the same thing for AWS and you gonna see, AWS CONSOLE UI response to the instance terminal call
and transitioned the EC2 to STOPPED state.

