import codecs
import os
import game
from hacktools import common, nitro


def run():
    infolder = "data/extract/data/data/scenario/"
    outfolder = "data/repack/data/data/scenario/"
    infile = "data/scenario_input.txt"
    fontfile = "data/replace/data/data/font/font.nftr"
    chartot = transtot = 0

    if not os.path.isfile(infile):
        common.logError("Input file", infile, "not found")
        return

    common.copyFolder(infolder, outfolder)
    common.logMessage("Repacking SCE from", infile, "...")
    # Read the glyph size from the font
    if not os.path.isfile(fontfile):
        fontfile = fontfile.replace("replace/", "extract/")
    glyphs = nitro.readNFTR(fontfile).glyphs
    # Set glyph % to an arbitrary width, since it's used to replace character names
    glyphs["%"].length = 60
    with codecs.open(infile, "r", "utf-8") as script:
        files = common.getFiles(infolder, ".bin")
        for file in common.showProgress(files):
            section = common.getSection(script, file)
            if len(section) == 0:
                common.copyFile(infolder + file, outfolder + file)
                continue
            chartot, transtot = common.getSectionPercentage(section, chartot, transtot)
            # Repack the file
            common.logDebug("Processing", file, "...")
            parts = game.readScenario(infolder + file)
            with common.Stream(outfolder + file, "wb") as f:
                # Write the parts and string data
                f.writeUInt(len(parts))
                for part in parts:
                    f.writeUInt(part.num)
                    f.writeUInt(part.unk1)
                    f.writeUInt(part.unk2)
                for part in parts:
                    for string in part.strings:
                        f.writeInt(string.unk1)
                        f.writeUInt(string.index)
                        f.writeUInt(string.unk2)
                        string.pointeroff = f.tell()
                        f.writeUInt(0)
                addedstrings = {}
                for part in parts:
                    # Order the strings by offset and write the new strings
                    for string in part.strings:
                        sjis = string.sjis
                        add1f = False
                        if sjis.endswith("<1f>"):
                            sjis = sjis[:-4]
                            add1f = True
                        newsjis = ""
                        if sjis in section:
                            newsjis = section[sjis].pop(0)
                            if len(section[sjis]) == 0:
                                del section[sjis]
                        if newsjis != "":
                            if newsjis == "!":
                                newsjis = ""
                            if file == "scenario2.bin" and "|" not in newsjis:
                                tryfit = common.wordwrap(newsjis, glyphs, game.wordwrapkira1, game.detectTextCode)
                                if tryfit.count("|") > 0:
                                    tryfit = common.wordwrap(newsjis, glyphs, game.wordwrapkira2, game.detectTextCode)
                                    if tryfit.count("|") > 1:
                                        tryfit = common.wordwrap(newsjis, glyphs, game.wordwrapkira3, game.detectTextCode)
                                        if tryfit.count("|") > 1:
                                            common.logError("Line too long", tryfit)
                                newsjis = tryfit
                            elif newsjis.startswith("<<"):
                                newsjis = common.wordwrap(newsjis[2:], glyphs, game.wordwrapfull, game.detectTextCode)
                                newsjis = common.centerLines("<<" + newsjis.replace("|", "|<<"), glyphs, game.wordwrapfull, game.detectTextCode)
                            else:
                                newsjis = common.wordwrap(newsjis, glyphs, game.wordwrap, game.detectTextCode)
                        else:
                            newsjis = sjis
                        if add1f:
                            newsjis += "<1f>"
                        if newsjis in addedstrings:
                            string.sjisoff = addedstrings[newsjis]
                        else:
                            string.sjisoff = f.tell()
                            game.writeShiftJIS(f, newsjis)
                            addedstrings[newsjis] = string.sjisoff
                    f.writeUInt(0)
                    f.writeZero(16 - (f.tell() % 16))
                    # Write the new pointers
                    for string in part.strings:
                        ptroff = f.tell()
                        f.writeUInt(string.sjisoff)
                        f.seek(string.pointeroff)
                        f.writeUInt(ptroff)
                        f.seek(ptroff + 4)
                f.writeZero(16 - (f.tell() % 16))
    common.logMessage("Done! Translation is at {0:.2f}%".format((100 * transtot) / chartot))
