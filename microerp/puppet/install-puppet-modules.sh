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

if [ ! -d /etc/puppet/modules/mysql ];
    then puppet module install puppetlabs-mysql --version 3.4.0
fi

locale-gen en_US en_US.UTF-8 pt_BR.UTF-8
dpkg-reconfigure locales