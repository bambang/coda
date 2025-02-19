import os
import sys

if len(sys.argv) == 1 or sys.argv[1] == 'cffi':
    import __init__ as coda
elif sys.argv[1] == 'swig':
    import coda

REPEAT=10


def test():
    # index conversion
    print('index:', coda.c_index_to_fortran_index([4,10], 9))

    # NaN, Inf
    print(coda.NaN(), coda.MinInf(), coda.PlusInf())
    print(coda.isNaN(0), coda.isNaN(coda.NaN()))
    print(coda.isInf(0), coda.isInf(coda.PlusInf()), coda.isInf(coda.MinInf()))
    print(coda.isMinInf(0), coda.isMinInf(coda.MinInf()), coda.isMinInf(coda.PlusInf()))
    print(coda.isPlusInf(0), coda.isPlusInf(coda.PlusInf()), coda.isPlusInf(coda.MinInf()))

    # open product
    what = coda.recognize_file('madis-raob.nc')
    print('what:', what)
    product = coda.open('madis-raob.nc')

    print('class', coda.get_product_class(product))
    print('type', coda.get_product_type(product))
    print('version', coda.get_product_version(product))
    print('deffile', coda.get_product_definition_file(product))
    print('file size', coda.get_product_file_size(product))
    print('filename', coda.get_product_filename(product))
    print('format', coda.get_product_format(product))
    print('root type', coda.type_get_class(coda.get_product_root_type(product)))

    # fetch array
    array = coda.fetch(product, 'tpTropQCD')
    print(array)

    # fetch scalar
    scalar = coda.fetch(product, 'globalInventory')
    print(scalar)

    # read scalar int32
    cursor = coda.Cursor()
    coda.cursor_set_product(cursor, product)

    print('cursor has attrs', coda.cursor_has_attributes(cursor))
    type_ = coda.cursor_get_type(cursor)
    print('type has attrs', coda.type_has_attributes(type_))
    a = coda.type_get_attributes(type_)
    print('attrs type name', coda.type_get_class_name(coda.type_get_class(a)))

    coda.cursor_goto(cursor, 'globalInventory')

    gi = coda.cursor_read_int32(cursor)
    print('globalInventory:', gi)
    try:
        coda.cursor_read_uint16(cursor)
    except coda.CodacError as e:
        print(str(e))

    coda.cursor_goto_root(cursor)
    expr = coda.expression_from_string('2 * int(./globalInventory)')
    print('expr:', coda.expression_eval_integer(expr, cursor))
    coda.expression_delete(expr)

    # read double array
    coda.cursor_goto_root(cursor)
    type_ = coda.cursor_get_type(cursor)
    cl = coda.cursor_get_type_class(cursor)
    print('cl', cl)
    print('num recs:', coda.type_get_num_record_fields(type_))
    print('nt name:', coda.type_get_native_type_name(coda.type_get_read_type(type_)))
    print('0 hidden:', coda.type_get_record_field_hidden_status(type_, 0))
    print('0 available:', coda.type_get_record_field_available_status(type_, 0))
    print('field type:', coda.type_get_class(coda.type_get_record_field_type(type_, 0)))
    print('field name:', coda.type_get_record_field_name(type_, 0))
    print('field realname:', coda.type_get_record_field_real_name(type_, 0))
    print('index:', coda.type_get_record_field_index_from_name(type_, 'nStaticIds'))
    print('index:', coda.cursor_get_record_field_index_from_name(cursor, 'nStaticIds'))
    print('indexreal:', coda.type_get_record_field_index_from_real_name(type_, 'nStaticIds'))
    print('has attributes:', coda.type_has_attributes(type_))
    print('unit:', coda.type_get_unit(type_))
    print('union status:', coda.type_get_record_union_status(type_))
    print('union av i:', coda.cursor_get_available_union_field_index(cursor))
    print('product file', coda.get_product_filename(coda.cursor_get_product_file(cursor)))


    coda.cursor_goto_root(cursor)
    coda.cursor_goto_record_field_by_index(cursor, 0)
    coda.cursor_goto_root(cursor)
    coda.cursor_goto_record_field_by_name(cursor, 'nStaticIds')

    coda.cursor_goto_root(cursor)
    coda.cursor_goto(cursor, 'tpTropQCD')
    coda.cursor_goto_parent(cursor)
    coda.cursor_goto(cursor, 'tpTropQCD')

    shape = coda.cursor_get_array_dim(cursor)
    print('shape:', shape)

    type_ = coda.cursor_get_type(cursor)
    print('numdims:', coda.type_get_array_num_dims(type_))
    print('dims:', coda.type_get_array_dim(type_))
