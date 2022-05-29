from edinet_xbrl.edinet_xbrl_parser import EdinetXbrlParser
from bs4 import BeautifulSoup


def get_taxonomy(xbrl_file_path):
    with open(xbrl_file_path, 'r') as f:
        soup = BeautifulSoup(f.read(), 'lxml')
    xbrli = soup.find("xbrli:xbrl")
    return list(xbrli.attrs)


def is_html(value):
    # intなど
    if not isinstance(value, str):
        return False
    soup = BeautifulSoup(value, 'lxml')
    # 空文字など
    if not soup.html:
        return False
    # タグ無し文字
    return soup.html.body.p.text != value


def load():
    parser = EdinetXbrlParser()
    xbrl_file_path = "public.xbrl"
    edinet_xbrl_object = parser.parse_file(xbrl_file_path)

    keys = edinet_xbrl_object.get_keys()
    for taxonomy in sorted(get_taxonomy(xbrl_file_path)):
        taxonomy_name = taxonomy.split(":")[1]
        print(taxonomy_name)
        print('  ', len(list(filter(lambda x: x.startswith(taxonomy_name), keys))))

    # keys = list(filter(lambda x: x.startswith('jpigp_cor:'), keys))
    for key in keys:
        print(key)
        data_list = edinet_xbrl_object.get_data_list(key)
        for data in data_list:
            # int(data.get_value())
            value = "[HTML]" if is_html(data.get_value()) else data.get_value()
            print('  ', data.get_context_ref(), value, data.get_unit_ref(), data.get_decimals())


def main():
    load()


if __name__ == "__main__":
    main()
