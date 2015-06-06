# -*- mode: ruby -*-
VAGRANTFILE_API_VERSION = "2"
Vagrant.configure(VAGRANTFILE_API_VERSION) do |config|
  config.vm.box = "ubuntu/trusty64"
  config.vm.hostname = "microerp"
  config.vm.network "forwarded_port", guest: 8000, host: 8000
  config.vm.network "forwarded_port", guest: 5432, host: 15432
  config.vm.network "forwarded_port", guest: 3306, host: 13306
  config.vm.synced_folder "microerp/", "/opt/microerp/source", disabled: false
  config.vm.provision "shell", path: "microerp/puppet/install-puppet-modules.sh"
  config.vm.provision "puppet" do |puppet|
    puppet.manifests_path = "microerp/puppet/manifests"
  end
  config.vm.define "microerpt-vm" do |microerp_vm|
  end
  config.vm.provider "virtualbox" do |v|
        v.memory = 2048
    end
end

