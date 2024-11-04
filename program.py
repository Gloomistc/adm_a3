import sys
import csv
import struct


def get_format(data_type):
    formats = {
        "int8": "b",
        "int16": "h",
        "int32": "i",
        "int64": "q",
        "string": "s"
    }
    return formats.get(data_type)


def read_csv(filepath, data_type):
    data = []
    with open(filepath, newline='') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            for item in row:
                if data_type.startswith('int'):
                    data.append(int(item))
                    # data.append(item)
                else:
                    data.append(item)
    return data


def write_bin(filepath, data, format_str):
    # with open(filepath, "wb") as binfile:
    #     for item in data:
    #         if isinstance(item, int):
    #             binfile.write(struct.pack(format_str, item))
    #         else:
    #             binfile.write(item.encode('utf-8'))
    with open(filepath, "wb") as binfile:
        packed_data = b"".join(
            struct.pack(format_str, item) if isinstance(
                item, int) else item.encode("utf-8")
            for item in data
        )
        binfile.write(packed_data)


# def read_bin(filepath, format_str, data_type):
#     data = []
#     size = struct.calcsize(format_str)
#     with open(filepath, "rb") as binfile:
#         while chunk := binfile.read(size):
#             if data_type.startswith('int'):
#                 data.append(struct.unpack(format_str, chunk)[0])
#             else:
#                 data.append(chunk.decode('utf-8'))
#     return data

def read_bin(filepath, format_str, data_type):
    data = []
    size = struct.calcsize(format_str)
    with open(filepath, "rb") as binfile:
        content = binfile.read()
        for i in range(0, len(content), size):
            chunk = content[i:i+size]
            if data_type.startswith("int"):
                data.append(struct.unpack(format_str, chunk)[0])
            else:
                data.append(chunk.decode("utf-8"))
    return data


def encode_bin(data):
    return data


def decode_bin(data):
    return data


def encode_rle(data):
    encoded_data = []
    i = 0
    while i < len(data):
        count = 1
        while i + 1 < len(data) and data[i] == data[i + 1]:
            count += 1
            i += 1
        encoded_data.append((data[i], count))
        i += 1
    return encoded_data


# def decode_rle(data):
#     decoded_data = []
#     for value, count in data:
#         decoded_data.extend([value] * count)
#     return decoded_data

def decode_rle(data):
    for value, count in data:
        for _ in range(count):
            yield value


def encode_dic(data):
    dictionary = list(set(data))
    encoded_data = [dictionary.index(item) for item in data]
    return dictionary, encoded_data


def decode_dic(dictionary, encoded_data):
    return [dictionary[index] for index in encoded_data]


def encode_for(data):
    min_val = min(data)
    encoded_data = [item - min_val for item in data]
    return min_val, encoded_data


def decode_for(min_val, encoded_data):
    return [item + min_val for item in encoded_data]


def encode_dif(data):
    encoded_data = [data[0]]
    for i in range(1, len(data)):
        encoded_data.append(data[i] - data[i - 1])
    return encoded_data


def decode_dif(data):
    decoded_data = [data[0]]
    for i in range(1, len(data)):
        decoded_data.append(decoded_data[-1] + data[i])
    return decoded_data


