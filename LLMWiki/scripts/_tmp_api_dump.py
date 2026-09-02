# -*- coding: utf-8 -*-
"""Minimal CLI metadata reader: dumps TypeDef members for a target type."""
import struct
import sys

path = sys.argv[1]
want = sys.argv[2].encode() if len(sys.argv) > 2 else b''
data = open(path, 'rb').read()

pe_off = struct.unpack_from('<I', data, 0x3C)[0]
assert data[pe_off:pe_off + 4] == b'PE\0\0'
nsec = struct.unpack_from('<H', data, pe_off + 6)[0]
opt_size = struct.unpack_from('<H', data, pe_off + 20)[0]
opt_off = pe_off + 24
sect_off = opt_off + opt_size
sections = []
for i in range(nsec):
    o = sect_off + i * 40
    name = data[o:o + 8].rstrip(b'\0')
    vsize, vaddr, rsize, raddr = struct.unpack_from('<IIII', data, o + 8)
    sections.append((name, vaddr, vsize, raddr, rsize))


def rva2off(rva):
    for name, vaddr, vsize, raddr, rsize in sections:
        if vaddr <= rva < vaddr + max(vsize, rsize):
            return raddr + (rva - vaddr)
    return None


magic = struct.unpack_from('<H', data, opt_off)[0]
if magic == 0x20B:
    cli_dir = 208
else:
    cli_dir = 208
cli_rva, cli_size = struct.unpack_from('<II', data, opt_off + cli_dir)
cli = rva2off(cli_rva)
md_rva, md_size = struct.unpack_from('<II', data, cli + 8)
md = rva2off(md_rva)
ver_len = struct.unpack_from('<I', data, md + 12)[0]
p = md + 16 + ver_len
p += 2  # Flags
nstreams = struct.unpack_from('<H', data, p)[0]
p += 2
streams = {}
for _ in range(nstreams):
    off, size = struct.unpack_from('<II', data, p)
    p += 8
    name = b''
    while data[p] != 0:
        name += bytes([data[p]])
        p += 1
    p += 1
    p = (p + 3) & ~3
    streams[name.decode()] = (md + off, size)

str_base = streams['#Strings'][0]
blob_base = streams['#Blob'][0]
tbl_off, tbl_size = streams['#~']
tp = tbl_off
reserved, major, minor, heapsizes, reserved2 = struct.unpack_from('<IBBBB', data, tp)
tp += 8
valid = struct.unpack_from('<Q', data, tp)[0]
tp += 8
sorted_ = struct.unpack_from('<Q', data, tp)[0]
tp += 8

row_counts = {}
tid = 0
while valid:
    if valid & 1:
        c = struct.unpack_from('<I', data, tp)[0]
        tp += 4
        row_counts[tid] = c
    valid >>= 1
    tid += 1

str_idx = 4 if heapsizes & 1 else 2
guid_idx = 4 if heapsizes & 2 else 2
blob_idx = 4 if heapsizes & 4 else 2


def idx_size(tables):
    m = max(row_counts.get(t, 0) for t in tables)
    return 4 if m >= (1 << 16) else 2


def tag_size(tables, bits):
    m = max(row_counts.get(t, 0) for t in tables)
    return 4 if m >= (1 << (16 - bits)) else 2


typedef_or_ref = [0x00, 0x01, 0x1B]
has_constant = [0x04, 0x08, 0x17]
has_custom_attribute = [0x06, 0x04, 0x01, 0x00, 0x08, 0x09, 0x0A, 0x00, 0x0E, 0x17, 0x14,
                        0x11, 0x1A, 0x1B, 0x20, 0x23, 0x26, 0x27, 0x28, 0x2A, 0x2C, 0x2B]
has_field_marshal = [0x04, 0x08]
has_decl_security = [0x00, 0x06, 0x20]
member_ref_parent = [0x00, 0x01, 0x1A, 0x06, 0x1B]
has_semantics = [0x14, 0x17]
method_def_or_ref = [0x06, 0x0A]
member_forwarded = [0x04, 0x06]
implementation = [0x26, 0x23, 0x27]
custom_attribute_type = [0x00, 0x00, 0x06, 0x0A, 0x00]
resolution_scope = [0x00, 0x1A, 0x23, 0x01]
type_or_method_def = [0x00, 0x06]

