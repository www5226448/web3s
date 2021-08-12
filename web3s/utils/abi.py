from collections import (
    namedtuple,
)
import itertools
import re

from eth_abi import (
    is_encodable as eth_abi_is_encodable,
)



from eth_utils import (
    is_hex,
    is_list_like,
    to_bytes,
    to_text,
    to_tuple,
)

from web3s.exceptions import (
    FallbackNotFound,
)


from web3s.utils.formatters import (
    recursive_map,
)
from web3s.utils.toolz import (
    curry,
    partial,
    pipe,
)


def filter_by_type(_type, contract_abi):
    return [abi for abi in contract_abi if abi['type'] == _type]


def filter_by_name(name, contract_abi):
    return [
        abi
        for abi
        in contract_abi
        if (
            abi['type'] not in ('fallback', 'constructor') and
            abi['name'] == name
        )
    ]


def get_abi_input_types(abi):
    if 'inputs' not in abi and abi['type'] == 'fallback':
        return []
    else:
        return [arg['type'] for arg in abi['inputs']]


def get_abi_output_types(abi):
    if abi['type'] == 'fallback':
        return []
    else:
        return [arg['type'] for arg in abi['outputs']]


def get_abi_input_names(abi):
    if 'inputs' not in abi and abi['type'] == 'fallback':
        return []
    else:
        return [arg['name'] for arg in abi['inputs']]


def get_fallback_func_abi(contract_abi):
    fallback_abis = filter_by_type('fallback', contract_abi)
    if fallback_abis:
        return fallback_abis[0]
    else:
        raise FallbackNotFound("No fallback function was found in the contract ABI.")


def fallback_func_abi_exists(contract_abi):
    return filter_by_type('fallback', contract_abi)


def get_indexed_event_inputs(event_abi):
    return [arg for arg in event_abi['inputs'] if arg['indexed'] is True]


def exclude_indexed_event_inputs(event_abi):
    return [arg for arg in event_abi['inputs'] if arg['indexed'] is False]


def filter_by_argument_count(num_arguments, contract_abi):
    return [
        abi
        for abi
        in contract_abi
        if len(abi['inputs']) == num_arguments
    ]


def filter_by_argument_name(argument_names, contract_abi):
    return [
        abi
        for abi in contract_abi
        if set(argument_names).intersection(
            get_abi_input_names(abi)
        ) == set(argument_names)
    ]


def is_encodable(_type, value):
    try:
        base, sub, arrlist = _type
    except ValueError:
        base, sub, arrlist = process_type(_type)

    if arrlist:
        if not is_list_like(value):
            return False
        if arrlist[-1] and len(value) != arrlist[-1][0]:
            return False
        sub_type = (base, sub, arrlist[:-1])
        return all(is_encodable(sub_type, sub_value) for sub_value in value)

    elif base == 'bytes' and isinstance(value, str):
        # Hex-encoded bytes values can be used anywhere a bytes value is needed
        if is_hex(value) and len(value) % 2 == 0:
            # Require hex-encoding of full bytes (even length)
            bytes_val = to_bytes(hexstr=value)
            return eth_abi_is_encodable(_type, bytes_val)
        else:
            return False
    elif base == 'string' and isinstance(value, bytes):
        # bytes that were encoded with utf-8 can be used anywhere a string is needed
        try:
            string_val = to_text(value)
        except UnicodeDecodeError:
            return False
        else:
            return eth_abi_is_encodable(_type, string_val)
    else:
        return eth_abi_is_encodable(_type, value)


def filter_by_encodability(args, kwargs, contract_abi):
    return [
        function_abi
        for function_abi
        in contract_abi
        if check_if_arguments_can_be_encoded(function_abi, args, kwargs)
    ]


def check_if_arguments_can_be_encoded(function_abi, args, kwargs):
    try:
        arguments = merge_args_and_kwargs(function_abi, args, kwargs)
    except TypeError:
        return False

    if len(function_abi.get('inputs', [])) != len(arguments):
        return False

    types = get_abi_input_types(function_abi)

    return all(
        is_encodable(_type, arg)
        for _type, arg in zip(types, arguments)
    )