#print('attrs:', coda.type_get_attributes(type_))
    print('bitsize:', coda.type_get_bit_size(type_))
    print('class:', coda.type_get_class_name(coda.type_get_class(type_)))
    print('fixed:', coda.type_get_fixed_value(type_))
    print('format:', coda.type_get_format(type_))
    print('formatname:', coda.type_get_format_name(coda.type_get_format(type_)))
    print('name:', coda.type_get_name(type_))

    array = coda.cursor_read_double_array(cursor)
    print(array)

    #get specific element
    coda.cursor_goto_array_element(cursor, [0,1,7])
    print(coda.cursor_read_double(cursor))

    # read string
    coda.cursor_goto_root(cursor)
    coda.cursor_goto(cursor, 'staName')
    type_ = coda.cursor_get_type(cursor)
    print(coda.type_get_name(type_))
    print('dims:', coda.type_get_array_dim(type_))
    coda.cursor_goto_first_array_element(cursor)
    print(coda.cursor_get_string_length(cursor))
    print(repr(coda.cursor_read_string(cursor)))

    # read double partial array
    coda.cursor_goto_root(cursor)
    coda.cursor_goto(cursor, 'tpTropQCD')

    array = coda.cursor_read_double_partial_array(cursor, 10, 22)
    print(array.shape)
    print(array)

    try:
        coda.cursor_goto_available_union_field(cursor)
    except coda.CodacError as e:
        print(str(e))

    # exceptions
    coda.cursor_goto_root(cursor)

    try:
        coda.cursor_goto(cursor, 'zzz')
    except coda.CodacError as e:
        print(str(e))

    try:
        coda.cursor_read_int32(cursor)
    except coda.CodacError as e:
        print(str(e))

    try:
        coda.open('pipo')
    except coda.CodacError as e:
        print(str(e))

    # version
    print(coda.version())

    # node expr
    coda.cursor_goto_root(cursor)
    print('root depth:', coda.cursor_get_depth(cursor))
    expr = coda.expression_from_string('/globalInventory')
    coda.expression_eval_node(expr, cursor)
    print('expr depth:', coda.cursor_get_depth(cursor))
    coda.expression_delete(expr)

    # product class etc
    what = coda.recognize_file('AE_TEST_ALD_U_N_1B_20190105T011602023_008364010_002143_0001.DBL')
    print('what:', what)

    # close
    coda.close(product)

    product = coda.open_as('AE_TEST_ALD_U_N_1B_20190105T011602023_008364010_002143_0001.DBL', 'AEOLUS', 'ALD_U_N_1B', 9)

    print('class', coda.get_product_class(product))
    print('type', coda.get_product_type(product))
    print('version', coda.get_product_version(product))
    print('description', coda.get_description(product))
    print('attrs', coda.get_attributes(product))

    try:
        coda.get_product_variable_value(product, 'geolocation', 0)
    except coda.CodacError as e:
        print(str(e))

    # product/cursor methods
    cursor = coda.Cursor()
    coda.cursor_set_product(cursor, product)

    print('description', coda.get_description(product))
    print('description', coda.get_description(cursor))

    coda.cursor_goto(cursor, 'geolocation')
    coda.cursor_goto_array_element_by_index(cursor, 0)
    coda.cursor_goto(cursor, 'start_of_observation_time')

    type_ = coda.cursor_get_type(cursor)
    print('T', coda.type_get_special_type(type_))
    print('N', coda.type_get_special_type_name(2))
    print('B', coda.type_get_native_type_name(coda.type_get_read_type(coda.type_get_special_base_type(type_))))

    coda.cursor_use_base_type_of_special_type(cursor)
    print('bitsize:', coda.cursor_get_bit_size(cursor))
    print('bytesize:', coda.cursor_get_byte_size(cursor))
    print('bitoff', coda.cursor_get_file_bit_offset(cursor))
    print('byteoff', coda.cursor_get_file_byte_offset(cursor))
    print('format', coda.cursor_get_format(cursor))
    data = coda.cursor_read_bytes(cursor, 0, 4)
    print(type(data), data.shape, data.dtype, data)
    data = coda.cursor_read_bits(cursor, 8, 40)
    print(type(data), data.shape, data.dtype, data)

    # expressions
    expr = coda.expression_from_string('1+2')
    print(coda.expression_is_constant(expr))
    print(coda.expression_is_equal(expr, expr))
    result = coda.expression_eval_integer(expr)
    print(result)
    type_ = coda.expression_get_type(expr)
    name = coda.expression_get_type_name(type_)
    print('type', type_, name)
    coda.expression_delete(expr)

    expr = coda.expression_from_string('4.5')
    print(coda.expression_eval_float(expr, cursor))
    coda.expression_delete(expr)

    expr = coda.expression_from_string('true')
    print(coda.expression_eval_bool(expr))
    coda.expression_delete(expr)

    expr = coda.expression_from_string('"bananen" + "vla"')
    print(coda.expression_eval_string(expr))
    coda.expression_delete(expr)

    # time
    parts = coda.time_double_to_parts(12345.67890)
    print(parts)
    parts_utc = coda.time_double_to_parts_utc(12345.67890)
    print(parts_utc)
    s = coda.time_double_to_string(12345.67890, 'yyyy-mm-dd')
    print(s)
    s_utc = coda.time_double_to_string_utc(12345.67890, 'yyyy-mm-dd')
    print(s_utc)

    d = coda.time_parts_to_double(*parts)
    print(d)
    d = coda.time_parts_to_double_utc(*parts_utc)
    print(d)
    s = coda.time_parts_to_string(*parts+['yyyy-mm-dd'])
    print(s)

    d = coda.time_string_to_double('yyyy-mm-dd', s)
    print(d)
    d = coda.time_string_to_double_utc('yyyy-mm-dd', s)
    print(d)
    parts = coda.time_string_to_parts( 'yyyy-mm-dd', s)
    print(parts)

    #callback
    def findhelper(filepath, status, error):
        print('match?', filepath, status, error)

    #broken on swig side?
