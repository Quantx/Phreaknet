Welcome to PhreakNET

PhreakNET is an online hacking themed MMO that is currently under development. Development is being done entirely with Python 3. While hacking is the primary theme of PhreakNET, the entire simulation is self-contained and no actual hacking is being done.

Information about running phreaknet can be found within the ```src/README.md```

PhreakNET attempts to simulate a network hosts, each running simplified *nix style enviornments. These simplified enviornments provide many of the familiar features found within *nix style systems such as file and group permission systems as well a simulated directory system.

PhreakNET is not an attempt to create a near 1 to 1 simulation of *nix style operating systems and features many "dumbed down" elements in an attempt to apeal to a wider audience. PhreakNET is not a CTF.

The primary gameplay loop entails writing scripts and running exploits to explore around the virtual network. Upgrading your personal gateway machine, create and expand botnets, and collecting proccessing power, to run more complex exploits.

PhreakNET features Player vs. Enemy aspects such as stealing data and root access from non-player machines. And Player vs. Player aspects such as compromising other players' gateway machines and impeading their progress to your advantage.

Each player is given one low-end gateway system when they join. The player is able to access their gateway by means of local TTY and the system will operate independantly of them when they are offline. This means that even though a player may not be actively connected to their machine, any programs or processes running in the background will persist. This can be advantageous since some programs take long periods of time to complete, but may also be worse in the long run since it leaves your system open to exploitation by other players while you're away.



Getting started:

Once phreaknet is up and running and you've connected to it (see ```src/README.md```)

First create an account and password by pressing "R" to register then entering your username / password

Passwords are stored using 512bit encryption with a 64 byte random salt and 100,000 rounds of hashing

Answer yes to the privacy agreement (i've yet to write this, but i'll get around to it)

Then startup your gateway by pressing "N" (The safemode option will boot your gateway with no network connectivity. This can be usefull for debugging your system without risk of being hacked by other players)

Now connect to TTY 0 (They're all the same, but having multiple means you can multitask)

If you accidently close out of telnet early dont worry! PhreakNET saves your TTY session and will automatically recover it when you reconnect to that TTY.

Once you're inside your gateway machine, now the real fun can begin!

The ```cd``` and ```pwd``` commands can be used to change and view your current working directory and ```ls``` will list all files in that directory

Try navigating to the root of your directory tree with ```cd /``` and then running ```ls```

The four directories listed hear are:
```
bin - stores your executable programs (check here for a complete list of programs to run)
sys - stores operating system related files
log - stores log files from various programs
usr - contains the home directory for each user
```

These directories of each host can be found on disk under ```dir``` in your repo. Every file and directory on phreaknet is accompanied by an .inode file which contains the relevant file permissions. If phreaknet is unable to find an acompanying .inode file then that directory or file will not be visible, this ensures players can't escape their own directories' scope.

Inside the ```sys``` directory you'll find an aproximation of ```/etc/passwd``` and ```/etc/group``` which stores user and group data

When prompted for a password in PhreakNET you should submit the one you signed up with. This password will not be visible to other users, and should not be saved to disk.

Password hashes for PhreakNET are NOT accessable by users from within the game.

Now, lets hack another host!

First, run the ```arp``` program. This program will list the DCA address of your Host, your Router, and your ISP.

Direct Connect Addressing or DCA, is a packet routing system developed for PhreakNET.

An example DCA address is as follows, DCA addressing should NOT be entered as hexadecimal:
```12345.12345.12345```

Where each partition is a value between 0 and 65535 (0xFFFF).

The loopback address is: ```0.0.0```

The first part of the DCA address indicates the ISP.

The second part indicates which Router connected to that ISP.

And the third part indicates which Host connected to that Router

If your DCA address was: ```1.2.3```

You would connect to your router by SSH-ing to: ```1.2.0```

And you would connect to your ISP at: ```1.0.0```

For this example we will be hacking into the router "PhreakNET", so note that host's DCA

Now run the Porthack program by executing: ```porthack```

When prompted enter PhreakNET's DCA address

The correct port to try is 0 (this will change)

Now that you have an account on PhreakNET, we can connect by executing ```ssh <PhreakNET's DCA>```

When prompted for your password, enter the one you signed up with.

Now you're remotely connected to PhreakNET and can explore arround.

To view all hosts on this router run ```arp -n```

If you hack into an ISP, you can run ```arp -r``` to view all routers subscribed to that ISP.

Also, try out the ```worldmap``` program which will render an ASCII-art map of the earth and display the location of the host you run it on with an ```X```.
