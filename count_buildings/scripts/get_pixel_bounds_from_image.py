
def start(argv=sys.argv):
    with script.Starter(run, argv) as starter:
        starter.add_argument(
            '--image_path', metavar='PATH', required=True,
            help='satellite image')
        starter.add_argument(
            '--tile_dimensions', metavar='WIDTH,HEIGHT',
            type=script.parse_dimensions,
            help='dimensions of extracted tile in geographic units')
