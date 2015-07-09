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
            - syntax    : *<addr> = ?
            - example   : *0x400400 = ?
                          *0x400500=?
        - write         : Writes specified address with, value after applying optional value_mask
            - syntax    : *<addr>  = <value> [ & value_mask]
            - example   : *0x1000 =  0x20
                          *0x100 = 0x20 & 0b11
        - rmwrite       : Read-Modify-Write address with, value after applying optional value_mask
            - syntax    : *<addr> = ? <value> [ & value_mask]
            - example   : *0x1000 =?0x20
                          *0x100  = ? 0x20 & 0b11


Advanced usage
==============
    1) File loading commands
        - load_regbank  : Loads the specified register file into database for operations
            - pre-reqs  : None
            - syntax    : load_regbank <regbank_path>
            - example   : load_regbank "../regbank_sheet_examples/demo_regbank.xlsx"
            - note      : File name without extension will be referred to as regbank once it is
                          loaded. So no two unique regbank xls should share the same name.
                          Same must not be loaded again.
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
            - note      : Sheets loaded using 'as <name>' must be dereferenced in the same way as other sheets.
    
    2) Register read and write commands
        - Register Access for writing :
            - syntax    : *<regbank>.<sheet_name>.<register_name>[.<field_name>] = <value> [ & value_mask ]
            - example   : *demo_regbank.Sheet_A.Register_A = 0x200
                          *demo_regbank.Sheet_A.Register_A.Subfield_A_A = 0x2 & 0x1
        - Register Access for reading :
            - syntax    : *<regbank>.<sheet_name>.<register_name>[.<field_name>] = ?
            - example   : *demo_regbank.Sheet_A.Register_A = ?
                          *demo_regbank.Sheet_A.Register_A.Subfield_A_A = ?