def merge_args_and_kwargs(function_abi, args, kwargs):
    if len(args) + len(kwargs) != len(function_abi.get('inputs', [])):
        raise TypeError(
            "Incorrect argument count.  Expected '{0}'.  Got '{1}'".format(
                len(function_abi['inputs']),
                len(args) + len(kwargs),
            )
        )

    if not kwargs:
        return args

    args_as_kwargs = {
        arg_abi['name']: arg
        for arg_abi, arg in zip(function_abi['inputs'], args)
    }
    duplicate_keys = set(args_as_kwargs).intersection(kwargs.keys())
    if duplicate_keys:
        raise TypeError(
            "{fn_name}() got multiple values for argument(s) '{dups}'".format(
                fn_name=function_abi['name'],
                dups=', '.join(duplicate_keys),
            )
        )

    sorted_arg_names = [arg_abi['name'] for arg_abi in function_abi['inputs']]

    unknown_kwargs = {key for key in kwargs.keys() if key not in sorted_arg_names}
    if unknown_kwargs:
        if function_abi.get('name'):
            raise TypeError(
                "{fn_name}() got unexpected keyword argument(s) '{dups}'".format(
                    fn_name=function_abi.get('name'),
                    dups=', '.join(unknown_kwargs),
                )
            )
        # show type instead of name in the error message incase key 'name' is missing.
        raise TypeError(
            "Type: '{_type}' got unexpected keyword argument(s) '{dups}'".format(
                _type=function_abi.get('type'),
                dups=', '.join(unknown_kwargs),
            )
        )

    sorted_args = list(zip(
        *sorted(
            itertools.chain(kwargs.items(), args_as_kwargs.items()),
            key=lambda kv: sorted_arg_names.index(kv[0])
        )
    ))
    if sorted_args:
        return sorted_args[1]
    else:
        return tuple()


def get_constructor_abi(contract_abi):
    candidates = [
        abi for abi in contract_abi if abi['type'] == 'constructor'
    ]
    if len(candidates) == 1:
        return candidates[0]
    elif len(candidates) == 0:
        return None
    elif len(candidates) > 1:
        raise ValueError("Found multiple constructors.")


DYNAMIC_TYPES = ['bytes', 'string']

INT_SIZES = range(8, 257, 8)
BYTES_SIZES = range(1, 33)
UINT_TYPES = ['uint{0}'.format(i) for i in INT_SIZES]
INT_TYPES = ['int{0}'.format(i) for i in INT_SIZES]
BYTES_TYPES = ['bytes{0}'.format(i) for i in BYTES_SIZES] + ['bytes32.byte']

STATIC_TYPES = list(itertools.chain(
    ['address', 'bool'],
    UINT_TYPES,
    INT_TYPES,
    BYTES_TYPES,
))

BASE_TYPE_REGEX = '|'.join((
    _type + '(?![a-z0-9])'
    for _type
    in itertools.chain(STATIC_TYPES, DYNAMIC_TYPES)
))

SUB_TYPE_REGEX = (
    r'\['
    '[0-9]*'
    r'\]'
)

TYPE_REGEX = (
    '^'
    '(?:{base_type})'
    '(?:(?:{sub_type})*)?'
    '$'
).format(
    base_type=BASE_TYPE_REGEX,
    sub_type=SUB_TYPE_REGEX,
)


def is_recognized_type(abi_type):
    return bool(re.match(TYPE_REGEX, abi_type))


def is_bool_type(abi_type):
    return abi_type == 'bool'


def is_uint_type(abi_type):
    return abi_type in UINT_TYPES


def is_int_type(abi_type):
    return abi_type in INT_TYPES


def is_address_type(abi_type):
    return abi_type == 'address'


def is_bytes_type(abi_type):
    return abi_type in BYTES_TYPES + ['bytes']


def is_string_type(abi_type):
    return abi_type == 'string'


