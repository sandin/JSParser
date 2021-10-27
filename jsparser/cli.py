import argparse
import os
from . import parser
from . import codegen


def main():
    argparser = argparse.ArgumentParser()
    argparser.add_argument("input", help="input file(*.js)")
    argparser.add_argument("output", help="output file(*.py)")
    args = argparser.parse_args()

    if not os.path.exists(args.input):
        print("input file %s is not exists!" % args.input)

    ctx = { "globals": [], "functions": [] }
    with open(args.input, "r") as f:
        parser.parse_code_to_ast(f.read(), ctx)

    code = codegen.generate_python_code(ctx)
    print(code)
    with open(args.output, "w") as f:
        f.write(code)
    print("Success write code into output file %s" % args.output)


if __name__ == "__main__":
    main()