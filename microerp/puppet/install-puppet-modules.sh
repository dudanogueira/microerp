#!/bin/bash

mkdir -p /etc/puppet/modules;

if [ ! -d /etc/puppet/modules/apt ];
    then puppet module install puppetlabs-apt --version 2.0.1
fi
:
if [ ! -d /etc/puppet/modules/python ];
    then puppet module install stankevich-python --version 1.9.4
fi

if [ ! -d /etc/puppet/modules/postgresql ];
    then puppet module install puppetlabs-postgresql --version 4.3.0
fi

if [ ! -d /etc/puppet/modules/vcsrepo ];
    then puppet module install puppetlabs-vcsrepo --version 1.3.0
fi