def size_of_type(abi_type):
    """
    Returns size in bits of abi_type
    """
    if 'string' in abi_type:
        return None
    if 'byte' in abi_type:
        return None
    if '[' in abi_type:
        return None
    if abi_type == 'bool':
        return 8
    if abi_type == 'address':
        return 160
    return int(re.sub(r"\D", "", abi_type))


END_BRACKETS_OF_ARRAY_TYPE_REGEX = r"\[[^]]*\]$"


def sub_type_of_array_type(abi_type):
    if not is_array_type(abi_type):
        raise ValueError(
            "Cannot parse subtype of nonarray abi-type: {0}".format(abi_type)
        )

    return re.sub(END_BRACKETS_OF_ARRAY_TYPE_REGEX, '', abi_type, 1)


def length_of_array_type(abi_type):
    if not is_array_type(abi_type):
        raise ValueError(
            "Cannot parse length of nonarray abi-type: {0}".format(abi_type)
        )

    inner_brackets = re.search(END_BRACKETS_OF_ARRAY_TYPE_REGEX, abi_type).group(0).strip("[]")
    if not inner_brackets:
        return None
    else:
        return int(inner_brackets)


ARRAY_REGEX = (
    "^"
    "[a-zA-Z0-9_]+"
    "({sub_type})+"
    "$"
).format(sub_type=SUB_TYPE_REGEX)


def is_array_type(abi_type):
    return bool(re.match(ARRAY_REGEX, abi_type))


NAME_REGEX = (
    '[a-zA-Z_]'
    '[a-zA-Z0-9_]*'
)


ENUM_REGEX = (
    '^'
    '{lib_name}'
    r'\.'
    '{enum_name}'
    '$'
).format(lib_name=NAME_REGEX, enum_name=NAME_REGEX)


def is_probably_enum(abi_type):
    return bool(re.match(ENUM_REGEX, abi_type))


@to_tuple
def normalize_event_input_types(abi_args):
    for arg in abi_args:
        if is_recognized_type(arg['type']):
            yield arg
        elif is_probably_enum(arg['type']):
            yield {k: 'uint8' if k == 'type' else v for k, v in arg.items()}
        else:
            yield arg


def abi_to_signature(abi):
    function_signature = "{fn_name}({fn_input_types})".format(
        fn_name=abi['name'],
        fn_input_types=','.join([
            arg['type'] for arg in normalize_event_input_types(abi.get('inputs', []))
        ]),
    )
    return function_signature


########################################################
#
#  Conditionally modifying data, tagged with ABI Types
#
########################################################


@curry
def map_abi_data(normalizers, types, data):
    '''
    This function will apply normalizers to your data, in the
    context of the relevant types. Each normalizer is in the format:

    def normalizer(datatype, data):
        # Conditionally modify data
        return (datatype, data)

    Where datatype is a valid ABI type string, like "uint".

    In case of an array, like "bool[2]", normalizer will receive `data`
    as an iterable of typed data, like `[("bool", True), ("bool", False)]`.

    Internals
    ---

    This is accomplished by:

    1. Decorating the data tree with types
    2. Recursively mapping each of the normalizers to the data
    3. Stripping the types back out of the tree
    '''
    pipeline = itertools.chain(
        [abi_data_tree(types)],
        map(data_tree_map, normalizers),
        [partial(recursive_map, strip_abi_type)],
    )

    return pipe(data, *pipeline)


@curry
def abi_data_tree(types, data):
    '''
    Decorate the data tree with pairs of (type, data). The pair tuple is actually an
    ABITypedData, but can be accessed as a tuple.

    As an example:

    >>> abi_data_tree(types=["bool[2]", "uint"], data=[[True, False], 0])
    [("bool[2]", [("bool", True), ("bool", False)]), ("uint256", 0)]
    '''
    return [
        abi_sub_tree(data_type, data_value)
        for data_type, data_value
        in zip(types, data)
    ]


@curry
def data_tree_map(func, data_tree):
    '''
    Map func to every ABITypedData element in the tree. func will
    receive two args: abi_type, and data
    '''
    def map_to_typed_data(elements):
        if isinstance(elements, ABITypedData) and elements.abi_type is not None:
            return ABITypedData(func(*elements))
        else:
            return elements
    return recursive_map(map_to_typed_data, data_tree)


