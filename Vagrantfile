Vagrant.configure(2) do |config|
  config.vm.box = "debian/contrib-buster64"
  config.vm.synced_folder ".", "/app", type: "virtualbox"
  config.vm.provider "virtualbox" do |vb|
    vb.gui = true
    vb.memory = "2000"
    vb.customize ["modifyvm", :id, "--vram", "128"]
  end
  config.vm.provision "shell", inline: <<-SHELL
    apt-get update
    # lightweight desktop environment
    apt-get install -y xfce4
    # enable autologin
    perl -pi.back -e "s/^#?autologin-user=.*$/autologin-user=vagrant/" /etc/lightdm/lightdm.conf
    perl -pi.back -e "s/^#?autologin-user-timeout=.*$/autologin-user-timeout=0/" /etc/lightdm/lightdm.conf
    # disable screen locker
    rm -f /etc/xdg/autostart/light-locker.desktop

    # impf-botpy requirements
    apt-get install -y python3 python3-pip chromium-driver

    ## VirtualBox integration
    VBoxClient --clipboard
    VBoxClient --draganddrop
    VBoxClient --vmsvga
    VBoxClient --checkhostversion
    VBoxClient --seamless
  SHELL
  config.vm.provision "shell", privileged: false, inline: <<-SHELL
    # use the default panel configuration and do not ask the user
    if [[ ! -f ~/.config/xfce4/xfconf/xfce-perchannel-xml/xfce4-panel.xml ]] ; then
      mkdir -p ~/.config/xfce4/xfconf/xfce-perchannel-xml
      cp /etc/xdg/xfce4/panel/default.xml ~/.config/xfce4/xfconf/xfce-perchannel-xml/xfce4-panel.xml
    fi

    # impf-botpy Python dependencies
    cd /app
    pip3 install -r requirements.txt
  SHELL
end
