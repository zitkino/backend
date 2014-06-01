# -*- mode: ruby -*-

name = "zitkino"

Vagrant.configure("2") do |config|
  config.vm.hostname = name
  config.vm.box = "precise64"
  config.vm.box_url = "http://files.vagrantup.com/precise64.box"
  config.vm.provision :shell, :path => "bootstrap.sh"
  config.vm.provider "virtualbox" do |v|
    v.name = name
    v.customize ["modifyvm", :id, "--memory", "1024"]
  end
end
