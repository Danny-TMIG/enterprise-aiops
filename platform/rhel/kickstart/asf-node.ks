# ASF hardened node kickstart for RHEL 10.0
lang en_US.UTF-8
keyboard us
timezone UTC --utc
rootpw --lock
user --name=asfadmin --groups=wheel --lock
part /boot     --fstype=xfs --size=1024 --fsoptions="nodev,nosuid"
part /boot/efi --fstype=efi --size=600
part pv.01 --size=1 --grow --encrypted --passphrase=SET-BY-VAULT
volgroup vg_asf pv.01
logvol /              --fstype=xfs --name=lv_root  --vgname=vg_asf --size=20480 --fsoptions="nodev"
logvol /var           --fstype=xfs --name=lv_var   --vgname=vg_asf --size=20480 --fsoptions="nodev,nosuid"
logvol /var/log       --fstype=xfs --name=lv_log   --vgname=vg_asf --size=10240 --fsoptions="nodev,nosuid,noexec"
logvol /var/log/audit --fstype=xfs --name=lv_audit --vgname=vg_asf --size=10240 --fsoptions="nodev,nosuid,noexec"
logvol /tmp           --fstype=xfs --name=lv_tmp   --vgname=vg_asf --size=4096 --fsoptions="nodev,nosuid,noexec"
logvol /home          --fstype=xfs --name=lv_home  --vgname=vg_asf --size=4096 --fsoptions="nodev,nosuid"
logvol /opt/asf       --fstype=xfs --name=lv_asf   --vgname=vg_asf --size=1 --grow
%packages --exclude-weakdeps
@^minimal-environment
aide
audit
chrony
firewalld
openscap-scanner
scap-security-guide
rhel-system-roles
podman
keylime
%end
%post
oscap xccdf eval --profile xccdf_org.ssgproject.content_profile_cis_server_l1 \
  --remediate /usr/share/xml/scap/ssg/content/ssg-rhel10-ds.xml || true
fips-mode-setup --enable
%end
