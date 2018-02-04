from __future__ import print_function

import argparse
import traceback

import dji_log_data.frames
import dji_log_data.keys

import sys


def decode_frame(frame_type, body):
    if frame_type.value < 1 or frame_type.value >= 16:
        # remove the first byte (the encoding index), and the trailer (0xFF)
        return body[1:-1]
    encoding_index = body[0]
    body = [x for x in body[1:-1]]
    key = get_key(frame_type, encoding_index)

    for i in range(len(body)):
        body[i] = body[i] ^ key[i % len(key)]
    return bytes(body)


def get_key(frame_type, encoding_index):
    key_index = ((frame_type.value - 1) * 256) + encoding_index
    return dji_log_data.keys.keys[key_index]


def decode_file(buffer):
    body = buffer[100:]
    frames = []

    i = 0
    while i < len(body):
        try:
            start = i
            try:
                frame_type = dji_log_data.frames.FrameType(body[i])
            except ValueError:
                frame_type = dji_log_data.frames.FrameType.UnrecognizedFrame

            frame_size = body[i+1]

            frame_end = i+2+frame_size
            frame_body = body[i+2:frame_end]
            trailer = body[frame_end]
            if trailer != 0xff:
                # Probably the end of the file. Don't understand the final chunk yet.
                break

            i += frame_size+3

            decoded_body = decode_frame(frame_type, frame_body)

            decoded_body = decode_frame(frame_type, frame_body)
            frame = dji_log_data.frames.TYPE_CLASS_MAP[frame_type](decoded_body, 1)
            frames.append(frame)
        except ValueError:
            traceback.print_exc()
    return frames


def hexstr(arr):
    return " ".join(["%02x" % x for x in arr])


def cli_decoder():
    parser = argparse.ArgumentParser(description='Parses DJI TXT log files')
    parser.add_argument('filename', type=argparse.FileType('rb'))

    args = parser.parse_args()
    contents = args.filename.read()
    frames = decode_file(contents)

    for f in frames:
        if isinstance(f, dji_log_data.frames.Position):
            print("Lat: %6f, Lon: %6f, Speed: (%4f, %4f, %4f), Fly time: %4f, Rev: %6d,  Sats: %3d, State: %s" %
                  (f.fields['latitude'],
                   f.fields['longitude'],
                   f.fields['x_speed'],
                   f.fields['y_speed'],
                   f.fields['z_speed'],
                   f.fields['fly_time'],
                   f.fields['motor_revolution'],
                   f.fields['satellites'],
                   f.fields['fly_c_state']['fly_c_state']))
        if isinstance(f, dji_log_data.frames.Time):
            print("Speed: %4f, Distance: %4f, Timestamp: %s" %
                  (f.fields['speed'],
                   f.fields['distance'],
                   f.fields['timestamp']))



if __name__ == '__main__':
    cli_decoder()