from edinet_xbrl.edinet_xbrl_parser import EdinetXbrlParser


def load():
    parser = EdinetXbrlParser()

    xbrl_file_path = "public.xbrl"
    edinet_xbrl_object = parser.parse_file(xbrl_file_path)

    key = "jppfs_cor:Assets"
    # context_ref = "CurrentYearInstant"
    context_ref = "CurrentYearInstant_NonConsolidatedMember"
    current_year_assets = edinet_xbrl_object.get_data_by_context_ref(key, context_ref).get_value()
    print(current_year_assets)


def main():
    load()


if __name__ == "__main__":
    main()
