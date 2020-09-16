# Copyright 2019 The FastEstimator Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================
from typing import Optional, Union, Any

from pylatex import NoEscape, Package, escape_latex
from pylatex.base_classes import Container, Environment, LatexObject, Options
from pylatex.lists import Enumerate
from pylatex.utils import bold, dumps_list

from fastestimator.util.util import FEID


class ContainerList(Container):
    """A class to expedite combining pieces of latex together.

    This class is intentionally not @traceable.
    """
    def dumps(self) -> str:
        """Get a string representation of this container.

        Returns:
            A string representation of itself.
        """
        return self.dumps_content()


class PyContainer(ContainerList):
    """A class to convert python containers to a LaTeX representation.

    This class is intentionally not @traceable.

    Args:
        data: The python object to be converted to LaTeX.
        truncate: How many values to display before truncating with an ellipsis. This should be a positive integer or
            None to disable truncation.
    """
    def __init__(self, data: Union[list, tuple, set, dict], truncate: Optional[int] = None):
        self.packages.add(Package('enumitem', options='inline'))
        assert isinstance(data, (list, tuple, set, dict)), f"Unacceptable data type for PyContainer: {type(data)}"
        open_char = '[' if isinstance(data, list) else '(' if isinstance(data, tuple) else r'\{'
        close_char = ']' if isinstance(data, list) else ')' if isinstance(data, tuple) else r'\}'
        ltx = Enumerate(options=Options(NoEscape('label={}'), NoEscape('itemjoin={,}')))
        ltx._star_latex_name = True  # Converts this to an inline list
        self.raw_input = data
        if isinstance(data, dict):
            for key, val in list(data.items())[:truncate]:
                ltx.add_item(ContainerList(data=[key, ": ", val]))
        else:
            for val in list(data)[:truncate]:
                ltx.add_item(val)
        if truncate and len(data) > truncate:
            ltx.add_item(NoEscape(r'\ldots'))
        super().__init__(data=[NoEscape(open_char), ltx, NoEscape(close_char)])


class Verbatim(Environment):
    """A class to put a string inside the latex verbatim environment.

    This class is intentionally not @traceable.

    Args:
        data: The string to be wrapped.
    """
    def __init__(self, data: str):
        super().__init__(options=None, arguments=None, start_arguments=None, data=NoEscape(data))
        self.content_separator = '\n'


class Center(Environment):
    """A class to center content in a page.

    This class is intentionally not @traceable.
    """
    pass


class AdjustBox(Environment):
    """A class to adjust the size of boxes.

    This class is intentionally not @traceable.
    """
    packages = [Package('adjustbox')]


class HrefFEID(ContainerList):
    """A class to represent a colored and underlined hyperref based on a given fe_id.

    This class is intentionally not @traceable.

    Args:
        fe_id: The id used to link this hyperref.
        name: A string suffix to be printed as part of the link text.
        link_prefix: The prefix for the hyperlink.
        id_in_name: Whether to include the id in front of the name text.
        bold_name: Whether to bold the name.
    """
    def __init__(self,
                 fe_id: FEID,
                 name: str,
                 link_prefix: str = 'tbl',
                 id_in_name: bool = True,
                 bold_name: bool = False):
        self.content_separator = ''
        self.packages.add(Package('hyperref', options='hidelinks'))
        self.packages.add(Package('ulem'))
        self.packages.add(Package('xcolor', options='table'))
        self.fe_id = fe_id
        self.name = name
        data = [
            NoEscape(r'\hyperref['), escape_latex(f"{link_prefix}:"), fe_id, NoEscape(r']{\textcolor{blue}{\uline{')
        ]
        if id_in_name:
            data.append(fe_id)
            if name:
                data.append(": ")
        if name:
            data.append(bold(escape_latex(name)) if bold_name else escape_latex(name))
        data.append(NoEscape("}}}"))
        super().__init__(data=data)


class IterJoin(Container):
    """A class to convert an iterable to a latex representation.

    The data of this class can be any type. Usually it is iterable due to its capability to setup interval string.

    Args:
        data: Data of the cell.
        token: String to be added in the interval of data entries.
    """
    def __init__(self, data: Any, token: str):
        super().__init__(data=data)
        self.token = token

    def dumps(self) -> str:
        """Get a string representation of this cell.

        Returns:
            A string representation of itself.
        """
        return dumps_list(self, token=self.token)


class WrapText(LatexObject):
    """A class to convert strings or numbers to wrappable latex representation.

    This class will first convert the data to string, and then to wrappable latex representation if its length is too
    long. This is to fix the issue that first string or number is not wrappable in X column type.

    Args:
        data: Input data to be converted.
        threshold: When the length of <data> is greater than <threshold>, the resulting string will be made wrappable
    """
    def __init__(self, data: Union[str, int, float], threshold: int):
        assert isinstance(data, (str, int, float)), "the self.data type needs to be str, int, float"
        self.threshold = threshold
        self.data = str(data)
        super().__init__()

    def dumps(self) -> str:
        """Get a string representation of this cell.

        Returns:
            A string representation of itself.
        """
        if len(self.data) > self.threshold:
            return NoEscape(r'\seqsplit{' + escape_latex(self.data) + '}')
        else:
            return escape_latex(self.data)
