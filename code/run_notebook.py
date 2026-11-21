"""执行 Notebook 并把输出（stdout / 图）回写到 .ipynb 文件。

用法（可在任意目录运行）:
    py -3.14 run_notebook.py                # 默认执行脚本同目录下的 A题_求解.ipynb
    py -3.14 run_notebook.py "其他.ipynb"    # 相对路径先按当前目录、再按脚本目录解析
"""
import sys
import time
from pathlib import Path

import nbformat
from nbclient import NotebookClient
from nbclient.exceptions import CellExecutionError

HERE = Path(__file__).resolve().parent
DEFAULT = "A题_求解.ipynb"


def resolve(path):
    """相对路径先以当前工作目录为基准，找不到再以脚本所在目录为基准。"""
    p = Path(path).expanduser()
    cands = [p] if p.is_absolute() else [Path.cwd() / p, HERE / p]
    for c in cands:
        if c.is_file():
            return c.resolve()
    raise FileNotFoundError("找不到 Notebook 文件，已尝试：\n  " + "\n  ".join(str(c) for c in cands))


def main(path):
    p = resolve(path)
    nb = nbformat.read(str(p), as_version=4)
    client = NotebookClient(
        nb,
        timeout=3600,
        kernel_name="python3",
        resources={"metadata": {"path": str(p.parent)}},
        allow_errors=False,
    )
    t0 = time.time()
    print("执行 %s（工作目录 %s）" % (p, p.parent))
    try:
        client.execute()
    except CellExecutionError as e:
        nbformat.write(nb, str(p))
        print("执行失败（已保存部分输出）：\n%s" % e)
        return 1
    nbformat.write(nb, str(p))
    n_ok = sum(1 for c in nb.cells if c.cell_type == "code" and c.get("outputs"))
    print("执行成功，用时 %.1f s；%d 个代码单元产生输出；已回写 %s" % (time.time() - t0, n_ok, p))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else DEFAULT))
