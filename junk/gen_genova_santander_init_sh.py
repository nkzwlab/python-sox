#!/usr/bin/python

print '#!/bin/sh'

# generate genova node creation commands
print '\n# generate genova node creation commands'
g_id_start = 5
g_id_end = 32
g_id = g_id_start
while g_id <= g_id_end:
    print 'python create_node.py genova%d_data' % g_id
    print 'python create_node.py genova%d_meta' % g_id
    g_id += 1

# generate santander node creation commands
print '\n# generate santander node creation commands'
s_ids = (173, 181, 193, 199)
for s_id in s_ids:
    print 'python create_node.py santander%d_data' % s_id
    print 'python create_node.py santander%d_meta' % s_id
    s_id += 1

# generate genova meta post commands
print '\n# generate genova meta post commands'
print 'python genova_meta_post.py'

# generate santande meta post commands
print '\n# generate santande meta post commands'
print 'python santander_meta_post.py'

