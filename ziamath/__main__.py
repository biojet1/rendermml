import argparse

parser = argparse.ArgumentParser(description="Process some integers.")

parser.add_argument("src", metavar="INPUT", default=None, help="source file")

parser.add_argument(
    "-o", dest="dest", metavar="OUTPUT", default=None, help="destination file"
)

parser.add_argument(
    "--cache",
    dest="cache",
    action="store_true",
    default=None,
    help="reference identical glyph",
)

parser.add_argument(
    "--no-cache",
    dest="cache",
    action="store_false",
    help="identical glyph duplicated",
)

parser.add_argument(
    "--latex",
    "-l",
    dest="latex",
    action="count",
    default=0,
    help="input is latex",
)

parser.add_argument(
    "--precision",
    "-p",
    dest="precision",
    type=int,
    default=None,
    help="decimal precision to use in SVG path coordinates",
)

parser.add_argument(
    "--size",
    "-s",
    dest="size",
    type=int,
    default=None,
    help="font size to use in pixels",
)

parser.add_argument(
    "--font",
    "-f",
    default=None,
    dest="font_file",
    help="font file, must contain MATH typesetting table",
)

parser.add_argument(
    "--defs",
    action="store_true",
    default=None,
    help="Put symbols inside defs",
)

parser.add_argument(
    "--group",
    action="store_true",
    default=None,
    help="use group per node",
)

parser.add_argument(
    "--data_text",
    action="store_true",
    default=None,
    help="add data-text attribute",
)

parser.add_argument(
    "--attr_id",
    action="store_true",
    default=None,
    help="pass id attribute",
)

parser.add_argument(
    "--attr_data",
    action="store_true",
    default=None,
    help="pass data-* attribute",
)


def as_source(path, mode="rb"):
    if path and path != "-":
        return open(path, mode)
    from sys import stdin

    return stdin.buffer if "b" in mode else stdin


def as_sink(path, mode="wb"):
    if path and path != "-":
        return open(path, mode)
    from sys import stdout

    return stdout.buffer if "b" in mode else stdout


args = parser.parse_args()

from xml.etree import ElementTree as ET

################

kwopt = {}

if args.size is not None:
    kwopt["size"] = args.size

if args.cache is not None:
    kwopt["svg2"] = args.cache

if args.precision is not None:
    from .zmath import set_precision

    set_precision(args.precision)

if args.font_file is not None:
    kwopt["font"] = args.font_file

################

opt = {"use_group": args.group, "data_text": args.data_text}

if args.attr_id:
    opt["pass_id_attr"] = True

if args.attr_data:
    opt["pass_data_attr"] = True


################

with as_source(args.src) as src:
    from .zmath import Math

    if args.latex > 1:
        mml = Math.fromlatextext(src.read().decode("UTF-8").strip(), **kwopt)
        svg = mml.svgxml(opt)
    elif args.latex > 0:
        mml = Math.fromlatex(src.read().decode("UTF-8").strip(), **kwopt)
        svg = mml.svgxml(opt)
    else:
        mml = ET.parse(src)
        mmr = Math(mml.getroot(), **kwopt)
        svg = mmr.svgxml(opt)
    if args.defs:
        defs = None
        for psym in [svg, *svg.findall(".//*[symbol]")]:
            for symbol in list(psym.findall("symbol")):
                if not defs:
                    defs = ET.SubElement(svg, "defs")
                psym.remove(symbol)
                defs.append(symbol)

    with as_sink(args.dest, "wb") as w:
        etr = ET.ElementTree(svg)
        etr.write(w)
