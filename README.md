# py3toolkit
toolkit for my common use

# Install and Usage
```bash
pip3 install -U py3toolkit
```

Command line tools

- [sshx](docs/sshx.md): Clone of [sshw](https://github.com/yinheli/sshw) written in Python
- [gen_supervisor_conf](docs/gen_supervisor_conf.md): generate supervisor conf through yaml

# Build and Publish

```bash
poetry self add "poetry-dynamic-versioning[plugin]"
poetry publish --build
```

# Refs
- https://pypi.org/project/poetry-dynamic-versioning/