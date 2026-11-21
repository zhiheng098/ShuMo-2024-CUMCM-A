"""把 src.py（单元以 `# %%` 分隔）转换为 Notebook 文件。"""
import re
from pathlib import Path

import nbformat as nbf

HERE = Path(__file__).resolve().parent
SRC = HERE / "src.py"
DST = HERE / "A题_求解.ipynb"


def main():
    lines = SRC.read_text(encoding="utf-8").splitlines()
    cells = []
    kind = "code"
    buf = []

    def flush():
        if not buf:
            return
        text = "\n".join(buf).strip("\n")
        if not text.strip():
            return
        if kind == "markdown":
            out = []
            for ln in text.splitlines():
                if ln.startswith("# "):
                    out.append(ln[2:])
                elif ln.strip() == "#":
                    out.append("")
                elif ln.startswith("#"):
                    out.append(ln[1:].lstrip())
                else:
                    out.append(ln)
            cells.append(nbf.v4.new_markdown_cell("\n".join(out)))
        else:
            cells.append(nbf.v4.new_code_cell(text))

    for ln in lines:
        if re.match(r"^# %%.*", ln):
            flush()
            kind = "markdown" if "[markdown]" in ln else "code"
            buf = []
        else:
            buf.append(ln)
    flush()

    nb = nbf.v4.new_notebook()
    nb.cells = cells
    nb.metadata = {
        "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
        "language_info": {"name": "python", "version": "3.14.4"},
    }
    nbf.write(nb, DST)
    print("已生成 %s（%d 个单元，其中代码单元 %d 个）"
          % (DST, len(cells), sum(1 for c in cells if c.cell_type == "code")))


if __name__ == "__main__":
    main()
