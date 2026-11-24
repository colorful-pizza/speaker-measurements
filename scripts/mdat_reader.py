#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Minimal reader for REW ``.mdat`` files.

An ``.mdat`` file is a Java Object Serialization stream (magic ``AC ED 00 05``)
written by Room EQ Wizard.  A single-measurement file holds one
``roomeqwizard.MeasData`` object; a "save all measurements" file holds several.
This module walks the stream just far enough to pull out the measurement
objects and their fields -- no Java required.

Usage:
    from mdat_reader import load_measurements
    for meas in load_measurements("file.mdat"):
        meas["freqs"], meas["spl"], meas["thd_pct"]
"""

import struct
import numpy as np

# --- stream token bytes -----------------------------------------------------
TC_NULL = 0x70
TC_REFERENCE = 0x71
TC_CLASSDESC = 0x72
TC_OBJECT = 0x73
TC_STRING = 0x74
TC_ARRAY = 0x75
TC_CLASS = 0x76
TC_BLOCKDATA = 0x77
TC_ENDBLOCKDATA = 0x78
TC_RESET = 0x79
TC_BLOCKDATALONG = 0x7A
TC_EXCEPTION = 0x7B
TC_LONGSTRING = 0x7C
TC_PROXYCLASSDESC = 0x7D
TC_ENUM = 0x7E

BASE_HANDLE = 0x7E0000


class JObj:
    __slots__ = ("cls", "fields")

    def __init__(self, cls):
        self.cls = cls
        self.fields = {}

    def __repr__(self):
        return "<%s>" % self.cls


class JArray:
    __slots__ = ("desc", "data")

    def __init__(self, desc, data):
        self.desc = desc
        self.data = data

    def __len__(self):
        return len(self.data) if self.data is not None else 0

    def __repr__(self):
        return "<array %s len=%d>" % (self.desc, len(self))


class JClassDesc:
    __slots__ = ("name", "fluidd", "flags", "fields", "super")

    def __init__(self):
        self.name = None
        self.flags = 0
        self.fields = []
        self.super = None

    def __repr__(self):
        return "<classdesc %s>" % self.name


class EnumVal:
    __slots__ = ("cls", "name")

    def __init__(self, cls, name):
        self.cls = cls
        self.name = name

    def __repr__(self):
        return "%s.%s" % (self.cls, self.name)


class JavaStreamParser:
    def __init__(self, data):
        self.d = data
        self.p = 0
        self.handles = {}

    # -- primitives ---------------------------------------------------------
    def u1(self):
        v = self.d[self.p]
        self.p += 1
        return v

    def u2(self):
        v = struct.unpack_from(">H", self.d, self.p)[0]
        self.p += 2
        return v

    def s2(self):
        v = struct.unpack_from(">h", self.d, self.p)[0]
        self.p += 2
        return v

    def s4(self):
        v = struct.unpack_from(">i", self.d, self.p)[0]
        self.p += 4
        return v

    def s8(self):
        v = struct.unpack_from(">q", self.d, self.p)[0]
        self.p += 8
        return v

    def f4(self):
        v = struct.unpack_from(">f", self.d, self.p)[0]
        self.p += 4
        return v

    def f8(self):
        v = struct.unpack_from(">d", self.d, self.p)[0]
        self.p += 8
        return v

    def utf(self):
        n = self.u2()
        raw = self.d[self.p:self.p + n]
        self.p += n
        return decode_mutf8(raw)

    def utf_long(self):
        n = self.s8()
        raw = self.d[self.p:self.p + n]
        self.p += n
        return decode_mutf8(raw)

    def new_handle(self, obj):
        self.handles[BASE_HANDLE + len(self.handles)] = obj

    # -- structure ----------------------------------------------------------
    def parse(self):
        magic = self.u2()
        version = self.u2()
        if magic != 0xACED:
            raise ValueError("not a Java serialization stream")
        if version != 5:
            raise ValueError("unsupported stream version %d" % version)

    def content(self):
        return self.read_by_tc(self.u1())

    def read_by_tc(self, tc):
        if tc == TC_NULL:
            return None
        if tc == TC_REFERENCE:
            return self.handles.get(self.s4())
        if tc == TC_STRING:
            s = self.utf()
            self.new_handle(s)
            return s
        if tc == TC_LONGSTRING:
            s = self.utf_long()
            self.new_handle(s)
            return s
        if tc == TC_OBJECT:
            return self.read_object()
        if tc == TC_ARRAY:
            return self.read_array()
        if tc == TC_CLASSDESC:
            return self.read_classdesc(proxy=False)
        if tc == TC_PROXYCLASSDESC:
            return self.read_classdesc(proxy=True)
        if tc == TC_CLASS:
            cd = self.content()
            self.new_handle(cd)
            return cd
        if tc == TC_ENUM:
            return self.read_enum()
        if tc == TC_BLOCKDATA:
            n = self.u1()
            self.p += n
            return None
        if tc == TC_BLOCKDATALONG:
            n = self.s4()
            self.p += n
            return None
        if tc == TC_RESET:
            self.handles.clear()
            return None
        if tc == TC_EXCEPTION:
            self.content()
            return None
        if tc == TC_ENDBLOCKDATA:
            return None
        raise ValueError("unknown token 0x%02x at offset %d" % (tc, self.p - 1))

    def read_classdesc(self, proxy):
        cd = JClassDesc()
        self.new_handle(cd)
        if proxy:
            for _ in range(self.s4()):
                self.utf()
            cd.name = "PROXY"
        else:
            cd.name = self.utf()
            self.s8()                      # serialVersionUID
            cd.flags = self.u1()
            for _ in range(self.u2()):
                t = chr(self.u1())
                fn = self.utf()
                # object/array fields carry a type-signature string
                if t in ("L", "["):
                    self.content()
                cd.fields.append((t, fn))
        while self.u1() != TC_ENDBLOCKDATA:   # classAnnotation
            self.p -= 1
            self.read_by_tc(self.u1())
        sup = self.content()
        cd.super = sup if isinstance(sup, JClassDesc) else None
        return cd

    def read_object(self):
        cd = self.content()
        obj = JObj(cd.name if isinstance(cd, JClassDesc) else "?")
        self.new_handle(obj)
        if not isinstance(cd, JClassDesc):
            return obj
        chain = []
        c = cd
        while c is not None:
            chain.append(c)
            c = c.super
        fields = []
        for c in reversed(chain):
            fields.extend(c.fields)
        for t, fn in fields:
            obj.fields[fn] = self.read_value(t)
        for c in reversed(chain):
            if c.flags & 0x01 or (c.flags & 0x04 and c.flags & 0x08):
                while self.u1() != TC_ENDBLOCKDATA:
                    self.p -= 1
                    self.read_by_tc(self.u1())
        return obj

    def read_value(self, t):
        if t == "B":
            v = self.u1()
            return v - 256 if v > 127 else v
        if t == "C":
            return chr(self.u2())
        if t == "D":
            return self.f8()
        if t == "F":
            return self.f4()
        if t == "I":
            return self.s4()
        if t == "J":
            return self.s8()
        if t == "S":
            return self.s2()
        if t == "Z":
            return bool(self.u1())
        if t in ("L", "["):
            return self.content()
        raise ValueError("bad field type %r" % t)

    def read_array(self):
        cd = self.content()
        desc = cd.name if isinstance(cd, JClassDesc) else "?"
        arr = JArray(desc, None)
        self.new_handle(arr)
        n = self.s4()
        t = desc[1] if desc.startswith("[") else "L"
        p = self.p
        if t == "F":
            arr.data = np.frombuffer(self.d, dtype=">f4", count=n, offset=p).astype(float)
            self.p += 4 * n
        elif t == "D":
            arr.data = np.frombuffer(self.d, dtype=">f8", count=n, offset=p).astype(float)
            self.p += 8 * n
        elif t == "I":
            arr.data = np.frombuffer(self.d, dtype=">i4", count=n, offset=p)
            self.p += 4 * n
        elif t == "J":
            arr.data = np.frombuffer(self.d, dtype=">i8", count=n, offset=p)
            self.p += 8 * n
        elif t == "S":
            arr.data = np.frombuffer(self.d, dtype=">i2", count=n, offset=p)
            self.p += 2 * n
        elif t == "B":
            arr.data = self.d[p:p + n]
            self.p += n
        elif t == "Z":
            arr.data = np.frombuffer(self.d, dtype="u1", count=n, offset=p).astype(bool)
            self.p += n
        elif t == "C":
            arr.data = np.frombuffer(self.d, dtype=">u2", count=n, offset=p)
            self.p += 2 * n
        else:
            arr.data = [self.content() for _ in range(n)]
        return arr

    def read_enum(self):
        cd = self.content()
        self.new_handle(cd)
        name = self.content()
        return EnumVal(cd.name if isinstance(cd, JClassDesc) else "?", name)


def decode_mutf8(raw):
    return raw.replace(b"\xc0\x80", b"\x00").decode("utf-8", "replace")


def _val(x, default=None):
    if isinstance(x, JObj) and "value" in x.fields:
        return x.fields["value"]
    return default if x is None else x


def load_measurements(path):
    """Return a list of measurement dicts found in an .mdat file."""
    data = open(path, "rb").read()
    p = JavaStreamParser(data)
    p.parse()
    items = []
    while p.p < len(data):
        items.append(p.content())

    out = []
    for obj in items:
        if not (isinstance(obj, JObj) and obj.cls.endswith("MeasData")):
            continue
        F = obj.fields
        n = len(F["splValues"])
        freqs = F["startFreq"] + F["freqStep"] * np.arange(n)

        d = F.get("distortionData")
        dfields = d.fields if isinstance(d, JObj) else {}
        harm = dfields.get("harmData")
        if isinstance(harm, JArray) and isinstance(harm.data[0], JArray):
            harm = np.array([np.asarray(a.data, float) for a in harm.data])
            harm_freqs = np.asarray(dfields["freqs"].data, float)
            rel = harm[2:] - harm[1]                      # H2..H9 re fundamental
            thd = 10 * np.log10((10 ** (rel / 10)).sum(axis=0))
            thd_pct = 100 * 10 ** (thd / 20)
        else:
            harm = thd = thd_pct = None
            harm_freqs = None

        ir = F.get("irData")
        ir = ir.fields if isinstance(ir, JObj) else {}

        out.append(dict(
            name=F.get("shortDesc", ""),
            measurement_date=F.get("sourceFileDate"),
            start_freq=float(F["startFreq"]),
            step=float(F["freqStep"]),
            freqs=freqs,
            spl=np.asarray(F["splValues"].data, float),
            phase=np.asarray(F["phaseValues"].data, float),
            spl_offset=_val(F.get("splCalOffset")),
            sample_rate=F.get("sampleRate"),
            sweep_format=F.get("sourceFileFormat"),
            output_name=F.get("outputName"),
            rew_version="%s%s" % (_val(F.get("rewVersion")), F.get("versionSt", "")),
            snr_db=_val(ir.get("signalToNoisedB")),
            sdr_db=_val(ir.get("signalToDistdB")),
            thd_freqs=harm_freqs,
            thd_pct=thd_pct,
            harmonics=harm,
        ))
    return out


if __name__ == "__main__":
    import sys
    for f in sys.argv[1:]:
        for m in load_measurements(f):
            print("%-24s %6d pts  %.3f-%.0f Hz  SPL@1k=%.1f"
                  % (m["name"], len(m["freqs"]), m["freqs"][0], m["freqs"][-1],
                     np.interp(1000, m["freqs"], m["spl"])))
