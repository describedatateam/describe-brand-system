"""
python -m describe_charts fonts             download the brand faces (once per machine)
python -m describe_charts fonts --install   ...and install them for Chrome / Plotly export
python -m describe_charts styles            regenerate styles/*.mplstyle from tokens.json
"""
import sys

from . import fonts

if __name__ == "__main__":
    args = sys.argv[1:]
    if args[:1] == ["fonts"]:
        got = fonts.download()
        print("\n".join(got))
        if "--install" in args:
            print("installed to", fonts.install_user(got))
    elif args[:1] == ["styles"]:
        from . import mpl
        print("\n".join(mpl.write_styles()))
    else:
        print(__doc__)
