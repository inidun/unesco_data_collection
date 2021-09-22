import os
from pathlib import Path
from typing import List, Optional, Union

import argh
from jinja2 import Environment, PackageLoader, Template, select_autoescape
from tqdm import tqdm

from courier.utils import cdata, get_courier_ids, valid_xml

jinja_env = Environment(
    loader=PackageLoader('courier', 'templates'),
    autoescape=select_autoescape(['html', 'xml']),
    trim_blocks=True,
    lstrip_blocks=True,
)
jinja_env.filters['valid_xml'] = valid_xml
jinja_env.filters['cdata'] = cdata


def read(filename: Union[str, bytes, os.PathLike]) -> str:
    with open(filename, 'r', encoding='utf-8') as fp:
        text = fp.read()
    return text


def join_pages(basename: str, folder: Union[str, os.PathLike], template: Optional[Template] = None) -> str:
    default_template = '{% for page in pages %}\n--- {{ loop.index }} ---\n{{ page|trim }}{% endfor %}'
    template = template or Template(default_template)
    page_files = sorted(Path(folder).glob(f'{basename}*.txt'))
    pages = [read(page) for page in page_files]
    return template.render(basename=basename, pages=pages, template=template)


class IssueCompiler:
    def __init__(self, template: Union[str, Template]):
        if isinstance(template, str):
            if not template.endswith('.jinja'):
                template += '.jinja'
            template = jinja_env.get_template(template)
        self.template: Template = template

    def compile_issues(
        self,
        basenames: List[str],
        input_folder: Union[str, os.PathLike],
        output_folder: Union[str, os.PathLike],
        extension: str = 'xml',
    ) -> None:

        Path(output_folder).mkdir(parents=True, exist_ok=True)

        pbar = tqdm(basenames, desc='File')
        for basename in pbar:
            pbar.set_description(f'Processing {basename}')
            if (len(list(Path(input_folder).glob(f'{basename}*.txt')))) > 0:
                with open(Path(output_folder) / f'{basename}.{extension}', 'w', encoding='utf-8') as fp:
                    fp.write(join_pages(basename, input_folder, self.template))


def pages_to_issues(
    input_folder: Union[str, os.PathLike],
    output_folder: Union[str, os.PathLike],
    extension: str = 'xml',
    template: Union[str, Template] = 'courier_issue.xml',
) -> None:
    compiler = IssueCompiler(template)
    compiler.compile_issues(get_courier_ids(), input_folder, output_folder, extension)


if __name__ == '__main__':
    argh.dispatch_command(pages_to_issues)
