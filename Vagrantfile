Vagrant.configure("2") do |config|
  config.vm.box = "ubuntu/bionic64"
  config.vm.provider "virtualbox" do |vb|
    vb.memory = "2048"
  end
  config.vm.provision "shell", inline: <<-SHELL
    apt-get update
    apt-get install -y python3 nodejs
  SHELL
  # .quiz_project -> /www/quiz_project sycronic  AUTOMATIC CHANGES
  config.vm.synced_folder ".", "/www/quiz_project"


  # CREATE FOLDER ON THE VIRTUAL MACHINE AND SYNCHRONIZE WITH THE LOCAL MACHINE NEW  FOLDER AND SYNCHRONIZE
  config.vm.synced_folder "new_folder", "/www/new_folder" 


end
