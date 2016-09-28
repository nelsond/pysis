# pySIS [![Build Status](https://travis-ci.org/nelsond/pysis.svg?branch=master)](https://travis-ci.org/nelsond/pysis)

Simple module for reading `.SIS` image files created by BECAnalyze.

## Requirements

- `numpy` >= 1.9

## Install

Install with pip

```shell
$ pip install git+git://github.com/nelsond/pysis.git
```

## Example usage

```python
import numpy as np
from sis import Image

# read an image
image = Image.from_path('some-image.SIS')
image.width # => 10
image.height # => 10
image.frame_count # => 2
image.frames[0] # [[12, ..., 0], ..., [14, ..., 12]]

# create an image
data = np.array([[100, ..., 30], ..., [5023, ..., 7301]])
new_image = Image(data)
new_image.dimensions # => (10, 10)
new_image.to_buffer # => b'.SIS...'
new_image.save_to('a-new-image.SIS')
```

## Development

Install requirements for development environment

```shell
$ pip install -r requirements/dev.txt
```

Run tests

```shell
$ py.test tests/
```

Generate coverage report

```shell
$ py.test --cov=sis tests/
```

### Open tasks

- Add `sis2png` command line tool
