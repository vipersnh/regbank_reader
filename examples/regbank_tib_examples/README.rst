Using
=====

Basic usage
===========
    1) Each line starting with '#' or having '#' in the middle are treated as comments 
       after the first occurance of '#' character.
    2) Number notations as follows can be used where-ever integer is expected
        - Decimal : [0-9]\+
        - Hex     : 0x[0-9A-F]\+
        - Octal   : 0o[0-7]\+
        - Binary  : 0b[0-1]\+
    2) Basic commands
        - read          : Reads specified address upto nbytes if specified else 4 bytes
            - syntax    : read <addr> [nbytes]
            - example   : read 0x400400
                          read 0x400400 10
        - write         : Writes specified address with, value after applying optional value_mask
            - syntax    : write <addr> <value> [value_mask]
            - example   : write 0x1000 0x20
                          write 0x100  0x20    0b11
        - rmwrite       : Read-Modify-Write address with, value after applying optional value_mask
            - syntax    : rmwrite <addr> <value> [value_mask]
            - example   : rmwrite 0x1000 0x20
                          rmwrite 0x100  0x20    0b11


Advanced usage
==============
    1) File loading commands, (execute and apply configurations for CLI)
        - load_regbank  : Loads the specified register file into database for operations
            - pre-reqs  : None
            - syntax    : load_regbank <regbank_path>
            - example   : load_regbank "../regbank_sheet_examples/demo_regbank.xlsx"
            - note      : File name without extension will be referred to as regbank once it is
                          loaded. So no two unique regbank xls should share the same name.
        - load_sheet    : Loads the specified sheet at specified base-offset with 
                          byte_offsets|word_offsets from regbank already loaded.
                          By default it loads regbank_sheet using BYTE_OFFSET
            - pre-reqs  : Regbank containing the specified sheet must be already loaded
                          before executing this command
            - syntax    : load_sheet <regbank>.<sheet_name> at <base_addr> [using <BYTE_OFFSETS|WORD_OFFSETS>] [as <name>]
            - example   : load_regbank "../regbank_sheet_examples/demo_regbank.xlsx"
                          load_sheet demo_regbank.Sheet_A at 0x400400
                          load_sheet demo_regbank.Sheet_B at 0x400400 using WORD_OFFSETS
                          load_sheet demo_regbank.Sheet_B at 0x40000  using WORD_OFFSETS as sheetX
    2) File loading commands, (execute and apply configurations for GUI)
        - load_regbank_gui : Loads the specified register file into database for GUI operations
            - pre-reqs     : None
            - syntax       : load_regbank_gui <regbank_path>
            - example      : load_regbank_gui "../regbank_sheet_examples/demo_regbank.xlsx"
            - post-reqs    : ALL sheets of the regbank must be manually loaded using load_sheet_gui command 
            - note         : File name without extension will be referred to as regbank once it is
                             loaded. So no two unique regbank xls should share the same name.
        - load_sheet_gui   : Loads regbank sheets one by one as specified into the GUI database.
            - pre-reqs     : Regbank must be loaded into GUI before using this command.
            - syntax       : load_sheet_gui <regbank>.<sheet_name> at <base_addr> [using <BYTE_OFFSETS|WORD_OFFSETS>] [as <name>],
                                            <regbank>.<sheet_name> at <base_addr> [using <BYTE_OFFSETS|WORD_OFFSETS>] [as <name>] end
            - example      : load_regbank_gui "../regbank_sheet_examples/demo_regbank.xlsx"
                             load_sheet_gui demo_regbank.Sheet_A at 0x400000, 
                                            demo_regbank.Sheet_B at 0x200200 using WORD_OFFSETS as Sheet_B1,
                                            demo_regbank.Sheet_B at 0x200400 using WORD_OFFSETS as Sheet_B2

