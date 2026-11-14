# 📜 LogTail

A lightweight log reader for Windows, Linux and macOS. It uses only Python's standard library.

## Examples

```bash
python logtail.py app.log
python logtail.py app.log --lines 100
python logtail.py app.log --match ERROR --ignore-case
python logtail.py app.log --exclude DEBUG --follow
python logtail.py server.log worker.log --follow --from-start
```

`--follow` watches appended content and handles basic file rotation/truncation. `--match` and `--exclude` are plain-text filters, not regular expressions. Press Ctrl+C to stop.

Requires Python 3.8+. No installation.
