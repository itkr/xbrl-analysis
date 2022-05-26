from edinet_xbrl.edinet_xbrl_parser import EdinetXbrlParser


def load():
    parser = EdinetXbrlParser()
    xbrl_file_path = "public.xbrl"
    edinet_xbrl_object = parser.parse_file(xbrl_file_path)

    # context_ref = "CurrentYearInstant_NonConsolidatedMember"
    # current_year_assets = edinet_xbrl_object.get_data_by_context_ref("jppfs_cor:Assets", context_ref).get_value()
    # print(current_year_assets)

    for key in list(edinet_xbrl_object.get_keys())[20: 24]:
        data_list = edinet_xbrl_object.get_data_list(key)
        print(key)
        for data in data_list:
            print('    ', data.get_context_ref(), data.get_value(), data.get_unit_ref(), data.get_decimals())


def main():
    load()


if __name__ == "__main__":
    main()