SCHEMA = {
    0x00: (('Generation', 2), ('Name', 'S'), ('Mvid', 'G'), ('EncId', 'G'), ('EncBaseId', 'G')),
    0x01: (('ResolutionScope', ('C', resolution_scope)), ('Name', 'S'), ('Namespace', 'S')),
    0x02: (('Flags', 4), ('Name', 'S'), ('Namespace', 'S'),
           ('Extends', ('C', typedef_or_ref)), ('FieldList', ('T', 0x04)), ('MethodList', ('T', 0x06))),
    0x03: (('Field', ('T', 0x04)),),
    0x04: (('Flags', 2), ('Name', 'S'), ('Signature', 'B')),
    0x05: (('Method', ('T', 0x06)),),
    0x06: (('RVA', 4), ('ImplFlags', 2), ('Flags', 2), ('Name', 'S'), ('Signature', 'B'),
           ('ParamList', ('T', 0x08))),
    0x07: (('Param', ('T', 0x08)),),
    0x08: (('Flags', 2), ('Sequence', 2), ('Name', 'S')),
    0x09: (('Class', ('T', 0x02)), ('Interface', ('C', typedef_or_ref))),
    0x0A: (('Class', ('C', member_ref_parent)), ('Name', 'S'), ('Signature', 'B')),
    0x0B: (('Type', 1), ('Padding', 1), ('Parent', ('C', has_constant)), ('Value', 'B')),
    0x0C: (('Parent', ('C', has_custom_attribute)), ('Type', ('C', custom_attribute_type)),
           ('Value', 'B')),
    0x0D: (('Parent', ('C', has_field_marshal)), ('NativeType', 'B')),
    0x0E: (('Action', 2), ('Parent', ('C', has_decl_security)), ('PermissionSet', 'B')),
    0x0F: (('PackingSize', 2), ('ClassSize', 4), ('Parent', ('T', 0x02))),
    0x10: (('Offset', 4), ('Field', ('T', 0x04))),
    0x11: (('Signature', 'B'),),
    0x12: (('Parent', ('T', 0x02)), ('EventList', ('T', 0x14))),
    0x13: (('Event', ('T', 0x14)),),
    0x14: (('EventFlags', 2), ('Name', 'S'), ('EventType', ('C', typedef_or_ref))),
    0x15: (('Parent', ('T', 0x02)), ('PropertyList', ('T', 0x17))),
    0x16: (('Property', ('T', 0x17)),),
    0x17: (('Flags', 2), ('Name', 'S'), ('Type', 'B')),
    0x18: (('Semantics', 2), ('Method', ('T', 0x06)), ('Association', ('C', has_semantics))),
    0x19: (('Class', ('T', 0x02)), ('MethodBody', ('C', method_def_or_ref)),
           ('MethodDeclaration', ('C', method_def_or_ref))),
    0x1A: (('Name', 'S'),),
    0x1B: (('Signature', 'B'),),
    0x1C: (('MappingFlags', 2), ('MemberForwarded', ('C', member_forwarded)),
           ('ImportName', 'S'), ('ImportScope', ('T', 0x1A))),
    0x1D: (('RVA', 4), ('Field', ('T', 0x04))),
    0x20: (('HashAlgId', 4), ('Major', 2), ('Minor', 2), ('Build', 2), ('Rev', 2),
           ('Flags', 4), ('PublicKey', 'B'), ('Name', 'S'), ('Culture', 'S')),
    0x23: (('Major', 2), ('Minor', 2), ('Build', 2), ('Rev', 2), ('Flags', 4),
           ('PublicKeyOrToken', 'B'), ('Name', 'S'), ('Culture', 'S'), ('HashValue', 'B')),
    0x26: (('Flags', 4), ('Name', 'S'), ('HashValue', 'B')),
    0x27: (('Flags', 4), ('TypeDefId', 4), ('TypeName', 'S'), ('TypeNamespace', 'S'),
           ('Implementation', ('C', implementation))),
    0x28: (('Offset', 4), ('Flags', 4), ('Name', 'S'), ('Implementation', ('C', implementation))),
    0x29: (('Nested', ('T', 0x02)), ('Enclosing', ('T', 0x02))),
    0x2A: (('Number', 2), ('Flags', 2), ('Owner', ('C', type_or_method_def)), ('Name', 'S')),
    0x2B: (('Method', ('C', method_def_or_ref)), ('Instantiation', 'B')),
    0x2C: (('Owner', ('T', 0x2A)), ('Constraint', ('C', typedef_or_ref))),
}

