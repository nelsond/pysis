import pytest
import numpy as np
from random import randint
import struct
import os

from sis import Image

@pytest.fixture
def random_image_array():
    depth = 2**16-1
    dimensions = (10, 10)

    return np.random.randint(0, depth, dimensions).astype(Image.PIXEL_DATA_TYPE)

# __init__
def test_init_typecasts_data_with_PIXEL_DATA_TYPE():
    w, h = (3, 3)
    data = np.random.randint(0, 2**16-1, (w, h)).astype(np.uint8)
    image = Image(data, width=w, height=h)

    assert(image.data.dtype == Image.PIXEL_DATA_TYPE)

def test_init_guesses_dimensions_from_array_shape_for_single_frame(random_image_array):
    w, h = np.shape(random_image_array.T)
    image = Image(random_image_array)

    assert(image.dimensions == (w, h))

def test_init_guesses_dimensions_from_array_shape_for_multi_frames(random_image_array):
    w, h = np.shape(random_image_array.T)
    random_two_frame_array = np.array([random_image_array, random_image_array])
    image = Image(random_two_frame_array)

    assert(image.dimensions == (w, h))

# .is_valid
def test_is_valid_returns_true_with_correct_dimensions_and_data_present(random_image_array):
    w, h = np.shape(random_image_array.T)
    image = Image(random_image_array, width=w, height=h)

    assert(image.is_valid == True)

def test_is_valid_returns_false_without_data_present():
    image = Image(width=10, height=10)

    assert(image.is_valid == False)

def test_is_valid_returns_false_without_width_present(random_image_array):
    _, h = np.shape(random_image_array.T)
    image = Image(random_image_array.flatten(), height=h)

    assert(image.is_valid == False)

def test_is_valid_returns_false_without_height_present(random_image_array):
    w, _ = np.shape(random_image_array.T)
    image = Image(random_image_array.flatten(), width=w)

    assert(image.is_valid == False)

def test_is_valid_returns_false_with_wrong_dimensions(random_image_array):
    w, h = np.shape(random_image_array.T)
    image = Image(random_image_array, width=w, height=h*2)

    assert(image.is_valid == False)

# .dimensions
def test_dimensions_returns_width_and_height():
    image = Image(width=2, height=1)

    assert(image.dimensions == (2, 1))

# .frame_count
def test_frame_count_returns_correct_frame_number_for_one_frame(random_image_array):
    image = Image(random_image_array)

    assert(image.frame_count == 1)

def test_frame_count_returns_correct_frame_number_for_multiple_frames(random_image_array):
    w, h = np.shape(random_image_array.T)

    random_two_frame_array = np.array([random_image_array, random_image_array]).T.reshape(w, 2*h)
    image = Image(random_two_frame_array.T, width=w, height=h)

    assert(image.frame_count == 2)

# .frames
def test_frame_returns_data_with_single_frame_image(random_image_array):
    image = Image(random_image_array)
    frame = image.frames[0]

    assert(np.array_equal(frame, random_image_array))

def test_frame_returns_data_with_multi_frame_image(random_image_array):
    w, h = np.shape(random_image_array.T)

    random_two_frame_array = np.array([random_image_array, random_image_array]).reshape(2*h, w)
    image = Image(random_two_frame_array, width=w, height=h)
    frame = image.frames[1]

    assert(np.array_equal(frame, random_image_array))

# ._header
def test_header_has_magic_signature_at_beginning(random_image_array):
    image = Image(random_image_array)
    header = image._header

    size = struct.calcsize('ccccIII')
    values = struct.unpack('ccccIII' + ('x' * (256 - size) ), header)
    expected_values = (b'.', b'S', b'I', b'S', image.width, image.height, 2)

    assert(values == expected_values)

# .to_buffer
def test_to_buffer_returns_header_and_data(random_image_array):
    image = Image(random_image_array)
    buf = image.to_buffer()

    expected_buf = image._header + random_image_array.T.ravel().tobytes()

    assert(buf == expected_buf)

# .save_to
def test_save_to_saves_buffer_to_file(random_image_array, tmp_path):
    image = Image(random_image_array)

    image_path = os.path.join(tmp_path, 'test.sis')
    image.save_to(image_path)
    with open(image_path, 'rb') as f: saved_buffer = f.read()

    assert(saved_buffer == image.to_buffer())

# Image.from_file
def test_Image_from_file_returns_image_from_file(fixtures_path):
    path = os.path.join(fixtures_path, 'valid.sis')
    with open(path, 'rb') as f:
        image = Image.from_file(f)

    assert(image.dimensions == (10, 10))

def test_Image_from_file_raises_ValueError_if_header_invalid(fixtures_path):
    path = os.path.join(fixtures_path, 'incomplete-header.sis')
    f = open(path, 'rb')

    with pytest.raises(ValueError) as exc_info:
        Image.from_file(f)

    f.close()

    assert('header' in str(exc_info.value))

def test_Image_from_file_raises_ValueError_if_pixel_depth_invalid(fixtures_path):
    path = os.path.join(fixtures_path, 'invalid-pixel-depth.sis')
    f = open(path, 'rb')

    with pytest.raises(ValueError) as exc_info:
        Image.from_file(f)

    f.close()

    assert('pixel depth' in str(exc_info.value))

def test_Image_from_file_raises_ValueError_if_not_a_sis_file(fixtures_path):
    path = os.path.join(fixtures_path, 'lorem.txt')
    f = open(path, 'rb')

    with pytest.raises(ValueError) as exc_info:
        Image.from_file(f)

    f.close()

    assert('SIS' in str(exc_info.value))

# Image.from_path
def test_Image_from_path_returns_image_from_file_path(fixtures_path):
    path = os.path.join(fixtures_path, 'valid.sis')
    image = Image.from_path(path)

    assert(image.dimensions == (10, 10))

