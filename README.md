# py3toolkit
toolkit for my common use

# Install and Usage
```bash
pip3 install -U py3toolkit
```

Command line tools

- sshx: Clone of [sshw](https://github.com/yinheli/sshw) written in Python
- gen_supervisor_conf: generate supervisor conf through yaml

# Build and Publish

```bash
poetry self add "poetry-dynamic-versioning[plugin]"
poetry publish --build
```

# Refs
- https://pypi.org/project/poetry-dynamic-versioning/