rows = {}
for tid_ in sorted(row_counts):
    if tid_ not in SCHEMA:
        # unknown table: advance using a generic size map is unsafe -> abort
        raise SystemExit('unsupported table 0x%02X present; extend schema' % tid_)
    cols = SCHEMA[tid_]
    n = row_counts[tid_]
    recs = []
    for _ in range(n):
        rec = {}
        for cname, ctype in cols:
            if ctype == 'S':
                v = struct.unpack_from('<I' if str_idx == 4 else '<H', data, tp)[0]
                tp += str_idx
                e = data.index(b'\0', str_base + v)
                rec[cname] = data[str_base + v:e].decode('utf-8', 'replace')
            elif ctype == 'B':
                v = struct.unpack_from('<I' if blob_idx == 4 else '<H', data, tp)[0]
                tp += blob_idx
                rec[cname] = blob_base + v
            elif isinstance(ctype, tuple) and ctype[0] == 'C':
                sz = tag_size(ctype[1], 2)
                raw = int.from_bytes(data[tp:tp + sz], 'little')
                tp += sz
                rec[cname] = (ctype[1][raw & 3], raw >> 2)
            elif isinstance(ctype, tuple) and ctype[0] == 'T':
                sz = idx_size([ctype[1]])
                rec[cname] = int.from_bytes(data[tp:tp + sz], 'little')
                tp += sz
            else:
                rec[cname] = int.from_bytes(data[tp:tp + ctype], 'little')
                tp += ctype
        recs.append(rec)
    rows[tid_] = recs

typedefs = rows.get(0x00, [])


def get_str(off):
    e = data.index(b'\0', off)
    return data[off:e].decode('utf-8', 'replace')


def blob_len(off):
    b0 = data[off]
    if b0 & 0x80 == 0:
        return 1, b0
    if b0 & 0xC0 == 0x80:
        return 2, ((b0 & 0x3F) << 8) | data[off + 1]
    if b0 & 0xE0 == 0xC0:
        return 4, ((b0 & 0x1F) << 24) | (data[off + 1] << 16) | (data[off + 2] << 8) | data[off + 3]
    raise ValueError


def decompress(off):
    b0 = data[off]
    if b0 & 0x80 == 0:
        return off + 1, b0
    if b0 & 0xC0 == 0x80:
        return off + 2, ((b0 & 0x3F) << 8) | data[off + 1]
    return off + 4, ((b0 & 0x1F) << 24) | (data[off + 1] << 16) | (data[off + 2] << 8) | data[off + 3]


ELEMENT_NAMES = {
    0x01: 'void', 0x02: 'bool', 0x03: 'char', 0x04: 'sbyte', 0x05: 'byte', 0x06: 'short',
    0x07: 'ushort', 0x08: 'int', 0x09: 'uint', 0x0A: 'long', 0x0B: 'ulong', 0x0C: 'float',
    0x0D: 'double', 0x0E: 'string', 0x16: 'typedref', 0x18: 'IntPtr', 0x19: 'UIntPtr',
    0x1C: 'object',
}