#coda.match_filefilter('', ['/home/srepmub/coda/python/cffi/blup'], findhelper)

    print('index', coda.cursor_get_index(cursor))
    print('has_ascii', coda.cursor_has_ascii_content(cursor))

    #close
    coda.close(product)

    #test self-fabricated product
    product = coda.open('woef.nc')
    cursor = coda.Cursor()
    coda.cursor_set_product(cursor, product)

    # scalar char
    coda.cursor_goto(cursor, 'mychar')
    coda.cursor_goto_first_array_element(cursor)
    type_ = coda.cursor_get_type(cursor)
    print('len', coda.type_get_string_length(type_))
    print(repr(coda.cursor_read_string(cursor)))
    print(coda.fetch(product, 'mychar'))

    coda.close(product)

    #complex numbers
    product = coda.open("MIP_NL__1PYDSI20120401_012202_000060153113_00161_52761_0000.N1")

    cursor = coda.Cursor()
    coda.cursor_set_product(cursor, product)

    print(coda.cursor_get_num_elements(cursor))
    type_ = coda.cursor_get_type(cursor)
    print(coda.type_get_class_name(coda.type_get_class(type_)))

    for i in range(14):
        print(i, coda.type_get_record_field_name(type_, i))

    coda.cursor_goto(cursor, 'mipas_level_1b_mds')
    coda.cursor_goto_array_element_by_index(cursor, 3)
    coda.cursor_goto_record_field_by_name(cursor, 'spike_amp')

    array = coda.cursor_read_complex_array(cursor)
    print(type(array), array.dtype, array.shape, array[50], type(array[50]))
    array = coda.cursor_read_complex_double_pairs_array(cursor)
    print(type(array), array.dtype, array.shape, array[50])
    array = coda.cursor_read_complex_double_split_array(cursor)
    print(type(array), len(array), len(array[0]), type(array[0]), array[0].dtype, array[0][50], array[1][50])

    coda.cursor_goto_array_element_by_index(cursor, 50)
    scalar = coda.cursor_read_complex(cursor)
    print(type(scalar), scalar)
    scalar = coda.cursor_read_complex_double_pair(cursor)
    print(type(scalar), scalar.dtype, scalar)
    scalar = coda.cursor_read_complex_double_split(cursor)
    print(type(scalar), scalar)

    coda.close(product)


coda.init()

coda.set_option_bypass_special_types(0)
print(coda.get_option_bypass_special_types())
coda.set_option_perform_boundary_checks(1)
print(coda.get_option_perform_boundary_checks())
coda.set_option_perform_conversions(1)
print(coda.get_option_perform_conversions())
coda.set_option_use_fast_size_expressions(1)
print(coda.get_option_use_fast_size_expressions())
coda.set_option_use_mmap(1)
print(coda.get_option_use_mmap())

for i in range(REPEAT):
    test()
coda.done()
