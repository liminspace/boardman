# boardman

MicroPython deployment tool


## Development

```bash
$ poetry config --local virtualenvs.create false
$ poetry install
```

```bash
$ poetry config repositories.testpypi https://test.pypi.org/legacy/
$ poetry config pypi-token.testpypi <token>


```
```bash
$ pip install -U --pre -i https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ -U "boardman>0.1.0" 
```