def read_type(off):
    e = data[off]
    off += 1
    if e in ELEMENT_NAMES:
        return off, ELEMENT_NAMES[e]
    if e in (0x0F, 0x10, 0x11, 0x12, 0x13, 0x14, 0x15, 0x1D, 0x1E, 0x1F, 0x41, 0x45, 0x50, 0x51, 0x52, 0x53, 0x54, 0x55):
        # PTR 0x0F, BYREF 0x10, VALUETYPE 0x11, CLASS 0x12, VAR 0x13, ARRAY 0x14,
        # GENERICINST 0x15, PINNED 0x45, SZARRAY 0x1D, MVAR 0x1E, CMOD_REQD 0x1F, CMOD_OPT 0x20,
        # SENTINEL 0x41
        if e in (0x13, 0x1E):
            off, v = decompress(off)
            return off, ('!' if e == 0x13 else '!!') + str(v)
        if e in (0x0F, 0x10, 0x11, 0x12, 0x45):
            off, tok = decompress(off)
            tbl = tok & 3
            rid = tok >> 2
            tn = {0: 'TypeDef', 1: 'TypeRef', 2: 'TypeSpec'}.get(tbl, '?')
            if tbl == 0 and rid - 1 < len(typedefs):
                td = typedefs[rid - 1]
                nm = (td['Namespace'] + '.' if td['Namespace'] else '') + td['Name']
                return off, nm
            if tbl == 1 and rid - 1 < len(rows.get(0x01, [])):
                tr = rows[0x01][rid - 1]
                return off, (tr['Namespace'] + '.' if tr['Namespace'] else '') + tr['Name']
            return off, tn + '#' + str(rid)
        if e == 0x1D:  # SZARRAY
            off, inner = read_type(off)
            return off, inner + '[]'
        if e == 0x14:  # ARRAY
            off, inner = read_type(off)
            off, rank = decompress(off)
            return off, inner + '[' + ','.join([''] * rank) + ']'
        if e == 0x15:  # GENERICINST
            off, inner = read_type(off)
            off, cnt = decompress(off)
            args = []
            for _ in range(cnt):
                off, a = read_type(off)
                args.append(a)
            return off, inner + '<' + ','.join(args) + '>'
        if e in (0x1F, 0x20):
            off, tok = decompress(off)
            off, inner = read_type(off)
            return off, inner
        if e in (0x41,):
            return off, '...'
        return off, 'ELEM_0x%02X' % e
    raise ValueError('unknown element 0x%02X at %d' % (e, off - 1))


def decode_method_sig(off):
    n, ln = blob_len(off)
    body = off + n
    p = body
    flags = data[p]
    p += 1
    if flags & 0x20:
        p, _ = decompress(p)
    p, pcount = decompress(p)
    p, ret = read_type(p)
    params = []
    for _ in range(pcount):
        p, pt = read_type(p)
        params.append(pt)
    return params, ret


params_by_id = {}
for pr in rows.get(0x08, []):
    params_by_id.setdefault(pr.get('_rid'), [])

for i, td in enumerate(typedefs):
    full = (td['Namespace'] + '.' if td['Namespace'] else '') + td['Name']
    if want and want.decode() not in full:
        continue
    print('=' * 70)
    print('TYPE', full, 'rows flags=0x%08X' % td['Flags'],
          'visibility=0x%X' % (td['Flags'] & 7))
    # methods
    mstart = td['MethodList']
    if i + 1 < len(typedefs):
        mend = typedefs[i + 1]['MethodList']
    else:
        mend = len(rows.get(0x06, [])) + 1
    for mi in range(mstart - 1, mend - 1):
        if mi >= len(rows.get(0x06, [])):
            break
        m = rows[0x06][mi]
        try:
            params, ret = decode_method_sig(m['Signature'])
        except Exception as ex:
            params, ret = (['<sig err %s>' % ex], '?')
        vis = m['Flags'] & 7
        vname = {0: 'private', 1: 'public', 2: 'public', 3: 'protected',
                 4: 'protected', 5: 'protected internal', 6: 'public'}.get(vis, str(vis))
        static = 'static ' if m['Flags'] & 0x10 else ''
        print('   METHOD %s%s %s(%s)' % (static, ret, m['Name'], ', '.join(params)))
    # fields
    fstart = td['FieldList']
    if i + 1 < len(typedefs):
        fend = typedefs[i + 1]['FieldList']
    else:
        fend = len(rows.get(0x04, [])) + 1
    for fi in range(fstart - 1, fend - 1):
        if fi >= len(rows.get(0x04, [])):
            break
        f = rows[0x04][fi]
        vis = f['Flags'] & 7
        vname = {0: 'private', 1: 'public', 3: 'protected', 4: 'protected',
                 5: 'protected internal', 6: 'public'}.get(vis, str(vis))
        print('   FIELD  %s %s' % (vname, f['Name']))
