import builtins
from zex import fs, xdict

_safe_bultins = None


def load_safe_bultins():
    global _safe_bultins

    if _safe_bultins is None:
        lst = []
        with open(f"{fs.dirname(__file__)}/safe_builtins") as f:
            for line in f:
                if line.strip() == "":
                    continue
                if line.startswith("#"):
                    continue
                lst.append(line.strip().split("#")[0])
        _safe_bultins = xdict.pick_attrs(builtins, lst)

    return {**_safe_bultins}
