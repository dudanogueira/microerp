# basic bootstrap
exec { 'apt-get update':
  command => '/usr/bin/apt-get update'
}

# basic bootstrap
exec { 'apt-get upgrade -y':
  command => '/usr/bin/apt-get upgrade -y'
}

# pacotes basicos
$enhancers = [ "git-core", "screen", "python-psycopg2", "libpq-dev", "freetds-dev", "libmysqlclient-dev",  "libjpeg-dev", "libfreetype6-dev", "zlib1g-dev", "libpng12-dev", "python-dev"]
package { 
  $enhancers: ensure => "installed"
}

# postgres
class { 'postgresql::server':
  ip_mask_allow_all_users    => '0.0.0.0/0',
  listen_addresses           => '*',
}

postgresql::server::role { 'microerp':
  password_hash => postgresql_password('microerp', 'microerp'),
  createdb  => true
}

postgresql::server::db { 'microerp':
  user     => 'microerp',
  password => postgresql_password('microerp', 'microerp'),
}

postgresql::server::database_grant { 'microerp':
  privilege => 'ALL',
  db        => 'microerp',
  role      => 'microerp',
}

postgresql::server::pg_hba_rule { 'permite acesso local para usuario':
  description => "permite acesso local para usuario",
  type => 'local',
  database => 'microerp',
  user => 'microerp',
  auth_method => 'md5',
  order=>'001',
}

# mysql
class { 'mysql::server':

      root_password    => 'root',

      override_options => {
          'mysqld' => {
              'connect_timeout'                 => '60',
              'bind_address'                    => '0.0.0.0',
              'max_connections'                 => '100',
              'max_allowed_packet'              => '512M',
              'thread_cache_size'               => '16',
              'query_cache_size'                => '128M',
          }
     }
}


mysql::db { 'microerp':
  user     => 'microerp',
  password => 'microerp',
  host     => '%',
  grant    => ['all'],
  charset => 'utf8',
  collate => 'utf8_general_ci',
}


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