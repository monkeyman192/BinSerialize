from BinSerialize import BinSerialize, dtype

d = dtype()


class main(BinSerialize):
    def __init__(self):
        BinSerialize.__init__(self)

        self._fs = d.filesize
        self._x = d.pointer(d.array(d.int32, 2))
        self._y = d.switch(d.int32,
                           {1: d.array(d.float32, 3),
                            2: d.array(d.float32, 2)})


if __name__ == "__main__":
    m = main()
    m.deserialize('file.bin')

    print(m.fs)
    print(m.x)
    print(m.y)
    m.y[1] = 3.555
    print(m.y)
    print(type(m.y))
    print(m.y.value)

    m.serialize('file2.bin')