class ABITypedData(namedtuple('ABITypedData', 'abi_type, data')):
    '''
    This class marks data as having a certain ABI-type.

    >>> a1 = ABITypedData(['address', addr1])
    >>> a2 = ABITypedData(['address', addr2])
    >>> addrs = ABITypedData(['address[]', [a1, a2])

    You can access the fields using tuple() interface, or with
    attributes:

    >>> assert a1.abi_type == a1[0]
    >>> assert a1.data == a1[1]

    Unlike a typical `namedtuple`, you initialize with a single
    positional argument that is iterable, to match the init
    interface of all other relevant collections.
    '''
    def __new__(cls, iterable):
        return super().__new__(cls, *iterable)


def abi_sub_tree(data_type, data_value):
    if data_type is None:
        return ABITypedData([None, data_value])

    try:
        base, sub, arrlist = data_type
    except ValueError:
        base, sub, arrlist = process_type(data_type)

    collapsed = collapse_type(base, sub, arrlist)

    if arrlist:
        sub_type = (base, sub, arrlist[:-1])
        return ABITypedData([
            collapsed,
            [
                abi_sub_tree(sub_type, sub_value)
                for sub_value in data_value
            ],
        ])
    else:
        return ABITypedData([collapsed, data_value])


def strip_abi_type(elements):
    if isinstance(elements, ABITypedData):
        return elements.data
    else:
        return elements





import functools
import re

from parsimonious import expressions
import parsimonious

from eth_abi.exceptions import (
    ABITypeError,
    ParseError,
)


grammar = parsimonious.Grammar(r"""
type = tuple_type / basic_type
tuple_type = non_zero_tuple / zero_tuple
non_zero_tuple = "(" type next_type* ")"
next_type = "," type
zero_tuple = "()"
basic_type = base sub? arrlist?
base = alphas
sub = two_size / digits
two_size = (digits "x" digits)
arrlist = (const_arr / dynam_arr)+
const_arr = "[" digits "]"
dynam_arr = "[]"
alphas = ~"[a-z]+"
digits = ~"[1-9][0-9]*"
""")


class NodeVisitor(parsimonious.NodeVisitor):
    """
    Parsimonious node visitor which performs both parsing of type strings and
    post-processing of parse trees.  Parsing operations are cached.
    """
    grammar = grammar

    def visit_non_zero_tuple(self, node, visited_children):
        # Ignore left and right parens
        _, first, rest, _ = visited_children

        return TupleType((first,) + rest, node=node)

    def visit_next_type(self, node, visited_children):
        # Ignore comma
        _, abi_type = visited_children

        return abi_type

    def visit_zero_tuple(self, node, visited_children):
        return TupleType(tuple(), node=node)

    def visit_basic_type(self, node, visited_children):
        base, sub, arrlist = visited_children

        return BasicType(base, sub, arrlist, node=node)

    def visit_two_size(self, node, visited_children):
        # Ignore "x"
        first, _, second = visited_children

        return first, second

    def visit_const_arr(self, node, visited_children):
        # Ignore left and right brackets
        _, int_value, _ = visited_children

        return (int_value,)

    def visit_dynam_arr(self, node, visited_children):
        return tuple()

    def visit_alphas(self, node, visited_children):
        return node.text

    def visit_digits(self, node, visited_children):
        return int(node.text)

    def generic_visit(self, node, visited_children):
        if isinstance(node.expr, expressions.OneOf):
            # Unwrap value chosen from alternatives
            return visited_children[0]

        if isinstance(node.expr, expressions.Optional):
            # Unwrap optional value or return `None`
            if len(visited_children) != 0:
                return visited_children[0]

            return None

        return tuple(visited_children)

    @functools.lru_cache(maxsize=None)
    def parse(self, type_str):
        """
        Caches and returns results of parsing operations.  Wraps any raised
        parsing errors in a custom error class.
        """
        if not isinstance(type_str, str):
            raise TypeError('Can only parse string values: got {}'.format(type(type_str)))

        try:
            return super().parse(type_str)
        except parsimonious.ParseError as e:
            raise ParseError(e.text, e.pos, e.expr)


