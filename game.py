from hacktools import common

binranges = [(0x8753c, 0xa3930)]
freeranges = [(0x87b6c, 0x08811a)]
wordwrap = 180
wordwrap2 = 240


class ScenarioPart:
    num = 0
    unk1 = 0
    unk2 = 0
    strings = []


class ScenarioString:
    unk1 = 0
    index = 0
    pointer = 0
    offset = 0
    sjis = ""


def readScenario(file):
    parts = []
    with common.Stream(file, "rb") as f:
        partnum = f.readUInt()
        for i in range(partnum):
            part = ScenarioPart()
            part.num = f.readUInt()
            part.unk1 = f.readUInt()
            part.unk2 = f.readUInt()
            part.strings = []
            # common.logDebug("part", i, common.toHex(f.tell()), vars(part))
            parts.append(part)
        for part in parts:
            for j in range(part.num):
                string = ScenarioString()
                string.unk1 = f.readInt()
                string.index = f.readUInt()
                f.seek(4, 1)  # Always 0xffffffff
                string.pointer = f.readUInt()
                string.part = j
                part.strings.append(string)
                # common.logDebug("string", j, common.toHex(f.tell()), vars(string))
        for part in parts:
            for string in part.strings:
                f.seek(string.pointer)
                string.offset = f.readUInt()
                f.seek(string.offset)
                string.sjis = readShiftJIS(f)
                # common.logDebug(common.toHex(f.tell()), vars(string))
    return parts


def convertXAPName(file, type):
    # "GCN0" = ".NCGR", "ECN0" = ".NCER", etc
    type = "." + (type[:3])[::-1] + "R"
    file = file.replace("_a.", ".").replace("_g.", ".")
    return file.replace(".xap", type)


def readShiftJIS(f, encoding="shift_jis"):
    sjis = ""
    while True:
        b1 = f.readByte()
        if b1 == 0x02:
            sjis += f.read(2).decode(encoding).replace("〜", "～")
        elif b1 == 0x0A:
            sjis += "|"
        elif b1 == 0x00:
            break
        elif b1 >= 0x20 and b1 <= 0x7e:
            sjis += chr(b1)
        else:
            if b1 == 0x03:
                color = f.readByte()
                sjis += "<col" + chr(color) + ">"
            else:
                if b1 != 0x1F:
                    common.logWarning("Unknown control code", common.toHex(b1))
                sjis += "<" + common.toHex(b1) + ">"
    return sjis


def writeShiftJIS(f, s, encoding="shift_jis"):
    s = s.replace("～", "〜")
    x = 0
    while x < len(s):
        c = s[x]
        if c == "|":
            f.writeByte(0x0A)
        elif c == "<" and s[x:x+4] == "<col":
            f.writeByte(0x03)
            f.writeByte(ord(s[x+4]))
            x += 5
        elif c == "<" and x < len(s) - 3 and s[x+3] == ">":
            code = s[x+1] + s[x+2]
            f.write(bytes.fromhex(code))
            x += 3
        elif ord(c) < 128:
            f.writeByte(ord(c))
        else:
            f.writeByte(0x02)
            f.write(c.encode(encoding))
        x += 1
    f.writeByte(0x00)


def detectTextCode(s, i=0):
    if s[i] == "<":
        return len(s[i:].split(">", 1)[0]) + 1
    return 0
