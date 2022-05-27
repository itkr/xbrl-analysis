from edinet_xbrl.edinet_xbrl_parser import EdinetXbrlParser
from bs4 import BeautifulSoup


# <?xml version="1.0" encoding="UTF-8"?>
# <xbrli:xbrl
#   xmlns:iso4217="http://www.xbrl.org/2003/iso4217"
#   xmlns:jpcrp030000-asr_E04837-000="http://disclosure.edinet-fsa.go.jp/jpcrp030000/asr/001/E04837-000/2021-03-31/01/2021-06-23"
#   xmlns:jpcrp_cor="http://disclosure.edinet-fsa.go.jp/taxonomy/jpcrp/2020-11-01/jpcrp_cor"
#   xmlns:jpdei_cor="http://disclosure.edinet-fsa.go.jp/taxonomy/jpdei/2013-08-31/jpdei_cor"
#   xmlns:jppfs_cor="http://disclosure.edinet-fsa.go.jp/taxonomy/jppfs/2020-11-01/jppfs_cor"
#   xmlns:link="http://www.xbrl.org/2003/linkbase"
#   xmlns:xbrldi="http://xbrl.org/2006/xbrldi"
#   xmlns:xbrli="http://www.xbrl.org/2003/instance"
#   xmlns:xlink="http://www.w3.org/1999/xlink"
#   xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
# >
# ...

def is_html(value):
    # intなど
    if not isinstance(value, str):
        return False
    soup = BeautifulSoup(value)
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

    print('iso4217')
    print('  ', len(list(filter(lambda x: x.startswith('iso4217:'), keys))))
    print('jpcrp030000')
    print('  ', len(list(filter(lambda x: x.startswith('jpcrp030000-asr_E04837-000:'), keys))))
    print('jpcrp_cor')
    print('  ', len(list(filter(lambda x: x.startswith('jpcrp_cor:'), keys))))
    print('jpdei_cor')
    print('  ', len(list(filter(lambda x: x.startswith('jpdei_cor:'), keys))))
    print('jppfs_cor')
    print('  ', len(list(filter(lambda x: x.startswith('jppfs_cor:'), keys))))
    print('link')
    print('  ', len(list(filter(lambda x: x.startswith('link:'), keys))))
    print('xbrldi')
    print('  ', len(list(filter(lambda x: x.startswith('xbrldi:'), keys))))
    print('xbrli')
    print('  ', len(list(filter(lambda x: x.startswith('xbrli:'), keys))))
    print('xlink')
    print('  ', len(list(filter(lambda x: x.startswith('xlink:'), keys))))
    print('xsi')
    print('  ', len(list(filter(lambda x: x.startswith('xsi:'), keys))))
    print('---')

    # keys = list(filter(lambda x: x.startswith('jpcrp_cor:'), keys))
    for key in keys:
        print(key)
        data_list = edinet_xbrl_object.get_data_list(key)
        for data in data_list:
            try:
                int(data.get_value())
                print('  ', data.get_context_ref(), data.get_value(), data.get_unit_ref(), data.get_decimals())
            except ValueError:
                if not is_html(data.get_value()):
                    print('  ', data.get_context_ref(), data.get_value(), data.get_unit_ref(), data.get_decimals())
                else:
                    print('  ', data.get_context_ref(), "[HTML]", data.get_unit_ref(), data.get_decimals())
            except TypeError:
                # None ?
                print('  ', data.get_context_ref(), data.get_value(), data.get_unit_ref(), data.get_decimals())


def main():
    load()


if __name__ == "__main__":
    main()