def write_compressed(filepath, data, compression_type, data_type):

    if compression_type == "bin":
        format_str = get_format(data_type)
        write_bin(filepath, data, format_str)

    elif compression_type == "rle":
        encoded_data = encode_rle(data)
        # with open(filepath, "wb") as f:
        #     for value, count in encoded_data:
        #         if data_type == "string":
        #             # f.write(value.encode('utf-8') + b'\n')
        #             # value_bytes = value.encode('utf-8')
        #             # f.write(struct.pack("I", len(value_bytes)))
        #             # f.write(value_bytes)
        #             value_bytes = value.encode('utf-8')
        #             f.write(len(value_bytes).to_bytes(4, byteorder='little'))
        #             f.write(value_bytes)
        #         else:
        #             f.write(struct.pack(get_format(data_type), value))
        #         # f.write(struct.pack("I", count))
        #         f.write(count.to_bytes(4, byteorder='little'))
        rle_content = bytearray()
        for value, count in encoded_data:
            if data_type == "string":
                value_bytes = value.encode("utf-8")
                rle_content.extend(
                    len(value_bytes).to_bytes(4, byteorder="little"))
                rle_content.extend(value_bytes)
            else:
                rle_content.extend(struct.pack(get_format(data_type), value))
            rle_content.extend(count.to_bytes(4, byteorder="little"))
        with open(filepath, "wb") as f:
            f.write(rle_content)

    elif compression_type == "dic":
        dictionary, encoded_data = encode_dic(data)
        # with open(filepath + ".dic_dict", "wb") as dict_file:
        #     for value in dictionary:
        #         if data_type == "string":
        #             # dict_file.write(value.encode("utf-8") + b"\n")
        #             # value_bytes = value.encode("utf-8")
        #             # dict_file.write(struct.pack("I", len(value_bytes)))
        #             # dict_file.write(value_bytes)
        #             value_bytes = value.encode("utf-8")
        #             dict_file.write(len(value_bytes).to_bytes(
        #                 4, byteorder="little"))
        #             dict_file.write(value_bytes)
        #         else:
        #             dict_file.write(struct.pack(get_format(data_type), value))
        # with open(filepath, "wb") as f:
        #     for index in encoded_data:
        #         # f.write(struct.pack("I", index))
        #         f.write(index.to_bytes(4, byteorder="little"))
        dict_content = bytearray()
        for value in dictionary:
            if data_type == "string":
                value_bytes = value.encode("utf-8")
                dict_content.extend(
                    len(value_bytes).to_bytes(4, byteorder="little"))
                dict_content.extend(value_bytes)
            else:
                dict_content.extend(struct.pack(get_format(data_type), value))
        with open(filepath + ".dic_dict", "wb") as dict_file:
            dict_file.write(dict_content)

        encoded_content = bytearray()
        for index in encoded_data:
            encoded_content.extend(index.to_bytes(4, byteorder="little"))
        with open(filepath, "wb") as f:
            f.write(encoded_content)

    elif compression_type == "for":
        min_val, encoded_data = encode_for(data)
        with open(filepath + ".for_min", "wb") as min_file:
            min_file.write(struct.pack(get_format(data_type), min_val))
        write_bin(filepath, encoded_data, get_format(data_type))

    elif compression_type == "dif":
        encoded_data = encode_dif(data)
        write_bin(filepath, encoded_data, get_format(data_type))


def read_compressed(filepath, compression_type, data_type):

    if compression_type == "bin":
        format_str = get_format(data_type)
        return read_bin(filepath, format_str, data_type)

    elif compression_type == "rle":
        format_str = get_format(data_type)
        size = struct.calcsize(format_str)
        data = []
        with open(filepath, "rb") as f:
            while True:
                if data_type == "string":
                    length_data = f.read(4)
                    if not length_data:
                        break
                    length = struct.unpack("I", length_data)[0]
                    value = f.read(length).decode('utf-8')
                else:
                    value_data = f.read(size)
                    if not value_data:
                        break
                    value = struct.unpack(format_str, value_data)[0]
                count = struct.unpack("I", f.read(4))[0]
                data.append((value, count))
        return list(decode_rle(data))  # decode_rle(data)

    elif compression_type == "dic":
        dictionary = []
        format_str = get_format(data_type)
        size = struct.calcsize(format_str)
        with open(filepath + ".dic_dict", "rb") as dict_file:
            while True:
                if data_type == "string":
                    length_data = dict_file.read(4)
                    if not length_data:
                        break
                    length = struct.unpack("I", length_data)[0]
                    value = dict_file.read(length).decode('utf-8')
                    dictionary.append(value)
                else:
                    value_data = dict_file.read(struct.calcsize(format_str))
                    if not value_data:
                        break
                    dictionary.append(struct.unpack(format_str, value_data)[0])
        encoded_data = []
        with open(filepath, "rb") as f:
            while chunk := f.read(4):
                encoded_data.append(struct.unpack("I", chunk)[0])
        return decode_dic(dictionary, encoded_data)

    elif compression_type == "for":
        with open(filepath + ".for_min", "rb") as min_file:
            min_val = struct.unpack(get_format(data_type), min_file.read())[0]
        return decode_for(min_val, read_bin(filepath, get_format(data_type), data_type))

    elif compression_type == "dif":
        return decode_dif(read_bin(filepath, get_format(data_type), data_type))


def main():
    if len(sys.argv) != 5:
        print("Usage: program.py <en|de> <compression_type> <data_type> <file_path>")
        sys.exit(1)

    mode, compression_type, data_type, file_path = sys.argv[1:5]

    if compression_type not in ["bin", "rle", "dic", "for", "dif"]:
        print("Invalid compression type.")
        sys.exit(1)

    if data_type not in ["int8", "int16", "int32", "int64", "string"]:
        print("Invalid data type.")
        sys.exit(1)

    if compression_type in ["bin", "for", "dif"] and not data_type.startswith("int"):
        print(
            f"Error: '{compression_type}' encoding only supports integer types.")
        sys.exit(1)

    if mode == "en":
        data = read_csv(file_path, data_type)
        output_file = file_path + "." + compression_type
        write_compressed(output_file, data, compression_type, data_type)
        print(f"Encoded data saved to {output_file}")

    elif mode == "de":
        decoded_data = read_compressed(file_path, compression_type, data_type)
        for item in decoded_data:
            print(item)

    else:
        print("Invalid mode. Use 'en' for encoding or 'de' for decoding.")
        sys.exit(1)


if __name__ == "__main__":
    main()
