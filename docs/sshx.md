# sshx
ssh client wrapper for automatic login.

> Clone of [sshw](https://github.com/yinheli/sshw) written in Python

Add some features

- add ssh connect through gateway ssh server

# Config
config file load in following order

- `~/.sshx.yml`
- `~/.sshx.yaml`
- `~/.sshw.yml`
- `~/.sshw.yaml`

# Usage
Create configuration file in `~/.sshx.yml`

```yaml
- name: inner-server
  user: appuser
  host: 192.168.8.35
  port: 22
  password: 123456 # login password
  gateway:
    user: gateway-server
    host: 10.0.0.38
    port: 2222
- name: dev server fully configured
  user: appuser
  host: 192.168.1.1
  keypath: ~/.ssh/id_rsa
  password: abcdefghijklmn # passphrase
  callback-shells:
    - { delay: 1, cmd: "uptime" }
    - { cmd: "echo 1" }
- name: dev group
  port: 22 # children will inherit all the configs as default
  children:
    - user: pc01
      host: 192.168.3.1
    - user: pc02
      host: 192.168.3.2
    - host: 192.168.3.3 # leave user empty will set to current user
```


```bash
$ sshx
Use the arrow keys to navigate (support vim style): ↓ ↑ 
✨ Select host
  ➤ inner-server appuser@192.168.8.35
    dev server fully configured appuser@192.168.1.1
    dev group

# specify config file
$ sshx --conf ~/.sshx.yml
```