visitor = NodeVisitor()


class ABIType:
    """
    Base class for classes which represent the results of parsing operations on
    abi type strings after post-processing.
    """
    __slots__ = ('node',)

    def __init__(self, *, node=None):
        # The parsimonious `Node` instance associated with this parsed type may
        # be optionally included.  If a type must be validated during a parsing
        # operation, the `Node` instance is required since the `invalidate`
        # method expects it.
        self.node = node

    def __repr__(self):  # pragma: no cover
        return '<{} {}>'.format(type(self).__qualname__, repr(str(self)))

    def __eq__(self, other):
        """
        Two ABI types are equal if their canonical string representations are
        equal.
        """
        return (
            type(self) is type(other) and
            str(self) == str(other)
        )

    def __str__(self):  # pragma: no cover
        """
        An ABI type must have a canonical string representation.
        """
        raise NotImplementedError('Must implement `__str__`')

    def validate(self):  # pragma: no cover
        """
        An ABI type must be able to validate itself against the solidity ABI
        spec:
        https://solidity.readthedocs.io/en/develop/abi-spec.html
        """
        raise NotImplementedError('Must implement `validate`')

    def invalidate(self, error_msg):
        """
        Invalidates an ABI type with the given error message.  Expects that a
        parsimonious node was provided from the original parsing operation that
        yielded this type.
        """
        node = self.node

        raise ABITypeError(
            "For '{comp_str}' type at column {col} "
            "in '{type_str}': {error_msg}".format(
                comp_str=node.text,
                col=node.start + 1,
                type_str=node.full_text,
                error_msg=error_msg,
            ),
        )


class TupleType(ABIType):
    """
    Represents the result of parsing a type string which contains a tuple abi
    type.
    e.g. "(int,bool)"
    """
    __slots__ = ('components',)

    def __init__(self, components, *, node=None):
        super().__init__(node=node)

        self.components = components

    def __str__(self):
        return '({})'.format(','.join(str(c) for c in self.components))

    def validate(self):
        # A tuple type is valid if all of its components are valid i.e. if none
        # of its components contain an invalid type such as "uint7"
        for c in self.components:
            c.validate()


