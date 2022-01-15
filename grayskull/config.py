from dataclasses import dataclass, field
from typing import Dict, List, Tuple

from grayskull.utils import PyVer


@dataclass
class Configuration:
    name: str
    version: str = ""
    files_to_copy: List = field(default_factory=list)
    supported_py: List[PyVer] = field(
        default_factory=lambda: [
            PyVer(2, 7),
            PyVer(3, 6),
            PyVer(3, 7),
            PyVer(3, 8),
            PyVer(3, 9),
            PyVer(3, 10),
        ]
    )
    py_cf_supported: List[PyVer] = field(
        default_factory=lambda: [
            PyVer(3, 6),
            PyVer(3, 7),
            PyVer(3, 8),
            PyVer(3, 9),
            PyVer(3, 10),
        ]
    )
    is_strict_cf: bool = False
    pkg_need_c_compiler: Tuple = field(default_factory=lambda: ("cython",))
    pkg_need_cxx_compiler: Tuple = field(default_factory=lambda: ("pybind11",))
    url_pypi_metadata: str = "https://pypi.org/pypi/{pkg_name}/json"
    download: bool = False
    is_arch: bool = False

    def get_oldest_py3_version(self, list_py_ver: List[PyVer]) -> PyVer:
        list_py_ver = sorted(list_py_ver)
        min_python_version = (
            self.py_cf_supported[0] if self.is_strict_cf else PyVer(3, 0)
        )
        for py_ver in list_py_ver:
            if py_ver >= min_python_version:
                return py_ver
        return min_python_version

    def get_py_version_available(
        self, req_python: List[Tuple[str, str, str]]
    ) -> Dict[PyVer, bool]:
        """Get the python version available given the requires python received

        :param req_python: Requires python
        :return: Dict of Python versions if it is enabled or disabled
        """
        sup_python_ver = set(
            self.py_cf_supported if self.is_strict_cf else self.supported_py
        )
        sup_python_ver.update(
            {
                PyVer(int(major), int(minor or 0))
                for _, major, minor in req_python
                if major
            }
        )
        sup_python_ver = sorted(list(sup_python_ver))
        if self.is_strict_cf:
            py_ver_enabled = {
                py_ver: py_ver in self.py_cf_supported for py_ver in sup_python_ver
            }
        else:
            py_ver_enabled = {py_ver: True for py_ver in sup_python_ver}
        for op, major, minor in req_python:
            if not minor:
                minor = 0
            for sup_py, is_enabled in py_ver_enabled.items():
                if is_enabled is False:
                    continue
                py_ver_enabled[sup_py] = eval(
                    f"sup_py {op} PyVer(int({major}), int({minor}))"
                )
        return py_ver_enabled