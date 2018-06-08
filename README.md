# Overview
This charm serves the very narrow and specific purpose of validating that a
database connection provided over a Juju Charm relation is indeed ready for
persistent use instantly after the relation is complete.


# Usage
    juju deploy mysql
    juju deploy index-paratus
    juju add-relation mysql index-paratus


## Scale out Usage
    juju add-unit -n2 mysql
    juju add-unit -n2 index-paratus


## Known Limitations and Issues
This charm is meant for simulation and testing only.


# Configuration
The charm infers required information from the environment it is deployed in
and from relations with other charms.


# Contact Information
Author: OpenStack Charmers <openstack-dev@lists.openstack.org>

Icon based on "Database free icon" by smashicons from www.flaticon.com and
"ready" by Arbcom from https://commons.wikimedia.org