class BasicType(ABIType):
    """
    Represents the result of parsing a type string which contains a basic abi
    type.
    e.g. "uint", "address", "ufixed128x19[][2]"
    """
    __slots__ = ('base', 'sub', 'arrlist')

    def __init__(self, base, sub=None, arrlist=None, *, node=None):
        super().__init__(node=node)

        self.base = base
        self.sub = sub
        self.arrlist = arrlist

    def __str__(self):
        sub, arrlist = self.sub, self.arrlist

        if isinstance(sub, int):
            sub = str(sub)
        elif isinstance(sub, tuple):
            sub = 'x'.join(str(s) for s in sub)
        else:
            sub = ''

        if isinstance(arrlist, tuple):
            arrlist = ''.join(repr(list(a)) for a in arrlist)
        else:
            arrlist = ''

        return self.base + sub + arrlist

    @property
    def item_type(self):
        """
        If this type is an array type, returns the type of the array's items.
        """
        if self.arrlist is None:
            raise ValueError(
                "Cannot determine item type for non-array type '{}'".format(self)
            )

        return type(self)(
            self.base,
            self.sub,
            self.arrlist[:-1] or None,
            node=self.node,
        )

    def validate(self):
        """
        A basic type is valid if it appears to be one of the default types
        described in the solidity ABI spec and its components don't violate any
        of the assumptions set forth in that spec -or- if it does not appear to
        be a default type.
        Details found here:
        https://solidity.readthedocs.io/en/develop/abi-spec.html
        """
        base, sub = self.base, self.sub

        # Check validity of string type
        if base == 'string':
            if sub is not None:
                self.invalidate('string type cannot have suffix')

        # Check validity of bytes type
        elif base == 'bytes':
            if not (sub is None or isinstance(sub, int)):
                self.invalidate('bytes type must have either no suffix or a numerical suffix')

            if isinstance(sub, int) and sub > 32:
                self.invalidate('maximum 32 bytes for fixed-length bytes')

        # Check validity of integer type
        elif base in ('int', 'uint'):
            if not isinstance(sub, int):
                self.invalidate('integer type must have numerical suffix')

            if sub < 8 or 256 < sub:
                self.invalidate('integer size out of bounds (max 256 bits)')

            if sub % 8 != 0:
                self.invalidate('integer size must be multiple of 8')

        # Check validity of fixed type
        elif base in ('fixed', 'ufixed'):
            if not isinstance(sub, tuple):
                self.invalidate(
                    'fixed type must have suffix of form <bits>x<exponent>, e.g. 128x19',
                )

            bits, minus_e = sub

            if bits < 8 or 256 < bits:
                self.invalidate('fixed size out of bounds (max 256 bits)')

            if bits % 8 != 0:
                self.invalidate('fixed size must be multiple of 8')

            if minus_e < 1 or 80 < minus_e:
                self.invalidate(
                    'fixed exponent size out of bounds, {} must be in 1-80'.format(
                        minus_e,
                    ),
                )

        # Check validity of real type
        elif base in ('real', 'ureal'):
            if not isinstance(sub, tuple):
                self.invalidate('real type must have suffix of form <high>x<low>, e.g. 128x128')

            high, low = sub

            if (high + low) < 8 or 256 < (high + low):
                self.invalidate('real size out of bounds (max 256 bits)')

            if high % 8 != 0 or low % 8 != 0:
                self.invalidate('real high/low sizes must be multiples of 8')

        # Check validity of hash type
        elif base == 'hash':
            if not isinstance(sub, int):
                self.invalidate('hash type must have numerical suffix')

        # Check validity of address type
        elif base == 'address':
            if sub is not None:
                self.invalidate('address cannot have suffix')


TYPE_ALIASES = {
    'int': 'int256',
    'uint': 'uint256',
    'fixed': 'fixed128x18',
    'ufixed': 'ufixed128x18',
    'function': 'bytes24',
}

TYPE_ALIAS_RE = re.compile(r'\b({})\b'.format(
    '|'.join(re.escape(a) for a in TYPE_ALIASES.keys())
))


def normalize(type_str):
    # Replace aliases with substitutions
    return TYPE_ALIAS_RE.sub(
        lambda match: TYPE_ALIASES[match.group(0)],
        type_str,
    )


parse = visitor.parse






def collapse_type(base, sub, arrlist):
    return base + sub + ''.join(map(repr, arrlist))

def process_type(type_str):
    normalized_type_str = normalize(type_str)
    abi_type = parse(normalized_type_str)

    type_str_repr = repr(type_str)
    if type_str != normalized_type_str:
        type_str_repr = '{} (normalized to {})'.format(
            type_str_repr,
            repr(normalized_type_str),
        )

    if isinstance(abi_type, TupleType):
        raise ValueError(
            "Cannot process type {}: tuple types not supported".format(
                type_str_repr,
            )
        )

    abi_type.validate()

    sub = abi_type.sub
    if isinstance(sub, tuple):
        sub = 'x'.join(map(str, sub))
    elif isinstance(sub, int):
        sub = str(sub)
    else:
        sub = ''

    arrlist = abi_type.arrlist
    if isinstance(arrlist, tuple):
        arrlist = list(map(list, arrlist))
    else:
        arrlist = []

    return abi_type.base, sub, arrlist


import re

TYPE_ALIASES = {
    'int': 'int256',
    'uint': 'uint256',
    'fixed': 'fixed128x18',
    'ufixed': 'ufixed128x18',
    'function': 'bytes24',
}

TYPE_ALIAS_RE = re.compile(r'\b({})\b'.format(
    '|'.join(re.escape(a) for a in TYPE_ALIASES.keys())
))


def normalize(type_str):
    # Replace aliases with substitutions
    return TYPE_ALIAS_RE.sub(
        lambda match: TYPE_ALIASES[match.group(0)],
        type_str,
    )



