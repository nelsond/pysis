# -*- coding: utf-8 -*-

import struct
import numpy as np

class Image:
    PIXEL_DATA_TYPE = np.uint16
    HEADER_SIZE = 256

    def __init__(self, data=None, width=None, height=None):
        self.width = width
        self.height = height

        if type(data) == np.ndarray:
            self.data = data.astype(self.PIXEL_DATA_TYPE)
        else:
            self.data = None

        if not self.width or not self.height:
            self._guess_dimensions()

    @property
    def dimensions(self):
        return (self.width, self.height)

    @property
    def frames(self):
        dimensions = (self.frame_count, self.height, self.width)
        return self.data.reshape(dimensions)

    @property
    def frame_count(self):
        total_height = self.data.size / self.width
        return int(total_height/self.height)

    @property
    def is_valid(self):
        if self.data == None: return False
        if not self.width: return False
        if not self.height: return False

        return np.shape(self.data) == (self.height, self.width)

    @property
    def _header(self):

        # ┌─────────┬──────────────┬────────────────┬─────────────────┬───────────────┬─────────┐
        # │    Byte │     1 - 4    │        5       │        6        │       7       │ 8 - 256 │
        # ├─────────┼──────────────┼────────────────┼─────────────────┼───────────────┼─────────┤
        # | Content | .SIS (ascii) | width (uint32) | height (uint32) | depth(uint32) |  unused |
        #  ─────────┴──────────────┴────────────────┴─────────────────┴───────────────┴─────────┘

        width = self.width
        height = self.height
        depth = 2 # currently only 16-bit supported

        content = struct.pack('ccccIII', b'.', b'S', b'I', b'S', width, height, depth)
        pad = struct.pack( 'x' * (self.HEADER_SIZE - len(content)) )

        return content + pad

    def to_buffer(self):
        return self._header + self.frames.T.ravel().tobytes()

    def save_to(self, path):
        with open(path, 'wb') as f:
            f.write(self.to_buffer())

    def _guess_dimensions(self):
        shape = self.data.shape
        if len(shape) <= 1:
            return

        self.width = shape[-1]
        self.height = shape[-2]

    @classmethod
    def from_file(klass, f):
        width, height = klass._read_header(f)

        f.seek(klass.HEADER_SIZE)
        data = np.fromfile(f, klass.PIXEL_DATA_TYPE).reshape(width, height).T

        return klass(data, width=width, height=height)

    @classmethod
    def from_path(klass, path):
        with open(path, 'rb') as f:
            image = klass.from_file(f)

        return image

    @classmethod
    def _read_header(klass, f):
        f.seek(0)

        header = f.read(klass.HEADER_SIZE)

        if (len(header) < 256/8):
            raise ValueError('Invalid header')

        size = struct.calcsize('ccccIII')
        padding_size = (klass.HEADER_SIZE - size)
        values = struct.unpack('ccccIII' + ('x' * padding_size), header)

        magic = b''.join(values[0:4])
        if magic != b'.SIS':
            raise ValueError('Not a SIS file')

        # currently only 16-bit supported
        depth = values[6]
        if depth != 2:
            raise ValueError('Unsupported pixel depth (%i-bit)' % (depth*8))

        width, height = values[4:6]
        return (width, height)
