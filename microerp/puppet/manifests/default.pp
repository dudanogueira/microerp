# basic bootstrap
exec { 'apt-get update':
  command => '/usr/bin/apt-get update'
}

# basic bootstrap
exec { 'apt-get upgrade -y':
  command => '/usr/bin/apt-get upgrade -y'
}

# pacotes basicos
$enhancers = [ "git-core", "screen", "python-psycopg2", "libpq-dev", "freetds-dev", "libmysqlclient-dev",  "libjpeg-dev", "libfreetype6-dev", "zlib1g-dev", "libpng12-dev"]
package { 
  $enhancers: ensure => "installed"
}

# postgres
class { 'postgresql::server': }


#postgresql::server::role { 'intranet':
#  password_hash => postgresql_password('intranet', 'intranet'),
#}

#postgresql::server::database_grant { 'intranet':
#  privilege => 'ALL',
#  db        => 'intranet',
#  role      => 'intranet',
#}

# Install & configure Python
class { 'python' :
  virtualenv => true,
  dev        => true,
}

# Create the directory where the app will be installed
file { ['/opt/microerp/source/', '/opt/microerp/', '/opt/']:
  ensure => directory,
}

# Create a virtualenv and install deps
python::virtualenv { '/opt/microerp/virtualenv' :
    ensure       => present,
    version      => 'system',
    requirements => '/opt/microerp/source/requirements.txt',
    systempkgs   => false,
    distribute   => false,
    owner        => 'vagrant',
    group        => 'vagrant',
    #cwd          => '/var/www/project1',
    timeout      => 0,
  }