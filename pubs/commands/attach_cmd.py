from .. import repo
from .. import color
from ..configs import config
from ..uis import get_ui
from .. import content

def parser(subparsers):
    parser = subparsers.add_parser('attach',
            help='attach a document to an existing paper')
    # parser.add_argument('-c', '--copy', action='store_true', default=True,
    #         help="copy document files into library directory (default)")
    parser.add_argument('-L', '--link', action='store_false', dest='copy', default=True,
            help="don't copy document files, just create a link.")
    parser.add_argument('citekey',
            help='citekey of the paper')
    parser.add_argument('document',
            help='document file')
    return parser


def command(args):
    """
    :param bibfile: bibtex file (in .bib, .bibml or .yaml format.
    :param docfile: path (no url yet) to a pdf or ps file
    """

    ui = get_ui()

    rp = repo.Repository(config())
    paper = rp.pull_paper(args.citekey)

    try:
        document = args.document
        rp.push_doc(paper.citekey, document, copy=args.copy)
        ui.print_('{} attached to {}'.format(color.dye(document, color.bold), color.dye(paper.citekey, color.citekey)))

    except ValueError as v:
        ui.error(v.message)
        ui.exit(1)
    except IOError as v:
        ui.error(v.message)
        ui.exit(1)
