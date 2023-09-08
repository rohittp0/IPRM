# IPRM

This is my B. Tech Mini Project. You can find the full project report [here]()
## Abstract

Network computing refers to performing computation within

the network rather than forwarding data to a processing unit for compu-
tation. This mode of operation helps cut down latency by avoiding the

many slow software and hardware pipelines to be used to process network
data. Historically the approach for establishing In-Network computing
is by using dedicated hardware between the network endpoint and the
processing machine. This proves costly and hard to set up and maintain
as there is the added work of maintaining separate hardware (cooling,
security, stability).
Current state of art systems uses a more innovative approach. They
integrate hardware accelerator cards directly into the computing machine

to solve most drawbacks of separate hardware pass-through. These ac-
celerator cards perform tasks common in the network infrastructure, like

HMAC calculation, MD5 verication, SSL signing, Etc, without consum-
ing valuable CPU resources. Even though costly, these cards are widely

used in the industry to optimizes throughput and reduce latency.

In the project, a new hardware accelerator device is introduced, ca-
pable of direct integration into the NIC. A NIC add-on module has been

created as part of the project, enabling the interception and modication
of network packets after they are received by the NIC and before they
are forwarded to the PCI bus. The hardware, known as the In-Hardware

Proxy and Rewrite Module (IPRM), in a sense, performs a man-in-the-
middle attack.

