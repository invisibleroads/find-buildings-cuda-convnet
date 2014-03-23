# -*- mode: ruby -*-
# vi: set ft=ruby :

# Vagrantfile API/syntax version. Don't touch unless you know what you're doing!
VAGRANTFILE_API_VERSION = "2"

Vagrant.configure(VAGRANTFILE_API_VERSION) do |config|
  config.vm.box = "lucid64"
  config.vm.box_url = "http://files.vagrantup.com/lucid64.box"
  config.ssh.forward_agent = true
  config.vm.network "forwarded_port", guest: 22361, host: 22361

  # toss some stuff onto the box
  Vagrant.configure("2") do |config|
    config.vm.provision "shell",
      inline: "sudo apt-get install -y python-pip vim"
  end
end
