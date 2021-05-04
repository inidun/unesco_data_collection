import os
from pathlib import Path
from typing import List, Optional, Union

from jinja2 import Environment, PackageLoader, Template, select_autoescape

from courier.config import get_config
from courier.utils import cdata, get_courier_ids, valid_xml

CONFIG = get_config()

# TODO: get template
jinja_env = Environment(
    loader=PackageLoader('courier', 'templates'),
    autoescape=select_autoescape(['html', 'xml']),
    trim_blocks=True,
    lstrip_blocks=True,
)
jinja_env.filters['valid_xml'] = valid_xml
jinja_env.filters['cdata'] = cdata


def read(filename: Union[str, bytes, os.PathLike]) -> str:
    with open(filename, 'r') as fp:
        text = fp.read()
    return text


def join_pages(basename: str, folder: Union[str, os.PathLike], template: Optional[Template] = None) -> str:
    default_template = '{% for page in pages %}\n--- {{ loop.index }} ---\n{{ page|trim }}{% endfor %}'
    template = template or Template(default_template)
    page_files = sorted(list(Path(folder).glob(f'{basename}*.txt')))
    pages = [read(page) for page in page_files]
    return template.render(basename=basename, pages=pages, template=template)


def compile_issues(
    basenames: List[str],
    input_folder: Union[str, os.PathLike],
    output_folder: Union[str, os.PathLike],
    extension: str = 'xml',
    template: Optional[Template] = None,
) -> None:

    # TODO: Add tqdm
    Path(output_folder).mkdir(parents=True, exist_ok=True)
    for basename in basenames:
        with open(Path(output_folder) / f'{basename}.{extension}', 'w') as fp:
            fp.write(join_pages(basename, input_folder, template))


def main() -> None:

    # FIXME: Update main or add cli

    template = jinja_env.get_template('courier_issue.xml.jinja')
    courier_ids = get_courier_ids()

    compile_issues(
        courier_ids,
        input_folder=CONFIG.base_data_dir / 'pages/pdfbox',
        output_folder=CONFIG.xml_dir / 'pdfbox',
        template=template,
    )

    compile_issues(
        courier_ids,
        input_folder=CONFIG.base_data_dir / 'pages/pdfplumber',
        output_folder=CONFIG.xml_dir / 'pdfplumber',
        template=template,
    )

    compile_issues(
        courier_ids,
        input_folder=CONFIG.base_data_dir / 'pages/pdfminer',
        output_folder=CONFIG.xml_dir / 'pdfminer',
        template=template,
    )


if __name__ == '__main__':
    main()
